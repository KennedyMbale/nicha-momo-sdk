"""
MTN MoMo Collection Services
Handle payments from users to your account
"""

import os
import uuid
import requests
import re
from datetime import datetime
from typing import Dict, Union
from .auth import MomoAuth
from .utils import countdown
from dotenv import load_dotenv

from nicha_momo import auth

load_dotenv()

class Collections:
    def __init__(self, auth):  # Accept auth instance
        self.auth = auth
        self.subscription_key = os.getenv("COLLECTION_KEY")
        self.environment = os.getenv("MOMO_ENVIRONMENT", "sandbox")
        # Initialize headers correctly
        self.base_headers = {
            "X-Target-Environment": self.environment,
            "Ocp-Apim-Subscription-Key": self.subscription_key,
            "Content-Type": "application/json"
        }
        
    def _get_auth_header(self):
        return {"Authorization": f"Bearer {self.auth.get_collection_token()}"}

    def test_credentials():
        test_url = f"{auth.base_url}/v1_0/apiuser/{auth.api_user}"
        response = requests.get(
            test_url,
            headers={"Ocp-Apim-Subscription-Key": os.getenv("COLLECTION_KEY")}
        )
        if response.status_code == 200:
            print("Credentials validated successfully")
        else:
            print(f"Validation failed: {response.text}")

    # test_credentials()

    def request_payment(
        self, 
        phone: str, 
        amount: Union[str, float, int],
        payer_message: str = "Payment request",
        payee_note: str = "Transaction completed"
    ) -> str:
        
        if not self.auth.is_initialized():
            raise RuntimeError("Auth not initialized. Call initialize_momo() first")
        """
        Initiate payment collection from a user
        
        Args:
            phone (str): Payer's phone number (260XXXXXXXXX format)
            amount (number): Amount to collect
            payer_message (str): Message shown to payer (max 20 chars)
            payee_note (str): Internal transaction note (max 20 chars)
            
        Returns:
            str: Unique transaction reference ID
            
        Raises:
            ValueError: Invalid input parameters
            ConnectionError: API communication failure
        """
        # Validate inputs
        if not re.match(r'^260\d{9}$', phone):
            raise ValueError("Invalid phone format. Use 260XXXXXXXXX")
            
        try:
            amount = f"{float(amount):.2f}"
        except (ValueError, TypeError):
            raise ValueError("Invalid amount format")

        # Generate transaction IDs
        reference_id = str(uuid.uuid4())
        external_id = str(uuid.uuid1())

        # Build request
        url = f"{self.auth.base_url}/collection/v1_0/requesttopay"
        headers = {
            **self.base_headers,
            "X-Reference-Id": reference_id,
            "Authorization": f"Bearer {self.auth.get_collection_token()}"
        }
        
        payload = {
            "amount": amount,
            "currency": "EUR",
            "externalId": external_id,
            "payer": {
                "partyIdType": "MSISDN",
                "partyId": phone
            },
            "payerMessage": payer_message[:20],
            "payeeNote": payee_note[:20]
        }

        # Execute request
        try:
            response = requests.post(url, json=payload, headers=headers)
            
            
            if response.status_code == 202:
                return reference_id
                
            error_data = response.json()
            if response.status_code == 400:
                if "invalid currency" in error_data.get('message', '').lower():
                    raise ValueError("Only EUR supported in sandbox")
                    
            response.raise_for_status()
            
        except requests.exceptions.RequestException as e:
            raise ConnectionError(f"Payment collection failed: {str(e)}")
        return reference_id

    def check_payment_status(self, reference_id: str) -> Dict:
        """
        Check status of a payment request
        
        Args:
            reference_id (str): Transaction ID from request_payment()
            
        Returns:
            dict: Transaction status details
            
        Raises:
            ValueError: Invalid reference ID format
            ConnectionError: API communication failure
        """
        # Validate UUID format
        try:
            uuid.UUID(reference_id, version=4)
        except ValueError:
            raise ValueError("Invalid transaction reference ID format")

        # Wait for transaction processing
        countdown(6)
        
        url = f"{self.auth.base_url}/collection/v1_0/requesttopay/{reference_id}"
        headers = {
            **self.base_headers,
            "Authorization": f"Bearer {self.auth.get_collection_token()}"
        }

        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            return response.json()
            
        except requests.exceptions.HTTPError as e:
            if response.status_code == 404:
                raise ConnectionError("Transaction not found")
            raise ConnectionError(f"Status check failed: {str(e)}")
            
        except requests.exceptions.RequestException as e:
            raise ConnectionError(f"API connection failed: {str(e)}")

    def request_cash_out(
        self,
        phone: str,
        amount: Union[str, float, int],
        reason: str = "Cash withdrawal"
    ) -> str:
        """
        Initiate cash withdrawal from user's account
        
        Args:
            phone (str): Payer's phone number
            amount (number): Withdrawal amount
            reason (str): Withdrawal reason (max 20 chars)
            
        Returns:
            str: Unique transaction reference ID
            
        Raises:
            ValueError: Invalid input parameters
            ConnectionError: API communication failure
        """
        # Validate inputs
        if not re.match(r'^260\d{9}$', phone):
            raise ValueError("Invalid phone format. Use 260XXXXXXXXX")
            
        try:
            amount = f"{float(amount):.2f}"
        except (ValueError, TypeError):
            raise ValueError("Invalid amount format")

        # Generate transaction IDs
        reference_id = str(uuid.uuid4())
        external_id = str(uuid.uuid1())

        # Build request
        url = f"{self.auth.base_url}/collection/v1_0/requesttowithdraw"
        headers = {
            **self.base_headers,
            "X-Reference-Id": reference_id,
            "Authorization": f"Bearer {self.auth.get_collection_token()}"
        }
        
        payload = {
            "amount": amount,
            "currency": "EUR",
            "externalId": external_id,
            "payer": {
                "partyIdType": "MSISDN",
                "partyId": phone
            },
            "payerMessage": reason[:20],
            "payeeNote": "Cash withdrawal processed"
        }

        # Execute request
        try:
            response = requests.post(url, json=payload, headers=headers)
            
            if response.status_code == 202:
                return reference_id
                
            error_data = response.json()
            if response.status_code == 400:
                if "invalid currency" in error_data.get('message', '').lower():
                    raise ValueError("Only EUR supported in sandbox")
                    
            response.raise_for_status()
            
        except requests.exceptions.RequestException as e:
            raise ConnectionError(f"Cash out failed: {str(e)}")
            
        return reference_id

    def send_payment_notification(
        self, 
        reference_id: str,
        message: str = "Payment received successfully"
    ) -> bool:
        """
        Send payment confirmation notification
        
        Args:
            reference_id (str): Original transaction ID
            message (str): Notification message (max 100 chars)
            
        Returns:
            bool: True if notification sent successfully
            
        Raises:
            ConnectionError: API communication failure
        """
        url = f"{self.auth.base_url}/collection/v1_0/requesttopay/{reference_id}/deliverynotification"
        headers = {
            **self.base_headers,
            "Authorization": f"Bearer {self.auth.get_collection_token()}"
        }
        
        payload = {"notificationMessage": message[:100]}

        try:
            response = requests.post(url, json=payload, headers=headers)
            return response.status_code == 200
            
        except requests.exceptions.RequestException as e:
            raise ConnectionError(f"Notification failed: {str(e)}")