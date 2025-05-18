# MTN MoMo API Package [Sandbox]

Complete integration package for MTN Mobile Money APIs

## Table of Contents
- [Installation](#installation)
- [Configuration](#configuration)
- [Basic Usage](#basic-usage)
- [Advanced Features](#advanced-features)
- [Error Handling](#error-handling)
- [Testing](#testing)
- [Contributing](#contributing)

## Installation
```bash
pip install -r requirements.txt

## Installation
Configuration
Create .env file:

ini
MOMO_BASE_URL=https://sandbox.momodeveloper.mtn.com
COLLECTION_KEY=your_collection_key
DISBURSEMENT_KEY=your_disbursement_key
CALLBACK_HOST=your_callback_url
Basic Usage
python
from nicha_momo import MomoAuth, Collections

# Initialize
auth = MomoAuth()
auth.create_api_user(os.getenv("COLLECTION_KEY"))
auth.create_api_key(os.getenv("COLLECTION_KEY"))

collections = Collections(auth)

# Request payment
payment_id = collections.request_payment("260XXXXXXXXX", 10)


# Refund processing
from nicha_momo import Disbursements
disbursements = Disbursements(auth)
refund_id = disbursements.refund_transaction(payment_id, 10.50)

# KYC Verification
from nicha_momo import KYC
kyc = KYC(auth)
basic_info = kyc.get_basic_info("260XXXXXXXXX")


try:
    collections.momo_request_payment("invalid", "amount")
except ValueError as e:
    print(f"Validation error: {str(e)}")
except ConnectionError as e:
    print(f"API error: {str(e)}")
