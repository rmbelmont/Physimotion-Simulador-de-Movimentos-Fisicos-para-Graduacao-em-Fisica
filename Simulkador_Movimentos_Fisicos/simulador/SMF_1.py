import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import json
import os
from datetime import datetime
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import threading
from rdflib import Graph, Literal, RDF, RDFS, URIRef, Namespace
from rdflib.namespace import XSD

# ==================== NAMESPACES DA ONTOLOGIA RDF ====================
MOV = Namespace("http://www.simulador-movimentos.org/ontologia#")
BASE = Namespace("http://www.simulador-movimentos.org/")

class OntologiaRDF:
    """Classe para gerenciar a ontologia em RDF"""
    
    def __init__(self, arquivo="ontologia_movimentos.rdf"):
        self.arquivo = arquivo
        self.g = Graph()
        self.definir_namespaces()
        
        if os.path.exists(arquivo):
            try:
                self.g.parse(arquivo, format="xml")
            except:
                self.criar_ontologia_base()
        else:
            self.criar_ontologia_base()
    
    def definir_namespaces(self):
        """Define os namespaces da ontologia"""
        self.g.bind("mov", MOV)
        self.g.bind("base", BASE)
        self.g.bind("rdf", RDF)
        self.g.bind("rdfs", RDFS)
        self.g.bind("xsd", XSD)
    
    def criar_ontologia_base(self):
        """Cria a estrutura base da ontologia RDF"""
        # Definir classe principal
        self.g.add((MOV.Movimento, RDF.type, RDFS.Class))
        self.g.add((MOV.Movimento, RDFS.label, Literal("Movimento Físico", lang="pt")))
        self.g.add((MOV.Movimento, RDFS.comment, Literal("Classe que representa um movimento físico", lang="pt")))
        
        # Definir subclasses de movimento
        subclasses = {
            "MRU": "Movimento Retilíneo Uniforme",
            "MRUV": "Movimento Retilíneo Uniformemente Variado",
            "MCU": "Movimento Circular Uniforme",
            "MHS": "Movimento Harmônico Simples",
            "QuedaLivre": "Queda Livre",
            "LancamentoObliquo": "Lançamento Oblíquo"
        }
        
        for classe, desc in subclasses.items():
            classe_uri = MOV[classe]
            self.g.add((classe_uri, RDF.type, RDFS.Class))
            self.g.add((classe_uri, RDFS.subClassOf, MOV.Movimento))
            self.g.add((classe_uri, RDFS.label, Literal(desc, lang="pt")))
        
        # Definir propriedades
        propriedades = [
            ("tempoTotal", "Tempo total do movimento", XSD.float),
            ("velocidade", "Velocidade", XSD.float),
            ("velocidadeInicial", "Velocidade inicial", XSD.float),
            ("aceleracao", "Aceleração", XSD.float),
            ("posicaoInicial", "Posição inicial", XSD.float),
            ("raio", "Raio", XSD.float),
            ("velocidadeAngular", "Velocidade angular", XSD.float),
            ("amplitude", "Amplitude", XSD.float),
            ("frequencia", "Frequência", XSD.float),
            ("angulo", "Ângulo de lançamento", XSD.float),
            ("gravidade", "Aceleração da gravidade", XSD.float),
            ("alturaInicial", "Altura inicial", XSD.float),
            ("alcance", "Alcance máximo", XSD.float),
            ("alturaMaxima", "Altura máxima", XSD.float),
            ("dataExperimento", "Data do experimento", XSD.dateTime)
        ]
        
        for prop, desc, tipo in propriedades:
            prop_uri = MOV[prop]
            self.g.add((prop_uri, RDF.type, RDF.Property))
            self.g.add((prop_uri, RDFS.label, Literal(desc, lang="pt")))
            self.g.add((prop_uri, RDFS.range, tipo))
        
        self.salvar()
    
    def adicionar_experimento(self, tipo_movimento, parametros, resultado):
        """Adiciona um novo experimento à ontologia RDF"""
        exp_id = len(list(self.g.subjects(RDF.type, MOV.Experimento))) + 1
        exp_uri = MOV[f"Experimento_{exp_id}"]
        
        # Criar instância do experimento
        self.g.add((exp_uri, RDF.type, MOV.Experimento))
        self.g.add((exp_uri, RDF.type, MOV[tipo_movimento]))
        self.g.add((exp_uri, MOV.dataExperimento, Literal(datetime.now().isoformat(), datatype=XSD.dateTime)))
        
        # Adicionar parâmetros
        for key, value in parametros.items():
            prop_uri = MOV[self._mapear_propriedade(key)]
            self.g.add((exp_uri, prop_uri, Literal(value, datatype=XSD.float)))
        
        # Adicionar resultados
        for key, value in resultado.items():
            prop_uri = MOV[self._mapear_propriedade(key)]
            self.g.add((exp_uri, prop_uri, Literal(value, datatype=XSD.float)))
        
        self.salvar()
        return exp_id
    
    def _mapear_propriedade(self, key):
        """Mapeia chaves de parâmetros para propriedades RDF"""
        mapeamento = {
            'v': 'velocidade',
            'v0': 'velocidadeInicial',
            'a': 'aceleracao',
            'pos_inicial': 'posicaoInicial',
            'r': 'raio',
            'omega': 'velocidadeAngular',
            'A': 'amplitude',
            'f': 'frequencia',
            'phi': 'faseInicial',
            'angulo': 'angulo',
            'g': 'gravidade',
            'altura_inicial': 'alturaInicial',
            'tempo_total': 'tempoTotal',
            'alcance_maximo': 'alcance',
            'altura_maxima': 'alturaMaxima'
        }
        return mapeamento.get(key, key)
    
    def listar_experimentos(self):
        """Lista todos os experimentos salvos"""
        experimentos = []
        for exp in self.g.subjects(RDF.type, MOV.Experimento):
            exp_data = {
                'id': str(exp).split('_')[-1],
                'uri': exp
            }
            
            # Buscar tipo
            for tipo in [MOV.MRU, MOV.MRUV, MOV.MCU, MOV.MHS, MOV.QuedaLivre, MOV.LancamentoObliquo]:
                if (exp, RDF.type, tipo) in self.g:
                    exp_data['tipo'] = str(tipo).split('#')[-1]
                    break
            
            # Buscar data
            for data in self.g.objects(exp, MOV.dataExperimento):
                exp_data['data'] = str(data)
            
            # Buscar informações
            info = []
            for prop in self.g.predicates(exp):
                for obj in self.g.objects(exp, prop):
                    if prop not in [RDF.type, MOV.dataExperimento]:
                        info.append(f"{prop.split('#')[-1]}: {obj}")
            
            exp_data['info'] = " | ".join(info[:3])  # Primeiras 3 informações
            
            experimentos.append(exp_data)
        
        return experimentos
    
    def gerar_relatorio(self):
        """Gera um relatório da ontologia"""
        relatorio = "="*60 + "\n"
        relatorio += "RELATÓRIO DA ONTOLOGIA RDF\n"
        relatorio += "="*60 + "\n\n"
        
        # Contar experimentos por tipo
        tipos = {}
        for exp in self.g.subjects(RDF.type, MOV.Experimento):
            for tipo in [MOV.MRU, MOV.MRUV, MOV.MCU, MOV.MHS, MOV.QuedaLivre, MOV.LancamentoObliquo]:
                if (exp, RDF.type, tipo) in self.g:
                    tipo_nome = str(tipo).split('#')[-1]
                    tipos[tipo_nome] = tipos.get(tipo_nome, 0) + 1
        
        relatorio += f"📊 TOTAL DE EXPERIMENTOS: {len(list(self.g.subjects(RDF.type, MOV.Experimento)))}\n\n"
        relatorio += "📈 EXPERIMENTOS POR TIPO:\n"
        for tipo, count in tipos.items():
            relatorio += f"   - {tipo}: {count}\n"
        
        relatorio += "\n📝 INFORMAÇÕES DA ONTOLOGIA:\n"
        relatorio += f"   - Classes definidas: {len(list(self.g.subjects(RDF.type, RDFS.Class)))}\n"
        relatorio += f"   - Propriedades definidas: {len(list(self.g.subjects(RDF.type, RDF.Property)))}\n"
        
        return relatorio
    
    def salvar(self):
        """Salva a ontologia em formato RDF/XML"""
        self.g.serialize(destination=self.arquivo, format="xml")
    
    def exportar_json(self, arquivo_json="ontologia_movimentos.json"):
        """Exporta a ontologia para JSON"""
        dados = {
            "metadata": {
                "nome": "Ontologia de Movimentos Físicos",
                "formato": "RDF",
                "exportado_em": datetime.now().isoformat()
            },
            "experimentos": self.listar_experimentos()
        }
        
        with open(arquivo_json, 'w', encoding='utf-8') as f:
            json.dump(dados, f, indent=2, ensure_ascii=False)
        
        return arquivo_json


# ==================== CALCULADORA DE MOVIMENTOS ====================
class CalculadoraMovimentos:
    """Classe para calcular os diferentes tipos de movimento"""
    
    @staticmethod
    def calcular_mru(t, v, pos_inicial=0):
        x = pos_inicial + v * t
        y = np.zeros_like(t)
        z = np.zeros_like(t)
        info = f"MRU: v={v} m/s, x0={pos_inicial} m"
        return x, y, z, info
    
    @staticmethod
    def calcular_mruv(t, v0, a, pos_inicial=0):
        x = pos_inicial + v0 * t + 0.5 * a * t**2
        y = np.zeros_like(t)
        z = np.zeros_like(t)
        info = f"MRUV: v0={v0} m/s, a={a} m/s², x0={pos_inicial} m"
        return x, y, z, info
    
    @staticmethod
    def calcular_mcu(t, r, omega, centro_x=0, centro_y=0):
        angulo = omega * t
        x = centro_x + r * np.cos(angulo)
        y = centro_y + r * np.sin(angulo)
        z = np.zeros_like(t)
        info = f"MCU: r={r} m, ω={omega:.2f} rad/s, centro=({centro_x},{centro_y})"
        return x, y, z, info
    
    @staticmethod
    def calcular_mhs(t, A, f, phi=0):
        omega = 2 * np.pi * f
        x = A * np.sin(omega * t + phi)
        y = np.zeros_like(t)
        z = np.zeros_like(t)
        info = f"MHS: A={A} m, f={f} Hz, φ={phi:.2f} rad"
        return x, y, z, info
    
    @staticmethod
    def calcular_queda_livre(t, altura_inicial, v0=0, g=9.81):
        y = altura_inicial + v0 * t - 0.5 * g * t**2
        y = np.maximum(y, 0)
        x = np.zeros_like(t)
        z = np.zeros_like(t)
        t_total = np.sqrt(2 * altura_inicial / g) if v0 == 0 else (v0 + np.sqrt(v0**2 + 2*g*altura_inicial))/g
        info = f"Queda Livre: h0={altura_inicial} m, v0={v0} m/s, t_total={t_total:.2f}s"
        return x, y, z, info
    
    @staticmethod
    def calcular_lancamento_obliquo(t, v0, angulo, g=9.81):
        angulo_rad = np.radians(angulo)
        v0x = v0 * np.cos(angulo_rad)
        v0y = v0 * np.sin(angulo_rad)
        x = v0x * t
        y = v0y * t - 0.5 * g * t**2
        y = np.maximum(y, 0)
        z = np.zeros_like(t)
        t_total = 2 * v0y / g
        alcance = v0x * t_total
        altura_max = (v0y**2) / (2 * g)
        info = f"Lançamento Oblíquo: v0={v0} m/s, θ={angulo}°, alcance={alcance:.1f}m, Hmax={altura_max:.1f}m"
        return x, y, z, info
    
    @staticmethod
    def obter_tempo_total(tipo, parametros):
        if tipo == 'MRU':
            return 10
        elif tipo == 'MRUV':
            return 10
        elif tipo == 'MCU':
            return 2 * np.pi / parametros.get('omega', 2) * 2
        elif tipo == 'MHS':
            return 2 / parametros.get('f', 0.5) * 2
        elif tipo == 'Queda_Livre':
            h = parametros.get('altura_inicial', 100)
            g = 9.81
            v0 = parametros.get('v0', 0)
            if v0 == 0:
                return np.sqrt(2 * h / g)
            else:
                return (v0 + np.sqrt(v0**2 + 2*g*h)) / g
        elif tipo == 'Lancamento_Obliquo':
            v0 = parametros.get('v0', 20)
            angulo = parametros.get('angulo', 45)
            g = parametros.get('g', 9.81)
            angulo_rad = np.radians(angulo)
            v0y = v0 * np.sin(angulo_rad)
            return max(2 * v0y / g, 0.1)
        return 10


# ==================== INTERFACE PRINCIPAL ====================
class AppMovimentos:
    def __init__(self, root):
        self.root = root
        self.root.title("Simulador de Movimentos Físicos com Ontologia RDF")
        self.root.geometry("1400x800")
        
        # Inicializar ontologia RDF
        self.ontologia = OntologiaRDF()
        
        # Inicializar calculadora
        self.calculadora = CalculadoraMovimentos()
        
        # Dados atuais
        self.dados_atual = None
        
        # Configurar interface
        self.setup_interface()
        
        # Criar figura
        self.setup_figura()
        
    def setup_interface(self):
        """Configura a interface gráfica"""
        # Frame principal
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # === FRAME ESQUERDO - ENTRADA DE DADOS ===
        input_frame = ttk.LabelFrame(main_frame, text="📝 ENTRADA DE DADOS", padding="10")
        input_frame.pack(side=tk.LEFT, fill=tk.Y, padx=5)
        
        # Seleção do tipo de movimento
        ttk.Label(input_frame, text="Tipo de Movimento:", font=('Arial', 10, 'bold')).pack(anchor=tk.W, pady=5)
        
        self.tipo_movimento = tk.StringVar(value="MRU")
        tipos = ["MRU", "MRUV", "MCU", "MHS", "Queda_Livre", "Lancamento_Obliquo"]
        
        for tipo in tipos:
            rb = ttk.Radiobutton(input_frame, text=tipo, variable=self.tipo_movimento, 
                                value=tipo, command=self.atualizar_campos_parametros)
            rb.pack(anchor=tk.W, pady=2)
        
        ttk.Separator(input_frame, orient='horizontal').pack(fill=tk.X, pady=10)
        
        # Frame para parâmetros dinâmicos
        self.param_frame = ttk.LabelFrame(input_frame, text="Parâmetros do Movimento", padding="10")
        self.param_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # Botões de ação
        btn_frame = ttk.Frame(input_frame)
        btn_frame.pack(fill=tk.X, pady=10)
        
        ttk.Button(btn_frame, text="▶ GERAR GRÁFICO", command=self.gerar_grafico).pack(fill=tk.X, pady=2)
        ttk.Button(btn_frame, text="💾 SALVAR NA ONTOLOGIA RDF", command=self.salvar_ontologia).pack(fill=tk.X, pady=2)
        ttk.Button(btn_frame, text="📋 VER HISTÓRICO", command=self.mostrar_historico).pack(fill=tk.X, pady=2)
        ttk.Button(btn_frame, text="📊 RELATÓRIO", command=self.mostrar_relatorio).pack(fill=tk.X, pady=2)
        ttk.Button(btn_frame, text="📤 EXPORTAR JSON", command=self.exportar_json).pack(fill=tk.X, pady=2)
        ttk.Button(btn_frame, text="🔄 RESETAR", command=self.resetar).pack(fill=tk.X, pady=2)
        
        # === FRAME CENTRAL - GRÁFICO ===
        graph_frame = ttk.LabelFrame(main_frame, text="📊 VISUALIZAÇÃO 3D", padding="10")
        graph_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)
        
        self.figura_frame = ttk.Frame(graph_frame)
        self.figura_frame.pack(fill=tk.BOTH, expand=True)
        
        # === FRAME DIREITO - INFORMAÇÕES ===
        info_frame = ttk.LabelFrame(main_frame, text="ℹ️ INFORMAÇÕES", padding="10")
        info_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=5)
        
        self.info_text = scrolledtext.ScrolledText(info_frame, width=35, height=20, font=('Courier', 9))
        self.info_text.pack(fill=tk.BOTH, expand=True)
        
        # Inicializar campos
        self.atualizar_campos_parametros()
        
    def setup_figura(self):
        """Configura a figura matplotlib"""
        self.fig = plt.figure(figsize=(8, 6), facecolor='white')
        self.ax = self.fig.add_subplot(111, projection='3d')
        self.ax.set_facecolor('#f0f0f0')
        
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.figura_frame)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
    def atualizar_campos_parametros(self):
        """Atualiza os campos de entrada conforme o tipo de movimento"""
        for widget in self.param_frame.winfo_children():
            widget.destroy()
        
        tipo = self.tipo_movimento.get()
        self.entradas = {}
        
        if tipo == 'MRU':
            self.criar_campo('Velocidade (m/s):', 'v', 10.0, 0, 50)
            self.criar_campo('Posição Inicial (m):', 'pos_inicial', 0.0, -50, 50)
        
        elif tipo == 'MRUV':
            self.criar_campo('Velocidade Inicial (m/s):', 'v0', 10.0, -50, 50)
            self.criar_campo('Aceleração (m/s²):', 'a', 2.0, -20, 20)
            self.criar_campo('Posição Inicial (m):', 'pos_inicial', 0.0, -50, 50)
        
        elif tipo == 'MCU':
            self.criar_campo('Raio (m):', 'r', 5.0, 0.1, 20)
            self.criar_campo('Velocidade Angular (rad/s):', 'omega', 2.0, 0.1, 10)
            self.criar_campo('Centro X (m):', 'centro_x', 0.0, -10, 10)
            self.criar_campo('Centro Y (m):', 'centro_y', 0.0, -10, 10)
        
        elif tipo == 'MHS':
            self.criar_campo('Amplitude (m):', 'A', 5.0, 0.1, 20)
            self.criar_campo('Frequência (Hz):', 'f', 0.5, 0.1, 5)
            self.criar_campo('Fase Inicial (rad):', 'phi', 0.0, 0, 6.28)
        
        elif tipo == 'Queda_Livre':
            self.criar_campo('Altura Inicial (m):', 'altura_inicial', 100.0, 0, 200)
            self.criar_campo('Velocidade Inicial (m/s):', 'v0', 0.0, -50, 50)
        
        elif tipo == 'Lancamento_Obliquo':
            self.criar_campo('Velocidade Inicial (m/s):', 'v0', 20.0, 0, 100)
            self.criar_campo('Ângulo (graus):', 'angulo', 45.0, 0, 90)
            self.criar_campo('Gravidade (m/s²):', 'g', 9.81, 1, 20)
    
    def criar_campo(self, label, param, valor, min_val, max_val):
        """Cria um campo de entrada com slider"""
        frame = ttk.Frame(self.param_frame)
        frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(frame, text=label, width=22).pack(side=tk.LEFT)
        
        var = tk.DoubleVar(value=valor)
        self.entradas[param] = var
        
        entry = ttk.Entry(frame, textvariable=var, width=10)
        entry.pack(side=tk.LEFT, padx=5)
        
        slider = ttk.Scale(frame, from_=min_val, to=max_val, 
                          variable=var, orient=tk.HORIZONTAL,
                          length=150)
        slider.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
    
    def obter_parametros(self):
        """Obtém os parâmetros atuais dos campos"""
        params = {}
        for key, var in self.entradas.items():
            params[key] = var.get()
        return params
    
    def gerar_grafico(self):
        """Gera o gráfico 3D baseado nos parâmetros atuais"""
        try:
            tipo = self.tipo_movimento.get()
            params = self.obter_parametros()
            
            # Calcular tempo total
            t_total = self.calculadora.obter_tempo_total(tipo, params)
            
            # Garantir tempo total positivo
            if t_total <= 0:
                t_total = 10
            
            t = np.linspace(0, t_total, 500)
            
            # Calcular trajetória
            if tipo == 'MRU':
                x, y, z, info = self.calculadora.calcular_mru(t, params['v'], params.get('pos_inicial', 0))
            elif tipo == 'MRUV':
                x, y, z, info = self.calculadora.calcular_mruv(t, params['v0'], params['a'], params.get('pos_inicial', 0))
            elif tipo == 'MCU':
                x, y, z, info = self.calculadora.calcular_mcu(t, params['r'], params['omega'], 
                                                             params.get('centro_x', 0), params.get('centro_y', 0))
            elif tipo == 'MHS':
                x, y, z, info = self.calculadora.calcular_mhs(t, params['A'], params['f'], params.get('phi', 0))
            elif tipo == 'Queda_Livre':
                x, y, z, info = self.calculadora.calcular_queda_livre(t, params['altura_inicial'], 
                                                                      params.get('v0', 0))
            elif tipo == 'Lancamento_Obliquo':
                x, y, z, info = self.calculadora.calcular_lancamento_obliquo(t, params['v0'], 
                                                                             params['angulo'], params.get('g', 9.81))
            else:
                return
            
            # Verificar se os dados são válidos
            if len(x) == 0 or np.all(np.isnan(x)):
                messagebox.showerror("Erro", "Erro ao calcular a trajetória!")
                return
            
            # Salvar dados atuais
            self.dados_atual = {
                'tipo': tipo,
                'parametros': params,
                'trajetoria': (x.copy(), y.copy(), z.copy()),
                'info': info,
                't_total': t_total
            }
            
            # Plotar gráfico
            self.ax.clear()
            
            # Plotar trajetória
            self.ax.plot(x, y, z, 'b-', linewidth=3, label=f'{tipo}', alpha=0.9)
            
            # Destacar pontos
            self.ax.scatter(x[0], y[0], z[0], color='green', s=100, label='Início', alpha=0.8, edgecolors='black')
            self.ax.scatter(x[-1], y[-1], z[-1], color='red', s=100, label='Fim', alpha=0.8, edgecolors='black')
            
            # Adicionar informações
            self.ax.text2D(0.02, 0.98, info, transform=self.ax.transAxes, 
                          fontsize=9, verticalalignment='top',
                          bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8))
            
            self.ax.set_xlabel('X (m)', fontsize=12, fontweight='bold')
            self.ax.set_ylabel('Y (m)', fontsize=12, fontweight='bold')
            self.ax.set_zlabel('Z (m)', fontsize=12, fontweight='bold')
            self.ax.set_title(f'Simulador de Movimentos - {tipo}', fontsize=14, fontweight='bold')
            self.ax.legend(loc='upper right', fontsize=10)
            self.ax.grid(True, alpha=0.3)
            
            # Ajustar limites
            margin = 0.1
            x_min, x_max = np.min(x), np.max(x)
            y_min, y_max = np.min(y), np.max(y)
            z_min, z_max = np.min(z), np.max(z)
            
            x_range = max(x_max - x_min, 1) * margin
            y_range = max(y_max - y_min, 1) * margin
            z_range = max(z_max - z_min, 1) * margin
            
            self.ax.set_xlim([x_min - x_range, x_max + x_range])
            self.ax.set_ylim([y_min - y_range, y_max + y_range])
            self.ax.set_zlim([z_min - z_range, z_max + z_range])
            
            self.canvas.draw()
            
            # Atualizar informações
            self.atualizar_info(info, params, t_total)
            
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao gerar gráfico: {str(e)}")
    
    def atualizar_info(self, info, params, t_total):
        """Atualiza o painel de informações"""
        self.info_text.delete(1.0, tk.END)
        
        self.info_text.insert(tk.END, "="*35 + "\n")
        self.info_text.insert(tk.END, "📊 INFORMAÇÕES DO MOVIMENTO\n")
        self.info_text.insert(tk.END, "="*35 + "\n\n")
        
        self.info_text.insert(tk.END, f"{info}\n\n")
        
        self.info_text.insert(tk.END, "📝 PARÂMETROS:\n")
        for key, value in params.items():
            self.info_text.insert(tk.END, f"   {key}: {value:.2f}\n")
        
        self.info_text.insert(tk.END, f"\n⏱️ Tempo total: {t_total:.2f} s\n")
        
    def salvar_ontologia(self):
        """Salva o experimento atual na ontologia RDF"""
        if self.dados_atual is None:
            messagebox.showwarning("Aviso", "Gere um gráfico primeiro!")
            return
        
        # Preparar resultado
        x, y, z = self.dados_atual['trajetoria']
        resultado = {
            "tempo_total": self.dados_atual['t_total'],
            "alcance_maximo": float(np.max(x)) if len(x) > 0 else 0,
            "altura_maxima": float(np.max(y)) if len(y) > 0 else 0,
            "deslocamento_lateral": float(np.max(z)) if len(z) > 0 else 0
        }
        
        # Salvar na ontologia RDF
        exp_id = self.ontologia.adicionar_experimento(
            self.dados_atual['tipo'],
            self.dados_atual['parametros'],
            resultado
        )
        
        messagebox.showinfo("Sucesso", f"Experimento salvo na ontologia RDF!\nID: {exp_id}\nArquivo: ontologia_movimentos.rdf")
    
    def mostrar_historico(self):
        """Mostra o histórico de experimentos"""
        experimentos = self.ontologia.listar_experimentos()
        
        if not experimentos:
            messagebox.showinfo("Histórico", "Nenhum experimento salvo ainda!")
            return
        
        # Criar janela de histórico
        hist_window = tk.Toplevel(self.root)
        hist_window.title("Histórico de Experimentos - Ontologia RDF")
        hist_window.geometry("900x600")
        
        # Treeview para mostrar dados
        tree = ttk.Treeview(hist_window, columns=('ID', 'Tipo', 'Data', 'Info'), show='headings')
        tree.heading('ID', text='ID')
        tree.heading('Tipo', text='Tipo de Movimento')
        tree.heading('Data', text='Data')
        tree.heading('Info', text='Informações')
        
        tree.column('ID', width=50)
        tree.column('Tipo', width=150)
        tree.column('Data', width=200)
        tree.column('Info', width=450)
        
        for exp in experimentos:
            tree.insert('', tk.END, values=(
                exp['id'],
                exp['tipo'],
                exp.get('data', 'N/A')[:19],
                exp.get('info', 'N/A')
            ))
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(hist_window, orient=tk.VERTICAL, command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        
        tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y, pady=10)
        
        ttk.Button(hist_window, text="Fechar", command=hist_window.destroy).pack(pady=10)
    
    def mostrar_relatorio(self):
        """Mostra o relatório da ontologia RDF"""
        relatorio = self.ontologia.gerar_relatorio()
        
        # Criar janela de relatório
        rel_window = tk.Toplevel(self.root)
        rel_window.title("Relatório da Ontologia RDF")
        rel_window.geometry("700x500")
        
        text_area = scrolledtext.ScrolledText(rel_window, font=('Courier', 10))
        text_area.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        text_area.insert(1.0, relatorio)
        text_area.config(state=tk.DISABLED)
        
        ttk.Button(rel_window, text="Fechar", command=rel_window.destroy).pack(pady=10)
    
    def exportar_json(self):
        """Exporta a ontologia para JSON"""
        try:
            arquivo_json = self.ontologia.exportar_json()
            messagebox.showinfo("Sucesso", f"Ontologia exportada para JSON!\nArquivo: {arquivo_json}")
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao exportar: {str(e)}")
    
    def resetar(self):
        """Reseta a simulação"""
        self.dados_atual = None
        self.ax.clear()
        self.ax.set_xlabel('X (m)')
        self.ax.set_ylabel('Y (m)')
        self.ax.set_zlabel('Z (m)')
        self.ax.set_title('Simulador de Movimentos')
        self.ax.grid(True, alpha=0.3)
        self.canvas.draw()
        self.info_text.delete(1.0, tk.END)
        self.info_text.insert(1.0, "Gere um gráfico para ver as informações...")


# ==================== MAIN ====================
if __name__ == "__main__":
    print("="*60)
    print("🎯 SIMULADOR DE MOVIMENTOS FÍSICOS COM ONTOLOGIA RDF")
    print("="*60)
    print("\n📚 Ontologia salva em: ontologia_movimentos.rdf")
    print("📊 Gráficos 3D interativos")
    print("💾 Experimentos salvos em formato RDF/XML")
    print("\nIniciando interface gráfica...")
    
    root = tk.Tk()
    app = AppMovimentos(root)
    root.mainloop()