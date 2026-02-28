import subprocess
import os
import sys
import time
import webbrowser

root = os.path.dirname(os.path.abspath(__file__))
backend = os.path.join(root, 'backend')
frontend = os.path.join(root, 'frontend')
venv_path = os.path.join(backend, '.venv')

if sys.platform == "win32":
    venv_python = os.path.join(venv_path, "Scripts", "python.exe")
else:
    venv_python = os.path.join(venv_path, "bin", "python")


def setup():
    print("--- Setting up TrueWealth AI ---")
    
    # Create venv if not exists
    if not os.path.exists(venv_path):
        print("Creating virtual environment...")
        subprocess.check_call([sys.executable, "-m", "venv", venv_path])
    
    # Backend deps
    print("Installing backend dependencies...")
    subprocess.check_call([venv_python, "-m", "pip", "install", "-r", os.path.join(backend, "requirements.txt")])
    
    # Frontend deps
    if not os.path.exists(os.path.join(frontend, "node_modules")):
        print("Installing frontend dependencies...")
        subprocess.check_call(["npm", "install"], cwd=frontend, shell=True)


def run():
    setup()
    
    log_dir = os.path.join(backend, "logs")
    os.makedirs(log_dir, exist_ok=True)
    
    # Launch backend & frontend
    print("Launching services...")
    b_log = open(os.path.join(log_dir, "backend.log"), "a")
    f_log = open(os.path.join(log_dir, "frontend.log"), "a")
    
    env = os.environ.copy()
    env["PYTHONPATH"] = backend
    
    procs = [
        subprocess.Popen([venv_python, "-m", "app.main"], cwd=backend, env=env, stdout=b_log, stderr=b_log),
        subprocess.Popen(["npm", "run", "dev", "--", "--port", "3000"], cwd=frontend, shell=True, stdout=f_log, stderr=f_log)
    ]

    
    time.sleep(3)
    webbrowser.open("http://localhost:3000")
    print(f"Running! \nLocal: http://localhost:3000\nAPI:   http://localhost:5001\nPress Ctrl+C to stop.")

    try:
        while all(p.poll() is None for p in procs):
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nStopping...")
        for p in procs:
            if sys.platform == "win32":
                subprocess.call(["taskkill", "/F", "/T", "/PID", str(p.pid)], stdout=subprocess.DEVNULL)
            else:
                p.terminate()

if __name__ == "__main__":
    run()

