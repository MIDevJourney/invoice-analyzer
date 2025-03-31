Bugs and Fixes:

Bug1:
When installing the dependencies for my FastAPI backend I entered the following command into the terminal pip3 install fastapi uvicorn python-multipart python-jose[cryptography] passlib[bcrypt] sqlalchemy
which caused the error zsh: no matches found: python-jose[cryptography]. 

Solution:
After some research I found this error was due to zsh misinterpriting the square brackets as a globbing pattern so to fix this I placed quotes around the package names.



Wednesday's Plan
