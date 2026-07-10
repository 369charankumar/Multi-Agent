"""
Run: python start.py
Installs dependencies (if needed) then launches the FastAPI server.
"""
import subprocess, sys, os

def install():
    subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt", "-q"])

if __name__ == "__main__":
    install()
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
