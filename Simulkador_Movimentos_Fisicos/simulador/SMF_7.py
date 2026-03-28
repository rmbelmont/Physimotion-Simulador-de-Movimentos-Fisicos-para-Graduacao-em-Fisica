import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
import json
from datetime import datetime

# Configurar matplotlib
import matplotlib
matplotlib.use('TkAgg')

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
        self.callback_atualizacao = None
        
    def set_callback(self, callback):
        self.callback_atualizacao = callback
        
    def calcular_trajetoria(self):
        t_total = self.obter_tempo_total()
        t = np.linspace(0, t_total, 500)
        
        if self.modo_atual == 'MRU':
            p = self.parametros['MRU']
            x = p['pos_inicial'] + p['v'] * t
            return x, np.zeros_like(t), np.zeros_like(t)
        elif self.modo_atual == 'MRUV':
            p = self.parametros['MRUV']
            x = p['pos_inicial'] + p['v0'] * t + 0.5 * p['a'] * t**2
            return x, np.zeros_like(t), np.zeros_like(t)
        elif self.modo_atual == 'MCU':
            p = self.parametros['MCU']
            angulo = p['omega'] * t
            x = p['centro_x'] + p['r'] * np.cos(angulo)
            y = p['centro_y'] + p['r'] * np.sin(angulo)
            return x, y, np.zeros_like(t)
        elif self.modo_atual == 'MHS':
            p = self.parametros['MHS']
            omega = 2 * np.pi * p['f']
            x = p['A'] * np.sin(omega * t + p['phi'])
            return x, np.zeros_like(t), np.zeros_like(t)
        elif self.modo_atual == 'Queda_Livre':
            p = self.parametros['Queda_Livre']
            y = p['altura_inicial'] + p['v0'] * t - 0.5 * 9.81 * t**2
            y = np.maximum(y, 0)
            return np.zeros_like(t), y, np.zeros_like(t)
        elif self.modo_atual == 'Lancamento_Obliquo':
            p = self.parametros['Lancamento_Obliquo']
            ang_rad = np.radians(p['angulo'])
            v0x = p['v0'] * np.cos(ang_rad)
            v0y = p['v0'] * np.sin(ang_rad)
            x = v0x * t
            y = v0y * t - 0.5 * p['g'] * t**2
            y = np.maximum(y, 0)
            return x, y, np.zeros_like(t)
        return np.array([]), np.array([]), np.array([])
    
    def obter_tempo_total(self):
        if self.modo_atual == 'MRU' or self.modo_atual == 'MRUV':
            return 10
        elif self.modo_atual == 'MCU':
            return 2 * np.pi / self.parametros['MCU']['omega'] * 2
        elif self.modo_atual == 'MHS':
            return 2 / self.parametros['MHS']['f']
        elif self.modo_atual == 'Queda_Livre':
            h = self.parametros['Queda_Livre']['altura_inicial']
            return np.sqrt(2 * h / 9.81)
        elif self.modo_atual == 'Lancamento_Obliquo':
            p = self.parametros['Lancamento_Obliquo']
            ang_rad = np.radians(p['angulo'])
            v0y = p['v0'] * np.sin(ang_rad)
            return max(2 * v0y / p['g'], 0.1)
        return 10
    
    def atualizar_parametro(self, parametro, valor):
        if parametro in self.parametros[self.modo_atual]:
            self.parametros[self.modo_atual][parametro] = valor
            if self.callback_atualizacao:
                self.callback_atualizacao()
            return True
        return False
    
    def salvar_historico(self):
        x, y, z = self.calcular_trajetoria()
        self.historico.append({
            'modo': self.modo_atual,
            'parametros': self.parametros[self.modo_atual].copy(),
            'trajetoria': (x.copy(), y.copy(), z.copy()),
            'timestamp': datetime.now().isoformat()
        })
        if len(self.historico) > 10:
            self.historico.pop(0)
        if self.callback_atualizacao:
            self.callback_atualizacao()
    
    def get_info_text(self):
        p = self.parametros[self.modo_atual]
        if self.modo_atual == 'MRU':
            return f"MRU\nv = {p['v']} m/s\nx₀ = {p['pos_inicial']} m"
        elif self.modo_atual == 'MRUV':
            return f"MRUV\nv₀ = {p['v0']} m/s\na = {p['a']} m/s²\nx₀ = {p['pos_inicial']} m"
        elif self.modo_atual == 'MCU':
            return f"MCU\nr = {p['r']} m\nω = {p['omega']} rad/s"
        elif self.modo_atual == 'MHS':
            return f"MHS\nA = {p['A']} m\nf = {p['f']} Hz\nT = {1/p['f']:.2f} s"
        elif self.modo_atual == 'Queda_Livre':
            t = self.obter_tempo_total()
            return f"Queda Livre\nh₀ = {p['altura_inicial']} m\nv₀ = {p['v0']} m/s\nt = {t:.2f} s"
        elif self.modo_atual == 'Lancamento_Obliquo':
            ang_rad = np.radians(p['angulo'])
            v0y = p['v0'] * np.sin(ang_rad)
            t_total = 2 * v0y / p['g']
            v0x = p['v0'] * np.cos(ang_rad)
            alcance = v0x * t_total
            altura_max = (v0y**2) / (2 * p['g'])
            return f"Lançamento Oblíquo\nv₀ = {p['v0']} m/s\nθ = {p['angulo']}°\nAlcance = {alcance:.1f} m\nHmax = {altura_max:.1f} m"
        return ""
    
    def get_formula(self):
        formulas = {
            'MRU': 'x = x₀ + v·t',
            'MRUV': 'x = x₀ + v₀·t + ½·a·t²',
            'MCU': 'x = r·cos(ωt), y = r·sin(ωt)',
            'MHS': 'x = A·sin(2πft + φ)',
            'Queda_Livre': 'y = h₀ + v₀·t - ½·g·t²',
            'Lancamento_Obliquo': 'x = v₀·cosθ·t, y = v₀·sinθ·t - ½·g·t²'
        }
        return formulas.get(self.modo_atual, '')
    
    def get_formula_detalhada(self):
        formulas_detalhadas = {
            'MRU': 'x = x₀ + v·t\n\nOnde:\n• x = posição final (m)\n• x₀ = posição inicial (m)\n• v = velocidade constante (m/s)\n• t = tempo (s)',
            'MRUV': 'x = x₀ + v₀·t + ½·a·t²\n\nOnde:\n• x = posição final (m)\n• x₀ = posição inicial (m)\n• v₀ = velocidade inicial (m/s)\n• a = aceleração (m/s²)\n• t = tempo (s)',
            'MCU': 'x = r·cos(ωt)\ny = r·sin(ωt)\n\nOnde:\n• x, y = coordenadas (m)\n• r = raio da trajetória (m)\n• ω = velocidade angular (rad/s)\n• t = tempo (s)',
            'MHS': 'x = A·sin(2πft + φ)\n\nOnde:\n• x = posição (m)\n• A = amplitude (m)\n• f = frequência (Hz)\n• t = tempo (s)\n• φ = fase inicial (rad)',
            'Queda_Livre': 'y = h₀ + v₀·t - ½·g·t²\n\nOnde:\n• y = altura (m)\n• h₀ = altura inicial (m)\n• v₀ = velocidade inicial (m/s)\n• g = aceleração da gravidade (m/s²)\n• t = tempo (s)',
            'Lancamento_Obliquo': 'x = v₀·cosθ·t\ny = v₀·sinθ·t - ½·g·t²\n\nOnde:\n• x = alcance horizontal (m)\n• y = altura (m)\n• v₀ = velocidade inicial (m/s)\n• θ = ângulo de lançamento (°)\n• g = gravidade (m/s²)\n• t = tempo (s)'
        }
        return formulas_detalhadas.get(self.modo_atual, '')

class AppSimulador:
    def __init__(self, root):
        self.root = root
        self.root.title("Simulador de Movimentos - Versão Avançada")
        self.root.geometry("1300x750")
        self.root.configure(bg='#f0f0f0')
        
        self.simulador = SimuladorMovimentos()
        self.dimensao_atual = '3d'
        
        # Configurar callback para atualização automática
        self.simulador.set_callback(self.atualizar_grafico)
        
        self.setup_ui()
        self.atualizar_grafico()
        
    def setup_ui(self):
        # Frame principal
        main_frame = tk.Frame(self.root, bg='#f0f0f0')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Frame do gráfico (esquerda)
        graph_frame = tk.Frame(main_frame, bg='white', relief=tk.RAISED, bd=2)
        graph_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Toolbar do gráfico
        toolbar_frame = tk.Frame(graph_frame, bg='#2c3e50', height=35)
        toolbar_frame.pack(fill=tk.X)
        toolbar_frame.pack_propagate(False)
        
        tk.Label(toolbar_frame, text="VISUALIZAÇÃO DA TRAJETÓRIA", 
                font=('Arial', 11, 'bold'),
                bg='#2c3e50', fg='white').pack(expand=True)
        
        self.fig_frame = tk.Frame(graph_frame, bg='white')
        self.fig_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Frame de controles (direita)
        control_frame = tk.Frame(main_frame, bg='#f0f0f0', width=380)
        control_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=(10, 0))
        control_frame.pack_propagate(False)
        
        # Canvas com scroll
        canvas = tk.Canvas(control_frame, bg='#f0f0f0', highlightthickness=0)
        scrollbar = ttk.Scrollbar(control_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg='#f0f0f0')
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw", width=360)
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # ========== CONTEÚDO DO PAINEL DE CONTROLE ==========
        
        # Título
        title_frame = tk.Frame(scrollable_frame, bg='#3498db', height=45)
        title_frame.pack(fill=tk.X, pady=(0, 10))
        title_frame.pack_propagate(False)
        
        tk.Label(title_frame, text="🎮 CONTROLES DO SIMULADOR", 
                font=('Arial', 12, 'bold'),
                bg='#3498db', fg='white').pack(expand=True)
        
        # Fórmula em destaque
        formula_frame = tk.Frame(scrollable_frame, bg='#fff5e6', relief=tk.RAISED, bd=1)
        formula_frame.pack(fill=tk.X, padx=8, pady=8)
        
        tk.Label(formula_frame, text="📐 FÓRMULA UTILIZADA", 
                font=('Arial', 10, 'bold'),
                bg='#fff5e6', fg='#e67e22').pack(pady=(8, 3))
        
        self.formula_label = tk.Label(formula_frame, text="", 
                                      font=('Courier', 11, 'bold'),
                                      bg='#fff5e6', fg='#2c3e50',
                                      wraplength=320, justify=tk.CENTER)
        self.formula_label.pack(pady=3)
        
        self.formula_desc = tk.Label(formula_frame, text="",
                                     font=('Arial', 8),
                                     bg='#fff5e6', fg='#7f8c8d',
                                     wraplength=320, justify=tk.LEFT)
        self.formula_desc.pack(pady=(3, 8))
        
        # Seletor de movimento
        movimento_frame = tk.LabelFrame(scrollable_frame, text="⚡ SELECIONE O MOVIMENTO", 
                                        font=('Arial', 10, 'bold'),
                                        bg='#f0f0f0', fg='#2c3e50')
        movimento_frame.pack(fill=tk.X, padx=8, pady=8)
        
        # Frame para botões com tamanho fixo
        botoes_frame = tk.Frame(movimento_frame, bg='#f0f0f0')
        botoes_frame.pack(padx=8, pady=8)
        
        # Configurar botões com tamanho padronizado
        movimentos = [
            ("🚀 MRU", "MRU", '#3498db'),
            ("📈 MRUV", "MRUV", '#2ecc71'),
            ("🔄 MCU", "MCU", '#e74c3c'),
            ("📊 MHS", "MHS", '#f39c12'),
            ("⬇️ Queda Livre", "Queda_Livre", '#9b59b6'),
            ("🎯 Lançamento", "Lancamento_Obliquo", '#1abc9c')
        ]
        
        # Criar botões em grid com tamanho fixo
        for i, (texto, valor, cor) in enumerate(movimentos):
            row = i // 2
            col = i % 2
            btn = tk.Button(botoes_frame, text=texto, 
                           command=lambda v=valor: self.mudar_modo_completo(v),
                           bg=cor, fg='white',
                           font=('Arial', 9, 'bold'),
                           relief=tk.RAISED, padx=8, pady=6,
                           cursor='hand2', width=14, height=1)
            btn.grid(row=row, column=col, padx=4, pady=4, sticky='ew')
            
            # Efeito hover
            btn.bind('<Enter>', lambda e, b=btn, c=cor: b.configure(bg='#2c3e50'))
            btn.bind('<Leave>', lambda e, b=btn, c=cor: b.configure(bg=c))
        
        # Configurar grid para expandir igualmente
        botoes_frame.grid_columnconfigure(0, weight=1)
        botoes_frame.grid_columnconfigure(1, weight=1)
        
        # Parâmetros
        self.params_frame = tk.LabelFrame(scrollable_frame, text="📊 PARÂMETROS", 
                                          font=('Arial', 10, 'bold'),
                                          bg='#f0f0f0', fg='#2c3e50')
        self.params_frame.pack(fill=tk.X, padx=8, pady=8)
        
        # Visualização
        dim_frame = tk.LabelFrame(scrollable_frame, text="🎨 VISUALIZAÇÃO", 
                                  font=('Arial', 10, 'bold'),
                                  bg='#f0f0f0', fg='#2c3e50')
        dim_frame.pack(fill=tk.X, padx=8, pady=8)
        
        # Frame para botões de visualização
        dim_botoes_frame = tk.Frame(dim_frame, bg='#f0f0f0')
        dim_botoes_frame.pack(padx=8, pady=8)
        
        self.btn_3d = tk.Button(dim_botoes_frame, text="🌍 3D", 
                                command=lambda: self.mudar_dimensao('3D'),
                                bg='#3498db', fg='white', 
                                font=('Arial', 9, 'bold'),
                                relief=tk.RAISED, padx=15, pady=6,
                                width=12)
        self.btn_3d.pack(side=tk.LEFT, padx=5, expand=True, fill=tk.X)
        
        self.btn_2d = tk.Button(dim_botoes_frame, text="📊 2D", 
                                command=lambda: self.mudar_dimensao('2D'),
                                bg='#95a5a6', fg='white', 
                                font=('Arial', 9, 'bold'),
                                relief=tk.RAISED, padx=15, pady=6,
                                width=12)
        self.btn_2d.pack(side=tk.LEFT, padx=5, expand=True, fill=tk.X)
        
        dim_botoes_frame.grid_columnconfigure(0, weight=1)
        dim_botoes_frame.grid_columnconfigure(1, weight=1)
        
        # Botões de ação
        actions_frame = tk.LabelFrame(scrollable_frame, text="⚙️ AÇÕES", 
                                      font=('Arial', 10, 'bold'),
                                      bg='#f0f0f0', fg='#2c3e50')
        actions_frame.pack(fill=tk.X, padx=8, pady=8)
        
        buttons = [
            ("🔄 Atualizar Agora", self.atualizar_grafico, '#3498db'),
            ("💾 Salvar no Histórico", self.salvar_historico, '#2ecc71'),
            ("📄 Exportar JSON", self.exportar_json, '#f39c12'),
            ("🖋️ Exportar TTL", self.exportar_ttl, '#9b59b6'),
            ("🖼️ Exportar Gráfico", self.exportar_grafico, '#1abc9c'),
            ("🗑️ Limpar Histórico", self.limpar_historico, '#e74c3c')
        ]
        
        for texto, comando, cor in buttons:
            btn = tk.Button(actions_frame, text=texto, command=comando,
                           bg=cor, fg='white', font=('Arial', 9, 'bold'),
                           relief=tk.RAISED, padx=8, pady=5, width=30)
            btn.pack(padx=8, pady=3)
            btn.bind('<Enter>', lambda e, b=btn, c=cor: b.configure(bg='#2c3e50'))
            btn.bind('<Leave>', lambda e, b=btn, c=cor: b.configure(bg=c))
        
        # Informações detalhadas
        info_frame = tk.LabelFrame(scrollable_frame, text="📈 INFORMAÇÕES DETALHADAS", 
                                   font=('Arial', 10, 'bold'),
                                   bg='#f0f0f0', fg='#2c3e50')
        info_frame.pack(fill=tk.X, padx=8, pady=8)
        
        self.info_text = tk.Text(info_frame, height=10, wrap=tk.WORD,
                                 font=('Courier', 8), bg='#f8f9fa',
                                 relief=tk.FLAT, padx=5, pady=5)
        self.info_text.pack(fill=tk.X, padx=5, pady=5)
        
        # Status bar
        status_frame = tk.Frame(scrollable_frame, bg='#2c3e50', height=28)
        status_frame.pack(fill=tk.X, pady=(5, 0))
        status_frame.pack_propagate(False)
        
        self.status_label = tk.Label(status_frame, text="✅ Pronto", 
                                     bg='#2c3e50', fg='white',
                                     font=('Arial', 8))
        self.status_label.pack(side=tk.LEFT, padx=8, pady=4)
        
        # Configurar gráfico
        self.setup_grafico()
        self.atualizar_parametros()
        self.atualizar_formula()
        
    def setup_grafico(self):
        """Configura o gráfico"""
        self.fig = plt.figure(figsize=(8, 6), facecolor='white')
        if self.dimensao_atual == '3d':
            self.ax = self.fig.add_subplot(111, projection='3d')
        else:
            self.ax = self.fig.add_subplot(111)
        
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.fig_frame)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        toolbar = NavigationToolbar2Tk(self.canvas, self.fig_frame)
        toolbar.update()
        
    def mudar_dimensao(self, dimensao):
        """Muda a dimensão do gráfico"""
        self.dimensao_atual = '2d' if dimensao == '2D' else '3d'
        
        # Atualizar cores dos botões
        self.btn_3d.configure(bg='#3498db' if dimensao == '3D' else '#95a5a6')
        self.btn_2d.configure(bg='#2ecc71' if dimensao == '2D' else '#95a5a6')
        
        self.fig.clear()
        if self.dimensao_atual == '3d':
            self.ax = self.fig.add_subplot(111, projection='3d')
        else:
            self.ax = self.fig.add_subplot(111)
        
        self.atualizar_grafico()
        self.status_label.config(text=f"✅ Visualização alterada para {dimensao}")
        
    def mudar_modo_completo(self, modo):
        """Muda o modo de movimento com feedback visual"""
        self.simulador.modo_atual = modo
        self.atualizar_parametros()
        self.atualizar_formula()
        self.atualizar_grafico()
        self.status_label.config(text=f"✅ Movimento alterado para: {modo}")
        
    def atualizar_formula(self):
        """Atualiza a fórmula em destaque"""
        modo = self.simulador.modo_atual
        
        formulas = {
            'MRU': 'x = x₀ + v·t',
            'MRUV': 'x = x₀ + v₀·t + ½·a·t²',
            'MCU': 'x = r·cos(ωt)\ny = r·sin(ωt)',
            'MHS': 'x = A·sin(2πft + φ)',
            'Queda_Livre': 'y = h₀ + v₀·t - ½·g·t²',
            'Lancamento_Obliquo': 'x = v₀·cosθ·t\ny = v₀·sinθ·t - ½·g·t²'
        }
        
        self.formula_label.config(text=formulas.get(modo, ''))
        self.formula_desc.config(text=self.simulador.get_formula_detalhada())
        
    def atualizar_parametros(self):
        """Atualiza os campos de parâmetros"""
        for widget in self.params_frame.winfo_children():
            widget.destroy()
        
        modo = self.simulador.modo_atual
        params = self.simulador.parametros[modo]
        
        self.entries = {}
        
        nomes = {
            'v': 'Velocidade', 'pos_inicial': 'Posição inicial', 'v0': 'Velocidade inicial',
            'a': 'Aceleração', 'r': 'Raio', 'omega': 'Vel. angular',
            'A': 'Amplitude', 'f': 'Frequência', 'phi': 'Fase inicial',
            'altura_inicial': 'Altura inicial', 'angulo': 'Ângulo', 'g': 'Gravidade'
        }
        
        unidades = {
            'v': 'm/s', 'pos_inicial': 'm', 'v0': 'm/s', 'a': 'm/s²',
            'r': 'm', 'omega': 'rad/s', 'A': 'm', 'f': 'Hz', 'phi': 'rad',
            'altura_inicial': 'm', 'angulo': '°', 'g': 'm/s²'
        }
        
        for param, valor in params.items():
            frame = tk.Frame(self.params_frame, bg='#f0f0f0')
            frame.pack(fill=tk.X, padx=5, pady=3)
            
            nome = nomes.get(param, param)
            unidade = unidades.get(param, '')
            label_text = f"{nome} ({unidade}):" if unidade else f"{nome}:"
            
            tk.Label(frame, text=label_text, font=('Arial', 9),
                    bg='#f0f0f0', width=16, anchor=tk.W).pack(side=tk.LEFT)
            
            entry = tk.Entry(frame, font=('Arial', 9), width=10,
                            relief=tk.SUNKEN, bd=1)
            entry.insert(0, str(valor))
            entry.pack(side=tk.RIGHT, padx=5)
            
            entry.bind('<KeyRelease>', lambda e, p=param, ent=entry: self.atualizar_parametro_automatico(p, ent))
            self.entries[param] = entry
        
        self.atualizar_informacoes()
        
    def atualizar_parametro_automatico(self, parametro, entry):
        """Atualiza parâmetro automaticamente enquanto digita"""
        try:
            valor = float(entry.get())
            if self.simulador.atualizar_parametro(parametro, valor):
                self.atualizar_informacoes()
        except ValueError:
            pass
            
    def atualizar_informacoes(self):
        """Atualiza as informações detalhadas"""
        self.info_text.delete(1.0, tk.END)
        
        info = f"{'='*38}\n"
        info += f"  MOVIMENTO: {self.simulador.modo_atual}\n"
        info += f"{'='*38}\n\n"
        
        info += "📌 PARÂMETROS ATUAIS:\n"
        for param, valor in self.simulador.parametros[self.simulador.modo_atual].items():
            info += f"   • {param} = {valor}\n"
        
        info += "\n📊 DADOS CALCULADOS:\n"
        
        modo = self.simulador.modo_atual
        params = self.simulador.parametros[modo]
        
        if modo == 'MCU':
            periodo = 2 * np.pi / params['omega']
            info += f"   • Período = {periodo:.2f} s\n"
            info += f"   • Frequência = {1/periodo:.2f} Hz\n"
        elif modo == 'MHS':
            info += f"   • Período = {1/params['f']:.2f} s\n"
            info += f"   • Frequência angular = {2*np.pi*params['f']:.2f} rad/s\n"
        elif modo == 'Queda_Livre':
            t_total = self.simulador.obter_tempo_total()
            info += f"   • Tempo de queda = {t_total:.2f} s\n"
            info += f"   • Velocidade final = {9.81*t_total:.2f} m/s\n"
        elif modo == 'Lancamento_Obliquo':
            ang_rad = np.radians(params['angulo'])
            v0y = params['v0'] * np.sin(ang_rad)
            t_total = 2 * v0y / params['g']
            v0x = params['v0'] * np.cos(ang_rad)
            alcance = v0x * t_total
            altura_max = (v0y**2) / (2 * params['g'])
            info += f"   • Alcance = {alcance:.2f} m\n"
            info += f"   • Altura máxima = {altura_max:.2f} m\n"
            info += f"   • Tempo total = {t_total:.2f} s\n"
        
        info += f"\n📈 HISTÓRICO: {len(self.simulador.historico)} simulação(ões) salva(s)"
        
        self.info_text.insert(1.0, info)
        
    def atualizar_grafico(self):
        """Atualiza o gráfico com a trajetória atual - Versão corrigida sem viridis"""
        self.ax.clear()
        
        x, y, z = self.simulador.calcular_trajetoria()
        
        # Plotar histórico
        if self.simulador.historico:
            cores_hist = ['#95a5a6', '#7f8c8d', '#bdc3c7', '#ecf0f1']
            for i, hist in enumerate(self.simulador.historico[-5:]):
                xh, yh, zh = hist['trajetoria']
                if len(xh) > 0:
                    alpha = 0.2 + (i * 0.05)
                    cor = cores_hist[i % len(cores_hist)]
                    if self.dimensao_atual == '3d':
                        self.ax.plot(xh, yh, zh, '--', color=cor, linewidth=1, alpha=alpha)
                    else:
                        self.ax.plot(xh, yh, '--', color=cor, linewidth=1, alpha=alpha)
        
        # Plotar trajetória atual com gradiente de cores manual
        if len(x) > 0:
            # Criar gradiente de cores manualmente
            n_points = len(x)
            colors_3d = []
            colors_2d = []
            
            # Gerar cores em gradiente do azul ao vermelho
            for i in range(n_points):
                # Cor baseada na posição (azul -> verde -> vermelho)
                t_color = i / n_points
                if self.dimensao_atual == '3d':
                    # Para 3D: azul (0) -> verde (0.5) -> vermelho (1)
                    if t_color < 0.5:
                        r = 0
                        g = t_color * 2
                        b = 1 - t_color * 2
                    else:
                        r = (t_color - 0.5) * 2
                        g = 1 - (t_color - 0.5) * 2
                        b = 0
                    colors_3d.append((r, g, b))
                else:
                    # Para 2D: cores mais vibrantes
                    r = t_color
                    g = 0.2 + t_color * 0.6
                    b = 1 - t_color
                    colors_2d.append((r, g, b))
            
            if self.dimensao_atual == '3d':
                # Plotar segmentos com cores diferentes
                for i in range(len(x)-1):
                    self.ax.plot(x[i:i+2], y[i:i+2], z[i:i+2], 
                                color=colors_3d[i], linewidth=2.5)
                
                self.ax.scatter(x[0], y[0], z[0], color='#2ecc71', 
                               s=100, label='Início', edgecolors='white', linewidth=2)
                self.ax.scatter(x[-1], y[-1], z[-1], color='#e74c3c', 
                               s=100, label='Fim', edgecolors='white', linewidth=2)
                self.ax.set_zlabel('Z (m)', fontsize=10)
            else:
                # Plotar segmentos para 2D
                for i in range(len(x)-1):
                    self.ax.plot(x[i:i+2], y[i:i+2], color=colors_2d[i], linewidth=2.5)
                
                self.ax.scatter(x[0], y[0], color='#2ecc71', s=100, 
                               label='Início', edgecolors='white', linewidth=2, zorder=5)
                self.ax.scatter(x[-1], y[-1], color='#e74c3c', s=100, 
                               label='Fim', edgecolors='white', linewidth=2, zorder=5)
                
                # Adicionar seta de direção
                if len(x) > 20:
                    mid = len(x) // 2
                    self.ax.annotate('', xy=(x[mid+15], y[mid+15]), 
                                    xytext=(x[mid], y[mid]),
                                    arrowprops=dict(arrowstyle='->', 
                                                  color='#e67e22', lw=2, alpha=0.8))
        
        # Adicionar informações no gráfico
        info_text = self.simulador.get_info_text()
        formula_text = self.simulador.get_formula()
        
        info_completa = f"{info_text}\n\n{formula_text}"
        
        if self.dimensao_atual == '3d':
            self.ax.text2D(0.02, 0.98, info_completa, transform=self.ax.transAxes, 
                          fontsize=8, verticalalignment='top',
                          bbox=dict(boxstyle='round', facecolor='white', alpha=0.9, edgecolor='#3498db'))
        else:
            self.ax.text(0.02, 0.98, info_completa, transform=self.ax.transAxes, 
                        fontsize=8, verticalalignment='top',
                        bbox=dict(boxstyle='round', facecolor='white', alpha=0.9, edgecolor='#3498db'))
        
        # Configurar eixos
        self.ax.set_xlabel('X (m)', fontsize=10, fontweight='bold')
        self.ax.set_ylabel('Y (m)', fontsize=10, fontweight='bold')
        
        # Título com fórmula
        titulo = f'{self.simulador.modo_atual} - {self.simulador.get_formula()}'
        self.ax.set_title(titulo, fontsize=11, fontweight='bold', pad=12)
        self.ax.legend(loc='upper right', fontsize=8)
        self.ax.grid(True, alpha=0.3, linestyle='--')
        
        # Ajustar limites
        if len(x) > 0:
            margin = 0.15
            x_min, x_max = np.min(x), np.max(x)
            y_min, y_max = np.min(y), np.max(y)
            
            x_range = max(x_max - x_min, 1) * margin
            y_range = max(y_max - y_min, 1) * margin
            
            self.ax.set_xlim([x_min - x_range, x_max + x_range])
            self.ax.set_ylim([y_min - y_range, y_max + y_range])
            
            if self.dimensao_atual == '3d' and len(z) > 0 and np.max(z) > 0:
                z_min, z_max = np.min(z), np.max(z)
                z_range = max(z_max - z_min, 1) * margin
                self.ax.set_zlim([z_min - z_range, z_max + z_range])
        
        if self.dimensao_atual == '2d':
            self.ax.set_aspect('equal', adjustable='box')
        
        self.canvas.draw()
        self.status_label.config(text="✅ Gráfico atualizado")
        
    def salvar_historico(self):
        self.simulador.salvar_historico()
        self.atualizar_informacoes()
        self.status_label.config(text="✅ Histórico salvo com sucesso!")
        messagebox.showinfo("Sucesso", "Simulação salva no histórico!")
        
    def limpar_historico(self):
        if messagebox.askyesno("Confirmar", "Deseja limpar todo o histórico?"):
            self.simulador.historico.clear()
            self.atualizar_grafico()
            self.atualizar_informacoes()
            self.status_label.config(text="✅ Histórico limpo")
            messagebox.showinfo("Sucesso", "Histórico limpo com sucesso!")
        
    def exportar_json(self):
        nome = filedialog.asksaveasfilename(defaultextension=".json", 
                                           filetypes=[("JSON files", "*.json")],
                                           initialfile=f"simulacao_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
        if nome:
            dados = {
                "movimento": self.simulador.modo_atual,
                "parametros": self.simulador.parametros[self.simulador.modo_atual],
                "historico": self.simulador.historico,
                "timestamp": datetime.now().isoformat()
            }
            with open(nome, 'w', encoding='utf-8') as f:
                json.dump(dados, f, indent=2, ensure_ascii=False)
            self.status_label.config(text=f"✅ Exportado: {nome}")
            messagebox.showinfo("Sucesso", f"Dados exportados para:\n{nome}")
    
    def exportar_ttl(self):
        nome = filedialog.asksaveasfilename(defaultextension=".ttl", 
                                           filetypes=[("Turtle files", "*.ttl")],
                                           initialfile=f"simulacao_{datetime.now().strftime('%Y%m%d_%H%M%S')}.ttl")
        if nome:
            with open(nome, 'w', encoding='utf-8') as f:
                f.write("@prefix sim: <http://www.simulador.com#> .\n")
                f.write("@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .\n\n")
                f.write("sim:SimulacaoAtual\n")
                f.write(f"    a sim:{self.simulador.modo_atual} ;\n")
                for k, v in self.simulador.parametros[self.simulador.modo_atual].items():
                    f.write(f"    sim:{k} {v} ;\n")
                f.write(f'    sim:timestamp "{datetime.now().isoformat()}"^^xsd:dateTime .\n')
                
                if self.simulador.historico:
                    f.write("\n# Histórico de simulações\n")
                    for i, hist in enumerate(self.simulador.historico[-5:]):
                        f.write(f"\nsim:SimulacaoHistorico_{i+1}\n")
                        f.write(f"    a sim:{hist['modo']} ;\n")
                        for k, v in hist['parametros'].items():
                            f.write(f"    sim:{k} {v} ;\n")
                        f.write(f'    sim:timestamp "{hist.get("timestamp", datetime.now().isoformat())}"^^xsd:dateTime .\n')
            
            self.status_label.config(text=f"✅ Exportado: {nome}")
            messagebox.showinfo("Sucesso", f"Dados TTL exportados para:\n{nome}")
    
    def exportar_grafico(self):
        nome = filedialog.asksaveasfilename(defaultextension=".png", 
                                           filetypes=[("PNG files", "*.png")],
                                           initialfile=f"grafico_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png")
        if nome:
            self.fig.savefig(nome, dpi=150, bbox_inches='tight', facecolor='white')
            self.status_label.config(text=f"✅ Gráfico exportado: {nome}")
            messagebox.showinfo("Sucesso", f"Gráfico exportado para:\n{nome}")

def main():
    """Função principal"""
    try:
        root = tk.Tk()
        app = AppSimulador(root)
        root.mainloop()
    except Exception as e:
        print(f"Erro ao iniciar aplicação: {e}")
        print("Iniciando versão simplificada...")
        
        # Versão terminal simplificada
        simulador = SimuladorMovimentos()
        while True:
            print("\n" + "="*50)
            print(f"  SIMULADOR - {simulador.modo_atual}")
            print("="*50)
            print(f"\n📐 {simulador.get_formula()}")
            print("\n📊 PARÂMETROS:")
            for k, v in simulador.parametros[simulador.modo_atual].items():
                print(f"   {k} = {v}")
            print("\n🎮 OPÇÕES:")
            print("   1 - Mudar modo")
            print("   2 - Modificar parâmetros")
            print("   3 - Ver gráfico 2D")
            print("   4 - Ver gráfico 3D")
            print("   5 - Exportar JSON")
            print("   6 - Sair")
            
            op = input("\nEscolha: ").strip()
            
            if op == '1':
                print("\nModos: MRU, MRUV, MCU, MHS, Queda_Livre, Lancamento_Obliquo")
                novo = input("Novo modo: ").strip()
                if novo in simulador.parametros:
                    simulador.modo_atual = novo
            elif op == '2':
                for k, v in simulador.parametros[simulador.modo_atual].items():
                    novo = input(f"  {k} ({v}): ").strip()
                    if novo:
                        try:
                            simulador.atualizar_parametro(k, float(novo))
                        except:
                            pass
            elif op == '3' or op == '4':
                fig = plt.figure(figsize=(12, 8))
                if op == '4':
                    ax = fig.add_subplot(111, projection='3d')
                    x, y, z = simulador.calcular_trajetoria()
                    ax.plot(x, y, z, 'b-', linewidth=2)
                    ax.scatter(x[0], y[0], z[0], c='g', s=100)
                    ax.scatter(x[-1], y[-1], z[-1], c='r', s=100)
                    ax.set_xlabel('X (m)')
                    ax.set_ylabel('Y (m)')
                    ax.set_zlabel('Z (m)')
                else:
                    ax = fig.add_subplot(111)
                    x, y, _ = simulador.calcular_trajetoria()
                    ax.plot(x, y, 'b-', linewidth=2)
                    ax.scatter(x[0], y[0], c='g', s=100, label='Início')
                    ax.scatter(x[-1], y[-1], c='r', s=100, label='Fim')
                    ax.set_xlabel('X (m)')
                    ax.set_ylabel('Y (m)')
                    ax.grid(True, alpha=0.3)
                    ax.legend()
                info = simulador.get_info_text()
                formula = simulador.get_formula()
                ax.set_title(f'{simulador.modo_atual} - {formula}')
                if op == '4':
                    ax.text2D(0.02, 0.98, info, transform=ax.transAxes, fontsize=10,
                             bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))
                else:
                    ax.text(0.02, 0.98, info, transform=ax.transAxes, fontsize=10,
                           bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))
                plt.show()
            elif op == '5':
                nome = f"dados_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
                dados = {
                    "movimento": simulador.modo_atual,
                    "parametros": simulador.parametros[simulador.modo_atual],
                    "timestamp": datetime.now().isoformat()
                }
                with open(nome, 'w', encoding='utf-8') as f:
                    json.dump(dados, f, indent=2, ensure_ascii=False)
                print(f"✓ Exportado: {nome}")
            elif op == '6':
                break

if __name__ == "__main__":
    main()