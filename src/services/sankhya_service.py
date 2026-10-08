import os
import requests
import pandas as pd
from datetime import datetime, timedelta
from src.config.settings import CONTRATOS_MAPPING

class SankhyaService:
    def __init__(self):
        self.client_id = os.environ.get('SANKHYA_CLIENT_ID')
        self.client_secret = os.environ.get('SANKHYA_CLIENT_SECRET')
        self.x_token = os.environ.get('SANKHYA_X_TOKEN')
        env = os.environ.get('SANKHYA_ENV', 'sandbox')
        
        self.base_url = "https://api.sandbox.sankhya.com.br" if env == 'sandbox' else "https://api.sankhya.com.br"
        self.bearer_token = None

    def authenticate(self):
        auth_url = f"{self.base_url}/authenticate"
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
            'X-Token': self.x_token
        }
        payload = {
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "grant_type": "client_credentials"
        }
        response = requests.post(auth_url, headers=headers, data=payload)
        if response.status_code != 200:
            raise Exception(f"Falha ao autenticar no Sankhya Gateway: {response.status_code} - {response.text}")
        self.bearer_token = response.json().get('access_token')

    def get_headers(self):
        if not self.bearer_token:
            self.authenticate()
        return {
            'Authorization': f'Bearer {self.bearer_token}',
            'Content-Type': 'application/json'
        }

    def execute_query(self, sql_query: str) -> pd.DataFrame:
        payload = {
            "serviceName": "DbExplorerSP.executeQuery",
            "requestBody": {
                "sql": sql_query
            }
        }
        url = f"{self.base_url}/gateway/v1/mge/service.sbr?serviceName=DbExplorerSP.executeQuery&outputType=json"
        response = requests.post(url, headers=self.get_headers(), json=payload)
        if response.status_code != 200:
            raise Exception(f"Erro na API Sankhya ao executar a consulta: {response.status_code} - {response.text}")
        data = response.json()
        if 'status' in data and data['status'] == '0':
            raise Exception(f"Erro interno do Sankhya: {data.get('statusMessage', 'Sem detalhes')}")
        try:
            fields_meta = data['responseBody']['fieldsMetadata']
            if isinstance(fields_meta, dict) and 'field' in fields_meta:
                fields = [field['name'] for field in fields_meta['field']]
            else:
                fields = [field['name'] for field in fields_meta]
            rows = data['responseBody']['rows']
            return pd.DataFrame(rows, columns=fields)
        except Exception as e:
            raise Exception(f"Erro ao processar retorno da API. Response: {str(data)}")

    def buscar_precos_contratos(self) -> pd.DataFrame:
        nutabs = [f"'{v}'" for v in CONTRATOS_MAPPING.values() if v]
        nutabs_str = ",".join(nutabs)
        if not nutabs_str:
            return pd.DataFrame()

        sql = f"""
        SELECT 
            TAB.NUTAB AS NUM_CONTRATO,
            TAB.CODTAB AS CODIGO_TABELA,
            PRO.REFFORN AS REFPROD,
            EXC.VLRVENDA AS VALOR_TABELADO_BD
        FROM TGFTAB TAB
        INNER JOIN TGFEXC EXC ON TAB.NUTAB = EXC.NUTAB
        INNER JOIN TGFPRO PRO ON EXC.CODPROD = PRO.CODPROD
        WHERE TAB.NUTAB IN ({nutabs_str})
        """
        df = self.execute_query(sql)
        
        # Invertendo o mapeamento: {contrato: sigla}
        inv_map = {str(v): k for k, v in CONTRATOS_MAPPING.items() if v}
        df['NUM_CONTRATO'] = df['NUM_CONTRATO'].astype(str)
        df['GRUPO_CLIENTE'] = df['NUM_CONTRATO'].map(inv_map)
        
        df = df[df['GRUPO_CLIENTE'].notna()]
        return df

    def buscar_vendas(self, data_ini: str, data_fim: str, codemp: str = "1") -> pd.DataFrame:
        pass
