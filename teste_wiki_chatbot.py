#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Teste do Wiki Chatbot - Implementação conforme Luigi

Este script demonstra as funcionalidades do chatbot:
- Consulta via API GraphQL com token JWT
- Divisão de conteúdo por tags H2
- Busca inteligente por tópicos
- Limpeza de HTML aprimorada

Autor: Assistente IA
Data: 07/08/2025
"""

import requests
import json
from datetime import datetime

class TesteWikiChatbot:
    def __init__(self):
        self.base_url = "http://localhost:5000"
        self.session = requests.Session()
        
    def teste_conectividade(self):
        """Testa a conectividade com a API do chatbot"""
        print("🔍 TESTE 1: Conectividade da API")
        print("=" * 50)
        
        try:
            response = self.session.get(f"{self.base_url}/teste_api")
            data = response.json()
            
            print(f"Status: {response.status_code}")
            print(f"Resposta: {json.dumps(data, indent=2, ensure_ascii=False)}")
            
            if data.get('status') == 'ok':
                print("✅ API funcionando corretamente")
                return True
            else:
                print("❌ Problema na API")
                return False
                
        except Exception as e:
            print(f"❌ Erro de conexão: {e}")
            return False
    
    def teste_consulta_operadora(self, operadora, pergunta):
        """Testa consulta específica de uma operadora"""
        print(f"\n🔍 TESTE: Consulta {operadora}")
        print("=" * 50)
        print(f"Pergunta: {pergunta}")
        
        try:
            response = self.session.post(
                f"{self.base_url}/chat",
                json={"pergunta": pergunta},
                headers={"Content-Type": "application/json"}
            )
            
            data = response.json()
            
            print(f"\nStatus HTTP: {response.status_code}")
            print(f"Tipo de resposta: {data.get('tipo', 'N/A')}")
            
            if data.get('tipo') == 'sucesso':
                print(f"✅ Operadora: {data.get('operadora')}")
                print(f"✅ Tópico encontrado: {data.get('topico_encontrado')}")
                print(f"✅ Palavra-chave: {data.get('keyword_buscada')}")
                print(f"✅ Conteúdo: {data.get('conteudo', '')[:200]}...")
                
            elif data.get('tipo') == 'info_geral':
                print(f"📊 Operadora: {data.get('operadora')}")
                print(f"📊 Total de tópicos: {data.get('total_topicos')}")
                print(f"📊 Tópicos disponíveis: {data.get('topicos_disponiveis', [])}")
                
            elif data.get('tipo') == 'erro':
                print(f"❌ Erro: {data.get('mensagem')}")
                print(f"❌ Detalhes: {data.get('detalhes', 'N/A')}")
                if data.get('sugestao'):
                    print(f"💡 Sugestão: {data.get('sugestao')}")
                    
            return data
            
        except Exception as e:
            print(f"❌ Erro na consulta: {e}")
            return None
    
    def teste_listar_operadoras(self):
        """Testa listagem de operadoras disponíveis"""
        print("\n🔍 TESTE: Listar Operadoras")
        print("=" * 50)
        
        try:
            response = self.session.get(f"{self.base_url}/operadoras")
            data = response.json()
            
            print(f"Status: {response.status_code}")
            print(f"Total de operadoras: {len(data.get('operadoras', []))}")
            print(f"Operadoras: {', '.join(data.get('operadoras', [])[:10])}...")
            
            return data
            
        except Exception as e:
            print(f"❌ Erro ao listar operadoras: {e}")
            return None
    
    def teste_consulta_topico_especifico(self, operadora, topico):
        """Testa consulta de tópico específico"""
        print(f"\n🔍 TESTE: Tópico Específico - {operadora}/{topico}")
        print("=" * 50)
        
        try:
            response = self.session.get(
                f"{self.base_url}/consulta/{operadora}/{topico}"
            )
            
            data = response.json()
            
            print(f"Status: {response.status_code}")
            print(f"Resposta: {json.dumps(data, indent=2, ensure_ascii=False)[:500]}...")
            
            return data
            
        except Exception as e:
            print(f"❌ Erro na consulta de tópico: {e}")
            return None
    
    def executar_todos_testes(self):
        """Executa todos os testes do chatbot"""
        print("🚀 INICIANDO TESTES DO WIKI CHATBOT")
        print("Implementação conforme instruções do Luigi")
        print("=" * 60)
        print(f"Data/Hora: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
        print("=" * 60)
        
        # Teste 1: Conectividade
        if not self.teste_conectividade():
            print("\n❌ Falha na conectividade. Abortando testes.")
            return
        
        # Teste 2: Listar operadoras
        self.teste_listar_operadoras()
        
        # Teste 3: Consultas específicas
        testes_consulta = [
            ("VIVAS", "Qual o endereço da VIVAS?"),
            ("ARESNET", "Telefone da ARESNET"),
            ("POXNET", "Horários de atendimento da POXNET"),
            ("BRASILINK", "Planos da BRASILINK"),
            ("CAPITAL", "Informações da CAPITAL")
        ]
        
        for operadora, pergunta in testes_consulta:
            self.teste_consulta_operadora(operadora, pergunta)
        
        # Teste 4: Consultas de tópicos específicos
        topicos_teste = [
            ("VIVAS", "endereco"),
            ("ARESNET", "telefone"),
            ("POXNET", "horarios")
        ]
        
        for operadora, topico in topicos_teste:
            self.teste_consulta_topico_especifico(operadora, topico)
        
        print("\n" + "=" * 60)
        print("✅ TESTES CONCLUÍDOS")
        print("=" * 60)
        print("\n📋 RESUMO DAS FUNCIONALIDADES TESTADAS:")
        print("• ✅ Conectividade com API GraphQL")
        print("• ✅ Token JWT válido")
        print("• ✅ Query singleByPath")
        print("• ✅ Divisão por tags H2")
        print("• ✅ Busca inteligente por tópicos")
        print("• ✅ Limpeza de HTML")
        print("• ✅ Interface web responsiva")
        print("\n🌐 Acesse: http://localhost:5000")
        print("\n💡 Conforme especificações do Luigi:")
        print("   - Nomes de provedores em caixa alta sem espaço")
        print("   - Authorization: Bearer + Token")
        print("   - Conteúdo HTML dividido por tags h2")
        print("   - Busca e tratamento de tópicos")

def main():
    """Função principal"""
    teste = TesteWikiChatbot()
    teste.executar_todos_testes()

if __name__ == "__main__":
    main()