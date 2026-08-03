import subprocess
import os
import sys
import time
import signal
import webbrowser
import urllib.request
import urllib.error

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
    print("Checking backend dependencies...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", os.path.join(BACKEND_DIR, 'requirements.txt')], shell=False)
        print("Backend dependencies are ready.")
    except subprocess.CalledProcessError:
        print("Error: Failed to install/verify backend dependencies.")
        sys.exit(1)

def _taskkill(pid):
    subprocess.call(['taskkill', '/F', '/T', '/PID', str(pid)], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

def free_ports(ports):
    """Kill whatever is already listening on these ports so a stale process doesn't block startup"""
    if sys.platform == 'win32':
        try:
            output = subprocess.check_output('netstat -ano -p TCP', shell=True, text=True)
        except subprocess.CalledProcessError:
            return  # nothing listening
        wanted = {f':{p}' for p in ports}
        pids = {line.split()[-1] for line in output.splitlines()
                if 'LISTENING' in line and any(line.split()[1].endswith(suffix) for suffix in wanted)}
        for pid in pids:
            print(f"A port we need is already in use by PID {pid}, stopping it...")
            _taskkill(pid)
    else:
        flags = [flag for p in ports for flag in ('-i', f':{p}')]
        try:
            pids = set(subprocess.check_output(['lsof', '-t', *flags], text=True).split())
        except (subprocess.CalledProcessError, FileNotFoundError):
            return
        for pid in pids:
            print(f"A port we need is already in use by PID {pid}, stopping it...")
            os.kill(int(pid), signal.SIGKILL)

def wait_until_ready(name, url, proc, timeout):
    print(f"Waiting for {name} to become ready...")
    for _ in range(timeout):
        if proc.poll() is not None:
            return False
        try:
            urllib.request.urlopen(url, timeout=1)
            return True
        except (urllib.error.URLError, ConnectionError):
            time.sleep(1)
    return False

def run_services():
    # Define paths
    ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
    BACKEND_DIR = os.path.join(ROOT_DIR, 'backend')
    FRONTEND_DIR = os.path.join(ROOT_DIR, 'frontend')

    print("Starting TrueWealth AI...")

    # Check and install dependencies before launching
    check_dependencies()

    # Clear stale processes so this run doesn't silently fail to bind
    free_ports([5001, 3000])

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

    # Wait for each service to actually accept requests before opening the browser,
    # the backend's ML imports on first startup can take well over 5 seconds
    if not wait_until_ready("backend", "http://localhost:5001/docs", backend_process, timeout=60):
        print("Warning: backend did not respond within 60s, check backend/logs/backend_startup.log")
    if not wait_until_ready("frontend", "http://localhost:3000", frontend_process, timeout=15):
        print("Warning: frontend did not respond within 15s, check backend/logs/frontend_startup.log")

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
             _taskkill(frontend_process.pid)
        else:
             frontend_process.terminate()
        
        sys.exit(0)

if __name__ == "__main__":
    run_services()
