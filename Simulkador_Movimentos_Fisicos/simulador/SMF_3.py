import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext, filedialog
import json
import os
import shutil
import webbrowser
from datetime import datetime
from rdflib import Graph, Literal, RDF, RDFS, Namespace
from rdflib.namespace import XSD

# ==================== NAMESPACES DA ONTOLOGIA RDF ====================
MOV = Namespace("http://www.simulador-movimentos.org/ontologia#")
BASE = Namespace("http://www.simulador-movimentos.org/")

# ==================== FORMULÁRIO DE MOVIMENTOS ====================
class FormularioMovimentos:
    """Classe que armazena as fórmulas dos movimentos"""
    
    FORMULAS = {
        'MRU': {
            'nome': 'Movimento Retilíneo Uniforme',
            'equacao': 'x = x₀ + v·t',
            'equacao_detalhada': 'x(t) = x₀ + v·t',
            'parametros': {
                'x₀': 'Posição inicial (m)',
                'v': 'Velocidade constante (m/s)',
                't': 'Tempo (s)'
            },
            'propriedades': 'Velocidade constante → Aceleração = 0',
            'grafico': 'Reta inclinada no gráfico x × t'
        },
        'MRUV': {
            'nome': 'Movimento Retilíneo Uniformemente Variado',
            'equacao': 'x = x₀ + v₀·t + ½·a·t²',
            'equacao_detalhada': 'x(t) = x₀ + v₀·t + (1/2)·a·t²',
            'parametros': {
                'x₀': 'Posição inicial (m)',
                'v₀': 'Velocidade inicial (m/s)',
                'a': 'Aceleração constante (m/s²)',
                't': 'Tempo (s)'
            },
            'propriedades': 'Aceleração constante → Parábola no gráfico x × t',
            'grafico': 'Parábola no gráfico x × t'
        },
        'MCU': {
            'nome': 'Movimento Circular Uniforme',
            'equacao': 'x = x_c + r·cos(ω·t)\ny = y_c + r·sen(ω·t)',
            'equacao_detalhada': 'x(t) = x_c + r·cos(ω·t)\ny(t) = y_c + r·sen(ω·t)',
            'parametros': {
                'x_c': 'Centro X (m)',
                'y_c': 'Centro Y (m)',
                'r': 'Raio (m)',
                'ω': 'Velocidade angular (rad/s)',
                't': 'Tempo (s)'
            },
            'propriedades': 'Velocidade angular constante → Movimento circular',
            'grafico': 'Circunferência no plano XY'
        },
        'MHS': {
            'nome': 'Movimento Harmônico Simples',
            'equacao': 'x = A·sen(ω·t + φ)',
            'equacao_detalhada': 'x(t) = A·sen(2π·f·t + φ)',
            'parametros': {
                'A': 'Amplitude (m)',
                'f': 'Frequência (Hz)',
                'ω': 'Frequência angular = 2πf (rad/s)',
                'φ': 'Fase inicial (rad)',
                't': 'Tempo (s)'
            },
            'propriedades': 'Força restauradora proporcional ao deslocamento',
            'grafico': 'Senoide no gráfico x × t'
        },
        'Queda_Livre': {
            'nome': 'Queda Livre',
            'equacao': 'y = h₀ + v₀·t - ½·g·t²',
            'equacao_detalhada': 'y(t) = h₀ + v₀·t - (1/2)·g·t²',
            'parametros': {
                'h₀': 'Altura inicial (m)',
                'v₀': 'Velocidade inicial (m/s)',
                'g': 'Aceleração da gravidade (9,81 m/s²)',
                't': 'Tempo (s)'
            },
            'propriedades': 'Queda sob ação exclusiva da gravidade',
            'grafico': 'Parábola decrescente no gráfico y × t'
        },
        'Lancamento_Obliquo': {
            'nome': 'Lançamento Oblíquo',
            'equacao': 'x = (v₀·cosθ)·t\ny = (v₀·senθ)·t - ½·g·t²',
            'equacao_detalhada': 'x(t) = v₀·cosθ·t\ny(t) = v₀·senθ·t - (1/2)·g·t²',
            'parametros': {
                'v₀': 'Velocidade inicial (m/s)',
                'θ': 'Ângulo de lançamento (graus)',
                'g': 'Aceleração da gravidade (m/s²)',
                't': 'Tempo (s)'
            },
            'propriedades': 'Composição de MRU (horizontal) e MRUV (vertical)',
            'grafico': 'Parábola no plano XY'
        }
    }
    
    @classmethod
    def get_formula(cls, tipo):
        return cls.FORMULAS.get(tipo, {})

# ==================== ONTOLOGIA RDF ====================
class OntologiaRDF:
    def __init__(self, pasta_destino="", arquivo="ontologia_movimentos.rdf"):
        self.pasta_destino = pasta_destino
        self.arquivo = os.path.join(pasta_destino, arquivo) if pasta_destino else arquivo
        self.g = Graph()
        self.definir_namespaces()
        
        if os.path.exists(self.arquivo):
            try:
                self.g.parse(self.arquivo, format="xml")
            except:
                self.criar_ontologia_base()
        else:
            self.criar_ontologia_base()
    
    def definir_namespaces(self):
        self.g.bind("mov", MOV)
        self.g.bind("base", BASE)
        self.g.bind("rdf", RDF)
        self.g.bind("rdfs", RDFS)
        self.g.bind("xsd", XSD)
    
    def criar_ontologia_base(self):
        self.g.add((MOV.Movimento, RDF.type, RDFS.Class))
        self.g.add((MOV.Movimento, RDFS.label, Literal("Movimento Físico", lang="pt")))
        
        for tipo, dados in FormularioMovimentos.FORMULAS.items():
            classe_uri = MOV[tipo]
            self.g.add((classe_uri, RDF.type, RDFS.Class))
            self.g.add((classe_uri, RDFS.subClassOf, MOV.Movimento))
            self.g.add((classe_uri, RDFS.label, Literal(dados['nome'], lang="pt")))
            self.g.add((classe_uri, MOV.formula, Literal(dados['equacao'])))
        
        self.salvar()
    
    def adicionar_experimento(self, tipo_movimento, parametros, resultado, caminho_grafico=""):
        exp_id = len(list(self.g.subjects(RDF.type, MOV.Experimento))) + 1
        exp_uri = MOV[f"Experimento_{exp_id}"]
        
        self.g.add((exp_uri, RDF.type, MOV.Experimento))
        self.g.add((exp_uri, RDF.type, MOV[tipo_movimento]))
        self.g.add((exp_uri, MOV.dataExperimento, Literal(datetime.now().isoformat(), datatype=XSD.dateTime)))
        
        if caminho_grafico:
            self.g.add((exp_uri, MOV.grafico, Literal(caminho_grafico)))
        
        for key, value in parametros.items():
            prop_uri = MOV[self._mapear_propriedade(key)]
            self.g.add((exp_uri, prop_uri, Literal(value, datatype=XSD.float)))
        
        self.salvar()
        return exp_id
    
    def _mapear_propriedade(self, key):
        mapeamento = {
            'v': 'velocidade', 'v0': 'velocidadeInicial', 'a': 'aceleracao',
            'pos_inicial': 'posicaoInicial', 'r': 'raio', 'omega': 'velocidadeAngular',
            'A': 'amplitude', 'f': 'frequencia', 'angulo': 'angulo',
            'g': 'gravidade', 'altura_inicial': 'alturaInicial'
        }
        return mapeamento.get(key, key)
    
    def listar_experimentos(self):
        experimentos = []
        for exp in self.g.subjects(RDF.type, MOV.Experimento):
            exp_data = {'id': str(exp).split('_')[-1], 'uri': exp}
            
            for tipo in FormularioMovimentos.FORMULAS.keys():
                if (exp, RDF.type, MOV[tipo]) in self.g:
                    exp_data['tipo'] = tipo
                    break
            
            for data in self.g.objects(exp, MOV.dataExperimento):
                exp_data['data'] = str(data)
            
            for grafico in self.g.objects(exp, MOV.grafico):
                exp_data['grafico'] = str(grafico)
            
            experimentos.append(exp_data)
        
        return experimentos
    
    def salvar(self):
        if self.pasta_destino:
            os.makedirs(self.pasta_destino, exist_ok=True)
        self.g.serialize(destination=self.arquivo, format="xml")

# ==================== CALCULADORA DE MOVIMENTOS ====================
class CalculadoraMovimentos:
    @staticmethod
    def calcular_mru(t, v, pos_inicial=0):
        x = pos_inicial + v * t
        y = np.zeros_like(t)
        z = np.zeros_like(t)
        return x, y, z
    
    @staticmethod
    def calcular_mruv(t, v0, a, pos_inicial=0):
        x = pos_inicial + v0 * t + 0.5 * a * t**2
        y = np.zeros_like(t)
        z = np.zeros_like(t)
        return x, y, z
    
    @staticmethod
    def calcular_mcu(t, r, omega, centro_x=0, centro_y=0):
        angulo = omega * t
        x = centro_x + r * np.cos(angulo)
        y = centro_y + r * np.sin(angulo)
        z = np.zeros_like(t)
        return x, y, z
    
    @staticmethod
    def calcular_mhs(t, A, f, phi=0):
        omega = 2 * np.pi * f
        x = A * np.sin(omega * t + phi)
        y = np.zeros_like(t)
        z = np.zeros_like(t)
        return x, y, z
    
    @staticmethod
    def calcular_queda_livre(t, altura_inicial, v0=0, g=9.81):
        y = altura_inicial + v0 * t - 0.5 * g * t**2
        y = np.maximum(y, 0)
        x = np.zeros_like(t)
        z = np.zeros_like(t)
        return x, y, z
    
    @staticmethod
    def calcular_lancamento_obliquo(t, v0, angulo, g=9.81):
        angulo_rad = np.radians(angulo)
        v0x = v0 * np.cos(angulo_rad)
        v0y = v0 * np.sin(angulo_rad)
        x = v0x * t
        y = v0y * t - 0.5 * g * t**2
        y = np.maximum(y, 0)
        z = np.zeros_like(t)
        return x, y, z
    
    @staticmethod
    def obter_tempo_total(tipo, parametros):
        if tipo == 'MRU' or tipo == 'MRUV':
            return 10
        elif tipo == 'MCU':
            return 2 * np.pi / parametros.get('omega', 2) * 2
        elif tipo == 'MHS':
            return 2 / parametros.get('f', 0.5) * 2
        elif tipo == 'Queda_Livre':
            h = parametros.get('altura_inicial', 100)
            g = 9.81
            return np.sqrt(2 * h / g)
        elif tipo == 'Lancamento_Obliquo':
            v0 = parametros.get('v0', 20)
            angulo = parametros.get('angulo', 45)
            g = parametros.get('g', 9.81)
            angulo_rad = np.radians(angulo)
            v0y = v0 * np.sin(angulo_rad)
            return max(2 * v0y / g, 0.1)
        return 10

# ==================== GERADOR DE RELATÓRIOS ====================
class GeradorRelatorio:
    @staticmethod
    def gerar_relatorio_html(pasta_destino, dados_experimento, caminho_grafico, formula_data):
        """Gera um relatório em HTML com o gráfico e a fórmula"""
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        nome_arquivo = f"relatorio_{dados_experimento['tipo']}_{timestamp}.html"
        caminho_relatorio = os.path.join(pasta_destino, nome_arquivo)
        
        # Copiar o gráfico para a pasta de relatórios
        nome_grafico = f"grafico_{dados_experimento['tipo']}_{timestamp}.png"
        caminho_grafico_relatorio = os.path.join(pasta_destino, nome_grafico)
        
        if os.path.exists(caminho_grafico):
            shutil.copy(caminho_grafico, caminho_grafico_relatorio)
        
        # Gerar HTML
        html_content = f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Relatório de Movimento - {formula_data['nome']}</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 20px;
            min-height: 100vh;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 20px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            overflow: hidden;
        }}
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            text-align: center;
        }}
        .header h1 {{
            font-size: 2.5em;
            margin-bottom: 10px;
        }}
        .header p {{
            font-size: 1.1em;
            opacity: 0.9;
        }}
        .content {{
            padding: 30px;
        }}
        .formula-box {{
            background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
            padding: 25px;
            border-radius: 15px;
            margin-bottom: 30px;
            text-align: center;
            border-left: 5px solid #667eea;
        }}
        .formula-box h2 {{
            color: #667eea;
            margin-bottom: 15px;
        }}
        .formula {{
            font-size: 1.8em;
            font-family: 'Courier New', monospace;
            font-weight: bold;
            color: #e74c3c;
            background: white;
            padding: 15px;
            border-radius: 10px;
            display: inline-block;
            margin: 10px 0;
        }}
        .params {{
            background: #f8f9fa;
            padding: 20px;
            border-radius: 10px;
            margin: 20px 0;
        }}
        .params table {{
            width: 100%;
            border-collapse: collapse;
        }}
        .params th, .params td {{
            padding: 10px;
            text-align: left;
            border-bottom: 1px solid #ddd;
        }}
        .params th {{
            background: #667eea;
            color: white;
        }}
        .grafico {{
            text-align: center;
            margin: 30px 0;
            background: #f8f9fa;
            padding: 20px;
            border-radius: 10px;
        }}
        .grafico img {{
            max-width: 100%;
            height: auto;
            border-radius: 10px;
            box-shadow: 0 5px 15px rgba(0,0,0,0.2);
        }}
        .propriedades {{
            background: #e8f4f8;
            padding: 20px;
            border-radius: 10px;
            margin-top: 20px;
            border-left: 5px solid #3498db;
        }}
        .footer {{
            background: #2c3e50;
            color: white;
            text-align: center;
            padding: 20px;
            font-size: 0.9em;
        }}
        .badge {{
            display: inline-block;
            background: #3498db;
            color: white;
            padding: 5px 15px;
            border-radius: 20px;
            font-size: 0.8em;
            margin: 5px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📊 RELATÓRIO DE MOVIMENTO FÍSICO</h1>
            <p>Gerado em {datetime.now().strftime('%d/%m/%Y às %H:%M:%S')}</p>
        </div>
        
        <div class="content">
            <div class="formula-box">
                <h2>📐 {formula_data['nome']}</h2>
                <div class="formula">
                    {formula_data['equacao_detalhada'].replace(chr(10), '<br>')}
                </div>
                <div>
                    <span class="badge">Equação Fundamental</span>
                    <span class="badge">Movimento Físico</span>
                </div>
            </div>
            
            <div class="params">
                <h3>📝 PARÂMETROS UTILIZADOS</h3>
                <table>
                    <tr>
                        <th>Parâmetro</th>
                        <th>Valor</th>
                        <th>Descrição</th>
                    </tr>
"""
        
        # Adicionar parâmetros
        for key, value in dados_experimento['parametros'].items():
            simbolo = GeradorRelatorio._mapear_simbolo(key)
            desc = formula_data['parametros'].get(simbolo, key)
            html_content += f"""
                    <tr>
                        <td><strong>{simbolo}</strong></td>
                        <td>{value:.2f}</td>
                        <td>{desc}</td>
                    </tr>
"""
        
        html_content += f"""
                </table>
            </div>
            
            <div class="grafico">
                <h3>📈 TRAJETÓRIA DO MOVIMENTO</h3>
                <img src="{nome_grafico}" alt="Gráfico 3D do Movimento">
                <p style="margin-top: 15px; color: #666;">
                    <strong>Figura 1:</strong> Representação 3D da trajetória do {formula_data['nome']}
                </p>
            </div>
            
            <div class="propriedades">
                <h3>⚡ PROPRIEDADES FÍSICAS</h3>
                <p>{formula_data['propriedades']}</p>
                <p style="margin-top: 10px;"><strong>📊 Característica do gráfico:</strong> {formula_data['grafico']}</p>
            </div>
            
            <div class="params" style="margin-top: 20px;">
                <h3>📊 RESULTADOS OBTIDOS</h3>
                <table>
                    <tr>
                        <th>Grandeza</th>
                        <th>Valor</th>
                    </tr>
                    <tr>
                        <td><strong>Tempo total</strong></td>
                        <td>{dados_experimento['t_total']:.2f} s</td>
                    </tr>
                    <tr>
                        <td><strong>Alcance máximo</strong></td>
                        <td>{dados_experimento['alcance']:.2f} m</td>
                    </tr>
                    <tr>
                        <td><strong>Altura máxima</strong></td>
                        <td>{dados_experimento['altura_max']:.2f} m</td>
                    </tr>
                </table>
            </div>
        </div>
        
        <div class="footer">
            <p>📚 Relatório gerado pelo Simulador de Movimentos Físicos</p>
            <p>🏷️ Ontologia RDF: {os.path.basename(dados_experimento.get('ontologia', 'ontologia_movimentos.rdf'))}</p>
        </div>
    </div>
</body>
</html>
"""
        
        with open(caminho_relatorio, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        return caminho_relatorio
    
    @staticmethod
    def _mapear_simbolo(key):
        simbolos = {
            'v': 'v', 'v0': 'v₀', 'a': 'a', 'pos_inicial': 'x₀',
            'r': 'r', 'omega': 'ω', 'centro_x': 'x_c', 'centro_y': 'y_c',
            'A': 'A', 'f': 'f', 'phi': 'φ', 'altura_inicial': 'h₀',
            'angulo': 'θ', 'g': 'g'
        }
        return simbolos.get(key, key)

# ==================== INTERFACE PRINCIPAL ====================
class AppMovimentos:
    def __init__(self, root):
        self.root = root
        self.root.title("Simulador de Movimentos Físicos - Com Relatórios")
        self.root.geometry("1500x850")
        
        self.pasta_destino = ""
        self.ontologia = None
        self.calculadora = CalculadoraMovimentos()
        self.dados_atual = None
        self.caminho_grafico_atual = None
        self.entradas = {}
        
        self.setup_interface()
        self.setup_figura()
        
    def setup_interface(self):
        """Configura a interface gráfica"""
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # === FRAME SUPERIOR - SELEÇÃO DE PASTA ===
        top_frame = ttk.LabelFrame(main_frame, text="📁 LOCAL DE ARMAZENAMENTO", padding="10")
        top_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.pasta_var = tk.StringVar(value="Nenhuma pasta selecionada")
        ttk.Label(top_frame, textvariable=self.pasta_var, foreground="blue").pack(side=tk.LEFT, padx=5)
        ttk.Button(top_frame, text="📂 Selecionar Pasta", command=self.selecionar_pasta).pack(side=tk.RIGHT, padx=5)
        
        # === FRAME PRINCIPAL ===
        middle_frame = ttk.Frame(main_frame)
        middle_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # FRAME ESQUERDO - ENTRADA DE DADOS
        input_frame = ttk.LabelFrame(middle_frame, text="📝 ENTRADA DE DADOS", padding="10")
        input_frame.pack(side=tk.LEFT, fill=tk.Y, padx=5)
        
        ttk.Label(input_frame, text="Tipo de Movimento:", font=('Arial', 10, 'bold')).pack(anchor=tk.W, pady=5)
        
        self.tipo_movimento = tk.StringVar(value="MRU")
        tipos = ["MRU", "MRUV", "MCU", "MHS", "Queda_Livre", "Lancamento_Obliquo"]
        
        for tipo in tipos:
            rb = ttk.Radiobutton(input_frame, text=tipo, variable=self.tipo_movimento, 
                                value=tipo, command=self.atualizar_campos_parametros)
            rb.pack(anchor=tk.W, pady=2)
        
        ttk.Separator(input_frame, orient='horizontal').pack(fill=tk.X, pady=10)
        
        self.param_frame = ttk.LabelFrame(input_frame, text="Parâmetros do Movimento", padding="10")
        self.param_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        btn_frame = ttk.Frame(input_frame)
        btn_frame.pack(fill=tk.X, pady=10)
        
        ttk.Button(btn_frame, text="▶ GERAR GRÁFICO", command=self.gerar_grafico).pack(fill=tk.X, pady=2)
        ttk.Button(btn_frame, text="💾 SALVAR NA ONTOLOGIA", command=self.salvar_ontologia).pack(fill=tk.X, pady=2)
        ttk.Button(btn_frame, text="📄 GERAR RELATÓRIO", command=self.gerar_relatorio).pack(fill=tk.X, pady=2)
        ttk.Button(btn_frame, text="📋 VER HISTÓRICO", command=self.mostrar_historico).pack(fill=tk.X, pady=2)
        
        # FRAME CENTRAL - GRÁFICO
        graph_frame = ttk.LabelFrame(middle_frame, text="📊 VISUALIZAÇÃO 3D COM FÓRMULA", padding="10")
        graph_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)
        
        self.figura_frame = ttk.Frame(graph_frame)
        self.figura_frame.pack(fill=tk.BOTH, expand=True)
        
        # FRAME DIREITO - FÓRMULA E INFORMAÇÕES
        right_frame = ttk.Frame(middle_frame)
        right_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=5)
        
        formula_frame = ttk.LabelFrame(right_frame, text="📐 FÓRMULA DO MOVIMENTO", padding="10")
        formula_frame.pack(fill=tk.X, pady=5)
        
        self.formula_text = scrolledtext.ScrolledText(formula_frame, width=40, height=8, 
                                                       font=('Courier', 11, 'bold'))
        self.formula_text.pack(fill=tk.X)
        
        info_frame = ttk.LabelFrame(right_frame, text="ℹ️ INFORMAÇÕES DO MOVIMENTO", padding="10")
        info_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        self.info_text = scrolledtext.ScrolledText(info_frame, width=40, height=15, font=('Courier', 9))
        self.info_text.pack(fill=tk.BOTH, expand=True)
        
        self.atualizar_campos_parametros()
        self.mostrar_formula("MRU")
    
    def selecionar_pasta(self):
        """Abre diálogo para selecionar a pasta de destino"""
        pasta = filedialog.askdirectory(title="Selecione a pasta para salvar relatórios e ontologia")
        if pasta:
            self.pasta_destino = pasta
            self.pasta_var.set(pasta)
            self.ontologia = OntologiaRDF(pasta_destino=self.pasta_destino)
            messagebox.showinfo("Sucesso", f"Pasta selecionada:\n{pasta}\n\nOntologia será salva em:\n{os.path.join(pasta, 'ontologia_movimentos.rdf')}")
    
    def setup_figura(self):
        """Configura a figura matplotlib"""
        self.fig = plt.figure(figsize=(9, 7), facecolor='white')
        self.ax = self.fig.add_subplot(111, projection='3d')
        self.ax.set_facecolor('#f8f9fa')
        
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.figura_frame)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
    
    def mostrar_formula(self, tipo):
        """Mostra a fórmula do movimento em destaque"""
        formula_data = FormularioMovimentos.get_formula(tipo)
        
        self.formula_text.delete(1.0, tk.END)
        
        self.formula_text.insert(tk.END, "="*40 + "\n", "center")
        self.formula_text.insert(tk.END, f"{formula_data['nome']}\n", "title")
        self.formula_text.insert(tk.END, "="*40 + "\n\n", "center")
        
        self.formula_text.insert(tk.END, "📐 EQUAÇÃO:\n", "subtitle")
        self.formula_text.insert(tk.END, f"   {formula_data['equacao_detalhada']}\n\n", "formula")
        
        self.formula_text.insert(tk.END, "📝 PARÂMETROS:\n", "subtitle")
        for param, desc in formula_data['parametros'].items():
            self.formula_text.insert(tk.END, f"   {param} = {desc}\n", "param")
        
        self.formula_text.insert(tk.END, "\n⚡ PROPRIEDADES:\n", "subtitle")
        self.formula_text.insert(tk.END, f"   {formula_data['propriedades']}\n", "prop")
        
        self.formula_text.tag_config("center", justify='center')
        self.formula_text.tag_config("title", font=('Arial', 12, 'bold'), foreground='#2c3e50')
        self.formula_text.tag_config("subtitle", font=('Arial', 10, 'bold'), foreground='#2980b9')
        self.formula_text.tag_config("formula", font=('Courier', 11, 'bold'), foreground='#e74c3c')
        self.formula_text.tag_config("param", font=('Courier', 9), foreground='#27ae60')
        self.formula_text.tag_config("prop", font=('Arial', 9), foreground='#f39c12')
    
    def atualizar_campos_parametros(self):
        """Atualiza os campos de entrada conforme o tipo de movimento"""
        for widget in self.param_frame.winfo_children():
            widget.destroy()
        
        tipo = self.tipo_movimento.get()
        self.entradas = {}
        
        self.mostrar_formula(tipo)
        
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
                          length=150, command=lambda x, p=param: self.atualizar_parametro(p))
        slider.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        
        var.trace('w', lambda *args, p=param: self.atualizar_parametro(p))
    
    def atualizar_parametro(self, param):
        if hasattr(self, 'entradas') and param in self.entradas:
            self.gerar_grafico()
    
    def obter_parametros(self):
        params = {}
        for key, var in self.entradas.items():
            params[key] = var.get()
        return params
    
    def gerar_grafico(self):
        """Gera o gráfico 3D e salva a imagem"""
        try:
            tipo = self.tipo_movimento.get()
            params = self.obter_parametros()
            
            t_total = self.calculadora.obter_tempo_total(tipo, params)
            if t_total <= 0:
                t_total = 10
            
            t = np.linspace(0, t_total, 500)
            
            if tipo == 'MRU':
                x, y, z = self.calculadora.calcular_mru(t, params['v'], params.get('pos_inicial', 0))
            elif tipo == 'MRUV':
                x, y, z = self.calculadora.calcular_mruv(t, params['v0'], params['a'], params.get('pos_inicial', 0))
            elif tipo == 'MCU':
                x, y, z = self.calculadora.calcular_mcu(t, params['r'], params['omega'], 
                                                       params.get('centro_x', 0), params.get('centro_y', 0))
            elif tipo == 'MHS':
                x, y, z = self.calculadora.calcular_mhs(t, params['A'], params['f'], params.get('phi', 0))
            elif tipo == 'Queda_Livre':
                x, y, z = self.calculadora.calcular_queda_livre(t, params['altura_inicial'], params.get('v0', 0))
            elif tipo == 'Lancamento_Obliquo':
                x, y, z = self.calculadora.calcular_lancamento_obliquo(t, params['v0'], params['angulo'], params.get('g', 9.81))
            else:
                return
            
            # Calcular resultados
            alcance = float(np.max(x)) if len(x) > 0 else 0
            altura_max = float(np.max(y)) if len(y) > 0 else 0
            
            self.dados_atual = {
                'tipo': tipo,
                'parametros': params,
                'trajetoria': (x, y, z),
                't_total': t_total,
                'alcance': alcance,
                'altura_max': altura_max
            }
            
            # Plotar gráfico
            self.ax.clear()
            
            self.ax.plot(x, y, z, 'b-', linewidth=3, label=f'{tipo}', alpha=0.9)
            self.ax.scatter(x[0], y[0], z[0], color='green', s=100, label='Início', alpha=0.8, edgecolors='black')
            self.ax.scatter(x[-1], y[-1], z[-1], color='red', s=100, label='Fim', alpha=0.8, edgecolors='black')
            
            formula_data = FormularioMovimentos.get_formula(tipo)
            
            x_pos = np.max(x) * 0.7 if len(x) > 0 else 5
            y_pos = np.max(y) * 0.8 if len(y) > 0 else 5
            z_pos = np.max(z) * 0.9 if len(z) > 0 else 5
            
            self.ax.text(x_pos, y_pos, z_pos, formula_data['equacao_detalhada'], 
                        fontsize=12, fontweight='bold', color='darkred',
                        bbox=dict(boxstyle='round,pad=0.5', facecolor='yellow', alpha=0.9, edgecolor='red'),
                        zorder=10)
            
            info_text = f"📐 {formula_data['nome']}\n{formula_data['propriedades']}"
            self.ax.text2D(0.02, 0.92, info_text, transform=self.ax.transAxes,
                          fontsize=9, verticalalignment='top',
                          bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.85))
            
            self.ax.set_xlabel('X (m)', fontsize=12, fontweight='bold')
            self.ax.set_ylabel('Y (m)', fontsize=12, fontweight='bold')
            self.ax.set_zlabel('Z (m)', fontsize=12, fontweight='bold')
            self.ax.set_title(f'Simulador de Movimentos - {formula_data["nome"]}', fontsize=14, fontweight='bold')
            self.ax.legend(loc='upper right', fontsize=10)
            self.ax.grid(True, alpha=0.3)
            
            margin = 0.1
            if len(x) > 0:
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
            
            # Salvar imagem do gráfico
            if self.pasta_destino:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                self.caminho_grafico_atual = os.path.join(self.pasta_destino, f"grafico_{tipo}_{timestamp}.png")
                self.fig.savefig(self.caminho_grafico_atual, dpi=150, bbox_inches='tight', facecolor='white')
            
            # Atualizar informações
            self.atualizar_info(params, t_total, formula_data, alcance, altura_max)
            
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao gerar gráfico: {str(e)}")
    
    def atualizar_info(self, params, t_total, formula_data, alcance, altura_max):
        """Atualiza o painel de informações"""
        self.info_text.delete(1.0, tk.END)
        
        self.info_text.insert(tk.END, "="*38 + "\n")
        self.info_text.insert(tk.END, "📊 INFORMAÇÕES DO MOVIMENTO\n")
        self.info_text.insert(tk.END, "="*38 + "\n\n")
        
        self.info_text.insert(tk.END, f"📐 {formula_data['nome']}\n")
        self.info_text.insert(tk.END, f"   {formula_data['equacao_detalhada']}\n\n")
        
        self.info_text.insert(tk.END, "📝 VALORES UTILIZADOS:\n")
        for key, value in params.items():
            simbolo = GeradorRelatorio._mapear_simbolo(key)
            self.info_text.insert(tk.END, f"   {simbolo} = {value:.2f}\n")
        
        self.info_text.insert(tk.END, f"\n⏱️ Tempo total: {t_total:.2f} s\n")
        self.info_text.insert(tk.END, f"📈 Alcance máximo: {alcance:.2f} m\n")
        self.info_text.insert(tk.END, f"📈 Altura máxima: {altura_max:.2f} m\n")
        
        if self.pasta_destino and self.caminho_grafico_atual:
            self.info_text.insert(tk.END, f"\n💾 Gráfico salvo em:\n   {os.path.basename(self.caminho_grafico_atual)}")
    
    def salvar_ontologia(self):
        """Salva o experimento na ontologia RDF"""
        if not self.pasta_destino:
            messagebox.showwarning("Aviso", "Selecione uma pasta para salvar primeiro!")
            return
        
        if self.dados_atual is None:
            messagebox.showwarning("Aviso", "Gere um gráfico primeiro!")
            return
        
        if not self.ontologia:
            self.ontologia = OntologiaRDF(pasta_destino=self.pasta_destino)
        
        resultado = {
            "tempo_total": self.dados_atual['t_total'],
            "alcance_maximo": self.dados_atual['alcance'],
            "altura_maxima": self.dados_atual['altura_max']
        }
        
        exp_id = self.ontologia.adicionar_experimento(
            self.dados_atual['tipo'],
            self.dados_atual['parametros'],
            resultado,
            self.caminho_grafico_atual or ""
        )
        
        messagebox.showinfo("Sucesso", f"Experimento salvo na ontologia!\nID: {exp_id}\nArquivo: {self.ontologia.arquivo}")
    
    def gerar_relatorio(self):
        """Gera o relatório HTML com gráfico e fórmula"""
        if not self.pasta_destino:
            messagebox.showwarning("Aviso", "Selecione uma pasta para salvar o relatório primeiro!")
            return
        
        if self.dados_atual is None:
            messagebox.showwarning("Aviso", "Gere um gráfico primeiro!")
            return
        
        if not self.caminho_grafico_atual or not os.path.exists(self.caminho_grafico_atual):
            messagebox.showwarning("Aviso", "Gráfico não encontrado. Gere o gráfico novamente!")
            return
        
        formula_data = FormularioMovimentos.get_formula(self.dados_atual['tipo'])
        
        caminho_relatorio = GeradorRelatorio.gerar_relatorio_html(
            self.pasta_destino,
            self.dados_atual,
            self.caminho_grafico_atual,
            formula_data
        )
        
        messagebox.showinfo("Sucesso", f"Relatório gerado com sucesso!\n\nArquivo: {caminho_relatorio}\n\nClique em OK para abrir o relatório.")
        
        # Abrir o relatório no navegador
        caminho_corrigido = caminho_relatorio.replace('\\', '/')
        webbrowser.open(f"file:///{caminho_corrigido}")
    
    def mostrar_historico(self):
        """Mostra o histórico de experimentos"""
        if not self.ontologia:
            messagebox.showwarning("Aviso", "Selecione uma pasta com ontologia primeiro!")
            return
        
        experimentos = self.ontologia.listar_experimentos()
        
        if not experimentos:
            messagebox.showinfo("Histórico", "Nenhum experimento salvo!")
            return
        
        hist_window = tk.Toplevel(self.root)
        hist_window.title("Histórico de Experimentos")
        hist_window.geometry("800x500")
        
        tree = ttk.Treeview(hist_window, columns=('ID', 'Tipo', 'Data', 'Grafico'), show='headings')
        tree.heading('ID', text='ID')
        tree.heading('Tipo', text='Tipo de Movimento')
        tree.heading('Data', text='Data')
        tree.heading('Grafico', text='Gráfico')
        
        tree.column('ID', width=50)
        tree.column('Tipo', width=150)
        tree.column('Data', width=200)
        tree.column('Grafico', width=300)
        
        for exp in experimentos:
            tree.insert('', tk.END, values=(
                exp['id'],
                exp['tipo'],
                exp.get('data', 'N/A')[:19],
                os.path.basename(exp.get('grafico', 'N/A'))
            ))
        
        tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        def abrir_grafico():
            item = tree.selection()
            if item:
                valores = tree.item(item[0])['values']
                nome_grafico = valores[3]
                if nome_grafico != 'N/A':
                    caminho = os.path.join(self.pasta_destino, nome_grafico)
                    if os.path.exists(caminho):
                        os.startfile(caminho)
                    else:
                        messagebox.showerror("Erro", "Arquivo do gráfico não encontrado!")
        
        ttk.Button(hist_window, text="Abrir Gráfico", command=abrir_grafico).pack(pady=5)
        ttk.Button(hist_window, text="Fechar", command=hist_window.destroy).pack(pady=5)


# ==================== MAIN ====================
if __name__ == "__main__":
    print("="*70)
    print("🎯 SIMULADOR DE MOVIMENTOS FÍSICOS COM RELATÓRIOS COMPLETOS")
    print("="*70)
    print("\n📌 Funcionalidades:")
    print("   ✅ Escolha a pasta para salvar relatórios e ontologia")
    print("   ✅ Gere gráficos 3D com fórmulas em destaque")
    print("   ✅ Salve experimentos na ontologia RDF")
    print("   ✅ Gere relatórios HTML com gráfico e fórmula")
    print("   ✅ Visualize histórico com acesso aos gráficos")
    print("\n🚀 Iniciando interface gráfica...\n")
    
    root = tk.Tk()
    app = AppMovimentos(root)
    root.mainloop()