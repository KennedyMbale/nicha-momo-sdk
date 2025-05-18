import os
import requests
import uuid
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()

class MomoAuth:
    def __init__(self):
        self.base_url = os.getenv("MOMO_BASE_URL", "https://sandbox.momodeveloper.mtn.com")
        self.api_user = None
        self.api_key = None
        self.token = None
        self.token_expiry = datetime.now()
        self.oauth_token = None
        self.oauth_expiry = datetime.now()
        
    def create_api_user(self, subscription_key):
        self.api_user = str(uuid.uuid4())
        response = requests.post(
            f"{self.base_url}/v1_0/apiuser",
            headers={
                "X-Reference-Id": self.api_user,
                "Ocp-Apim-Subscription-Key": subscription_key,
                "Content-Type": "application/json"
            },
            json={"providerCallbackHost": os.getenv("CALLBACK_HOST")}
        )
        response.raise_for_status()
        return self.api_user
    
    def is_initialized(self):
        """Check if credentials exist"""
        return all([self.api_user, self.api_key])
    
    def create_api_key(self, subscription_key):
        response = requests.post(
            f"{self.base_url}/v1_0/apiuser/{self.api_user}/apikey",
            headers={"Ocp-Apim-Subscription-Key": subscription_key}
        )
        response.raise_for_status()
        self.api_key = response.json()['apiKey']
        return self.api_key
    
    def get_collection_token(self):
        try:
            if datetime.now() < self.token_expiry and self.token:
                return self.token
            
            if not self.api_user or not self.api_key:
                raise ValueError("API User/Key not initialized. Call create_api_user() first")

            # print(f"Debug - API User: {self.api_user}")
            # print(f"Debug - API Key: {self.api_key[:4]}...{self.api_key[-4:]}")
                
            response = requests.post(
                f"{self.base_url}/collection/token/",
                auth=(self.api_user, self.api_key),
                headers={"Ocp-Apim-Subscription-Key": os.getenv("COLLECTION_KEY")},
                timeout=10
            )
            response.raise_for_status()
        except requests.exceptions.HTTPError as e:
            print(f"Token Error Details: {e.response.text}")
            raise
        self.token = response.json()['access_token']
        self.token_expiry = datetime.now() + timedelta(seconds=response.json()['expires_in'])
        return self.token
    
    def get_disbursement_token(self):
        if datetime.now() < self.token_expiry:
            return self.token
            
        response = requests.post(
            f"{self.base_url}/disbursement/token/",
            auth=(self.api_user, self.api_key),
            headers={"Ocp-Apim-Subscription-Key": os.getenv("DISBURSEMENT_KEY")}
        )
        response.raise_for_status()
        self.token = response.json()['access_token']
        self.token_expiry = datetime.now() + timedelta(seconds=response.json()['expires_in'])
        return self.token
    
    def get_oauth_token(self, auth_req_id):
        response = requests.post(
            f"{self.base_url}/disbursement/oauth2/token/",
            headers={
                "Ocp-Apim-Subscription-Key": os.getenv("DISBURSEMENT_KEY"),
                "Content-Type": "application/x-www-form-urlencoded"
            },
            data=f"grant_type=urn:openid:params:grant-type:ciba&auth_req_id={auth_req_id}",
            auth=(self.api_user, self.api_key)
        )
        response.raise_for_status()
        self.oauth_token = response.json()['access_token']
        self.oauth_expiry = datetime.now() + timedelta(seconds=response.json()['expires_in'])
        return self.oauth_token