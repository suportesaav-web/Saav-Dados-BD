import os
import requests
import pandas as pd
from datetime import datetime, timedelta

class SankhyaService:
    def __init__(self):
        self.client_id = os.environ.get('SANKHYA_CLIENT_ID')
        self.client_secret = os.environ.get('SANKHYA_CLIENT_SECRET')
        self.x_token = os.environ.get('SANKHYA_X_TOKEN')
        env = os.environ.get('SANKHYA_ENV', 'sandbox')
        
        self.base_url = "https://api.sandbox.sankhya.com.br" if env == 'sandbox' else "https://api.sankhya.com.br"
        self.bearer_token = None

    def authenticate(self):
        """
        Gera um Bearer Token temporário usando as credenciais e o X-Token.
        """
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
            
        data = response.json()
        self.bearer_token = data.get('access_token')

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
            # O outputType=json retorna fieldsMetadata diretamente como uma lista ou dentro de 'field' dependendo da versão
            if isinstance(fields_meta, dict) and 'field' in fields_meta:
                fields = [field['name'] for field in fields_meta['field']]
            else:
                fields = [field['name'] for field in fields_meta]
                
            rows = data['responseBody']['rows']
            
            df = pd.DataFrame(rows, columns=fields)
            return df
        except Exception as e:
            raise Exception(f"Erro ao processar retorno da API. O formato esperado não foi retornado.\nResponse: {str(data)}")

    def buscar_vendas(self, data_ini: str, data_fim: str, codemp: str = "1") -> pd.DataFrame:
        """
        Busca os dados de vendas (Saídas) no período informado.
        As datas devem estar no formato DD/MM/YYYY.
        """
        sql = f"""
        SELECT
            SUB.*,
            SUB.VLRPROD + SUB.VLRIPI + SUB.VLRSUBST + SUB.VLRFRETE + SUB.VLROUTROS AS VLRCONTABIL
        FROM (
            SELECT UFSPAR.UF, PRO.CODPROD, PRO.REFFORN AS REFERENCIA, PAR.CODPARC AS CODPARC, 
            PAR.RAZAOSOCIAL AS RAZSOCIAL, PAR.CGC_CPF AS CNPJ_PARCEIRO, PER.DESCRTIPPARC AS PERFIL, 
            CAB.NUMNOTA AS NUMNF, CAB.DTNEG AS DTEMISSAO, CAB.DTENTSAI, PRO.DESCRPROD AS DESCRICAO, 
            PRO.CODGRUPOPROD AS GRUPO, GRU.DESCRGRUPOPROD AS GRUPODESCRICAO, PRO.NCM, ITE.CODCFO AS CFOP, 
            PRO.MARCA AS MARCA, ITE.QTDNEG AS QTDCOM, ITE.VLRUNIT, ITE.VLRTOT AS VLRPROD, ITE.BASEICMS AS BCICMS, 
            ITE.ALIQICMS, ITE.VLRICMS, ITE.VLRIPI, ITE.VLRSUBST, ITE.BASESUBSTIT, ITE.CONTROLE AS CONTROLE, 
            (CASE WHEN ITE.VLRTOT = 0 OR CAB.VLRFRETE = 0 THEN 0 ELSE ITE.VLRTOT / (SELECT SUM( ITE.VLRTOT ) FROM TGFITE ITE WHERE ITE.NUNOTA = CAB.NUNOTA AND ITE.SEQUENCIA > 0) END)*CAB.VLRFRETE AS VLRFRETE, 
            TPO.CODTIPOPER, TPO.DESCROPER, ITE.VLRDESC, 
            (CASE WHEN ITE.VLRTOT = 0 OR CAB.VLROUTROS = 0 THEN 0 ELSE ITE.VLRTOT / (SELECT SUM( ITE.VLRTOT ) FROM TGFITE ITE WHERE ITE.NUNOTA = CAB.NUNOTA AND ITE.SEQUENCIA > 0 ) END)*CAB.VLROUTROS AS VLROUTROS 
            
            FROM TGFCAB CAB
            INNER JOIN TGFPAR PAR ON CAB.CODPARC = PAR.CODPARC
            INNER JOIN TSICID CIDPAR ON PAR.CODCID = CIDPAR.CODCID
            INNER JOIN TSIUFS UFSPAR ON UFSPAR.CODUF = CIDPAR.UF
            LEFT JOIN TGFTPP PER ON PER.CODTIPPARC = PAR.CODTIPPARC
            INNER JOIN TGFITE ITE ON CAB.NUNOTA = ITE.NUNOTA
            INNER JOIN TGFPRO PRO ON ITE.CODPROD = PRO.CODPROD
            INNER JOIN TGFTOP TPO ON CAB.CODTIPOPER = TPO.CODTIPOPER AND CAB.DHTIPOPER = TPO.DHALTER
            INNER JOIN TGFGRU GRU ON PRO.CODGRUPOPROD = GRU.CODGRUPOPROD
            
            WHERE CAB.CODEMP = {codemp}
            AND CAB.DTNEG BETWEEN '{data_ini}' AND '{data_fim}'
            AND CAB.STATUSNOTA = 'L'
            AND TPO.ATUALLIVFIS <> 'N'
            AND CAB.TIPMOV IN ('V', 'E')
        ) SUB
        ORDER BY SUB.DTENTSAI, SUB.NUMNF
        """
        return self.execute_query(sql)
