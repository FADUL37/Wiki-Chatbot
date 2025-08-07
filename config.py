# Configurações da API de Operadoras

# Token JWT fornecido pelo Luigi (atualizado em 07/01/2025)
API_TOKEN = "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJhcGkiOjExLCJncnAiOjExNCwiaWF0IjoxNzU0NTcyNzAwLCJleHAiOjE3ODYxMzAzMDAsImF1ZCI6InVybjp3aWtpLmpzIiwiaXNzIjoidXJuOndpa2kuanMifQ.hYQIoRqN3Vts7OvH2CFf3uv0gqRNHr0ilwgrMs2JMRAjEH0izXU4BaaLCK4dqbunOEXVF1cAkvsA5IOVNWHoWtL1bF9r8q5sJFkaafbNiyS6aten2RcIsKFgbo-8ih1IM95vHI_J_BFe0ShewMdc2W4XPiRhT9xv-nWfjtowMWHXXFPF2BxgIEc_pFOMOj8jaQjfM70VNJUL9bRACgyGmNcAmmcK4K9kRItsvrBuH4gG2tbnKFMmITewbgtw5MN8kdD9ULbUoFb2ZYpsh3MH6MSkQU2YBmluaRpPIqGe0ItC4SUR34djGAWoybpIP-XYH0Zme6KFhSHcaesVn07xNg"

# URL base do Wiki.js - ALTERE PARA SUA URL REAL
BASE_URL = "https://wiki.upcall.com.br"

# Lista de operadoras para monitoramento
OPERADORAS_MONITORAR = [
    "vivas",
    "meo",
    "nos",
    "vodafone",
    "nowo"
]

# Configurações de monitoramento
INTERVALO_ATUALIZACAO = 300  # 5 minutos em segundos
MAX_TENTATIVAS = 3
TIMEOUT_REQUEST = 30

# Configurações de log
LOG_LEVEL = "INFO"
LOG_FILE = "operadoras.log"

# Campos específicos para extrair dos dados das operadoras
CAMPOS_INTERESSE = [
    "prazo",
    "vencimento",
    "dias",
    "tarifa",
    "preço",
    "promoção",
    "desconto",
    "validade",
    "condições"
]