import os
import sys
import io

# 1. SET ENVIRONMENT VARIABLE FIRST (Before any Django imports)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'todo.settings')

# 2. Setup PyInstaller Bundle Directory
if getattr(sys, 'frozen', False):
    BASE_DIR = sys._MEIPASS
else:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

sys.path.insert(0, BASE_DIR)

# 3. Redirect stdout/stderr to prevent windowed mode crashes
if sys.stdout is None:
    sys.stdout = io.StringIO()
if sys.stderr is None:
    sys.stderr = io.StringIO()

# 4. Direct SQLite Database Path to AppData
app_data = os.path.join(os.environ.get('LOCALAPPDATA', os.path.expanduser('~')), 'TaskFlow')
os.makedirs(app_data, exist_ok=True)
os.environ['TASKFLOW_DB_PATH'] = os.path.join(app_data, 'db.sqlite3')

# NOW you can safely import Django modules and WSGI
import django
from django.core.management import call_command
from django.core.wsgi import get_wsgi_application
from waitress import serve
import time
import socket
import webbrowser
from threading import Thread

def wait_for_server(host='127.0.0.1', port=8000, timeout=10):
    """Continuously pings the port until Waitress is live and accepting connections."""
    start_time = time.time()
    while time.time() - start_time < timeout:
        try:
            with socket.create_connection((host, port), timeout=0.5):
                return True
        except (OSError, ConnectionRefusedError):
            time.sleep(0.2)
    return False

def launch_browser():
    """Waits for the server to spin up, then opens the default browser."""
    if wait_for_server():
        webbrowser.open('http://127.0.0.1:8000/')
    else:
        print("Server took too long to start.")

if __name__ == '__main__':
    # ... your django setup & migrations ...

    # Start browser thread that waits for the server safely
    Thread(target=launch_browser, daemon=True).start()

    # Serve application via Waitress (blocks main thread)
    application = get_wsgi_application()
    serve(application, host='127.0.0.1', port=8000, _quiet=True)