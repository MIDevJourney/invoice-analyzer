# test_ai_extraction.py

import requests

# Configuration - change these to match your setup!
API_BASE = "http://localhost:8000"  # URL where your FastAPI server is running
USERNAME = "test@test.com"  # Replace with a user in your system
PASSWORD = "test123"  # Replace with the user's password

def get_token():
    """Log in and get an access token for API requests"""
    print("Logging in to get access token...")
    
    response = requests.post(
        f"{API_BASE}/auth/token",
        data={"username": USERNAME, "password": PASSWORD}
    )
    
    if response.status_code != 200:
        print(f"Login failed with status {response.status_code}: {response.text}")
        return None
    
    token = response.json().get("access_token")
    print(f"Got token: {token[:10]}...")
    return token

def list_invoices(token):
    """Get a list of invoices to extract data from"""
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(
        f"{API_BASE}/invoices/",
        headers=headers
    )
    
    if response.status_code == 200:
        invoices = response.json()
        print(f"Found {len(invoices)} invoices to process")
        return invoices
    else:
        print(f"Failed to list invoices: {response.status_code}")
        return []

def extract_invoice_data(token, invoice_id):
    """Extract data from an invoice using AI"""
    print(f"\n🔥🔥🔥 Calling /extract for invoice {invoice_id} 🔥🔥🔥")
    print(f"Extracting data for invoice {invoice_id}...")
    
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.post(
        f"{API_BASE}/invoices/{invoice_id}/extract",
        headers=headers
    )
    
    if response.status_code == 200:
        result = response.json()
        print("✅ Extraction successful:")
        print(f"   Vendor: {result.get('vendor')}")
        print(f"   Amount: ${result.get('amount')}")
        print(f"   Date: {result.get('invoice_date')}")
        print(f"   Category: {result.get('category')}")
        return result
    else:
        print(f"❌ Extraction failed (Status: {response.status_code})")
        print(f"   Error: {response.text}")
        return None

def main():
    """Run the AI extraction test"""
    print("===== TESTING AI EXTRACTION =====")
    
    # Get auth token
    token = get_token()
    if not token:
        return
    
    # Get list of invoices
    invoices = list_invoices(token)
    if not invoices:
        return
    
    # Extract data from each invoice
    for invoice in invoices:
        extract_invoice_data(token, invoice["id"])
    
    print("===== TEST COMPLETED =====")

if __name__ == "__main__":
    main()