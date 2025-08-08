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
        Função de busca inteligente aprimorada
        Procura por tópicos relacionados e retorna todas as informações relevantes
        Implementa busca por similaridade e palavras relacionadas
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
        
        # Dividir o conteúdo por tags h2
        sections = self.split_by_h2_tags(html_content)
        
        # Busca inteligente com múltiplas estratégias
        resultados_encontrados = self.busca_inteligente_multipla(sections, keyword)
        
        if resultados_encontrados:
            return {
                'found': True,
                'resultados_multiplos': resultados_encontrados,
                'total_encontrados': len(resultados_encontrados),
                'busca_expandida': True
            }
        
        return {
            'found': False,
            'message': f"Nenhuma informação relacionada a '{keyword}' foi encontrada"
        }
    
    def busca_inteligente_multipla(self, sections, keyword):
        """
        Implementa busca inteligente com múltiplas estratégias:
        1. Busca exata
        2. Busca por palavras relacionadas
        3. Busca por similaridade
        4. Busca por contexto
        """
        keyword_lower = keyword.lower()
        resultados = []
        
        # Expandir palavras-chave relacionadas
        palavras_relacionadas = self.expandir_palavras_chave(keyword_lower)
        
        for section in sections:
            header = section.get('header', '').lower()
            content = section.get('content', '').lower()
            content_clean = self.clean_html_content(section.get('content', ''))
            
            # Calcular relevância da seção
            relevancia = self.calcular_relevancia_secao(header, content, keyword_lower, palavras_relacionadas)
            
            if relevancia > 0:
                resultados.append({
                    'header': section.get('header', ''),
                    'content': content_clean,
                    'relevancia': relevancia,
                    'palavras_encontradas': self.identificar_palavras_encontradas(content, palavras_relacionadas),
                    'tipo_match': self.identificar_tipo_match(header, content, keyword_lower, palavras_relacionadas)
                })
        
        # Ordenar por relevância (maior primeiro)
        resultados.sort(key=lambda x: x['relevancia'], reverse=True)
        
        return resultados
    
    def expandir_palavras_chave(self, keyword):
        """
        Expande a palavra-chave com termos relacionados para busca mais abrangente
        """
        expansoes = {
            'mudança': ['mudança', 'alteração', 'modificação', 'troca', 'transferência', 'migração', 'mudanca', 'alteracao', 'modificacao'],
            'endereco': ['endereço', 'endereco', 'localização', 'localizacao', 'local', 'sede', 'escritório', 'escritorio'],
            'telefone': ['telefone', 'fone', 'contato', 'número', 'numero', 'celular', 'whatsapp'],
            'horario': ['horário', 'horario', 'atendimento', 'funcionamento', 'expediente', 'plantão', 'plantao'],
            'pagamento': ['pagamento', 'fatura', 'boleto', 'cobrança', 'cobranca', 'vencimento', 'débito', 'debito'],
            'desbloqueio': ['desbloqueio', 'liberação', 'liberacao', 'reativação', 'reativacao', 'religação', 'religacao'],
            'plano': ['plano', 'planos', 'pacote', 'pacotes', 'serviço', 'servico', 'produto'],
            'suporte': ['suporte', 'técnico', 'tecnico', 'assistência', 'assistencia', 'ajuda', 'apoio'],
            'instalacao': ['instalação', 'instalacao', 'ativação', 'ativacao', 'configuração', 'configuracao']
        }
        
        # Buscar expansões diretas
        for chave, valores in expansoes.items():
            if keyword in valores:
                return valores
        
        # Se não encontrou expansão específica, criar lista com variações básicas
        variacoes = [keyword]
        
        # Adicionar variações sem acentos
        keyword_sem_acento = keyword.replace('ã', 'a').replace('ç', 'c').replace('é', 'e').replace('ê', 'e').replace('í', 'i').replace('ó', 'o').replace('ô', 'o').replace('ú', 'u')
        if keyword_sem_acento != keyword:
            variacoes.append(keyword_sem_acento)
        
        return variacoes
    
    def calcular_relevancia_secao(self, header, content, keyword, palavras_relacionadas):
        """
        Calcula a relevância de uma seção baseada na presença de palavras-chave
        """
        relevancia = 0
        
        # Pontuação por presença no título (maior peso)
        for palavra in palavras_relacionadas:
            if palavra in header:
                relevancia += 10
        
        # Pontuação por presença no conteúdo
        for palavra in palavras_relacionadas:
            count = content.count(palavra)
            relevancia += count * 3
        
        # Bonus por palavra-chave exata
        if keyword in header:
            relevancia += 15
        if keyword in content:
            relevancia += content.count(keyword) * 5
        
        return relevancia
    
    def identificar_palavras_encontradas(self, content, palavras_relacionadas):
        """
        Identifica quais palavras relacionadas foram encontradas no conteúdo
        """
        encontradas = []
        for palavra in palavras_relacionadas:
            if palavra in content:
                encontradas.append(palavra)
        return encontradas
    
    def identificar_tipo_match(self, header, content, keyword, palavras_relacionadas):
        """
        Identifica o tipo de correspondência encontrada
        """
        if keyword in header:
            return 'titulo_exato'
        elif keyword in content:
            return 'conteudo_exato'
        elif any(palavra in header for palavra in palavras_relacionadas):
            return 'titulo_relacionado'
        elif any(palavra in content for palavra in palavras_relacionadas):
            return 'conteudo_relacionado'
        else:
            return 'contexto'
    
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
    
    def processar_pergunta(self, pergunta, data_ultimo_pagamento=None):
        """
        Processa a pergunta do usuário com busca inteligente aprimorada
        Inclui sistema de desbloqueio baseado em data de pagamento
        """
        pergunta_lower = pergunta.lower()
        
        # Verificar se é uma consulta de desbloqueio
        if self.is_consulta_desbloqueio(pergunta_lower):
            return self.processar_consulta_desbloqueio(pergunta_lower, data_ultimo_pagamento)
        
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
        
        # Buscar com sistema inteligente aprimorado
        resultado_busca = self.find_topic_in_wiki(api_response, keyword)
        
        if resultado_busca['found']:
            if resultado_busca.get('busca_expandida'):
                # Retornar múltiplos resultados encontrados
                return {
                    'tipo': 'sucesso_multiplo',
                    'operadora': operadora_encontrada,
                    'keyword_buscada': keyword,
                    'resultados_encontrados': resultado_busca['resultados_multiplos'],
                    'total_resultados': resultado_busca['total_encontrados'],
                    'timestamp': datetime.now().strftime('%d/%m/%Y às %H:%M:%S')
                }
            else:
                # Resultado único (compatibilidade com versão anterior)
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
    
    def is_consulta_desbloqueio(self, pergunta):
        """
        Verifica se a pergunta é sobre desbloqueio/liberação
        """
        palavras_desbloqueio = [
            'desbloqueio', 'desbloquear', 'liberação', 'liberar', 'reativação', 'reativar',
            'religação', 'religar', 'bloqueado', 'suspenso', 'cortado', 'prazo'
        ]
        
        return any(palavra in pergunta for palavra in palavras_desbloqueio)
    
    def processar_consulta_desbloqueio(self, pergunta, data_ultimo_pagamento):
        """
        Processa consultas específicas sobre desbloqueio baseado na data de pagamento
        """
        # Identificar operadora
        operadora_encontrada = None
        for operadora in self.operadoras_disponiveis:
            if operadora.lower() in pergunta:
                operadora_encontrada = operadora
                break
        
        if not operadora_encontrada:
            return {
                'tipo': 'erro',
                'mensagem': 'Para consultar desbloqueio, preciso saber qual operadora.',
                'sugestao': 'Informe a operadora junto com sua consulta de desbloqueio.'
            }
        
        # Consultar informações de desbloqueio na wiki
        api_response = self.consultar_operadora_api(operadora_encontrada)
        
        if not api_response.get('sucesso'):
            return {
                'tipo': 'erro',
                'mensagem': f'Erro ao consultar informações de {operadora_encontrada}',
                'detalhes': api_response.get('erro')
            }
        
        # Buscar informações sobre desbloqueio/pagamento
        resultado_desbloqueio = self.find_topic_in_wiki(api_response, 'desbloqueio')
        resultado_pagamento = self.find_topic_in_wiki(api_response, 'pagamento')
        
        # Calcular prazo de desbloqueio baseado na data de pagamento
        info_prazo = self.calcular_prazo_desbloqueio(data_ultimo_pagamento)
        
        # Compilar informações encontradas
        informacoes_encontradas = []
        
        if resultado_desbloqueio['found']:
            if resultado_desbloqueio.get('busca_expandida'):
                informacoes_encontradas.extend(resultado_desbloqueio['resultados_multiplos'])
            else:
                informacoes_encontradas.append({
                    'header': resultado_desbloqueio['header'],
                    'content': resultado_desbloqueio['content'],
                    'relevancia': 10
                })
        
        if resultado_pagamento['found']:
            if resultado_pagamento.get('busca_expandida'):
                informacoes_encontradas.extend(resultado_pagamento['resultados_multiplos'])
            else:
                informacoes_encontradas.append({
                    'header': resultado_pagamento['header'],
                    'content': resultado_pagamento['content'],
                    'relevancia': 8
                })
        
        return {
            'tipo': 'desbloqueio',
            'operadora': operadora_encontrada,
            'informacoes_desbloqueio': informacoes_encontradas,
            'calculo_prazo': info_prazo,
            'data_ultimo_pagamento': data_ultimo_pagamento,
            'timestamp': datetime.now().strftime('%d/%m/%Y às %H:%M:%S')
        }
    
    def calcular_prazo_desbloqueio(self, data_ultimo_pagamento):
        """
        Calcula o prazo estimado para desbloqueio baseado na data do último pagamento
        """
        if not data_ultimo_pagamento:
            return {
                'status': 'sem_data',
                'mensagem': 'Data do último pagamento não informada',
                'recomendacao': 'Informe a data do último pagamento para cálculo preciso do prazo'
            }
        
        try:
            # Tentar diferentes formatos de data
            formatos = ['%d/%m/%Y', '%Y-%m-%d', '%d-%m-%Y']
            data_pagamento = None
            
            for formato in formatos:
                try:
                    data_pagamento = datetime.strptime(data_ultimo_pagamento, formato)
                    break
                except ValueError:
                    continue
            
            if not data_pagamento:
                return {
                    'status': 'data_invalida',
                    'mensagem': 'Formato de data inválido',
                    'recomendacao': 'Use o formato DD/MM/AAAA (ex: 15/01/2024)'
                }
            
            # Calcular diferença em dias
            hoje = datetime.now()
            dias_desde_pagamento = (hoje - data_pagamento).days
            
            # Lógica de prazo baseada em dias desde o pagamento
            if dias_desde_pagamento <= 1:
                prazo_estimado = '2-4 horas'
                status = 'rapido'
            elif dias_desde_pagamento <= 3:
                prazo_estimado = '4-8 horas'
                status = 'normal'
            elif dias_desde_pagamento <= 7:
                prazo_estimado = '8-24 horas'
                status = 'moderado'
            elif dias_desde_pagamento <= 30:
                prazo_estimado = '1-2 dias úteis'
                status = 'lento'
            else:
                prazo_estimado = '2-5 dias úteis'
                status = 'muito_lento'
            
            return {
                'status': status,
                'dias_desde_pagamento': dias_desde_pagamento,
                'prazo_estimado': prazo_estimado,
                'data_pagamento_formatada': data_pagamento.strftime('%d/%m/%Y'),
                'recomendacao': self.get_recomendacao_prazo(status, dias_desde_pagamento)
            }
            
        except Exception as e:
            return {
                'status': 'erro',
                'mensagem': f'Erro ao processar data: {str(e)}',
                'recomendacao': 'Verifique o formato da data e tente novamente'
            }
    
    def get_recomendacao_prazo(self, status, dias):
        """
        Retorna recomendações baseadas no status do prazo
        """
        recomendacoes = {
            'rapido': 'Pagamento recente. Desbloqueio deve ocorrer rapidamente.',
            'normal': 'Prazo normal de processamento. Aguarde algumas horas.',
            'moderado': 'Pode levar mais tempo devido ao prazo. Entre em contato se necessário.',
            'lento': 'Pagamento com mais de uma semana. Recomendamos contato direto.',
            'muito_lento': 'Pagamento antigo. Necessário verificação manual com a operadora.'
        }
        
        return recomendacoes.get(status, 'Consulte diretamente a operadora para mais informações.')
    
    def obter_informacoes_essenciais_operadora(self, operadora):
        """
        Retorna informações essenciais que nunca devem deixar de ser informadas sobre uma operadora
        """
        # Consultar a operadora na API
        api_response = self.consultar_operadora_api(operadora)
        
        if not api_response.get('sucesso'):
            return {
                'tipo': 'erro',
                'mensagem': f'Erro ao consultar informações essenciais de {operadora}',
                'detalhes': api_response.get('erro')
            }
        
        # Informações críticas que sempre devem ser buscadas
        informacoes_criticas = [
            'telefone', 'contato', 'endereço', 'endereco', 'horário', 'horario',
            'funcionamento', 'atendimento', 'suporte', 'emergência', 'emergencia',
            'pagamento', 'boleto', 'pix', 'débito', 'debito', 'cartão', 'cartao',
            'instalação', 'instalacao', 'técnico', 'tecnico', 'visita',
            'planos', 'valores', 'preços', 'precos', 'promoção', 'promocao',
            'velocidade', 'internet', 'wifi', 'fibra', 'cobertura'
        ]
        
        informacoes_encontradas = []
        
        # Buscar cada informação crítica
        for keyword in informacoes_criticas:
            resultado = self.find_topic_in_wiki(api_response, keyword)
            
            if resultado['found']:
                if resultado.get('busca_expandida'):
                    # Adicionar todos os resultados encontrados
                    for res in resultado['resultados_multiplos']:
                        if not any(info['header'] == res['header'] for info in informacoes_encontradas):
                            informacoes_encontradas.append({
                                'categoria': keyword,
                                'header': res['header'],
                                'content': res['content'],
                                'relevancia': res['relevancia'],
                                'prioridade': self.calcular_prioridade_informacao(keyword)
                            })
                else:
                    # Adicionar resultado único
                    if not any(info['header'] == resultado['header'] for info in informacoes_encontradas):
                        informacoes_encontradas.append({
                            'categoria': keyword,
                            'header': resultado['header'],
                            'content': resultado['content'],
                            'relevancia': 10,
                            'prioridade': self.calcular_prioridade_informacao(keyword)
                        })
        
        # Ordenar por prioridade e relevância
        informacoes_encontradas.sort(key=lambda x: (x['prioridade'], x['relevancia']), reverse=True)
        
        # Limitar a 10 informações mais importantes
        informacoes_encontradas = informacoes_encontradas[:10]
        
        return {
            'tipo': 'informacoes_essenciais',
            'operadora': operadora,
            'total_informacoes': len(informacoes_encontradas),
            'informacoes_criticas': informacoes_encontradas,
            'timestamp': datetime.now().strftime('%d/%m/%Y às %H:%M:%S')
        }
    
    def calcular_prioridade_informacao(self, keyword):
        """
        Calcula a prioridade de uma informação baseada na palavra-chave
        """
        prioridades = {
            # Prioridade máxima (10) - Informações de contato
            'telefone': 10, 'contato': 10, 'emergência': 10, 'emergencia': 10,
            
            # Prioridade alta (9) - Localização e horários
            'endereço': 9, 'endereco': 9, 'horário': 9, 'horario': 9,
            'funcionamento': 9, 'atendimento': 9,
            
            # Prioridade média-alta (8) - Pagamentos e suporte
            'pagamento': 8, 'boleto': 8, 'pix': 8, 'débito': 8, 'debito': 8,
            'cartão': 8, 'cartao': 8, 'suporte': 8,
            
            # Prioridade média (7) - Serviços técnicos
            'instalação': 7, 'instalacao': 7, 'técnico': 7, 'tecnico': 7,
            'visita': 7,
            
            # Prioridade média-baixa (6) - Planos e preços
            'planos': 6, 'valores': 6, 'preços': 6, 'precos': 6,
            'promoção': 6, 'promocao': 6,
            
            # Prioridade baixa (5) - Especificações técnicas
            'velocidade': 5, 'internet': 5, 'wifi': 5, 'fibra': 5, 'cobertura': 5
        }
        
        return prioridades.get(keyword, 3)
    
    def gerar_resposta_inteligente(self, operadora, tipo_atendimento, contexto=None):
        """
        Gera respostas inteligentes baseadas na wiki da operadora
        """
        try:
            # Obter informações da operadora
            info_operadora = self.obter_informacoes_essenciais_operadora(operadora)
            
            if info_operadora.get('tipo') == 'erro':
                return f"Desculpe, não consegui obter informações sobre a {operadora}. Posso ajudá-lo de outra forma?"
            
            # Templates de resposta baseados no tipo de atendimento
            templates = {
                'saudacao': self._template_saudacao,
                'contato': self._template_contato,
                'pagamento': self._template_pagamento,
                'suporte': self._template_suporte,
                'despedida': self._template_despedida,
                'informacoes': self._template_informacoes_gerais
            }
            
            template_func = templates.get(tipo_atendimento, self._template_padrao)
            return template_func(operadora, info_operadora, contexto)
            
        except Exception as e:
            return f"Desculpe, ocorreu um erro ao gerar a resposta. Como posso ajudá-lo?"
    
    def _template_saudacao(self, operadora, info, contexto):
        """Template para saudação inicial"""
        contatos = [item for item in info.get('informacoes_criticas', []) if 'telefone' in item.get('header', '').lower() or 'contato' in item.get('header', '').lower()]
        contato_principal = contatos[0].get('content', 'Entre em contato conosco') if contatos else "Entre em contato conosco"
        
        return f"""Olá! Bem-vindo ao atendimento da {operadora}! 👋

Estou aqui para ajudá-lo com informações sobre nossos serviços. 

📞 {contato_principal[:100]}...

Como posso ajudá-lo hoje? Posso fornecer informações sobre:
• Contatos e atendimento
• Pagamentos e faturas
• Suporte técnico
• Planos e serviços"""
    
    def _template_contato(self, operadora, info, contexto):
        """Template para informações de contato"""
        contatos = [item for item in info.get('informacoes_criticas', []) if any(palavra in item.get('header', '').lower() for palavra in ['telefone', 'contato', 'whatsapp', 'email', 'chat'])]
        
        resposta = f"📞 **Contatos da {operadora}:**\n\n"
        
        if contatos:
            for contato in contatos[:5]:  # Limitar a 5 contatos principais
                resposta += f"• {contato.get('header', '')}: {contato.get('content', '')[:100]}...\n"
        else:
            resposta += "• Entre em contato através dos canais oficiais da operadora\n"
        
        resposta += "\n💡 **Dica:** Tenha sempre em mãos seu CPF e número da linha para um atendimento mais rápido!"
        return resposta
    
    def _template_pagamento(self, operadora, info, contexto):
        """Template para informações de pagamento"""
        pagamentos = [item for item in info.get('informacoes_criticas', []) if any(palavra in item.get('header', '').lower() for palavra in ['pagamento', 'fatura', 'boleto', 'débito', 'pix'])]
        
        resposta = f"💳 **Formas de Pagamento - {operadora}:**\n\n"
        
        if pagamentos:
            for pagamento in pagamentos[:4]:
                resposta += f"• {pagamento.get('header', '')}: {pagamento.get('content', '')[:100]}...\n"
        else:
            resposta += "• Consulte as opções de pagamento disponíveis\n"
        
        resposta += "\n⚠️ **Importante:** Mantenha suas faturas em dia para evitar interrupções no serviço!"
        return resposta
    
    def _template_suporte(self, operadora, info, contexto):
        """Template para suporte técnico"""
        suporte = [item for item in info.get('informacoes_criticas', []) if any(palavra in item.get('header', '').lower() for palavra in ['suporte', 'técnico', 'problema', 'reparo', 'manutenção'])]
        
        resposta = f"🔧 **Suporte Técnico - {operadora}:**\n\n"
        
        if suporte:
            for item in suporte[:4]:
                resposta += f"• {item.get('header', '')}: {item.get('content', '')[:100]}...\n"
        else:
            resposta += "• Entre em contato com o suporte técnico para assistência\n"
        
        resposta += "\n💡 **Antes de ligar:** Verifique se todos os cabos estão conectados e reinicie o equipamento."
        return resposta
    
    def _template_despedida(self, operadora, info, contexto):
        """Template para despedida"""
        return f"""Obrigado por entrar em contato com a {operadora}! 😊

Espero ter ajudado com suas dúvidas. Se precisar de mais alguma coisa, estarei sempre aqui!

📞 Lembre-se: nossos canais de atendimento estão sempre disponíveis para você.

Tenha um ótimo dia! 🌟"""
    
    def _template_informacoes_gerais(self, operadora, info, contexto):
        """Template para informações gerais"""
        informacoes = info.get('informacoes_criticas', [])
        
        resposta = f"ℹ️ **Informações Importantes - {operadora}:**\n\n"
        
        if informacoes:
            # Mostrar as 6 informações mais relevantes
            for item in informacoes[:6]:
                resposta += f"• {item.get('header', '')}: {item.get('content', '')[:80]}...\n"
        else:
            resposta += "• Consulte nossos canais oficiais para mais informações\n"
        
        resposta += "\n📋 Precisa de algo específico? Posso ajudá-lo com contatos, pagamentos ou suporte técnico!"
        return resposta
    
    def _template_padrao(self, operadora, info, contexto):
        """Template padrão para casos não específicos"""
        return f"""Olá! Estou aqui para ajudá-lo com informações sobre a {operadora}.

Posso fornecer informações sobre:
• 📞 Contatos e atendimento
• 💳 Pagamentos e faturas  
• 🔧 Suporte técnico
• 📋 Informações gerais

O que você gostaria de saber?"""
    
    def gerar_faq_operadora(self, operadora):
        """Gera FAQ no estilo D-KIROS baseado nas informações da wiki"""
        try:
            # Obter informações da operadora
            resultado_api = self.consultar_operadora_api(operadora)
            
            if resultado_api.get('status') == 'erro':
                return {
                    'status': 'erro',
                    'erro': f'Não foi possível obter informações da {operadora}'
                }
            
            conteudo_wiki = resultado_api.get('conteudo', '')
            
            # Extrair seções principais
            secoes = self.extrair_secoes_wiki(conteudo_wiki)
            
            # Gerar FAQ estruturado
            faq_items = []
            contador = 1
            
            # Seções prioritárias para FAQ
            secoes_prioritarias = [
                'contato', 'atendimento', 'telefone', 'horário', 'funcionamento',
                'pagamento', 'fatura', 'boleto', 'débito', 'pix',
                'suporte', 'técnico', 'problema', 'reparo',
                'plano', 'pacote', 'internet', 'velocidade',
                'endereço', 'localização', 'site'
            ]
            
            for secao in secoes:
                titulo = secao.get('titulo', '').lower()
                conteudo = secao.get('conteudo', '')
                
                # Verificar se é uma seção prioritária
                if any(palavra in titulo for palavra in secoes_prioritarias) and conteudo:
                    faq_item = self.criar_item_faq(contador, titulo, conteudo, operadora)
                    if faq_item:
                        faq_items.append(faq_item)
                        contador += 1
                        
                        if contador > 15:  # Limitar a 15 itens
                            break
            
            return {
                'status': 'sucesso',
                'operadora': operadora,
                'total_itens': len(faq_items),
                'faq_items': faq_items,
                'timestamp': datetime.now().strftime('%d/%m/%Y às %H:%M:%S')
            }
            
        except Exception as e:
            return {
                'status': 'erro',
                'erro': f'Erro ao gerar FAQ: {str(e)}'
            }
    
    def criar_item_faq(self, numero, titulo, conteudo, operadora):
        """Cria um item de FAQ formatado no estilo D-KIROS"""
        try:
            # Limpar e formatar título
            titulo_limpo = self.limpar_titulo_faq(titulo)
            
            # Gerar pergunta baseada no título
            pergunta = self.gerar_pergunta_faq(titulo_limpo, operadora)
            
            # Limpar e formatar conteúdo
            resposta = self.formatar_resposta_faq(conteudo)
            
            # Adicionar observações específicas baseadas no tipo
            observacao = self.gerar_observacao_faq(titulo_limpo)
            
            return {
                'numero': numero,
                'categoria': titulo_limpo,
                'pergunta': pergunta,
                'resposta': resposta,
                'observacao': observacao
            }
            
        except Exception as e:
            return None
    
    def limpar_titulo_faq(self, titulo):
        """Limpa e formata título para FAQ"""
        # Remover caracteres especiais e normalizar
        titulo = re.sub(r'[^a-záàâãéèêíìîóòôõúùûç\s]', '', titulo.lower())
        titulo = titulo.strip()
        
        # Mapear para categorias conhecidas
        mapeamento = {
            'contato': 'Contato e Atendimento',
            'telefone': 'Contato e Atendimento', 
            'atendimento': 'Contato e Atendimento',
            'horário': 'Horários de Funcionamento',
            'funcionamento': 'Horários de Funcionamento',
            'pagamento': 'Pagamentos e Faturas',
            'fatura': 'Pagamentos e Faturas',
            'boleto': 'Pagamentos e Faturas',
            'pix': 'Pagamentos e Faturas',
            'suporte': 'Suporte Técnico',
            'técnico': 'Suporte Técnico',
            'problema': 'Suporte Técnico',
            'reparo': 'Suporte Técnico',
            'plano': 'Planos e Serviços',
            'pacote': 'Planos e Serviços',
            'internet': 'Planos e Serviços',
            'velocidade': 'Planos e Serviços',
            'endereço': 'Localização e Endereço',
            'localização': 'Localização e Endereço',
            'site': 'Informações Gerais'
        }
        
        for palavra, categoria in mapeamento.items():
            if palavra in titulo:
                return categoria
        
        return titulo.title()
    
    def gerar_pergunta_faq(self, categoria, operadora):
        """Gera pergunta baseada na categoria"""
        perguntas = {
            'Contato e Atendimento': f'Qual o telefone e formas de contato da {operadora}?',
            'Horários de Funcionamento': f'Qual o horário de atendimento da {operadora}?',
            'Pagamentos e Faturas': f'Quais são as formas de pagamento da {operadora}?',
            'Suporte Técnico': f'Como solicitar suporte técnico da {operadora}?',
            'Planos e Serviços': f'Quais planos e serviços a {operadora} oferece?',
            'Localização e Endereço': f'Onde fica localizada a {operadora}?',
            'Informações Gerais': f'Quais informações importantes sobre a {operadora}?'
        }
        
        return perguntas.get(categoria, f'Informações sobre {categoria.lower()} da {operadora}?')
    
    def formatar_resposta_faq(self, conteudo):
        """Formata resposta no estilo FAQ"""
        # Limpar HTML e caracteres especiais
        conteudo = self.limpar_html(conteudo)
        
        # Quebrar em linhas e formatar
        linhas = conteudo.split('\n')
        resposta_formatada = []
        
        for linha in linhas:
            linha = linha.strip()
            if linha and len(linha) > 10:  # Ignorar linhas muito curtas
                # Adicionar marcadores para listas
                if any(palavra in linha.lower() for palavra in ['telefone', 'contato', 'email', 'whatsapp']):
                    resposta_formatada.append(f'• {linha}')
                elif any(palavra in linha.lower() for palavra in ['horário', 'segunda', 'terça', 'sábado', 'domingo']):
                    resposta_formatada.append(f'• {linha}')
                else:
                    resposta_formatada.append(linha)
        
        return '\n'.join(resposta_formatada[:5])  # Limitar a 5 linhas
    
    def gerar_observacao_faq(self, categoria):
        """Gera observação específica baseada na categoria"""
        observacoes = {
            'Contato e Atendimento': 'Obs: Tenha sempre em mãos seu CPF e número da linha para um atendimento mais rápido.',
            'Horários de Funcionamento': 'Obs: Horários podem variar em feriados. Consulte sempre antes de entrar em contato.',
            'Pagamentos e Faturas': 'Obs: Mantenha suas faturas em dia para evitar interrupções no serviço.',
            'Suporte Técnico': 'Obs: Antes de solicitar suporte, verifique se todos os cabos estão conectados.',
            'Planos e Serviços': 'Obs: Consulte disponibilidade de planos para sua região.',
            'Localização e Endereço': 'Obs: Confirme o endereço antes de se deslocar até o local.',
            'Informações Gerais': 'Obs: Informações sujeitas a alterações. Consulte sempre os canais oficiais.'
        }
        
        return observacoes.get(categoria, 'Obs: Para mais informações, entre em contato com a operadora.')
    
    def extrair_secoes_wiki(self, conteudo):
        """Extrai seções estruturadas da wiki"""
        secoes = []
        
        # Dividir por tags H2, H3, etc.
        import re
        padrao_secao = r'<h[2-4][^>]*>([^<]+)</h[2-4]>([\s\S]*?)(?=<h[2-4]|$)'
        matches = re.findall(padrao_secao, conteudo, re.IGNORECASE)
        
        for titulo, conteudo_secao in matches:
            secoes.append({
                'titulo': self.limpar_html(titulo).strip(),
                'conteudo': self.limpar_html(conteudo_secao).strip()
            })
        
        return secoes
    
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

@app.route('/widget-qa')
def widget_qa():
    """Rota para servir o widget Q&A com cenários pré-definidos"""
    return render_template('widget_qa_operadoras.html')

@app.route('/widget')
def widget():
    """Rota para servir apenas o widget do chatbot (ícone flutuante)"""
    return render_template('chatbot_widget.html')

@app.route('/chat', methods=['POST'])
def chat():
    try:
        data = request.get_json()
        pergunta = data.get('pergunta', '').strip()
        data_ultimo_pagamento = data.get('data_ultimo_pagamento', None)
        
        if not pergunta:
            return jsonify({
                'erro': 'Pergunta não pode estar vazia',
                'status': 'erro'
            }), 400
        
        # Processar pergunta com sistema aprimorado
        resposta = wiki_chatbot.processar_pergunta(pergunta, data_ultimo_pagamento)
        
        return jsonify(resposta)
        
    except Exception as e:
        return jsonify({
            'erro': f'Erro interno: {str(e)}',
            'status': 'erro'
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

@app.route('/informacoes_essenciais/<operadora>')
def informacoes_essenciais(operadora):
    try:
        resultado = wiki_chatbot.obter_informacoes_essenciais_operadora(operadora.upper())
        return jsonify(resultado)
    except Exception as e:
        return jsonify({
            'erro': f'Erro ao obter informações essenciais: {str(e)}',
            'status': 'erro'
        }), 500

@app.route('/resposta_inteligente')
def resposta_inteligente():
    try:
        operadora = request.args.get('operadora', 'OPERADORA')
        tipo = request.args.get('tipo', 'saudacao')
        contexto = request.args.get('contexto', None)
        
        resposta = wiki_chatbot.gerar_resposta_inteligente(operadora.upper(), tipo, contexto)
        
        return jsonify({
            'resposta': resposta,
            'operadora': operadora,
            'tipo': tipo,
            'timestamp': datetime.now().strftime('%d/%m/%Y às %H:%M:%S')
        })
    except Exception as e:
        return jsonify({
            'erro': f'Erro ao gerar resposta: {str(e)}',
            'status': 'erro'
        }), 500

@app.route('/faq/<operadora>')
def faq_operadora(operadora):
    """Gera FAQ estruturado para uma operadora específica"""
    try:
        resultado = wiki_chatbot.gerar_faq_operadora(operadora.upper())
        return jsonify(resultado)
        
    except Exception as e:
        return jsonify({
            'status': 'erro',
            'erro': f'Erro ao gerar FAQ: {str(e)}'
        }), 500

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
    print("   • Respostas inteligentes baseadas na wiki")
    print("   • Limpeza avançada de HTML")
    print("   • Templates de resposta personalizados")
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
    print("   • /informacoes_essenciais/<operadora>")
    print("   • /resposta_inteligente (respostas baseadas na wiki)")
    print("   • /faq/<operadora> (FAQ estruturado da operadora)")
    print("   • /teste_api (diagnóstico)")
    print("="*60 + "\n")
    
    app.run(debug=debug_mode, host='0.0.0.0', port=port)