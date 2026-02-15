import subprocess
import os
import sys
import time
import signal
import webbrowser

def run_services():
    # Define paths
    ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
    BACKEND_DIR = os.path.join(ROOT_DIR, 'backend')
    FRONTEND_DIR = os.path.join(ROOT_DIR, 'frontend')

    print("🚀 Starting TrueWealth AI...")

    # Start Backend
    print("Backend launching on http://localhost:5001...")
    backend_env = os.environ.copy()
    # Add backend directory to PYTHONPATH so 'app' module can be found
    backend_env["PYTHONPATH"] = BACKEND_DIR
    
    backend_process = subprocess.Popen(
        [sys.executable, "-m", "app.main"],
        cwd=BACKEND_DIR,
        env=backend_env,
        shell=False
    )

    # Start Frontend
    print("Frontend launching...")
    # Using 'npm run dev' for local development
    frontend_process = subprocess.Popen(
        ["npm", "run", "dev", "--", "--port", "3000"],
        cwd=FRONTEND_DIR,
        shell=True
    )

    # Wait for services to start
    time.sleep(5)
    
    print("✅ Services are running!")
    print("👉 Frontend: http://localhost:3000")
    print("👉 Backend:  http://localhost:5001")
    
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
        print("\n🛑 Shutting down services...")
        backend_process.terminate()
        # Frontend is shell=True, so termination might be tricky on Windows without taskkill
        if sys.platform == 'win32':
             subprocess.call(['taskkill', '/F', '/T', '/PID', str(frontend_process.pid)])
        else:
             frontend_process.terminate()
        
        sys.exit(0)

if __name__ == "__main__":
    run_services()
