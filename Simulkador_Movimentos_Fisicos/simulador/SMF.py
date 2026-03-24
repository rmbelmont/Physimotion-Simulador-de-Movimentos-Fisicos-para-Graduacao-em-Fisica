import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from matplotlib.animation import FuncAnimation
import tkinter as tk
from tkinter import ttk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
import threading

class SimuladorMovimentos:
    def __init__(self):
        self.modo_atual = 'MRU'
        self.parametros = {
            'MRU': {'v': 10, 'pos_inicial': 0},
            'MRUV': {'v0': 10, 'a': 2, 'pos_inicial': 0},
            'MCU': {'r': 5, 'omega': 2, 'centro_x': 0, 'centro_y': 0},
            'MHS': {'A': 5, 'f': 0.5, 'phi': 0},
            'Queda_Livre': {'v0': 0, 'altura_inicial': 100},
            'Lancamento_Obliquo': {'v0': 20, 'angulo': 45, 'g': 9.81}
        }
        self.historico = []
        self.animacao = None
        self.fig = None
        self.ax = None
        
    def calcular_mru(self, t, v, pos_inicial=0):
        x = pos_inicial + v * t
        y = np.zeros_like(t)
        z = np.zeros_like(t)
        return x, y, z
    
    def calcular_mruv(self, t, v0, a, pos_inicial=0):
        x = pos_inicial + v0 * t + 0.5 * a * t**2
        y = np.zeros_like(t)
        z = np.zeros_like(t)
        return x, y, z
    
    def calcular_mcu(self, t, r, omega, centro_x=0, centro_y=0):
        angulo = omega * t
        x = centro_x + r * np.cos(angulo)
        y = centro_y + r * np.sin(angulo)
        z = np.zeros_like(t)
        return x, y, z
    
    def calcular_mhs(self, t, A, f, phi=0):
        omega = 2 * np.pi * f
        x = A * np.sin(omega * t + phi)
        y = np.zeros_like(t)
        z = np.zeros_like(t)
        return x, y, z
    
    def calcular_queda_livre(self, t, altura_inicial, v0=0, g=9.81):
        y = altura_inicial + v0 * t - 0.5 * g * t**2
        y = np.maximum(y, 0)
        x = np.zeros_like(t)
        z = np.zeros_like(t)
        return x, y, z
    
    def calcular_lancamento_obliquo(self, t, v0, angulo, g=9.81):
        angulo_rad = np.radians(angulo)
        v0x = v0 * np.cos(angulo_rad)
        v0y = v0 * np.sin(angulo_rad)
        x = v0x * t
        y = v0y * t - 0.5 * g * t**2
        y = np.maximum(y, 0)
        z = np.zeros_like(t)
        return x, y, z
    
    def obter_tempo_total(self):
        if self.modo_atual == 'MRU':
            return 10
        elif self.modo_atual == 'MRUV':
            return 10
        elif self.modo_atual == 'MCU':
            return 2 * np.pi / self.parametros['MCU']['omega'] * 2
        elif self.modo_atual == 'MHS':
            return 2 / self.parametros['MHS']['f'] * 2
        elif self.modo_atual == 'Queda_Livre':
            h = self.parametros['Queda_Livre']['altura_inicial']
            g = 9.81
            t_total = np.sqrt(2 * h / g)
            return t_total
        elif self.modo_atual == 'Lancamento_Obliquo':
            v0 = self.parametros['Lancamento_Obliquo']['v0']
            angulo = self.parametros['Lancamento_Obliquo']['angulo']
            g = self.parametros['Lancamento_Obliquo']['g']
            angulo_rad = np.radians(angulo)
            v0y = v0 * np.sin(angulo_rad)
            t_total = 2 * v0y / g
            return max(t_total, 0.1)
        return 10
    
    def calcular_trajetoria(self):
        t_total = self.obter_tempo_total()
        t = np.linspace(0, t_total, 200)
        
        if self.modo_atual == 'MRU':
            p = self.parametros['MRU']
            return self.calcular_mru(t, p['v'], p['pos_inicial'])
        elif self.modo_atual == 'MRUV':
            p = self.parametros['MRUV']
            return self.calcular_mruv(t, p['v0'], p['a'], p['pos_inicial'])
        elif self.modo_atual == 'MCU':
            p = self.parametros['MCU']
            return self.calcular_mcu(t, p['r'], p['omega'], p['centro_x'], p['centro_y'])
        elif self.modo_atual == 'MHS':
            p = self.parametros['MHS']
            return self.calcular_mhs(t, p['A'], p['f'], p['phi'])
        elif self.modo_atual == 'Queda_Livre':
            p = self.parametros['Queda_Livre']
            return self.calcular_queda_livre(t, p['altura_inicial'], p['v0'])
        elif self.modo_atual == 'Lancamento_Obliquo':
            p = self.parametros['Lancamento_Obliquo']
            return self.calcular_lancamento_obliquo(t, p['v0'], p['angulo'], p['g'])
        return np.array([]), np.array([]), np.array([])
    
    def atualizar_parametro(self, modo, parametro, valor):
        if modo in self.parametros:
            if parametro in self.parametros[modo]:
                self.salvar_historico()
                self.parametros[modo][parametro] = valor
                return True
        return False
    
    def salvar_historico(self):
        x, y, z = self.calcular_trajetoria()
        self.historico.append({
            'modo': self.modo_atual,
            'parametros': self.parametros[self.modo_atual].copy(),
            'trajetoria': (x.copy(), y.copy(), z.copy())
        })
        if len(self.historico) > 20:
            self.historico.pop(0)
    
    def plotar_grafico(self, ax):
        """Plota o gráfico 3D com histórico - VERSÃO CORRIGIDA"""
        ax.clear()
        
        x, y, z = self.calcular_trajetoria()
        
        # Plotar histórico com cores fixas
        if self.historico:
            cores = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', 
                     '#8c564b', '#e377c2', '#7f7f7f', '#bcbd22', '#17becf']
            
            for i, hist in enumerate(self.historico):
                x_hist, y_hist, z_hist = hist['trajetoria']
                alpha = 0.3 * (i + 1) / len(self.historico)
                cor = cores[i % len(cores)]
                ax.plot(x_hist, y_hist, z_hist, '--', 
                       color=cor, linewidth=1, alpha=alpha,
                       label=f'Versão {i+1}' if i < 5 else "")
        
        # Plotar trajetória atual
        if len(x) > 0:
            ax.plot(x, y, z, 'b-', linewidth=3, label='Trajetória Atual', alpha=0.9)
            ax.scatter(x[0], y[0], z[0], color='green', s=100, label='Início', alpha=0.8)
            ax.scatter(x[-1], y[-1], z[-1], color='red', s=100, label='Fim', alpha=0.8)
        
        # Informações
        info_text = self.get_info_text()
        ax.text2D(0.02, 0.98, info_text, transform=ax.transAxes, 
                 fontsize=10, verticalalignment='top',
                 bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8))
        
        ax.set_xlabel('X (m)', fontsize=12)
        ax.set_ylabel('Y (m)', fontsize=12)
        ax.set_zlabel('Z (m)', fontsize=12)
        ax.set_title(f'Simulador de Movimentos - {self.modo_atual}', fontsize=14, fontweight='bold')
        ax.legend(loc='upper right', fontsize=9)
        ax.grid(True, alpha=0.3)
        
        self.ajustar_limites(ax, x, y, z)
        return ax
    
    def ajustar_limites(self, ax, x, y, z):
        all_x = [x]
        all_y = [y]
        all_z = [z]
        
        for hist in self.historico:
            xh, yh, zh = hist['trajetoria']
            if len(xh) > 0:
                all_x.append(xh)
                all_y.append(yh)
                all_z.append(zh)
        
        try:
            x_all = np.concatenate(all_x) if all_x else x
            y_all = np.concatenate(all_y) if all_y else y
            z_all = np.concatenate(all_z) if all_z else z
            
            if len(x_all) > 0:
                x_min, x_max = np.min(x_all), np.max(x_all)
                y_min, y_max = np.min(y_all), np.max(y_all)
                z_min, z_max = np.min(z_all), np.max(z_all)
                
                margin = 0.1
                x_range = max(x_max - x_min, 1) * margin
                y_range = max(y_max - y_min, 1) * margin
                z_range = max(z_max - z_min, 1) * margin
                
                ax.set_xlim([x_min - x_range, x_max + x_range])
                ax.set_ylim([y_min - y_range, y_max + y_range])
                ax.set_zlim([z_min - z_range, z_max + z_range])
        except:
            pass
    
    def get_info_text(self):
        if self.modo_atual == 'MRU':
            p = self.parametros['MRU']
            return f"MRU\nv = {p['v']} m/s\nx₀ = {p['pos_inicial']} m"
        elif self.modo_atual == 'MRUV':
            p = self.parametros['MRUV']
            return f"MRUV\nv₀ = {p['v0']} m/s\na = {p['a']} m/s²\nx₀ = {p['pos_inicial']} m"
        elif self.modo_atual == 'MCU':
            p = self.parametros['MCU']
            return f"MCU\nr = {p['r']} m\nω = {p['omega']} rad/s\nT = {2*np.pi/p['omega']:.2f} s"
        elif self.modo_atual == 'MHS':
            p = self.parametros['MHS']
            f = p['f']
            return f"MHS\nA = {p['A']} m\nf = {f} Hz\nT = {1/f:.2f} s"
        elif self.modo_atual == 'Queda_Livre':
            p = self.parametros['Queda_Livre']
            t_total = self.obter_tempo_total()
            return f"Queda Livre\nh₀ = {p['altura_inicial']} m\nv₀ = {p['v0']} m/s\nt = {t_total:.2f} s"
        elif self.modo_atual == 'Lancamento_Obliquo':
            p = self.parametros['Lancamento_Obliquo']
            ang_rad = np.radians(p['angulo'])
            v0x = p['v0'] * np.cos(ang_rad)
            v0y = p['v0'] * np.sin(ang_rad)
            t_total = 2 * v0y / p['g']
            alcance = v0x * t_total
            altura_max = (v0y**2) / (2 * p['g'])
            return f"Lançamento Oblíquo\nv₀ = {p['v0']} m/s\nθ = {p['angulo']}°\nAlcance = {alcance:.1f} m\nHmax = {altura_max:.1f} m"
        return ""

# Classe AppTkinter e versao_terminal permanecem iguais...
# (mantenha o resto do código igual)

if __name__ == "__main__":
    print("Escolha a versão:")
    print("1 - Versão Terminal (mais simples)")
    print("2 - Versão Gráfica Tkinter (mais completa)")
    
    escolha = input("Digite 1 ou 2: ").strip()
    
    if escolha == '1':
        # Criar uma versão simplificada para terminal
        simulador = SimuladorMovimentos()
        
        while True:
            print(f"\n📊 MOVIMENTO: {simulador.modo_atual}")
            params = simulador.parametros[simulador.modo_atual]
            for key, value in params.items():
                print(f"   {key}: {value}")
            
            print("\n1-Mudar modo 2-Modificar 3-Gráfico 4-Sair")
            opcao = input("Escolha: ")
            
            if opcao == '3':
                fig = plt.figure(figsize=(10, 8))
                ax = fig.add_subplot(111, projection='3d')
                simulador.plotar_grafico(ax)
                plt.show()
            elif opcao == '4':
                break
    elif escolha == '2':
        # Versão gráfica completa
        root = tk.Tk()
        
        # Classe AppTkinter simplificada
        class AppSimples:
            def __init__(self, root):
                self.root = root
                self.root.title("Simulador de Movimentos")
                self.root.geometry("1200x700")
                self.simulador = SimuladorMovimentos()
                
                # Frame para o gráfico
                self.fig_frame = ttk.Frame(root)
                self.fig_frame.pack(fill=tk.BOTH, expand=True)
                
                self.fig = plt.figure(figsize=(8, 6))
                self.ax = self.fig.add_subplot(111, projection='3d')
                self.canvas = FigureCanvasTkAgg(self.fig, master=self.fig_frame)
                self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
                
                # Frame de controles
                control_frame = ttk.Frame(root)
                control_frame.pack(side=tk.BOTTOM, fill=tk.X, padx=10, pady=10)
                
                ttk.Label(control_frame, text="Movimento:").pack(side=tk.LEFT, padx=5)
                self.modo_var = tk.StringVar(value='MRU')
                modos = ['MRU', 'MRUV', 'MCU', 'MHS', 'Queda_Livre', 'Lancamento_Obliquo']
                self.modo_combo = ttk.Combobox(control_frame, textvariable=self.modo_var, 
                                               values=modos, state='readonly', width=15)
                self.modo_combo.pack(side=tk.LEFT, padx=5)
                self.modo_combo.bind('<<ComboboxSelected>>', self.mudar_modo)
                
                ttk.Button(control_frame, text="Atualizar Gráfico", 
                          command=self.atualizar_grafico).pack(side=tk.LEFT, padx=20)
                
                self.atualizar_grafico()
            
            def mudar_modo(self, event):
                self.simulador.modo_atual = self.modo_var.get()
                self.atualizar_grafico()
            
            def atualizar_grafico(self):
                self.simulador.plotar_grafico(self.ax)
                self.canvas.draw()
        
        app = AppSimples(root)
        root.mainloop()
    else:
        print("Opção inválida!")