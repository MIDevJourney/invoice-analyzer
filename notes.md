## Bugs and Fixes:

## March 31, 2025 - Pre-Week 1: Setting Up FastAPI Backend
Ran into a bug while installing FastAPI dependencies:
- Command: `pip3 install fastapi uvicorn python-multipart python-jose[cryptography] passlib[bcrypt] sqlalchemy`
- Error: `zsh: no matches found: python-jose[cryptography]` (zsh thought `[cryptography]` was a globbing pattern).
- Fix: Quoted the package names: `pip3 install fastapi uvicorn python-multipart "python-jose[cryptography]" "passlib[bcrypt]" sqlalchemy`.
- Learned: zsh needs quotes around special characters like square brackets. Also learned about pip "extras" (e.g., `[cryptography]`).
- Felt a bit frustrated but it was a quick fix-ready to get FastAPI running


## Wednesday's Plan
