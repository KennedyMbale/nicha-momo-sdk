import os
import uuid
import requests
from .auth import MomoAuth
from dotenv import load_dotenv

load_dotenv()

class Invoices:
    def __init__(self, auth):
        self.auth = auth
        self.subscription_key = os.getenv("COLLECTION_KEY")
        self.headers = {
            "X-Target-Environment": os.getenv("MOMO_ENVIRONMENT"),
            "Ocp-Apim-Subscription-Key": self.subscription_key,
            "Content-Type": "application/json"
        }
    
    def create(self, amount, payer_phone, payee_phone):
        invoice_id = str(uuid.uuid4())
        response = requests.post(
            f"{self.auth.base_url}/collection/v2_0/invoice",
            headers={
                **self.headers,
                "X-Reference-Id": invoice_id,
                "Authorization": f"Bearer {self.auth.get_collection_token()}"
            },
            json={
                "amount": str(amount),
                "currency": "EUR",
                "externalId": str(uuid.uuid1()),
                "validityDuration": "360",
                "intendedPayer": {"partyIdType": "MSISDN", "partyId": payer_phone},
                "payee": {"partyIdType": "MSISDN", "partyId": payee_phone},
                "description": "Generated Invoice"
            }
        )
        response.raise_for_status()
        return invoice_id
    
    def check_status(self, invoice_id):
        response = requests.get(
            f"{self.auth.base_url}/collection/v2_0/invoice/{invoice_id}",
            headers={
                **self.headers,
                "Authorization": f"Bearer {self.auth.get_collection_token()}"
            }
        )
        return response.json()
    
    def delete(self, invoice_id):
        response = requests.delete(
            f"{self.auth.base_url}/collection/v2_0/invoice/{invoice_id}",
            headers={
                **self.headers,
                "X-Reference-Id": str(uuid.uuid4()),
                "Authorization": f"Bearer {self.auth.get_collection_token()}"
            }
        )
        return response.status_code == 200