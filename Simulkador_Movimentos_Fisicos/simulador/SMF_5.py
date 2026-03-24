"""
================================================================================
PHYSIMOTION - SIMULADOR DE MOVIMENTOS FÍSICOS PARA GRADUAÇÃO
================================================================================
PhysiMotion: Fusão de "Physics" (Física) e "Motion" (Movimento)

Desenvolvido para auxiliar estudantes de graduação no aprendizado de:
- Movimento Retilíneo Uniforme (MRU)
- Movimento Retilíneo Uniformemente Variado (MRUV)
- Movimento Circular Uniforme (MCU)
- Movimento Harmônico Simples (MHS)
- Queda Livre
- Lançamento Oblíquo

Autor: PhysiMotion Team
Versão: 2.0 - Modo Treinamento Acadêmico
Licença: Uso Educacional
================================================================================
"""

import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext, filedialog
import json
import os
import shutil
import webbrowser
from datetime import datetime
from rdflib import Graph, Literal, RDF, RDFS, Namespace
from rdflib.namespace import XSD

# ==================== CONFIGURAÇÕES DO PROGRAMA ====================
PROGRAM_NAME = "PhysiMotion"
PROGRAM_VERSION = "2.0"
PROGRAM_SUBTITLE = "Simulador de Movimentos Físicos para Graduação"
PROGRAM_AUTHOR = "PhysiMotion Team"
PROGRAM_YEAR = "2025"

# ==================== NAMESPACES DA ONTOLOGIA RDF ====================
MOV = Namespace("http://www.physicsimulator.org/ontologia#")
BASE = Namespace("http://www.physicsimulator.org/")

# ==================== FORMULÁRIO COMPLETO DE MOVIMENTOS ====================
class FormularioMovimentos:
    """Classe que armazena as fórmulas e conceitos físicos"""
    
    FORMULAS = {
        'MRU': {
            'nome': 'Movimento Retilíneo Uniforme',
            'nome_latim': 'Motum Rectilineum Uniforme',
            'equacao': 'x = x₀ + v·t',
            'equacao_detalhada': 'x(t) = x₀ + v·t',
            'parametros': {
                'x₀': 'Posição inicial (m)',
                'v': 'Velocidade constante (m/s)',
                't': 'Tempo (s)'
            },
            'propriedades': 'Velocidade constante → Aceleração = 0',
            'grafico': 'Reta inclinada no gráfico x × t',
            'conceito': 'Um corpo em MRU percorre distâncias iguais em intervalos de tempo iguais.',
            'aplicacao': 'Veículos em movimento constante, esteiras transportadoras, movimento de planetas (aproximação)',
            'exercicio': 'Um carro se move com velocidade constante de 20 m/s. Qual a posição após 10 segundos?',
            'resposta': 'x = 0 + 20·10 = 200 m'
        },
        'MRUV': {
            'nome': 'Movimento Retilíneo Uniformemente Variado',
            'nome_latim': 'Motum Rectilineum Uniformiter Variatum',
            'equacao': 'x = x₀ + v₀·t + ½·a·t²',
            'equacao_detalhada': 'x(t) = x₀ + v₀·t + (1/2)·a·t²',
            'parametros': {
                'x₀': 'Posição inicial (m)',
                'v₀': 'Velocidade inicial (m/s)',
                'a': 'Aceleração constante (m/s²)',
                't': 'Tempo (s)'
            },
            'propriedades': 'Aceleração constante → Velocidade varia linearmente',
            'grafico': 'Parábola no gráfico x × t',
            'conceito': 'A aceleração constante implica que a velocidade varia uniformemente com o tempo.',
            'aplicacao': 'Queda livre (desprezando resistência), frenagem de veículos, foguetes',
            'exercicio': 'Um corpo parte do repouso com aceleração 2 m/s². Qual a velocidade após 5 segundos?',
            'resposta': 'v = v₀ + a·t = 0 + 2·5 = 10 m/s'
        },
        'MCU': {
            'nome': 'Movimento Circular Uniforme',
            'nome_latim': 'Motum Circulare Uniforme',
            'equacao': 'x = x_c + r·cos(ω·t)\ny = y_c + r·sen(ω·t)',
            'equacao_detalhada': 'x(t) = x_c + r·cos(ω·t)\ny(t) = y_c + r·sen(ω·t)',
            'parametros': {
                'x_c': 'Centro X (m)',
                'y_c': 'Centro Y (m)',
                'r': 'Raio (m)',
                'ω': 'Velocidade angular (rad/s)',
                't': 'Tempo (s)'
            },
            'propriedades': 'Velocidade angular constante → Aceleração centrípeta',
            'grafico': 'Circunferência no plano XY',
            'conceito': 'Aceleração centrípeta: a_c = ω²·r = v²/r, direcionada ao centro',
            'aplicacao': 'Satélites em órbita, roda-gigante, CDs/DVDs',
            'exercicio': 'Um disco gira com frequência 10 Hz. Qual sua velocidade angular?',
            'resposta': 'ω = 2π·f = 2π·10 = 62,8 rad/s'
        },
        'MHS': {
            'nome': 'Movimento Harmônico Simples',
            'nome_latim': 'Motum Harmonicum Simplex',
            'equacao': 'x = A·sen(ω·t + φ)',
            'equacao_detalhada': 'x(t) = A·sen(2π·f·t + φ)',
            'parametros': {
                'A': 'Amplitude (m)',
                'f': 'Frequência (Hz)',
                'ω': 'Frequência angular = 2πf (rad/s)',
                'φ': 'Fase inicial (rad)',
                't': 'Tempo (s)'
            },
            'propriedades': 'Força restauradora F = -k·x → Movimento oscilatório',
            'grafico': 'Senoide no gráfico x × t',
            'conceito': 'Energia mecânica se conserva: E = (1/2)kA²',
            'aplicacao': 'Pêndulo simples, sistema massa-mola, circuitos LC',
            'exercicio': 'Um oscilador tem amplitude 0,5 m e frequência 2 Hz. Qual a velocidade máxima?',
            'resposta': 'v_max = ω·A = 2πf·A = 2π·2·0,5 = 6,28 m/s'
        },
        'Queda_Livre': {
            'nome': 'Queda Livre',
            'nome_latim': 'Casus Liber',
            'equacao': 'y = h₀ + v₀·t - ½·g·t²',
            'equacao_detalhada': 'y(t) = h₀ + v₀·t - (1/2)·g·t²',
            'parametros': {
                'h₀': 'Altura inicial (m)',
                'v₀': 'Velocidade inicial (m/s)',
                'g': 'Aceleração da gravidade (9,81 m/s²)',
                't': 'Tempo (s)'
            },
            'propriedades': 'Queda sob ação exclusiva da gravidade (resistência desprezada)',
            'grafico': 'Parábola decrescente no gráfico y × t',
            'conceito': 'Aceleração constante g, independente da massa do corpo',
            'aplicacao': 'Pára-quedismo, experimentos de Galileu, física atmosférica',
            'exercicio': 'Um objeto é abandonado de 50 m de altura. Quanto tempo leva para atingir o solo?',
            'resposta': 't = √(2h/g) = √(2·50/9,81) = 3,19 s'
        },
        'Lancamento_Obliquo': {
            'nome': 'Lançamento Oblíquo',
            'nome_latim': 'Iactus Obliquus',
            'equacao': 'x = (v₀·cosθ)·t\ny = (v₀·senθ)·t - ½·g·t²',
            'equacao_detalhada': 'x(t) = v₀·cosθ·t\ny(t) = v₀·senθ·t - (1/2)·g·t²',
            'parametros': {
                'v₀': 'Velocidade inicial (m/s)',
                'θ': 'Ângulo de lançamento (graus)',
                'g': 'Aceleração da gravidade (m/s²)',
                't': 'Tempo (s)'
            },
            'propriedades': 'Composição de MRU (horizontal) e MRUV (vertical)',
            'grafico': 'Parábola no plano XY',
            'conceito': 'Alcance máximo para θ = 45° (desprezando resistência)',
            'aplicacao': 'Projéteis, esportes (futebol, basquete), foguetes',
            'exercicio': 'Um projétil é lançado com 20 m/s a 30°. Qual o alcance máximo?',
            'resposta': 'A = (v₀²·sen(2θ))/g = (400·sen60°)/9,81 = 35,3 m'
        }
    }
    
    @classmethod
    def get_formula(cls, tipo):
        return cls.FORMULAS.get(tipo, {})
    
    @classmethod
    def get_tipos(cls):
        return list(cls.FORMULAS.keys())
    
    @classmethod
    def get_conceito(cls, tipo):
        return cls.FORMULAS.get(tipo, {}).get('conceito', '')
    
    @classmethod
    def get_exercicio(cls, tipo):
        return cls.FORMULAS.get(tipo, {}).get('exercicio', '')
    
    @classmethod
    def get_resposta(cls, tipo):
        return cls.FORMULAS.get(tipo, {}).get('resposta', '')

# ==================== ONTOLOGIA RDF ====================
class OntologiaRDF:
    def __init__(self, pasta_destino="", arquivo="ph_ontologia_movimentos.rdf"):
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
        self.g.bind("ph", MOV)
        self.g.bind("base", BASE)
        self.g.bind("rdf", RDF)
        self.g.bind("rdfs", RDFS)
        self.g.bind("xsd", XSD)
    
    def criar_ontologia_base(self):
        self.g.add((MOV.Movimento, RDF.type, RDFS.Class))
        self.g.add((MOV.Movimento, RDFS.label, Literal("Movimento Físico", lang="pt")))
        self.g.add((MOV.Movimento, RDFS.comment, Literal("Classe que representa um movimento físico", lang="pt")))
        
        for tipo, dados in FormularioMovimentos.FORMULAS.items():
            classe_uri = MOV[tipo]
            self.g.add((classe_uri, RDF.type, RDFS.Class))
            self.g.add((classe_uri, RDFS.subClassOf, MOV.Movimento))
            self.g.add((classe_uri, RDFS.label, Literal(dados['nome'], lang="pt")))
            self.g.add((classe_uri, MOV.formula, Literal(dados['equacao'])))
            self.g.add((classe_uri, MOV.conceito, Literal(dados['conceito'], lang="pt")))
        
        self.salvar()
    
    def adicionar_experimento(self, tipo_movimento, parametros, resultado, caminho_grafico="", nota_aluno=""):
        exp_id = len(list(self.g.subjects(RDF.type, MOV.Experimento))) + 1
        exp_uri = MOV[f"Experimento_{exp_id}"]
        
        self.g.add((exp_uri, RDF.type, MOV.Experimento))
        self.g.add((exp_uri, RDF.type, MOV[tipo_movimento]))
        self.g.add((exp_uri, MOV.dataExperimento, Literal(datetime.now().isoformat(), datatype=XSD.dateTime)))
        
        if caminho_grafico:
            self.g.add((exp_uri, MOV.grafico, Literal(caminho_grafico)))
        if nota_aluno:
            self.g.add((exp_uri, MOV.notaAluno, Literal(nota_aluno, lang="pt")))
        
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
            'g': 'gravidade', 'altura_inicial': 'alturaInicial', 'phi': 'faseInicial'
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
    
    @staticmethod
    def calcular_resultados(tipo, parametros):
        """Calcula resultados específicos para cada movimento"""
        resultados = {}
        
        if tipo == 'MRU':
            v = parametros.get('v', 0)
            resultados['velocidade'] = v
            resultados['aceleracao'] = 0
        
        elif tipo == 'MRUV':
            v0 = parametros.get('v0', 0)
            a = parametros.get('a', 0)
            resultados['velocidade_inicial'] = v0
            resultados['aceleracao'] = a
            resultados['velocidade_final'] = v0 + a * 10
        
        elif tipo == 'MCU':
            r = parametros.get('r', 0)
            omega = parametros.get('omega', 0)
            resultados['raio'] = r
            resultados['velocidade_angular'] = omega
            resultados['velocidade_linear'] = omega * r
            resultados['aceleracao_centripeta'] = omega**2 * r
        
        elif tipo == 'MHS':
            A = parametros.get('A', 0)
            f = parametros.get('f', 0)
            omega = 2 * np.pi * f
            resultados['amplitude'] = A
            resultados['frequencia'] = f
            resultados['velocidade_maxima'] = omega * A
            resultados['aceleracao_maxima'] = omega**2 * A
        
        elif tipo == 'Queda_Livre':
            h = parametros.get('altura_inicial', 0)
            g = 9.81
            t_total = np.sqrt(2 * h / g) if h > 0 else 0
            resultados['altura_inicial'] = h
            resultados['tempo_queda'] = t_total
            resultados['velocidade_impacto'] = g * t_total
        
        elif tipo == 'Lancamento_Obliquo':
            v0 = parametros.get('v0', 0)
            angulo = parametros.get('angulo', 45)
            g = parametros.get('g', 9.81)
            ang_rad = np.radians(angulo)
            v0x = v0 * np.cos(ang_rad)
            v0y = v0 * np.sin(ang_rad)
            t_total = 2 * v0y / g
            resultados['velocidade_inicial'] = v0
            resultados['angulo'] = angulo
            resultados['alcance'] = v0x * t_total
            resultados['altura_maxima'] = (v0y**2) / (2 * g)
            resultados['tempo_voo'] = t_total
        
        return resultados

# ==================== GERADOR DE RELATÓRIOS ACADÊMICOS ====================
class GeradorRelatorio:
    @staticmethod
    def gerar_relatorio_academico(pasta_destino, dados_experimento, caminho_grafico, formula_data, resultados):
        """Gera um relatório acadêmico em HTML com formato científico"""
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        nome_arquivo = f"ph_relatorio_{dados_experimento['tipo']}_{timestamp}.html"
        caminho_relatorio = os.path.join(pasta_destino, nome_arquivo)
        
        nome_grafico = f"ph_grafico_{dados_experimento['tipo']}_{timestamp}.png"
        caminho_grafico_relatorio = os.path.join(pasta_destino, nome_grafico)
        
        if os.path.exists(caminho_grafico):
            shutil.copy(caminho_grafico, caminho_grafico_relatorio)
        
        # Gerar HTML acadêmico
        html_content = f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>PhysiMotion - Relatório Acadêmico | {formula_data['nome']}</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        body {{
            font-family: 'Times New Roman', Georgia, serif;
            background: #f5f5f5;
            padding: 30px;
        }}
        .paper {{
            max-width: 1100px;
            margin: 0 auto;
            background: white;
            box-shadow: 0 5px 20px rgba(0,0,0,0.1);
            border-radius: 5px;
        }}
        .header {{
            background: linear-gradient(135deg, #1a3e60 0%, #2c5a7a 100%);
            color: white;
            padding: 30px;
            text-align: center;
            border-bottom: 3px solid #e67e22;
        }}
        .header h1 {{
            font-size: 2.2em;
            margin-bottom: 10px;
            letter-spacing: 2px;
        }}
        .header h1 span {{
            color: #e67e22;
        }}
        .header .subtitle {{
            font-size: 1.1em;
            opacity: 0.9;
            font-style: italic;
        }}
        .content {{
            padding: 40px;
        }}
        .section {{
            margin-bottom: 30px;
            page-break-inside: avoid;
        }}
        .section-title {{
            font-size: 1.5em;
            color: #1a3e60;
            border-left: 4px solid #e67e22;
            padding-left: 15px;
            margin-bottom: 20px;
            font-weight: bold;
        }}
        .formula-box {{
            background: #f8f9fa;
            padding: 25px;
            border-radius: 10px;
            text-align: center;
            border: 1px solid #dee2e6;
            margin: 20px 0;
        }}
        .formula {{
            font-size: 1.8em;
            font-family: 'Courier New', monospace;
            font-weight: bold;
            color: #c7254e;
            background: #f9f2f4;
            padding: 15px;
            border-radius: 8px;
            display: inline-block;
        }}
        .params-table {{
            width: 100%;
            border-collapse: collapse;
            margin: 15px 0;
        }}
        .params-table th, .params-table td {{
            padding: 10px;
            border: 1px solid #ddd;
            text-align: left;
        }}
        .params-table th {{
            background: #1a3e60;
            color: white;
        }}
        .params-table tr:nth-child(even) {{
            background: #f9f9f9;
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
            border-radius: 5px;
            box-shadow: 0 3px 10px rgba(0,0,0,0.1);
        }}
        .conceito-box {{
            background: #e8f4f8;
            padding: 20px;
            border-radius: 10px;
            margin: 20px 0;
            border-left: 5px solid #3498db;
        }}
        .resultados {{
            background: #fef9e6;
            padding: 20px;
            border-radius: 10px;
            margin: 20px 0;
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
            background: #e67e22;
            color: white;
            padding: 5px 15px;
            border-radius: 20px;
            font-size: 0.8em;
            margin: 5px;
        }}
        .reference {{
            font-size: 0.85em;
            color: #666;
            margin-top: 20px;
            padding-top: 20px;
            border-top: 1px solid #ddd;
        }}
        @media print {{
            body {{
                background: white;
                padding: 0;
            }}
            .header {{
                -webkit-print-color-adjust: exact;
                print-color-adjust: exact;
            }}
        }}
    </style>
</head>
<body>
    <div class="paper">
        <div class="header">
            <h1>PHYSIMOTION <span>®</span></h1>
            <div class="subtitle">Laboratório Virtual de Física Computacional</div>
            <p style="margin-top: 15px; font-size: 1.2em;">{formula_data['nome']}</p>
            <p style="margin-top: 5px; font-size: 0.9em;">{formula_data['nome_latim']}</p>
            <p style="margin-top: 5px; font-size: 0.8em;">Gerado em {datetime.now().strftime('%d de %B de %Y às %H:%M')}</p>
        </div>
        
        <div class="content">
            <div class="section">
                <div class="section-title">📐 1. FUNDAMENTAÇÃO TEÓRICA</div>
                <div class="formula-box">
                    <div class="formula">
                        {formula_data['equacao_detalhada'].replace(chr(10), '<br>')}
                    </div>
                </div>
                <div class="conceito-box">
                    <strong>📖 Conceito Físico:</strong><br>
                    {formula_data['conceito']}
                </div>
                <p><strong>🔬 Aplicações Práticas:</strong> {formula_data['aplicacao']}</p>
            </div>
            
            <div class="section">
                <div class="section-title">📝 2. PARÂMETROS UTILIZADOS</div>
                <table class="params-table">
                    <thead>
                        <tr><th>Parâmetro</th><th>Símbolo</th><th>Valor</th><th>Unidade</th></tr>
                    </thead>
                    <tbody>
"""
        
        # Adicionar parâmetros
        for key, value in dados_experimento['parametros'].items():
            simbolo = GeradorRelatorio._mapear_simbolo(key)
            unidade = GeradorRelatorio._obter_unidade(key)
            html_content += f"""
                        <tr><td>{GeradorRelatorio._descricao_param(key)}</td><td>{simbolo}</td><td>{value:.2f}</td><td>{unidade}</td></tr>
"""
        
        html_content += f"""
                    </tbody>
                </table>
            </div>
            
            <div class="section">
                <div class="section-title">📈 3. ANÁLISE GRÁFICA</div>
                <div class="grafico">
                    <img src="{nome_grafico}" alt="Gráfico 3D do Movimento - PhysiMotion">
                    <p style="margin-top: 15px; color: #666;">
                        <strong>Figura 1:</strong> Trajetória tridimensional do {formula_data['nome']}<br>
                        {formula_data['grafico']}
                    </p>
                </div>
            </div>
            
            <div class="section">
                <div class="section-title">📊 4. RESULTADOS OBTIDOS</div>
                <div class="resultados">
                    <table class="params-table">
                        <thead><tr><th>Grandeza Física</th><th>Valor</th><th>Unidade</th></tr></thead>
                        <tbody>
                            <tr><td>Tempo total de movimento</td><td>{dados_experimento['t_total']:.2f}</td><td>s</td></tr>
                            <tr><td>Alcance máximo</td><td>{dados_experimento['alcance']:.2f}</td><td>m</td></tr>
                            <tr><td>Altura máxima</td><td>{dados_experimento['altura_max']:.2f}</td><td>m</td></tr>
"""
        
        # Adicionar resultados específicos
        if resultados:
            for key, value in resultados.items():
                nome_formatado = key.replace('_', ' ').title()
                unidade = GeradorRelatorio._obter_unidade_resultado(key)
                html_content += f"""
                            <tr><td>{nome_formatado}</td><td>{value:.2f}</td><td>{unidade}</td></tr>
"""
        
        html_content += f"""
                        </tbody>
                    </table>
                </div>
            </div>
            
            <div class="section">
                <div class="section-title">💡 5. EXERCÍCIO DE FIXAÇÃO</div>
                <div class="conceito-box">
                    <strong>❓ Questão:</strong><br>
                    {formula_data['exercicio']}
                </div>
                <div class="conceito-box" style="background: #e8f5e9;">
                    <strong>✅ Resolução:</strong><br>
                    {formula_data['resposta']}
                </div>
            </div>
            
            <div class="reference">
                <strong>📚 Referências Bibliográficas:</strong><br>
                HALLIDAY, David; RESNICK, Robert; WALKER, Jearl. Fundamentos de Física. 10. ed. Rio de Janeiro: LTC, 2016.<br>
                NUSSENZVEIG, Herch Moysés. Curso de Física Básica. 5. ed. São Paulo: Blucher, 2015.<br>
                TIPLER, Paul A.; MOSCA, Gene. Física para Cientistas e Engenheiros. 6. ed. Rio de Janeiro: LTC, 2014.<br>
                YOUNG, Hugh D.; FREEDMAN, Roger A. Física Universitária. 14. ed. São Paulo: Pearson, 2016.
            </div>
        </div>
        
        <div class="footer">
            <p>📚 Relatório gerado pelo <strong>PhysiMotion®</strong> - Simulador de Movimentos Físicos para Graduação</p>
            <p>🏷️ Ontologia RDF: {os.path.basename(dados_experimento.get('ontologia', 'ph_ontologia_movimentos.rdf'))}</p>
            <p>© {datetime.now().year} PhysiMotion Team - Todos os direitos reservados para fins educacionais</p>
            <p>🔬 Laboratório Virtual de Física Computacional</p>
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
    
    @staticmethod
    def _descricao_param(key):
        descricoes = {
            'v': 'Velocidade', 'v0': 'Velocidade inicial', 'a': 'Aceleração',
            'pos_inicial': 'Posição inicial', 'r': 'Raio', 'omega': 'Velocidade angular',
            'centro_x': 'Centro X', 'centro_y': 'Centro Y', 'A': 'Amplitude',
            'f': 'Frequência', 'phi': 'Fase inicial', 'altura_inicial': 'Altura inicial',
            'angulo': 'Ângulo de lançamento', 'g': 'Aceleração da gravidade'
        }
        return descricoes.get(key, key)
    
    @staticmethod
    def _obter_unidade(key):
        unidades = {
            'v': 'm/s', 'v0': 'm/s', 'a': 'm/s²', 'pos_inicial': 'm',
            'r': 'm', 'omega': 'rad/s', 'centro_x': 'm', 'centro_y': 'm',
            'A': 'm', 'f': 'Hz', 'phi': 'rad', 'altura_inicial': 'm',
            'angulo': '°', 'g': 'm/s²'
        }
        return unidades.get(key, '')
    
    @staticmethod
    def _obter_unidade_resultado(key):
        unidades = {
            'velocidade': 'm/s', 'aceleracao': 'm/s²', 'velocidade_inicial': 'm/s',
            'velocidade_final': 'm/s', 'velocidade_angular': 'rad/s',
            'velocidade_linear': 'm/s', 'aceleracao_centripeta': 'm/s²',
            'amplitude': 'm', 'frequencia': 'Hz', 'velocidade_maxima': 'm/s',
            'aceleracao_maxima': 'm/s²', 'tempo_queda': 's', 'velocidade_impacto': 'm/s',
            'alcance': 'm', 'altura_maxima': 'm', 'tempo_voo': 's', 'angulo': '°'
        }
        return unidades.get(key, '')

# ==================== INTERFACE PRINCIPAL - PHYSIMOTION ====================
class PhysiMotionApp:
    def __init__(self, root):
        self.root = root
        self.root.title(f"PhysiMotion® - {PROGRAM_SUBTITLE} v{PROGRAM_VERSION}")
        self.root.geometry("1600x900")
        self.root.configure(bg='#f0f2f5')
        
        # Ícone da janela (se disponível)
        try:
            self.root.iconbitmap('ph_icon.ico')
        except:
            pass
        
        self.pasta_destino = ""
        self.ontologia = None
        self.calculadora = CalculadoraMovimentos()
        self.dados_atual = None
        self.caminho_grafico_atual = None
        self.entradas = {}
        
        self.setup_estilo()
        self.setup_interface()
        self.setup_figura()
        
    def setup_estilo(self):
        """Configura o estilo visual da interface"""
        style = ttk.Style()
        style.theme_use('clam')
        
        # Cores do PhysiMotion
        PH_PRIMARY = "#1a3e60"
        PH_SECONDARY = "#e67e22"
        PH_ACCENT = "#3498db"
        PH_SUCCESS = "#27ae60"
        
        style.configure("Title.TLabel", font=('Segoe UI', 18, 'bold'), foreground=PH_PRIMARY)
        style.configure("Subtitle.TLabel", font=('Segoe UI', 10), foreground='#666')
        style.configure("Success.TButton", font=('Segoe UI', 10, 'bold'), background=PH_SUCCESS)
        style.configure("Primary.TButton", font=('Segoe UI', 10, 'bold'), background=PH_ACCENT)
        style.configure("Warning.TButton", font=('Segoe UI', 10, 'bold'), background=PH_SECONDARY)
        
        style.configure("Card.TFrame", background='white', relief='raised', borderwidth=1)
        style.configure("Card.TLabelframe", background='white', relief='raised', borderwidth=1)
        style.configure("Card.TLabelframe.Label", background='white', foreground=PH_PRIMARY, font=('Segoe UI', 11, 'bold'))
        
    def setup_interface(self):
        """Configura a interface gráfica"""
        # Frame principal com scroll
        main_canvas = tk.Canvas(self.root, bg='#f0f2f5', highlightthickness=0)
        scrollbar = ttk.Scrollbar(self.root, orient="vertical", command=main_canvas.yview)
        self.scrollable_frame = ttk.Frame(main_canvas)
        
        self.scrollable_frame.bind("<Configure>", lambda e: main_canvas.configure(scrollregion=main_canvas.bbox("all")))
        main_canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        main_canvas.configure(yscrollcommand=scrollbar.set)
        
        main_canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        main_frame = self.scrollable_frame
        
        # === CABEÇALHO PHYSIMOTION ===
        header_frame = ttk.Frame(main_frame, style="Card.TFrame")
        header_frame.pack(fill=tk.X, padx=20, pady=10)
        
        # Logo e título
        title_frame = ttk.Frame(header_frame)
        title_frame.pack(pady=(15,5))
        
        ttk.Label(title_frame, text="⚛️ PHYSIMOTION ®", style="Title.TLabel").pack()
        ttk.Label(title_frame, text=PROGRAM_SUBTITLE, style="Subtitle.TLabel").pack()
        ttk.Label(title_frame, text="Explore, visualize e compreenda os fundamentos da Mecânica Clássica", style="Subtitle.TLabel").pack(pady=(0,15))
        
        # Versão
        ttk.Label(header_frame, text=f"Versão {PROGRAM_VERSION} | {PROGRAM_AUTHOR} | {PROGRAM_YEAR}", 
                  font=('Segoe UI', 8), foreground='#888').pack(pady=(0,10))
        
        # === BARRA DE FERRAMENTAS ===
        toolbar_frame = ttk.Frame(main_frame)
        toolbar_frame.pack(fill=tk.X, padx=20, pady=5)
        
        # Seleção de pasta
        pasta_frame = ttk.Frame(toolbar_frame, style="Card.TFrame")
        pasta_frame.pack(side=tk.LEFT, padx=5, pady=5)
        
        self.pasta_var = tk.StringVar(value="📁 Nenhuma pasta selecionada")
        ttk.Label(pasta_frame, textvariable=self.pasta_var, font=('Segoe UI', 9)).pack(side=tk.LEFT, padx=10)
        ttk.Button(pasta_frame, text="Selecionar Pasta", command=self.selecionar_pasta, style="Primary.TButton").pack(side=tk.RIGHT, padx=5)
        
        # === CONTEÚDO PRINCIPAL ===
        content_frame = ttk.Frame(main_frame)
        content_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # COLUNA ESQUERDA - CONTROLES
        left_frame = ttk.LabelFrame(content_frame, text="🎮 CONTROLES DO EXPERIMENTO", style="Card.TLabelframe", padding="15")
        left_frame.pack(side=tk.LEFT, fill=tk.Y, padx=5)
        
        # Seleção do movimento
        ttk.Label(left_frame, text="Tipo de Movimento:", font=('Segoe UI', 11, 'bold')).pack(anchor=tk.W, pady=(0,10))
        
        self.tipo_movimento = tk.StringVar(value="MRU")
        tipos = ["MRU", "MRUV", "MCU", "MHS", "Queda_Livre", "Lancamento_Obliquo"]
        
        tipo_frame = ttk.Frame(left_frame)
        tipo_frame.pack(fill=tk.X, pady=5)
        
        for i, tipo in enumerate(tipos):
            rb = ttk.Radiobutton(tipo_frame, text=tipo, variable=self.tipo_movimento, 
                                value=tipo, command=self.atualizar_campos_parametros)
            rb.grid(row=i//2, column=i%2, sticky=tk.W, padx=5, pady=3)
        
        ttk.Separator(left_frame, orient='horizontal').pack(fill=tk.X, pady=10)
        
        # Parâmetros
        self.param_frame = ttk.LabelFrame(left_frame, text="⚙️ PARÂMETROS DO MOVIMENTO", style="Card.TLabelframe", padding="10")
        self.param_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # Botões de ação
        btn_frame = ttk.Frame(left_frame)
        btn_frame.pack(fill=tk.X, pady=10)
        
        ttk.Button(btn_frame, text="▶ GERAR GRÁFICO", command=self.gerar_grafico, style="Success.TButton").pack(fill=tk.X, pady=3)
        ttk.Button(btn_frame, text="💾 SALVAR NA ONTOLOGIA", command=self.salvar_ontologia, style="Primary.TButton").pack(fill=tk.X, pady=3)
        ttk.Button(btn_frame, text="📄 GERAR RELATÓRIO", command=self.gerar_relatorio, style="Primary.TButton").pack(fill=tk.X, pady=3)
        ttk.Button(btn_frame, text="📋 VER HISTÓRICO", command=self.mostrar_historico, style="Primary.TButton").pack(fill=tk.X, pady=3)
        ttk.Button(btn_frame, text="🔄 RESETAR", command=self.resetar, style="Warning.TButton").pack(fill=tk.X, pady=3)
        
        # COLUNA CENTRAL - GRÁFICO
        center_frame = ttk.LabelFrame(content_frame, text="📊 VISUALIZAÇÃO 3D - PHYSIMOTION", style="Card.TLabelframe", padding="10")
        center_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10)
        
        self.figura_frame = ttk.Frame(center_frame)
        self.figura_frame.pack(fill=tk.BOTH, expand=True)
        
        # COLUNA DIREITA - CONCEITOS E INFORMAÇÕES
        right_frame = ttk.Frame(content_frame)
        right_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=5)
        
        # Fórmula
        formula_frame = ttk.LabelFrame(right_frame, text="📐 FÓRMULA FUNDAMENTAL", style="Card.TLabelframe", padding="10")
        formula_frame.pack(fill=tk.X, pady=5)
        
        self.formula_text = scrolledtext.ScrolledText(formula_frame, width=45, height=8, 
                                                       font=('Courier New', 11, 'bold'), bg='#f8f9fa')
        self.formula_text.pack(fill=tk.X)
        
        # Conceito
        conceito_frame = ttk.LabelFrame(right_frame, text="📖 CONCEITO FÍSICO", style="Card.TLabelframe", padding="10")
        conceito_frame.pack(fill=tk.X, pady=5)
        
        self.conceito_text = scrolledtext.ScrolledText(conceito_frame, width=45, height=5, 
                                                        font=('Segoe UI', 10), bg='#e8f4f8')
        self.conceito_text.pack(fill=tk.X)
        
        # Exercício
        exercicio_frame = ttk.LabelFrame(right_frame, text="💡 EXERCÍCIO DE FIXAÇÃO", style="Card.TLabelframe", padding="10")
        exercicio_frame.pack(fill=tk.X, pady=5)
        
        self.exercicio_text = scrolledtext.ScrolledText(exercicio_frame, width=45, height=4, 
                                                         font=('Segoe UI', 10), bg='#fef9e6')
        self.exercicio_text.pack(fill=tk.X)
        
        # Resultados
        info_frame = ttk.LabelFrame(right_frame, text="📊 RESULTADOS NUMÉRICOS", style="Card.TLabelframe", padding="10")
        info_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        self.info_text = scrolledtext.ScrolledText(info_frame, width=45, height=12, font=('Courier New', 9))
        self.info_text.pack(fill=tk.BOTH, expand=True)
        
        self.atualizar_campos_parametros()
        self.mostrar_formula("MRU")
    
    def selecionar_pasta(self):
        pasta = filedialog.askdirectory(title="Selecione a pasta para salvar relatórios e ontologia")
        if pasta:
            self.pasta_destino = pasta
            self.pasta_var.set(f"📁 {pasta}")
            self.ontologia = OntologiaRDF(pasta_destino=self.pasta_destino)
            messagebox.showinfo("PhysiMotion", f"✅ Pasta selecionada!\n\nOs relatórios e a ontologia serão salvos em:\n{pasta}")
    
    def setup_figura(self):
        self.fig = plt.figure(figsize=(10, 8), facecolor='white', dpi=100)
        self.ax = self.fig.add_subplot(111, projection='3d')
        self.ax.set_facecolor('#f8f9fa')
        self.ax.grid(True, alpha=0.3)
        
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.figura_frame)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        toolbar = NavigationToolbar2Tk(self.canvas, self.figura_frame)
        toolbar.update()
    
    def mostrar_formula(self, tipo):
        formula_data = FormularioMovimentos.get_formula(tipo)
        
        self.formula_text.delete(1.0, tk.END)
        self.formula_text.insert(tk.END, f"{'═'*45}\n", "center")
        self.formula_text.insert(tk.END, f"{formula_data['nome']}\n", "title")
        self.formula_text.insert(tk.END, f"{'═'*45}\n\n", "center")
        self.formula_text.insert(tk.END, f"📐 {formula_data['equacao_detalhada']}\n\n", "formula")
        
        self.conceito_text.delete(1.0, tk.END)
        self.conceito_text.insert(tk.END, formula_data['conceito'])
        
        self.exercicio_text.delete(1.0, tk.END)
        self.exercicio_text.insert(tk.END, f"❓ {formula_data['exercicio']}\n\n✅ {formula_data['resposta']}")
        
        self.formula_text.tag_config("center", justify='center')
        self.formula_text.tag_config("title", font=('Segoe UI', 12, 'bold'), foreground='#1a3e60')
        self.formula_text.tag_config("formula", font=('Courier New', 12, 'bold'), foreground='#e67e22')
    
    def atualizar_campos_parametros(self):
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
            
            alcance = float(np.max(x)) if len(x) > 0 else 0
            altura_max = float(np.max(y)) if len(y) > 0 else 0
            
            resultados = self.calculadora.calcular_resultados(tipo, params)
            
            self.dados_atual = {
                'tipo': tipo,
                'parametros': params,
                'trajetoria': (x, y, z),
                't_total': t_total,
                'alcance': alcance,
                'altura_max': altura_max,
                'resultados': resultados
            }
            
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
            self.ax.set_title(f'PhysiMotion® - {formula_data["nome"]}', fontsize=14, fontweight='bold')
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
            
            if self.pasta_destino:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                self.caminho_grafico_atual = os.path.join(self.pasta_destino, f"ph_grafico_{tipo}_{timestamp}.png")
                self.fig.savefig(self.caminho_grafico_atual, dpi=150, bbox_inches='tight', facecolor='white')
            
            self.atualizar_info(params, t_total, formula_data, alcance, altura_max, resultados)
            
        except Exception as e:
            messagebox.showerror("PhysiMotion - Erro", f"Erro ao gerar gráfico: {str(e)}")
    
    def atualizar_info(self, params, t_total, formula_data, alcance, altura_max, resultados):
        self.info_text.delete(1.0, tk.END)
        
        self.info_text.insert(tk.END, "═"*45 + "\n")
        self.info_text.insert(tk.END, "📊 PHYSIMOTION - RESULTADOS\n")
        self.info_text.insert(tk.END, "═"*45 + "\n\n")
        
        self.info_text.insert(tk.END, f"📐 {formula_data['nome']}\n")
        self.info_text.insert(tk.END, f"   {formula_data['equacao_detalhada']}\n\n")
        
        self.info_text.insert(tk.END, "📝 PARÂMETROS:\n")
        for key, value in params.items():
            simbolo = GeradorRelatorio._mapear_simbolo(key)
            self.info_text.insert(tk.END, f"   {simbolo} = {value:.2f}\n")
        
        self.info_text.insert(tk.END, f"\n⏱️ Tempo total: {t_total:.2f} s\n")
        self.info_text.insert(tk.END, f"📈 Alcance máximo: {alcance:.2f} m\n")
        self.info_text.insert(tk.END, f"📈 Altura máxima: {altura_max:.2f} m\n")
        
        if resultados:
            self.info_text.insert(tk.END, "\n🔬 ANÁLISE DETALHADA:\n")
            for key, value in resultados.items():
                nome_formatado = key.replace('_', ' ').title()
                self.info_text.insert(tk.END, f"   {nome_formatado}: {value:.3f}\n")
        
        if self.pasta_destino and self.caminho_grafico_atual:
            self.info_text.insert(tk.END, f"\n💾 Gráfico salvo em:\n   {os.path.basename(self.caminho_grafico_atual)}")
    
    def salvar_ontologia(self):
        if not self.pasta_destino:
            messagebox.showwarning("PhysiMotion", "Selecione uma pasta para salvar primeiro!")
            return
        
        if self.dados_atual is None:
            messagebox.showwarning("PhysiMotion", "Gere um gráfico primeiro!")
            return
        
        if not self.ontologia:
            self.ontologia = OntologiaRDF(pasta_destino=self.pasta_destino)
        
        resultado = {
            "tempo_total": self.dados_atual['t_total'],
            "alcance_maximo": self.dados_atual['alcance'],
            "altura_maxima": self.dados_atual['altura_max']
        }
        
        if self.dados_atual.get('resultados'):
            resultado.update(self.dados_atual['resultados'])
        
        exp_id = self.ontologia.adicionar_experimento(
            self.dados_atual['tipo'],
            self.dados_atual['parametros'],
            resultado,
            self.caminho_grafico_atual or ""
        )
        
        messagebox.showinfo("PhysiMotion", f"✅ Experimento salvo na ontologia!\n\nID: {exp_id}\nArquivo: {self.ontologia.arquivo}")
    
    def gerar_relatorio(self):
        if not self.pasta_destino:
            messagebox.showwarning("PhysiMotion", "Selecione uma pasta para salvar o relatório primeiro!")
            return
        
        if self.dados_atual is None:
            messagebox.showwarning("PhysiMotion", "Gere um gráfico primeiro!")
            return
        
        if not self.caminho_grafico_atual or not os.path.exists(self.caminho_grafico_atual):
            messagebox.showwarning("PhysiMotion", "Gráfico não encontrado. Gere o gráfico novamente!")
            return
        
        formula_data = FormularioMovimentos.get_formula(self.dados_atual['tipo'])
        resultados = self.dados_atual.get('resultados', {})
        
        caminho_relatorio = GeradorRelatorio.gerar_relatorio_academico(
            self.pasta_destino,
            self.dados_atual,
            self.caminho_grafico_atual,
            formula_data,
            resultados
        )
        
        messagebox.showinfo("PhysiMotion", f"📄 Relatório acadêmico gerado com sucesso!\n\nArquivo: {caminho_relatorio}\n\nO relatório será aberto no navegador.")
        
        caminho_corrigido = caminho_relatorio.replace('\\', '/')
        webbrowser.open(f"file:///{caminho_corrigido}")
    
    def mostrar_historico(self):
        if not self.ontologia:
            messagebox.showwarning("PhysiMotion", "Selecione uma pasta com ontologia primeiro!")
            return
        
        experimentos = self.ontologia.listar_experimentos()
        
        if not experimentos:
            messagebox.showinfo("PhysiMotion", "Nenhum experimento salvo ainda!")
            return
        
        hist_window = tk.Toplevel(self.root)
        hist_window.title("PhysiMotion - Histórico de Experimentos")
        hist_window.geometry("900x600")
        hist_window.configure(bg='#f0f2f5')
        
        tree = ttk.Treeview(hist_window, columns=('ID', 'Tipo', 'Data', 'Grafico'), show='headings')
        tree.heading('ID', text='ID')
        tree.heading('Tipo', text='Tipo de Movimento')
        tree.heading('Data', text='Data e Hora')
        tree.heading('Grafico', text='Arquivo do Gráfico')
        
        tree.column('ID', width=50)
        tree.column('Tipo', width=150)
        tree.column('Data', width=200)
        tree.column('Grafico', width=300)
        
        scrollbar = ttk.Scrollbar(hist_window, orient=tk.VERTICAL, command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        
        tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y, pady=10)
        
        for exp in experimentos:
            tree.insert('', tk.END, values=(
                exp['id'],
                exp['tipo'],
                exp.get('data', 'N/A')[:19],
                os.path.basename(exp.get('grafico', 'N/A'))
            ))
        
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
                        messagebox.showerror("PhysiMotion", "Arquivo do gráfico não encontrado!")
        
        btn_frame = ttk.Frame(hist_window)
        btn_frame.pack(pady=10)
        
        ttk.Button(btn_frame, text="📊 Abrir Gráfico", command=abrir_grafico, style="Primary.TButton").pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="🔒 Fechar", command=hist_window.destroy, style="Warning.TButton").pack(side=tk.LEFT, padx=5)
    
    def resetar(self):
        self.dados_atual = None
        self.caminho_grafico_atual = None
        self.ax.clear()
        self.ax.set_xlabel('X (m)')
        self.ax.set_ylabel('Y (m)')
        self.ax.set_zlabel('Z (m)')
        self.ax.set_title('PhysiMotion® - Simulador de Movimentos')
        self.ax.grid(True, alpha=0.3)
        self.canvas.draw()
        self.info_text.delete(1.0, tk.END)
        self.info_text.insert(1.0, "Gere um gráfico para visualizar os resultados...\n\nAjuste os parâmetros e clique em 'GERAR GRÁFICO'")
        
        messagebox.showinfo("PhysiMotion", "🔄 Simulação resetada!\n\nConfigure novos parâmetros e gere um novo gráfico.")


# ==================== MAIN ====================
if __name__ == "__main__":
    print("="*80)
    print("⚛️ PHYSIMOTION ® - SIMULADOR DE MOVIMENTOS FÍSICOS PARA GRADUAÇÃO")
    print("="*80)
    print(f"\n📌 {PROGRAM_NAME} v{PROGRAM_VERSION}")
    print(f"   {PROGRAM_SUBTITLE}")
    print(f"   {PROGRAM_AUTHOR} | {PROGRAM_YEAR}")
    print("\n📚 Funcionalidades do Modo Treinamento:")
    print("   ✅ 6 tipos de movimentos com fundamentação teórica completa")
    print("   ✅ Fórmulas em destaque no gráfico 3D")
    print("   ✅ Exercícios de fixação para cada movimento")
    print("   ✅ Análise detalhada de resultados numéricos")
    print("   ✅ Relatórios acadêmicos em formato HTML")
    print("   ✅ Ontologia RDF para registro de experimentos")
    print("   ✅ Histórico completo de simulações")
    print("\n🚀 Iniciando PhysiMotion...\n")
    
    root = tk.Tk()
    app = PhysiMotionApp(root)
    root.mainloop()