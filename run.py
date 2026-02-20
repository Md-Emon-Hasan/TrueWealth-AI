import subprocess
import os
import sys
import time
import signal
import webbrowser

def check_dependencies():
    ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
    BACKEND_DIR = os.path.join(ROOT_DIR, 'backend')
    FRONTEND_DIR = os.path.join(ROOT_DIR, 'frontend')

    print("Checking dependencies...")

    # Check for Node.js/NPM (required for frontend)
    try:
        subprocess.check_call(["npm", "--version"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, shell=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("Error: npm is not installed or not in PATH. Please install Node.js.")
        sys.exit(1)

    # Check for frontend node_modules
    if not os.path.exists(os.path.join(FRONTEND_DIR, 'node_modules')):
        print("frontend/node_modules not found. Installing frontend dependencies...")
        try:
            subprocess.check_call(["npm", "install"], cwd=FRONTEND_DIR, shell=True)
            print("Frontend dependencies installed successfully.")
        except subprocess.CalledProcessError:
            print("Error: Failed to install frontend dependencies.")
            sys.exit(1)

    # Check for backend dependencies
    # We'll run a quick check by trying to install them. 
    # This is safer for a "just run it" experience.
    print("Checking backend dependencies...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", os.path.join(BACKEND_DIR, 'requirements.txt')], shell=False)
        print("Backend dependencies are ready.")
    except subprocess.CalledProcessError:
        print("Error: Failed to install/verify backend dependencies.")
        sys.exit(1)

def run_services():
    # Define paths
    ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
    BACKEND_DIR = os.path.join(ROOT_DIR, 'backend')
    FRONTEND_DIR = os.path.join(ROOT_DIR, 'frontend')

    print("Starting TrueWealth AI...")

    # Check and install dependencies before launching
    check_dependencies()

    # Ensure logs directory exists inside backend
    LOGS_DIR = os.path.join(BACKEND_DIR, 'logs')
    if not os.path.exists(LOGS_DIR):
        os.makedirs(LOGS_DIR, exist_ok=True)

    backend_log = open(os.path.join(LOGS_DIR, 'backend_startup.log'), 'a')
    frontend_log = open(os.path.join(LOGS_DIR, 'frontend_startup.log'), 'a')

    # Start Backend
    print("Backend launching on http://localhost:5001...")
    backend_env = os.environ.copy()
    # Add backend directory to PYTHONPATH so 'app' module can be found
    backend_env["PYTHONPATH"] = BACKEND_DIR
    
    backend_process = subprocess.Popen(
        [sys.executable, "-m", "app.main"],
        cwd=BACKEND_DIR,
        env=backend_env,
        shell=False,
        stdout=backend_log,
        stderr=backend_log
    )

    # Start Frontend
    print("Frontend launching...")
    # Using 'npm run dev' for local development
    frontend_process = subprocess.Popen(
        ["npm", "run", "dev", "--", "--port", "3000"],
        cwd=FRONTEND_DIR,
        shell=True,
        stdout=frontend_log,
        stderr=frontend_log
    )

    # Wait for services to start
    time.sleep(5)
    
    print("Services are running!")
    print(f"Frontend: http://localhost:3000 (Logs: {os.path.join('backend', 'logs', 'frontend_startup.log')})")
    print(f"Backend:  http://localhost:5001 (Logs: {os.path.join('backend', 'logs', 'backend_startup.log')})")
    
    webbrowser.open("http://localhost:3000")

    try:
        while True:
            time.sleep(1)
            if backend_process.poll() is not None:
                print("Backend process ended unexpectedly.")
                break
            if frontend_process.poll() is not None:
                print("Frontend process ended unexpectedly.")
                break
    except KeyboardInterrupt:
        print("\n Shutting down services...")
        backend_process.terminate()
        # Frontend is shell=True, so termination might be tricky on Windows without taskkill
        if sys.platform == 'win32':
             subprocess.call(['taskkill', '/F', '/T', '/PID', str(frontend_process.pid)])
        else:
             frontend_process.terminate()
        
        sys.exit(0)

if __name__ == "__main__":
    run_services()
