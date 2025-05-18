"""
Advanced MoMo API Demo with Full Error Handling
"""
import os
import time
import uuid
from dotenv import load_dotenv
from nicha_momo import MomoAuth, Collections, Disbursements, KYC, Invoices

load_dotenv()

# Helper Functions
def print_response(title, data):
    """Format API responses consistently"""
    print(f"\n[{title}]")
    print("-" * 40)
    for key, value in data.items():
        print(f"{key.replace('_', ' ').title():<25}: {value}")
    print("-" * 40 + "\n")

def initialize_collection():
    """Complete MoMo initialization sequence"""
    auth = MomoAuth()
    
    # 1. Create API User
    #print("Initializing MoMo API User...")
    auth.api_user = auth.create_api_user(os.getenv('COLLECTION_KEY'))
    #print(f"User ID: {auth.api_user}")
    
    # 2. Generate API Key
    time.sleep(3)
    #print("Generating API Key...")
    auth.api_key = auth.create_api_key(os.getenv('COLLECTION_KEY'))
    #print(f"API Key: {auth.api_key[:8]}...{auth.api_key[-4:]}")
    
    # 3. Wait for activation
    time.sleep(3)
    return auth

def initialize_disbursement():
    """Complete MoMo initialization sequence"""
    auth = MomoAuth()
    
    # 1. Create API User
    #print("Initializing MoMo API User...")
    auth.api_user = auth.create_api_user(os.getenv('DISBURSEMENT_KEY'))
    #print(f"DIS User ID: {auth.api_user}")
    
    # 2. Generate API Key
    time.sleep(3)
    #print("Generating API Key...")
    auth.api_key = auth.create_api_key(os.getenv('DISBURSEMENT_KEY'))
    #print(f"DIS API Key: {auth.api_key[:8]}...{auth.api_key[-4:]}")
    
    # 3. Wait for activation
    time.sleep(3)
    return auth 
# Main Demo
def momo_advanced_demo():
    """Full lifecycle demo with error handling"""
    try:
        # Phase 1: Initialization
        print("\n=== MoMo Advanced Demo ===")
        collection_auth = initialize_collection()
        disbursement_auth = initialize_disbursement()
        
        # Phase 2: Service Setup
        collections = Collections(collection_auth)
        disbursements = Disbursements(disbursement_auth)
        kyc = KYC(collection_auth)
        invoices = Invoices(collection_auth)

        # Phase 3: KYC Verification
        test_phone = "260xxxxxxxxx"
        print("\n[KYC Verification]")
        basic_info = kyc.get_basic_info(test_phone)
        print_response("Basic KYC Infor", basic_info)

        # Phase 4: Payment Lifecycle
        print("\n[Payment Processing]")
        payment_id = collections.request_payment(test_phone, 25.00)
        print_response("Payment Initiated", {"payment_id": payment_id})
        
        # Monitor payment status
        while True:
            status = collections.check_payment_status(payment_id)
            if status['status'] != 'PENDING':
                print_response("Payment Status", status)
                break
            time.sleep(5)

        # Phase 5: Refund Handling
        if status['status'] == "SUCCESSFUL":
            print("\n[Refund Processing]")
            refund_id = disbursements.refund_transaction(payment_id, 25.00)
            print_response("Refund Initiated", {"refund_id": refund_id})
            
            refund_status = disbursements.check_cash_in_status(refund_id)
            print_response("Refund Status", refund_status)

        # Phase 6: Invoice Management
        print("\n[Invoice Lifecycle]")
        invoice_id = invoices.create(
            amount=100.00,
            payer_phone=test_phone,
            payee_phone="260xxxxxxxxx"
        )
        print_response("Invoice Created", {"invoice_id": invoice_id})
        
        invoice_status = invoices.check_status(invoice_id)
        print_response("Invoice Status", invoice_status)
        
        if invoices.delete(invoice_id):
            print("\nInvoice successfully deleted")

    except Exception as e:
        print(f"\nDemo Failed: {str(e)}")

# Error Handling Demo
def momo_error_demo():
    """Controlled error scenario demonstration"""
    try:
        print("\n=== Error Handling Demo ===")
        
        # Intentional bad initialization
        bad_collections = Collections(MomoAuth())
        bad_collections.request_payment("invalid", "amount")
        
    except RuntimeError as e:
        print(f"√ Caught Auth Error: {str(e)}")
    except ValueError as e:
        print(f"√ Caught Validation Error: {str(e)}")
    except Exception as e:
        print(f"Unexpected Error: {str(e)}")
    finally:
        print("Error test completed successfully")

if __name__ == "__main__":
    momo_advanced_demo()
    # momo_error_demo()