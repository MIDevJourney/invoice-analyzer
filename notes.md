# File: notes.md

## Bugs and Fixes:

## March 31, 2025 - Pre-Week 1: Setting Up FastAPI Backend
Ran into a bug while installing FastAPI dependencies:
- Command: `pip3 install fastapi uvicorn python-multipart python-jose[cryptography] passlib[bcrypt] sqlalchemy`
- Error: `zsh: no matches found: python-jose[cryptography]` (zsh thought `[cryptography]` was a globbing pattern).
- Fix: Quoted the package names: `pip3 install fastapi uvicorn python-multipart "python-jose[cryptography]" "passlib[bcrypt]" sqlalchemy`.
- Learned: zsh needs quotes around special characters like square brackets. Also learned about pip "extras" (e.g., `[cryptography]`).
- Felt a bit frustrated but it was a quick fix-ready to get FastAPI running

## Reflection
## March 31, 2025 - Pre-Week 1: Setting Up FastAPI Backend
Today I spent a few hours setting up what I needed to start this project. I made sure my tools were installed and updated to their latest versions. I also created my projects github repository and secured my OpenAI API key that I will need later. After accomplishing all that I went ahead and set up my project't folder structure, created a virtual environment in the backend folder, and set up the dependencies I would need for the FastAPI backend. While most of this was easy I did run into a zsh bug while installing the dependencies that I documented above in my ## Bugs and Fixes section. The bug was an easy fix after a bit of research. After fixing the zsh bug, I created `main.py` and ran my FastAPI server with `uvicorn main:app --reload`. and saw that it ran successful with `{"message": "Hello World"}` in my browser at http://127.0.0.1:8000 I also checked out the interactive docs at http://127.0.0.1:8000/docs. Overall I’m feeling more confident about learning FastAPI now, but I’m still a bit nervous about the more complex stuff I’ll be doing in Week 1.

## March 31, 2025 - Pre-Week 1: Learning FastAPI Basics
Added two new endpoints to my FastAPI backend:
- `/items/{item_id}`: Returns the item ID and a name (e.g., `{"item_id": 5, "name": "Item 5"}`).
- `/hello/{name}`: Returns a greeting (e.g., `{"message": "Hello, Michael!"}`).
Learned how to use path parameters (e.g., `{item_id}` and `{name}`) and specify their types (e.g., `item_id: int`, `name: str`). Tested the endpoints in the interactive docs at http://127.0.0.1:8000/docs Overall I found this super easy to use.

## March 31, 2025 - Pre-Week 1: First OpenAI API Call
I made my first OpenAI API call tonight:
- Activated my virtual environment with `source venv/bin/activate` (needed to do this again after closing my terminal).
- Ran my `test_openai.py` script with `python3 test_openai.py`.
- Sent a prompt ("Hello, how are you?") and got a response: "As an artificial intelligence, I don't have feelings, but I'm here and ready to help! How can I assist you today?"
- Learned that my `.env` file setup works (with the `sk-proj-` prefix in the API key), and I can successfully authenticate with the OpenAI API. Also learned how to activate my virtual environment, which I’ll need to do every time I start a new terminal session.
- I felt super excited to see the API respond. It's awesome that ill be using this to process invoices in a few weeks! I’m still a bit nervous about working with PDFs, but im sure ill be able to figure it out.

## March 31, 2025 - Pre-Week 1: Experimenting with OpenAI API
Tried a new prompt in `test_openai.py` to extract data from a fake invoice text:
- Prompt: "Extract the invoice number and total amount from this text: 'Invoice #12345, Date: 2025-03-31, Total: $500.00'"
- Response: "Invoice Number: 12345
             Total Amount: $500.00"
- From this test I learned that the OpenAI API can parse text and extract specific fields, which will be super useful for invoice processing in Week 4.
- After seeing this was successful I am very excited to see how powerful the API is and I’m starting to see how I’ll use it for my project.

## Wednesday's Plan
