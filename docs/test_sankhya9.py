import os
import requests
from dotenv import load_dotenv
load_dotenv()
from src.services.sankhya_service import SankhyaService
import json

srv = SankhyaService()
try:
    sql = "SELECT 1 AS TESTE FROM DUAL"
    payload = {
        "serviceName": "DbExplorerSP.executeQuery",
        "requestBody": {
            "sql": sql
        }
    }
    url = f"{srv.base_url}/gateway/v1/mge/service.sbr?serviceName=DbExplorerSP.executeQuery&outputType=json"
    print("Testing DbExplorerSP with DUAL query...")
    headers = srv.get_headers()
    res = requests.post(url, headers=headers, json=payload)
    print("STATUS:", res.status_code)
    print("RESPONSE:", res.text)
except Exception as e:
    print("EXCEPTION:", str(e))
