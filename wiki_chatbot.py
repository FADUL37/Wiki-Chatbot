#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Chatbot Wiki.js - Implementação conforme instruções do Luigi
Consulta operadoras usando API GraphQL com token JWT válido
Todos os tópicos são separados por tag h2 e processados individualmente
"""

import requests
import json
import re
from datetime import datetime
from flask import Flask, render_template, request, jsonify
from config import API_TOKEN, BASE_URL

app = Flask(__name__)

class WikiChatbot:
    def __init__(self):
        self.base_url = BASE_URL
        self.token = API_TOKEN
        self.headers = {
            'Authorization': f'Bearer {self.token}',
            'Content-Type': 'application/json'
        }
        
        # Lista de operadoras conforme Luigi (nomes em caixa alta e sem espaço)
        self.operadoras_disponiveis = [
            'VIVAS', 'ARESNET', 'BRASILINK', 'AVIANET', 'CAPITAL', 'CENSANET',
            'CENTRALTELECOM', 'CETECH', 'COMUNET', 'DELTAATIVA', 'DKIROS',
            'ETECC', 'FACILITI', 'ICLICK', 'INET', 'INFORNET', 'INFOSAFE',
            'ITAPOA', 'LASERNET', 'LESTETELECOM', 'MEGANETS', 'MUTUM',
            'NETCENTER', 'NETPLAY', 'NICKNETWORK', 'PERFECT', 'PLUSCOM',
            'PONTOINFO', 'POXNET', 'RBONLINE', 'VOE', 'WFNET', 'RTECH',
            'SEJAFIBRA', 'VMNET', 'WFT', 'SETTE', 'TBN', 'ZLINK', 'VMAX', 'TOPNET'
        ]
    
    def consultar_operadora_api(self, nome_operadora):
        """
        Consulta uma operadora específica usando a API GraphQL
        Conforme instruções do Luigi: query singleByPath
        """
        query = {
            "query": f'query {{ pages {{ singleByPath(path: "Suporte/{nome_operadora}", locale: "en") {{ id path title content }} }} }}'
        }
        
        try:
            response = requests.post(
                f"{self.base_url}/graphql",
                headers=self.headers,
                json=query,
                timeout=15
            )
            
            if response.status_code == 200:
                data = response.json()
                
                # Verificar se há dados válidos
                page_data = data.get('data', {}).get('pages', {}).get('singleByPath')
                
                if page_data and page_data.get('content'):
                    return {
                        'sucesso': True,
                        'dados': page_data,
                        'html_bruto': page_data['content']
                    }
                else:
                    return {
                        'sucesso': False,
                        'erro': f'Operadora {nome_operadora} não encontrada ou sem conteúdo'
                    }
            else:
                return {
                    'sucesso': False,
                    'erro': f'Erro HTTP {response.status_code}: {response.text}'
                }
                
        except Exception as e:
            return {
                'sucesso': False,
                'erro': f'Erro na consulta: {str(e)}'
            }
    
    def find_topic_in_wiki(self, api_response, keyword):
        """
        Função de busca conforme instruções do Luigi
        Procura por um tópico e retorna um objeto com o título e o conteúdo
        Todos os tópicos estão separados por tag h2
        """
        if not api_response.get('sucesso'):
            return {
                'found': False,
                'message': f"Erro na API: {api_response.get('erro', 'Erro desconhecido')}"
            }
        
        page_data = api_response['dados']
        html_content = page_data.get('content', '')
        
        if not html_content:
            return {
                'found': False,
                'message': "A página não possui conteúdo"
            }
        
        # Dividir o conteúdo por tags h2 conforme Luigi
        sections = self.split_by_h2_tags(html_content)
        
        # Buscar pela palavra-chave nos tópicos
        keyword_lower = keyword.lower()
        
        for section in sections:
            header = section.get('header', '').lower()
            content = section.get('content', '').lower()
            
            # Verificar se a palavra-chave está no título ou conteúdo
            if keyword_lower in header or keyword_lower in content:
                return {
                    'found': True,
                    'header': section.get('header', ''),
                    'content': self.clean_html_content(section.get('content', '')),
                    'raw_content': section.get('content', '')
                }
        
        return {
            'found': False,
            'message': f"Tópico '{keyword}' não encontrado na operadora"
        }
    
    def split_by_h2_tags(self, html_content):
        """
        Divide o conteúdo HTML por tags h2 conforme instruções do Luigi
        Retorna uma lista de seções com header e content
        """
        sections = []
        
        # Regex para encontrar tags h2 e seu conteúdo
        h2_pattern = r'<h2[^>]*>(.*?)</h2>'
        h2_matches = list(re.finditer(h2_pattern, html_content, re.IGNORECASE | re.DOTALL))
        
        if not h2_matches:
            # Se não há h2, retornar todo o conteúdo como uma seção
            return [{
                'header': 'Conteúdo Geral',
                'content': html_content
            }]
        
        for i, match in enumerate(h2_matches):
            header = self.clean_html_content(match.group(1))
            
            # Determinar onde começa e termina o conteúdo desta seção
            start_pos = match.end()
            
            if i + 1 < len(h2_matches):
                end_pos = h2_matches[i + 1].start()
            else:
                end_pos = len(html_content)
            
            content = html_content[start_pos:end_pos].strip()
            
            sections.append({
                'header': header,
                'content': content
            })
        
        return sections
    
    def clean_html_content(self, html_content):
        """
        Limpa o conteúdo HTML removendo tags e formatando texto
        Conforme instruções do Luigi para limpeza de header aprimorada
        """
        if not html_content:
            return ''
        
        # Remover tags HTML
        clean_text = re.sub(r'<[^>]+>', '', html_content)
        
        # Decodificar entidades HTML
        clean_text = clean_text.replace('&nbsp;', ' ')
        clean_text = clean_text.replace('&amp;', '&')
        clean_text = clean_text.replace('&lt;', '<')
        clean_text = clean_text.replace('&gt;', '>')
        clean_text = clean_text.replace('&quot;', '"')
        clean_text = clean_text.replace('&#39;', "'")
        
        # Limpar espaços extras e quebras de linha
        clean_text = re.sub(r'\s+', ' ', clean_text)
        clean_text = clean_text.strip()
        
        return clean_text
    
    def processar_pergunta(self, pergunta):
        """
        Processa a pergunta do usuário e retorna resposta estruturada
        """
        pergunta_lower = pergunta.lower()
        
        # Identificar operadora na pergunta
        operadora_encontrada = None
        for operadora in self.operadoras_disponiveis:
            if operadora.lower() in pergunta_lower:
                operadora_encontrada = operadora
                break
        
        if not operadora_encontrada:
            return {
                'tipo': 'erro',
                'mensagem': 'Não consegui identificar a operadora na sua pergunta.',
                'sugestao': 'Por favor, mencione o nome de uma operadora.',
                'operadoras_disponiveis': self.operadoras_disponiveis
            }
        
        # Consultar a operadora na API
        api_response = self.consultar_operadora_api(operadora_encontrada)
        
        if not api_response.get('sucesso'):
            return {
                'tipo': 'erro',
                'mensagem': f'Erro ao consultar {operadora_encontrada}',
                'detalhes': api_response.get('erro', 'Erro desconhecido')
            }
        
        # Extrair palavra-chave da pergunta
        keyword = self.extrair_keyword_pergunta(pergunta_lower)
        
        # Buscar tópico específico
        resultado_busca = self.find_topic_in_wiki(api_response, keyword)
        
        if resultado_busca['found']:
            return {
                'tipo': 'sucesso',
                'operadora': operadora_encontrada,
                'topico_encontrado': resultado_busca['header'],
                'conteudo': resultado_busca['content'],
                'keyword_buscada': keyword,
                'timestamp': datetime.now().strftime('%d/%m/%Y às %H:%M:%S')
            }
        else:
            # Se não encontrou tópico específico, retornar informações gerais
            return self.retornar_info_geral(operadora_encontrada, api_response)
    
    def extrair_keyword_pergunta(self, pergunta):
        """
        Extrai palavra-chave da pergunta para busca nos tópicos
        """
        keywords_comuns = {
            'endereço': 'endereço',
            'endereco': 'endereço',
            'telefone': 'telefone',
            'fone': 'telefone',
            'contato': 'contato',
            'horário': 'horário',
            'horario': 'horário',
            'atendimento': 'atendimento',
            'plano': 'plano',
            'planos': 'planos',
            'preço': 'preço',
            'preco': 'preço',
            'valor': 'valor',
            'custo': 'custo',
            'prazo': 'prazo',
            'suporte': 'suporte',
            'técnico': 'técnico',
            'tecnico': 'técnico',
            'tecnologia': 'tecnologia',
            'equipamento': 'equipamento',
            'fibra': 'fibra',
            'internet': 'internet',
            'velocidade': 'velocidade',
            'mbps': 'mbps',
            'instalação': 'instalação',
            'instalacao': 'instalação',
            'pagamento': 'pagamento',
            'fatura': 'fatura',
            'boleto': 'boleto'
        }
        
        for palavra, keyword in keywords_comuns.items():
            if palavra in pergunta:
                return keyword
        
        # Se não encontrou keyword específica, usar a primeira palavra significativa
        palavras = pergunta.split()
        palavras_filtradas = [p for p in palavras if len(p) > 3 and p not in ['qual', 'como', 'onde', 'quando', 'para', 'pela', 'pelo']]
        
        return palavras_filtradas[0] if palavras_filtradas else 'informações'
    
    def retornar_info_geral(self, operadora, api_response):
        """
        Retorna informações gerais quando não encontra tópico específico
        """
        html_content = api_response['dados'].get('content', '')
        sections = self.split_by_h2_tags(html_content)
        
        # Listar todos os tópicos disponíveis
        topicos_disponiveis = [section['header'] for section in sections if section['header']]
        
        return {
            'tipo': 'info_geral',
            'operadora': operadora,
            'mensagem': f'Informações gerais da {operadora}',
            'topicos_disponiveis': topicos_disponiveis,
            'total_topicos': len(topicos_disponiveis),
            'timestamp': datetime.now().strftime('%d/%m/%Y às %H:%M:%S')
        }
    
    def listar_todas_operadoras(self):
        """
        Lista todas as operadoras disponíveis
        """
        return {
            'operadoras': self.operadoras_disponiveis,
            'total': len(self.operadoras_disponiveis)
        }
    
    def consultar_topicos_operadora(self, nome_operadora):
        """
        Consulta todos os tópicos de uma operadora específica
        """
        api_response = self.consultar_operadora_api(nome_operadora)
        
        if not api_response.get('sucesso'):
            return {
                'sucesso': False,
                'erro': api_response.get('erro')
            }
        
        html_content = api_response['dados'].get('content', '')
        sections = self.split_by_h2_tags(html_content)
        
        topicos_detalhados = []
        for section in sections:
            if section['header']:
                topicos_detalhados.append({
                    'titulo': section['header'],
                    'conteudo_resumo': self.clean_html_content(section['content'])[:200] + '...',
                    'conteudo_completo': self.clean_html_content(section['content'])
                })
        
        return {
            'sucesso': True,
            'operadora': nome_operadora,
            'topicos': topicos_detalhados,
            'total_topicos': len(topicos_detalhados)
        }

# Instância global do chatbot
wiki_chatbot = WikiChatbot()

# Rotas Flask
@app.route('/')
def index():
    return render_template('wiki_chatbot.html')

@app.route('/widget')
def widget():
    """Rota para servir apenas o widget do chatbot (ícone flutuante)"""
    return render_template('chatbot_widget.html')

@app.route('/chat', methods=['POST'])
def chat():
    data = request.get_json()
    pergunta = data.get('pergunta', '')
    
    if not pergunta:
        return jsonify({
            'erro': 'Pergunta não fornecida'
        }), 400
    
    try:
        resposta = wiki_chatbot.processar_pergunta(pergunta)
        return jsonify(resposta)
    except Exception as e:
        return jsonify({
            'erro': f'Erro interno: {str(e)}'
        }), 500

@app.route('/operadoras')
def listar_operadoras():
    return jsonify(wiki_chatbot.listar_todas_operadoras())

@app.route('/operadora/<nome>/topicos')
def consultar_topicos(nome):
    nome_upper = nome.upper()
    if nome_upper not in wiki_chatbot.operadoras_disponiveis:
        return jsonify({
            'erro': f'Operadora {nome} não encontrada'
        }), 404
    
    resultado = wiki_chatbot.consultar_topicos_operadora(nome_upper)
    return jsonify(resultado)

@app.route('/teste_api')
def teste_api():
    """Endpoint para testar a conectividade com a API"""
    try:
        # Testar com VIVAS como exemplo
        resultado = wiki_chatbot.consultar_operadora_api('VIVAS')
        return jsonify({
            'status': 'sucesso' if resultado.get('sucesso') else 'erro',
            'detalhes': resultado
        })
    except Exception as e:
        return jsonify({
            'status': 'erro',
            'erro': str(e)
        })

if __name__ == '__main__':
    import os
    
    # Configuração para produção (Render, Heroku, etc.)
    port = int(os.environ.get('PORT', 5000))
    debug_mode = os.environ.get('FLASK_ENV') != 'production'
    
    print("\n" + "="*60)
    print("🚀 INICIANDO SERVIDOR FLASK - WIKI.JS CHATBOT")
    print("="*60)
    print(f"📊 Operadoras configuradas: {len(wiki_chatbot.operadoras_disponiveis)}")
    print("✅ Funcionalidades ativas:")
    print("   • Consulta API GraphQL")
    print("   • Divisão de conteúdo por tags H2")
    print("   • Busca inteligente de tópicos")
    print("   • Limpeza avançada de HTML")
    print("   • Interface web responsiva")
    print(f"\n🌐 Servidor rodando na porta: {port}")
    print(f"🔧 Modo debug: {debug_mode}")
    
    if debug_mode:
        print("\n🌐 URLs locais disponíveis:")
        print(f"   • http://localhost:{port}")
        print(f"   • http://127.0.0.1:{port}")
        
        # Tentar obter IP local
        try:
            import socket
            hostname = socket.gethostname()
            local_ip = socket.gethostbyname(hostname)
            print(f"   • http://{local_ip}:{port}")
        except:
            pass
    
    print("\n💬 Endpoints disponíveis:")
    print("   • / (interface principal)")
    print("   • /widget (widget flutuante)")
    print("   • /chat (API de mensagens)")
    print("   • /operadoras (listar todas)")
    print("   • /operadora/<nome>/topicos")
    print("   • /teste_api (diagnóstico)")
    print("="*60 + "\n")
    
    app.run(debug=debug_mode, host='0.0.0.0', port=port)