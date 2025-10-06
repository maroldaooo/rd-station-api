import requests
from datetime import datetime, timedelta
import os

class RDStationAPI:
    def __init__(self):
        self.client_id = os.getenv('RD_CLIENT_ID')
        self.client_secret = os.getenv('RD_CLIENT_SECRET')
        self.refresh_token = os.getenv('RD_REFRESH_TOKEN')
        self.token_url = 'https://api.rd.services/auth/token'
        self.base_url = 'https://api.rd.services/platform'
        
        self.access_token = None
        self.token_expiry = None
    
    def is_token_valid(self):
        """Verifica se o token ainda é válido"""
        if not self.access_token or not self.token_expiry:
            return False
        return datetime.now() < self.token_expiry
    
    def renovar_token(self):
        """Renova o access token usando o refresh token"""
        data = {
            'grant_type': 'refresh_token',
            'refresh_token': self.refresh_token,
            'client_id': self.client_id,
            'client_secret': self.client_secret
        }
        
        response = requests.post(self.token_url, data=data)
        
        if response.status_code == 200:
            token_data = response.json()
            self.access_token = token_data['access_token']
            
            # Atualiza refresh_token se vier um novo
            if 'refresh_token' in token_data:
                self.refresh_token = token_data['refresh_token']
            
            # Define expiração (23h para renovar antes)
            self.token_expiry = datetime.now() + timedelta(hours=23)
            
            return True
        else:
            raise Exception(f"Erro ao renovar token: {response.text}")
    
    def get_valid_token(self):
        """Retorna um token válido, renovando se necessário"""
        if not self.is_token_valid():
            self.renovar_token()
        return self.access_token
    
    def get_campanhas_email(self, data_inicio=None, data_fim=None):
        """Busca campanhas de email do RD Station"""
        token = self.get_valid_token()
        
        headers = {
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json'
        }
        
        # Se não informar datas, usa últimos 45 dias (limite do plano)
        if not data_fim:
            data_fim = datetime.now().strftime('%Y-%m-%d')
        
        if not data_inicio:
            data_inicio = (datetime.now() - timedelta(days=44)).strftime('%Y-%m-%d')
        
        url = f'{self.base_url}/analytics/emails'
        
        params = {
            'start_date': data_inicio,
            'end_date': data_fim
        }
        
        response = requests.get(url, headers=headers, params=params)
        
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"Erro ao buscar campanhas: {response.text}")
