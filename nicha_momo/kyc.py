"""
MTN MoMo KYC Services
Handles customer identity verification and data access
"""

import os
import re
import requests
from typing import Dict, Optional
from .auth import MomoAuth
from dotenv import load_dotenv

load_dotenv()

class KYC:
    def __init__(self, auth):
        """Initialize KYC services with authentication"""
        self.auth = auth
        self.environment = os.getenv("MOMO_ENVIRONMENT", "sandbox")
        self.subscription_key = os.getenv("DISBURSEMENT_KEY")
        
        self.base_headers = {
            "X-Target-Environment": self.environment,
            "Ocp-Apim-Subscription-Key": self.subscription_key
        }

    def get_basic_info(self, phone: str) -> Dict:
        """
        Get basic customer information
        
        Args:
            phone (str): Phone number in 2600000000 format
            
        Returns:
            dict: Contains:
                - given_name
                - family_name
                - birthdate
                - locale
                - gender
                
        Raises:
            ValueError: Invalid phone format
            ConnectionError: API communication failure
        """
        # Validate phone number
        if not re.match(r'^260\d{9}$', phone):
            raise ValueError("Invalid phone format. Use 2600000000")
            
        url = f"{self.auth.base_url}/disbursement/v1_0/accountholder/msisdn/{phone}/basicuserinfo"
        headers = {
            **self.base_headers,
            "Authorization": f"Bearer {self.auth.get_disbursement_token()}"
        }

        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            return self._parse_basic_info(response.json())
            
        except requests.exceptions.HTTPError as e:
            if response.status_code == 404:
                raise ConnectionError("User not found")
            raise ConnectionError(f"KYC check failed: {response.text}")

    def _parse_basic_info(self, data: Dict) -> Dict:
        """Standardize basic info format"""
        return {
            'full_name': f"{data.get('given_name', '')} {data.get('family_name', '')}".strip(),
            'birth_date': data.get('birthdate'),
            'gender': data.get('gender', 'U').upper(),
            'language': data.get('locale', 'en')
        }

    def request_consent(
        self, 
        phone: str,
        scopes: str = "all_info",
        consent_duration: int = 3600
    ) -> str:
        """
        Initiate customer consent request
        
        Args:
            phone (str): Customer phone number
            scopes (str): Requested data access (default: all_info)
            consent_duration (int): Consent validity in seconds
            
        Returns:
            str: Consent reference ID (auth_req_id)
            
        Raises:
            ConnectionError: API communication failure
        """
        url = f"{self.auth.base_url}/disbursement/v1_0/bc-authorize"
        headers = {
            **self.base_headers,
            "Authorization": f"Bearer {self.auth.get_disbursement_token()}",
            "Content-Type": "application/x-www-form-urlencoded"
        }
        
        body = {
            "scope": scopes,
            "login_hint": f"ID:{phone}/MSISDN",
            "access_type": "offline",
            "expires_in": str(consent_duration)
        }

        try:
            response = requests.post(url, data=body, headers=headers)
            response.raise_for_status()
            return response.json().get('auth_req_id')
            
        except requests.exceptions.HTTPError as e:
            error = response.json().get('error', '')
            if 'invalid_scope' in error:
                raise ConnectionError("Invalid data scope requested")
            raise ConnectionError(f"Consent request failed: {error}")

    def get_detailed_info(self, auth_req_id: str) -> Dict:
        """
        Get detailed customer information after consent
        
        Args:
            auth_req_id (str): Consent reference from request_consent()
            
        Returns:
            dict: Contains:
                - national_id
                - address
                - email
                - verified_status
                - account_balance
                - transaction_history
                
        Raises:
            ConnectionError: Consent not granted or expired
        """
        # Get OAuth token first
        oauth_token = self.auth.get_oauth_token(auth_req_id)
        
        url = f"{self.auth.base_url}/disbursement/oauth2/v1_0/userinfo"
        headers = {
            **self.base_headers,
            "Authorization": f"Bearer {oauth_token}"
        }

        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            return self._parse_detailed_info(response.json())
            
        except requests.exceptions.HTTPError as e:
            if response.status_code == 401:
                raise ConnectionError("Consent expired or revoked")
            raise ConnectionError(f"Data access failed: {response.text}")

    def _parse_detailed_info(self, data: Dict) -> Dict:
        """Standardize detailed info format"""
        return {
            'national_id': data.get('national_id'),
            'address': {
                'street': data.get('street_address'),
                'city': data.get('locality'),
                'country': data.get('country')
            },
            'email': data.get('email'),
            'verified': data.get('email_verified', False),
            'financials': {
                'balance': data.get('account_balance'),
                'currency': data.get('account_currency')
            }
        }

    def validate_identity(
        self, 
        phone: str, 
        full_name: str, 
        birth_date: Optional[str] = None
    ) -> bool:
        """
        Verify customer identity against MoMo records
        
        Args:
            phone (str): Customer phone number
            full_name (str): Full name to verify
            birth_date (str): Optional birthdate (YYYY-MM-DD)
            
        Returns:
            bool: True if identity matches
            
        Raises:
            ConnectionError: Verification failed
        """
        try:
            info = self.get_basic_info(phone)
            name_match = info['full_name'].lower() == full_name.lower()
            
            if birth_date:
                date_match = info['birth_date'] == birth_date
                return name_match and date_match
                
            return name_match
            
        except Exception as e:
            raise ConnectionError(f"Identity verification failed: {str(e)}")