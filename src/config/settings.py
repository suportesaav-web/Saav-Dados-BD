"""Configurações centrais, mapeamentos de contratos e identidade visual oficial da Saavedra."""

APP_TITLE = "Saav Dados BD - Portal Financeiro Saavedra"
APP_SUBTITLE = "Equalização, auditoria e consolidação precisa para contratos financeiros e materiais hospitalares."
APP_VERSION = "1.3.0"
APP_ICON = "📊"

# Paleta Corporativa Oficial Saavedra
PRIMARY_COLOR = "#DC4405"       # Laranja Oficial Saavedra
ACCENT_COLOR = "#DA291C"        # Vermelho Oficial Saavedra
DARK_NEUTRAL = "#25282A"        # Grafite Escuro Oficial Saavedra
BG_CARD_COLOR = "#F8F9FA"       # Fundo neutro suave
BORDER_COLOR = "#E9ECEF"        # Borda sutil
TEXT_MUTED = "#6C757D"          # Texto de apoio
SECONDARY_COLOR = DARK_NEUTRAL

# Configuração Centralizada de Clientes e Contratos BD
CLIENTES_CONFIG = [
    {
        'sigla': 'UNIMED',
        'contrato': '450128261',
        'termos': ['UNIMED', '87096616']
    },
    {
        'sigla': 'CONCEICAO',
        'contrato': '450166419',
        'termos': ['CONCEICAO', 'CONCEIÇÃO']
    },
    {
        'sigla': 'PUC',
        'contrato': '450155842',
        'termos': ['UNIAO BRASILEIRA', 'PUC', '88630413']
    },
    {
        'sigla': 'SANTA CASA',
        'contrato': None,
        'termos': ['SANTA CASA']
    },
    {
        'sigla': 'EBSERH',
        'contrato': '450098658',
        'termos': ['EBSERH', 'SERVICOS HOSPITALARES', '15126437']
    },
    {
        'sigla': 'HCAA',
        'contrato': '450137626',
        'termos': ['ASTROGILDO', '95610887']
    },
    {
        'sigla': 'H DIVINA',
        'contrato': '450146829',
        'termos': ['DIVINA', '87317764']
    },
    {
        'sigla': 'SMS POA',
        'contrato': '450120243',
        'termos': [],
        'custom_match': lambda r: 'PORTO ALEGRE' in r and ('PREF' in r or 'MUNICIPIO' in r or '92963560' in r)
    },
    {
        'sigla': 'HCPA',
        'contrato': '450139832',
        'termos': ['CLINICAS', '87020517']
    },
    {
        'sigla': 'GHC',
        'contrato': '450166419',
        'termos': ['GHC', '450166419']
    }
]

# Mapeamento Oficial de Contratos BD (derivado automaticamente para retrocompatibilidade)
CONTRATOS_MAPPING = {
    c['sigla']: c['contrato'] for c in CLIENTES_CONFIG if c.get('contrato')
}
CONTRATOS_MAPPING['GHC'] = '450166419'
CONTRATOS_MAPPING['CONCEICAO'] = '450166419'

# CSS Customizado Corporativo Refinado
CUSTOM_CSS = f"""
    <style>
        .main-title {{
            color: {PRIMARY_COLOR};
            font-size: 2.0rem;
            font-weight: 700;
            letter-spacing: -0.5px;
            margin-bottom: 0px;
            display: flex;
            align-items: center;
            gap: 12px;
        }}
        .sub-title {{
            color: {TEXT_MUTED};
            font-size: 0.95rem;
            font-weight: 400;
            margin-bottom: 1.5rem;
            margin-top: 4px;
        }}
        .metric-card {{
            background-color: {BG_CARD_COLOR};
            border: 1px solid {BORDER_COLOR};
            border-left: 4px solid {PRIMARY_COLOR};
            padding: 1.2rem;
            border-radius: 6px;
            box-shadow: 0 1px 2px rgba(0,0,0,0.05);
        }}
        .badge-version {{
            background-color: {DARK_NEUTRAL};
            color: #FFFFFF;
            padding: 2px 8px;
            border-radius: 4px;
            font-size: 0.75rem;
            font-weight: 600;
            letter-spacing: 0.5px;
        }}
        .stButton>button {{
            border-radius: 4px;
            font-weight: 600;
            letter-spacing: 0.3px;
        }}
        div[data-testid="stMetricValue"] {{
            color: {DARK_NEUTRAL};
            font-weight: 700;
        }}
    </style>
"""
