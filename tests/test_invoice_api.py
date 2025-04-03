#File: test_invoice_api.py

# This file tests our invoice management system API
# It uploads test invoices, lists them, gets details, updates, and deletes them
# Think of it like a checklist that makes sure all our backend functions work properly

import requests  # For making HTTP requests to our API
import json  # For handling JSON data
import os  # For file operations

# Our API settings - where the server lives and login details
API_BASE = "http://localhost:8000"  # This is just on my local computer for testing
USERNAME = "test@test.com"  # My test user email
PASSWORD = "test123"  # My test user password

# The PDF files we'll use for testing
# These should be in the same folder as this script
INVOICE_FILES = [
    "tech_solutions_invoice.pdf",
    "office_supplies_invoice.pdf",
    "consulting_services_invoice.pdf"
]

# Warning if test files don't exist - this saves frustration later
# I added this check after running into issues with missing files
for file in INVOICE_FILES:
    if not os.path.exists(file):
        print(f"WARNING: Test file {file} not found! Create this file first.")


def get_token():
    """
    Log in to get an access token for authentication
    This is like getting a visitor badge to enter a secure building
    """
    print("Logging in to get access token...")
    
    # Send username and password to get a token
    response = requests.post(
        f"{API_BASE}/auth/token",
        data={"username": USERNAME, "password": PASSWORD}
    )
    
    # If login fails, show error and return nothing
    if response.status_code != 200:
        print(f"Login failed with status {response.status_code}: {response.text}")
        return None
    
    # Get the token from response and show first few characters
    token = response.json().get("access_token")
    print(f"Got token: {token[:10]}...")  # Only show part of it for security
    return token


def test_upload(token, file_path, metadata):
    """
    Upload an invoice file with its information (vendor, amount, etc.)
    
    This was tricky to get right! I ran into several issues with how to
    properly format the metadata for the API.
    """
    print(f"\nUploading invoice: {os.path.basename(file_path)}")
    
    # Set up the authorization header with our token
    headers = {"Authorization": f"Bearer {token}"}
    
    # Open the PDF file and prepare it for upload
    with open(file_path, "rb") as f:
        # Set up the file for upload
        files = {"file": (os.path.basename(file_path), f, "application/pdf")}
        
        # IMPORTANT FIX: Convert metadata dictionary to JSON string
        # This was the key to solving our upload issues!
        data = {"invoice_data": json.dumps(metadata)}
        
        print(f"Sending metadata: {metadata}")
        
        # Send the file and metadata to our API
        response = requests.post(
            f"{API_BASE}/invoices/",
            headers=headers,
            files=files,
            data=data
        )
    
    # Check if upload worked and show results
    if response.status_code in (200, 201):
        print(f"✅ Upload successful (Status: {response.status_code})")
        result = response.json()
        print(f"   Invoice ID: {result.get('id')}")
        return result
    else:
        print(f"❌ Upload failed (Status: {response.status_code})")
        print(f"   Error: {response.text}")
        return None


def test_listing(token):
    """
    Get a list of all invoices for our user
    Like checking what files we have in our cabinet
    """
    print("\nListing all invoices")
    
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(
        f"{API_BASE}/invoices/",
        headers=headers
    )
    
    if response.status_code == 200:
        invoices = response.json()
        print(f"✅ Found {len(invoices)} invoices:")
        
        # Print each invoice's basic info in a nice format
        for i, inv in enumerate(invoices, 1):
            amount = inv.get('amount')
            amount_str = f"${amount:.2f}" if isinstance(amount, (int, float)) else "N/A"
            print(f"   {i}. {inv.get('vendor', 'Unknown')} - {amount_str} - {inv.get('invoice_date', 'No date')}")
        
        return invoices
    else:
        print(f"❌ Listing failed (Status: {response.status_code})")
        print(f"   Error: {response.text}")
        return []


def test_get_invoice(token, invoice_id):
    """
    Get detailed information about one specific invoice
    Like pulling a single file to examine it more closely
    """
    print(f"\nGetting invoice details for ID: {invoice_id}")
    
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(
        f"{API_BASE}/invoices/{invoice_id}",
        headers=headers
    )
    
    if response.status_code == 200:
        invoice = response.json()
        print("✅ Invoice details retrieved:")
        vendor = invoice.get("vendor") or "Unknown"
        amount = invoice.get("amount")
        amount_str = f"${amount:.2f}" if isinstance(amount, (int, float)) else "N/A"
        date = invoice.get("invoice_date") or "No date"
        category = invoice.get("category") or "Uncategorized"
        file_name = invoice.get("file_name") or "Missing file"

        print("✅ Invoice details retrieved:")
        print(f"   Vendor: {vendor}")
        print(f"   Amount: {amount_str}")
        print(f"   Date: {date}")
        print(f"   Category: {category}")
        print(f"   File: {file_name}")
        return invoice
    else:
        print(f"❌ Get invoice failed (Status: {response.status_code})")
        print(f"   Error: {response.text}")
        return None


def test_update(token, invoice_id, update_data):
    """
    Update an invoice's information
    For example, fix a typo in vendor name or change category
    """
    print(f"\nUpdating invoice ID: {invoice_id}")
    print(f"New data: {update_data}")
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    response = requests.put(
        f"{API_BASE}/invoices/{invoice_id}",
        headers=headers,
        json=update_data  # Sends update_data as JSON directly
    )
    
    if response.status_code == 200:
        updated = response.json()
        print("✅ Invoice updated successfully:")
        print(f"   New vendor: {updated.get('vendor') or 'Unknown'}")

        amount = updated.get("amount")
        amount_str = f"${amount:.2f}" if isinstance(amount, (int, float)) else "N/A"
        print(f"   New amount: {amount_str}")

        date = updated.get("invoice_date") or "No date"
        print(f"   New date: {date}")

        category = updated.get("category") or "Uncategorized"
        print(f"   New category: {category}")
        
        return updated
    else:
        print(f"❌ Update failed (Status: {response.status_code})")
        print(f"   Error: {response.text}")
        return None



def test_delete(token, invoice_id):
    """
    Delete an invoice from the system
    Remove it completely from our database
    """
    print(f"\nDeleting invoice ID: {invoice_id}")
    
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.delete(
        f"{API_BASE}/invoices/{invoice_id}",
        headers=headers
    )
    
    if response.status_code == 204:
        print("✅ Invoice deleted successfully")
        return True
    else:
        print(f"❌ Delete failed (Status: {response.status_code})")
        print(f"   Error: {response.text}")
        return False


def run_tests():
    """
    Run all tests in sequence to make sure every part of our API works
    This is like doing a complete systems check before launch
    """
    print("===== STARTING INVOICE API TESTS =====")
    
    # Step 1: Log in and get security token
    token = get_token()
    if not token:
        print("❌ Authentication failed - cannot continue tests")
        return
    
    # Step 2: Set up test data for our invoices
    test_invoices = [
        {"file_path": INVOICE_FILES[0], "metadata": {}},
        {"file_path": INVOICE_FILES[1], "metadata": {}},
        {"file_path": INVOICE_FILES[2], "metadata": {}},
    ]
    
    # Step 3: Upload all test invoices
    uploaded_ids = []
    for invoice in test_invoices:
        result = test_upload(token, invoice["file_path"], invoice["metadata"])
        if result:
            uploaded_ids.append(result["id"])
    
    if not uploaded_ids:
        print("❌ No invoices were uploaded successfully - cannot continue tests")
        return
    
    # Step 4: List all invoices to make sure uploads worked
    test_listing(token)
    
    # Step 5: Get details for one specific invoice
    if uploaded_ids:
        test_get_invoice(token, uploaded_ids[0])
    
    # Step 6: Update an invoice with new information
    if len(uploaded_ids) >= 2:
        update_data = {
            "vendor": "Office Supplies Inc. (Updated)",
            "category": "Office Expenses"
        }
        test_update(token, uploaded_ids[1], update_data)
    
    # Step 7: List again to verify the update worked
    print("\nListing invoices after update:")
    test_listing(token)
    
    # Step 8: Delete an invoice
    if len(uploaded_ids) >= 3:
        test_delete(token, uploaded_ids[2])
    
    # Step 9: List again to confirm deletion worked
    print("\nListing invoices after deletion:")
    test_listing(token)
    
    print("\n===== INVOICE API TESTS COMPLETED =====")


if __name__ == "__main__":
    run_tests()