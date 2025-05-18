# """
# PROPER Basic Usage with Full Initialization
# """
# import os
# import time
# from dotenv import load_dotenv
# from momo_api import MomoAuth, Collections

# load_dotenv()

# def verify_environment():
#     """Validate required environment variables"""
#     required_vars = [
#         "MOMO_BASE_URL",
#         "COLLECTION_KEY",
#         "CALLBACK_HOST"
#     ]
    
#     missing = []
#     for var in required_vars:
#         if not os.getenv(var):
#             missing.append(var)
    
#     if missing:
#         msg = f"Missing required environment variables: {', '.join(missing)}\n" \
#               "Check your .env file and ensure these values are set:\n" \
#               "- MOMO_BASE_URL (e.g. https://sandbox.momodeveloper.mtn.com)\n" \
#               "- COLLECTION_KEY (from MTN Developer Portal)\n" \
#               "- CALLBACK_HOST (e.g. webhook.site)"
#         raise EnvironmentError(msg)

# def main():
#     try:
#         print("=== Proper Initialization Demo ===")
#         verify_environment()
        
#         # 1. Initialize Auth
#         auth = MomoAuth()
#         user_id = auth.create_api_user(os.getenv("COLLECTION_KEY"))
#         print('USER ID: '+user_id)
#         auth.create_api_key(os.getenv("COLLECTION_KEY"))
        
#         # 2. Initialize Collections with auth
#         momo = Collections(auth)
        
#         # 3. Execute Transaction
#         payment_id = momo.request_payment("260762020814", 10)
#         print(f"Payment ID: {payment_id}")
#         cashout = momo.request_cash_out("260762020814", 10, 'I pay you')
#         status = momo.check_payment_status(cashout)
#         print(f"Cashed Out: {cashout}")
#         print(status)
        
#     except Exception as e:
#         print(f"Error: {str(e)}")

# if __name__ == "__main__":
#     main()

"""
Basic MoMo API Workflow with Consistent Naming
"""
import os
import time
from dotenv import load_dotenv
from nicha_momo import MomoAuth, Collections

load_dotenv()

def momo_verify_environment():
    """Validate required MoMo environment variables"""
    required_vars = [
        "MOMO_BASE_URL",
        "COLLECTION_KEY",
        "CALLBACK_HOST"
    ]
    missing = [var for var in required_vars if not os.getenv(var)]
    if missing:
        raise EnvironmentError(f"Missing MoMo config: {', '.join(missing)}")

def momo_initialize_auth():
    """Full MoMo authentication flow"""
    auth = MomoAuth()
    
    print("1. Creating MoMo API User...")
    api_user = auth.create_api_user(os.getenv('COLLECTION_KEY'))
    print(f"   User ID: {api_user}")
    
    print("2. Waiting 3s for user activation...")
    time.sleep(3)
    
    print("3. Generating MoMo API Key...")
    auth.api_key = auth.create_api_key(os.getenv('COLLECTION_KEY'))
    print(f"   API Key: {auth.api_key[:6]}...{auth.api_key[-4:]}")
    
    print("4. Waiting 3s for key activation...")
    time.sleep(3)
    
    return auth

def main():
    try:
        print("=== MoMo Basic Demo ===")
        momo_verify_environment()
        
        # Initialize authentication
        auth = momo_initialize_auth()
        
        # Initialize collections service
        momo = Collections(auth)
        
        # Execute payment
        print("5. Requesting payment...")
        payment_id = momo.request_payment(
            phone="260762020814",  # Test number
            amount=10.50
        )
        print(f"   Payment ID: {payment_id}")
        
        # Check status
        print("6. Checking payment status...")
        time.sleep(3)
        status = momo.check_payment_status(payment_id)
        print(f"   Final Status: {status.get('status')}")

    except Exception as e:
        print(f"\nError: {str(e)}")
        print("Solution: Check .env file and API credentials")

if __name__ == "__main__":
    main()