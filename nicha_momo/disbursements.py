"""
MTN MoMo Disbursement Services
Handle sending money to users
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

load_dotenv()

class Disbursements:
    def __init__(self, auth):
        """Initialize disbursement services with authentication"""
        self.auth =auth
        self.environment = os.getenv("MOMO_ENVIRONMENT", "sandbox")
        self.subscription_key = os.getenv("DISBURSEMENT_KEY")
        
        self.base_headers = {
            "X-Target-Environment": self.environment,
            "Ocp-Apim-Subscription-Key": self.subscription_key,
            "Content-Type": "application/json"
        }

    def transfer_funds(
        self,
        phone: str,
        amount: Union[str, float, int],
        recipient_name: str,
        currency: str = "EUR"
    ) -> str:
        """
        Transfer money to a user's account
        
        Args:
            phone (str): Recipient's phone number (260XXXXXXXXX format)
            amount (number): Transfer amount
            recipient_name (str): Recipient's name for validation
            currency (str): Currency code (EUR for sandbox)
            
        Returns:
            str: Unique transaction reference ID
            
        Raises:
            ValueError: Invalid input parameters
            ConnectionError: API communication failure
        """
        # Validate inputs
        if not re.match(r'^2567\d{9}$', phone):
            raise ValueError("Invalid phone format. Use 260XXXXXXXXX")
            
        try:
            amount = f"{float(amount):.2f}"
        except (ValueError, TypeError):
            raise ValueError("Invalid amount format")

        # Generate transaction IDs
        reference_id = str(uuid.uuid4())
        external_id = str(uuid.uuid1())

        # Build request
        url = f"{self.auth.base_url}/disbursement/v1_0/transfer"
        headers = {
            **self.base_headers,
            "X-Reference-Id": reference_id,
            "Authorization": f"Bearer {self.auth.get_disbursement_token()}"
        }
        
        payload = {
            "amount": amount,
            "currency": currency,
            "externalId": external_id,
            "payee": {
                "partyIdType": "MSISDN",
                "partyId": phone
            },
            "payerMessage": f"Transfer to {recipient_name[:15]}",
            "payeeNote": "Funds transfer"
        }

        # Execute request
        try:
            response = requests.post(url, json=payload, headers=headers)
            
            if response.status_code == 202:
                return reference_id
                
            error_data = response.json()
            if response.status_code == 400:
                if "name mismatch" in error_data.get('message', '').lower():
                    raise ValueError("Recipient name validation failed")
                    
            response.raise_for_status()
            
        except requests.exceptions.RequestException as e:
            raise ConnectionError(f"Funds transfer failed: {str(e)}")
            
        return reference_id

    def check_transfer_status(self, reference_id: str) -> Dict:
        """
        Check status of a funds transfer
        
        Args:
            reference_id (str): Transaction ID from transfer_funds()
            
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
        
        url = f"{self.auth.base_url}/disbursement/v1_0/transfer/{reference_id}"
        headers = {
            **self.base_headers,
            "Authorization": f"Bearer {self.auth.get_disbursement_token()}"
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

    def refund_transaction(
        self,
        original_reference: str,
        amount: Union[str, float, int],
        reason: str = "Transaction refund"
    ) -> str:
        """
        Refund a previous transaction
        
        Args:
            original_reference (str): Original transaction ID
            amount (number): Refund amount
            reason (str): Refund reason (max 20 chars)
            
        Returns:
            str: New refund transaction reference ID
            
        Raises:
            ValueError: Invalid input parameters
            ConnectionError: API communication failure
        """
        # Validate inputs
        try:
            amount = f"{float(amount):.2f}"
        except (ValueError, TypeError):
            raise ValueError("Invalid amount format")

        # Generate transaction IDs
        reference_id = str(uuid.uuid4())
        external_id = str(uuid.uuid1())

        # Build request
        url = f"{self.auth.base_url}/disbursement/v1_0/refund"
        headers = {
            **self.base_headers,
            "X-Reference-Id": reference_id,
            "Authorization": f"Bearer {self.auth.get_disbursement_token()}"
        }
        
        payload = {
            "amount": amount,
            "currency": "EUR",
            "externalId": external_id,
            "referenceIdToRefund": original_reference,
            "payerMessage": reason[:20],
            "payeeNote": "Refund processed"
        }

        # Execute request
        try:
            response = requests.post(url, json=payload, headers=headers)
            
            if response.status_code == 202:
                return reference_id
                
            error_data = response.json()
            if response.status_code == 400:
                if "invalid reference" in error_data.get('message', '').lower():
                    raise ValueError("Invalid original transaction ID")
                    
            response.raise_for_status()
            
        except requests.exceptions.RequestException as e:
            raise ConnectionError(f"Refund failed: {str(e)}")
            
        return reference_id

    def deposit_funds(
        self,
        phone: str,
        amount: Union[str, float, int],
        recipient_name: str
    ) -> str:
        """
        Deposit funds into a user's account
        
        Args:
            phone (str): Recipient's phone number
            amount (number): Deposit amount
            recipient_name (str): Recipient's name for validation
            
        Returns:
            str: Unique transaction reference ID
            
        Raises:
            ValueError: Invalid input parameters
            ConnectionError: API communication failure
        """
        # Validate inputs
        if not re.match(r'^2567\d{9}$', phone):
            raise ValueError("Invalid phone format. Use 260XXXXXXXXX")
            
        try:
            amount = f"{float(amount):.2f}"
        except (ValueError, TypeError):
            raise ValueError("Invalid amount format")

        # Generate transaction IDs
        reference_id = str(uuid.uuid4())
        external_id = str(uuid.uuid1())

        # Build request
        url = f"{self.auth.base_url}/disbursement/v1_0/deposit"
        headers = {
            **self.base_headers,
            "X-Reference-Id": reference_id,
            "Authorization": f"Bearer {self.auth.get_disbursement_token()}"
        }
        
        payload = {
            "amount": amount,
            "currency": "EUR",
            "externalId": external_id,
            "payee": {
                "partyIdType": "MSISDN",
                "partyId": phone
            },
            "payerMessage": f"Deposit to {recipient_name[:15]}",
            "payeeNote": "Funds deposit"
        }

        # Execute request
        try:
            response = requests.post(url, json=payload, headers=headers)
            
            if response.status_code == 202:
                return reference_id
                
            error_data = response.json()
            if response.status_code == 400:
                if "name mismatch" in error_data.get('message', '').lower():
                    raise ValueError("Recipient name validation failed")
                    
            response.raise_for_status()
            
        except requests.exceptions.RequestException as e:
            raise ConnectionError(f"Deposit failed: {str(e)}")
            
        return reference_id
    
    def cash_in(
        self,
        phone: str,
        amount: Union[str, float, int],
        recipient_name: str,
        currency: str = "EUR"
    ) -> str:
        """
        Deposit funds into a user's account (Cash In)
        
        Args:
            phone (str): Recipient's phone number (260XXXXXXXXX format)
            amount (number): Deposit amount
            recipient_name (str): Recipient's name for validation
            currency (str): Currency code (EUR for sandbox)
            
        Returns:
            str: Unique transaction reference ID
            
        Raises:
            ValueError: Invalid input parameters
            ConnectionError: API communication failure
        """
        # Validate phone format
        if not re.match(r'^260\d{9}$', phone):
            raise ValueError("Invalid phone format. Use 260XXXXXXXXX")

        # Validate amount
        try:
            amount = f"{float(amount):.2f}"
        except (ValueError, TypeError):
            raise ValueError("Invalid amount format")

        # Generate transaction IDs
        reference_id = str(uuid.uuid4())
        external_id = str(uuid.uuid1())

        # Build Cash In request
        url = f"{self.auth.base_url}/disbursement/v1_0/deposit"
        headers = {
            **self.base_headers,
            "X-Reference-Id": reference_id,
            "Authorization": f"Bearer {self.auth.get_disbursement_token()}"
        }
        
        payload = {
            "amount": amount,
            "currency": currency,
            "externalId": external_id,
            "payee": {
                "partyIdType": "MSISDN",
                "partyId": phone
            },
            "payerMessage": f"Cash deposit to {recipient_name[:15]}",
            "payeeNote": "Account funding"
        }

        # Execute request
        try:
            response = requests.post(url, json=payload, headers=headers)
            
            # Handle successful response
            if response.status_code == 202:
                return reference_id
                
            # Handle specific errors
            error_data = response.json()
            if response.status_code == 400:
                if "invalid currency" in error_data.get('message', '').lower():
                    raise ValueError("Only EUR supported in sandbox")
                if "name mismatch" in error_data.get('message', '').lower():
                    raise ValueError("Recipient name validation failed")
                    
            # Handle generic errors
            response.raise_for_status()
            
        except requests.exceptions.RequestException as e:
            raise ConnectionError(f"Cash In failed: {str(e)}")
            
        return reference_id

    def check_cash_in_status(self, reference_id: str) -> Dict:
        """
        Check status of a Cash In transaction
        
        Args:
            reference_id (str): Transaction ID from cash_in()
            
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
        
        url = f"{self.auth.base_url}/disbursement/v1_0/deposit/{reference_id}"
        headers = {
            **self.base_headers,
            "Authorization": f"Bearer {self.auth.get_disbursement_token()}"
        }

        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            return response.json()
            
        except requests.exceptions.HTTPError as e:
            if response.status_code == 404:
                raise ConnectionError("Cash In transaction not found")
            raise ConnectionError(f"Status check failed: {str(e)}")
            
        except requests.exceptions.RequestException as e:
            raise ConnectionError(f"API connection failed: {str(e)}")