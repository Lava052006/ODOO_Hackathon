#!/usr/bin/env python3
"""
ARIA One-Click Startup & Teammate Setup Script
Automatically configures PostgreSQL, migrations, database seeding, dependencies,
and launches both backend & frontend servers.
"""

import os
import sys
import time
import socket
import shutil
import subprocess
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent
BACKEND_DIR = ROOT_DIR / "backend"
FRONTEND_DIR = ROOT_DIR / "frontend"
PGDATA_DIR = BACKEND_DIR / "pgdata"

IS_WINDOWS = sys.platform.startswith("win")

def print_step(title):
    print(f"\n\033[1;34m==>\033[0m \033[1m{title}\033[0m")

def print_success(msg):
    print(f"\033[1;32m✓\033[0m {msg}")

def print_warning(msg):
    print(f"\033[1;33m!\033[0m {msg}")

def print_error(msg):
    print(f"\033[1;31m✗\033[0m {msg}")

def is_port_in_use(port, host="127.0.0.1"):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(1.0)
        return s.connect_ex((host, port)) == 0

def find_postgres_binaries():
    search_paths = [
        Path(r"I:\Program Files\PostgreSQL\18\bin"),
        Path(r"C:\Program Files\PostgreSQL\18\bin"),
        Path(r"C:\Program Files\PostgreSQL\17\bin"),
        Path(r"C:\Program Files\PostgreSQL\16\bin"),
        Path(r"C:\Program Files\PostgreSQL\15\bin"),
        Path(r"C:\Program Files\PostgreSQL\14\bin"),
    ]
    for p in search_paths:
        if (p / "postgres.exe").exists():
            return p

    # Check PATH
    pg_path = shutil.which("postgres") or shutil.which("postgres.exe")
    if pg_path:
        return Path(pg_path).parent

    return None

def setup_postgresql():
    print_step("Step 1: Checking PostgreSQL Database Service")

    if is_port_in_use(5432):
        print_success("PostgreSQL is already running and listening on port 5432.")
        return None

    pg_bin = find_postgres_binaries()
    if not pg_bin:
        print_warning("PostgreSQL binary not found in standard paths. Assuming external service.")
        return None

    initdb_exe = pg_bin / ("initdb.exe" if IS_WINDOWS else "initdb")
    postgres_exe = pg_bin / ("postgres.exe" if IS_WINDOWS else "postgres")

    if not PGDATA_DIR.exists():
        print(f"Initializing local cluster at {PGDATA_DIR}...")
        init_cmd = [str(initdb_exe), "-D", str(PGDATA_DIR), "-U", "postgres", "-A", "trust", "-E", "UTF8"]
        subprocess.run(init_cmd, check=True)
        print_success("Cluster initialized.")

    print("Starting PostgreSQL server...")
    pg_proc = subprocess.Popen(
        [str(postgres_exe), "-D", str(PGDATA_DIR)],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        creationflags=subprocess.CREATE_NEW_PROCESS_GROUP if IS_WINDOWS else 0
    )

    # Wait for port 5432 to open
    for _ in range(15):
        if is_port_in_use(5432):
            print_success("PostgreSQL server started successfully on port 5432.")
            return pg_proc
        time.sleep(1)

    print_warning("PostgreSQL started in background.")
    return pg_proc

def get_venv_python():
    if IS_WINDOWS:
        return BACKEND_DIR / ".venv" / "Scripts" / "python.exe"
    return BACKEND_DIR / ".venv" / "bin" / "python"

def setup_backend_env():
    print_step("Step 2: Checking Backend Python Environment")
    venv_py = get_venv_python()
    
    if not venv_py.exists():
        print("Creating virtual environment in backend/.venv...")
        subprocess.run([sys.executable, "-m", "venv", str(BACKEND_DIR / ".venv")], check=True)
        print_success("Virtual environment created.")

    req_file = BACKEND_DIR / "requirements.txt"
    if req_file.exists():
        print("Installing / updating dependencies from requirements.txt...")
        subprocess.run([str(venv_py), "-m", "pip", "install", "-q", "-r", str(req_file)], check=True)
        print_success("Python dependencies verified.")

    return venv_py

def setup_database_schema(venv_py):
    print_step("Step 3: Preparing Database Schema & Seeding")

    # Create aria_db if not exists using psycopg in venv
    create_db_script = """
import psycopg
try:
    with psycopg.connect('host=127.0.0.1 port=5432 user=postgres dbname=postgres', autocommit=True) as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT 1 FROM pg_database WHERE datname = 'aria_db'")
            if not cur.fetchone():
                cur.execute("CREATE DATABASE aria_db")
                print("Created database aria_db")
            else:
                print("Database aria_db exists")
except Exception as e:
    print(f"DB check note: {e}")
"""
    subprocess.run([str(venv_py), "-c", create_db_script], cwd=str(BACKEND_DIR))

    # Run migrations
    print("Applying database migrations...")
    subprocess.run([str(venv_py), "manage.py", "migrate"], cwd=str(BACKEND_DIR), check=True)
    print_success("Migrations applied.")

    # Check if seeded
    check_seed_script = """
import os, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()
from apps.accounts.models import User
count = User.objects.filter(role='employee').count()
print(f"USER_COUNT:{count}")
"""
    res = subprocess.run(
        [str(venv_py), "-c", check_seed_script],
        cwd=str(BACKEND_DIR),
        capture_output=True,
        text=True
    )
    
    user_count = 0
    for line in res.stdout.splitlines():
        if line.startswith("USER_COUNT:"):
            try:
                user_count = int(line.split(":")[1])
            except ValueError:
                pass

    if user_count < 10:
        print("Seeding database with 120 employees and dynamic records...")
        subprocess.run([str(venv_py), "manage.py", "seed_data"], cwd=str(BACKEND_DIR), check=True)
        print_success("Database seeded with full dataset.")
    else:
        print_success(f"Database already contains {user_count} employees.")

def setup_frontend():
    print_step("Step 4: Checking Frontend Dependencies")
    node_modules = FRONTEND_DIR / "node_modules"
    
    pm = "pnpm" if shutil.which("pnpm") else "npm"
    if not node_modules.exists():
        print(f"Installing frontend dependencies with {pm}...")
        cmd = [f"{pm}.cmd" if IS_WINDOWS else pm, "install"]
        subprocess.run(cmd, cwd=str(FRONTEND_DIR), check=True)
        print_success("Frontend dependencies installed.")
    else:
        print_success("Frontend dependencies ready.")
    return pm

def main():
    print("""
\033[1;36m=======================================================
   ARIA Workday Command Centre — Startup Assistant
=======================================================\033[0m""")

    pg_proc = setup_postgresql()
    venv_py = setup_backend_env()
    setup_database_schema(venv_py)
    pm = setup_frontend()

    print_step("Step 5: Starting Backend & Frontend Servers")

    # Start Django Backend
    backend_cmd = [str(venv_py), "manage.py", "runserver", "127.0.0.1:8000"]
    backend_proc = subprocess.Popen(backend_cmd, cwd=str(BACKEND_DIR))
    print_success("Django Backend running on http://127.0.0.1:8000/")

    # Start Frontend
    frontend_cmd = [f"{pm}.cmd" if IS_WINDOWS else pm, "run", "dev"]
    frontend_proc = subprocess.Popen(frontend_cmd, cwd=str(FRONTEND_DIR))
    print_success("Frontend Dev Server starting...")

    print(f"""
\033[1;32m=======================================================
   ARIA is live and ready!
=======================================================
\033[0m
   \033[1mFrontend:\033[0m  http://localhost:5173/ (or port shown below)
   \033[1mBackend API:\033[0m http://127.0.0.1:8000/api/

   \033[1mDemo Accounts:\033[0m
   • HR Admin:  admin@aria.com    (Password: Aria@2026)
   • Employee:  employee@aria.com (Password: Aria@2026)

   Press \033[1mCtrl+C\033[0m to stop all services cleanly.
=======================================================
""")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nStopping ARIA services...")
        backend_proc.terminate()
        frontend_proc.terminate()
        if pg_proc:
            pg_proc.terminate()
        print_success("All services stopped.")

if __name__ == "__main__":
    main()
