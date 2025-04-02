# backend/services/openai_service.py

import os
import json
import hashlib
import datetime
from dotenv import load_dotenv
from openai import OpenAI

# Load environment variables
load_dotenv()

# Set up OpenAI client with API key
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Ensure cache and logs directories exist
os.makedirs("cache", exist_ok=True)
os.makedirs("logs", exist_ok=True)

def validate_extracted_data(data):
    """Ensure the extracted data contains all required fields in correct types."""
    if not isinstance(data, dict):
        return False
    return (
        "vendor" in data and isinstance(data["vendor"], str) and
        "amount" in data and isinstance(data["amount"], (int, float)) and
        "invoice_date" in data and isinstance(data["invoice_date"], str) and
        "category" in data and isinstance(data["category"], str)
    )

def extract_invoice_data(invoice_text):
    try:
        system_prompt = """
        You are an AI assistant that extracts key information from invoices.
        Extract the following fields:
        - Vendor name (the company issuing the invoice)
        - Amount (the total amount due in numeric format without currency symbols)
        - Date (in YYYY-MM-DD format)
        - Category (one of: Services, Supplies, Utilities, Equipment, Travel, Consulting, Other)

        Format your response as a JSON object with fields: vendor, amount, invoice_date, category.
        Only respond with the JSON object, nothing else.
        """

        user_prompt = f"Extract information from this invoice:\n\n{invoice_text}"

        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": system_prompt.strip()},
                {"role": "user", "content": user_prompt.strip()}
            ],
            temperature=0.3,
            max_tokens=300
        )

        result_text = response.choices[0].message.content.strip()
        print("🧠 RAW OpenAI RESPONSE:\n", result_text)

        return json.loads(result_text), len(result_text.split())  # returning token count estimate

    except Exception as e:
        print(f"❌ Error extracting data with OpenAI:\n\n{e}")
        return {
            "vendor": None,
            "amount": None,
            "invoice_date": None,
            "category": None
        }, 0

def extract_invoice_data_with_cache(invoice_text, invoice_id):
    """
    Extracts invoice data, using a cache to avoid repeated API calls.
    """
    text_hash = hashlib.md5(invoice_text.encode()).hexdigest()
    cache_file = os.path.join("cache", f"{invoice_id}_{text_hash[:10]}.json")

    if os.path.exists(cache_file):
        try:
            with open(cache_file, "r") as f:
                print(f"🧠 Using cached result for invoice {invoice_id}")
                return json.load(f), 0
        except json.JSONDecodeError:
            print(f"⚠️ Corrupt cache for invoice {invoice_id}, re-extracting...")

    extracted_data, token_count = extract_invoice_data(invoice_text)

    with open(cache_file, "w") as f:
        json.dump(extracted_data, f)

    print(f"💾 Cached result for invoice {invoice_id}")
    log_api_usage(invoice_id, token_count, success=bool(extracted_data["vendor"]))
    return extracted_data, token_count

def log_api_usage(invoice_id, token_count, success):
    """
    Logs API usage to a local file for cost tracking and debugging.
    """
    timestamp = datetime.datetime.now().isoformat()
    log_entry = f"{timestamp},{invoice_id},{token_count},{'success' if success else 'fail'}\n"

    with open("logs/openai_usage.log", "a") as f:
        f.write(log_entry)
