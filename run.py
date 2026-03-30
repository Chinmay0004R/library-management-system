#!/usr/bin/env python
"""
Library Management System - Run Script
This script sets up the environment and runs the Flask application.
"""

import os
import sys
import subprocess
import platform

def main():
    # Get the directory of this script
    base_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(base_dir)
    
    # Virtual environment path
    venv_dir = os.path.join(base_dir, 'venv')
    
    # Determine Python executable path in venv
    if platform.system() == 'Windows':
        python_exe = os.path.join(venv_dir, 'Scripts', 'python.exe')
        activate_script = os.path.join(venv_dir, 'Scripts', 'activate.bat')
    else:
        python_exe = os.path.join(venv_dir, 'bin', 'python')
        activate_script = os.path.join(venv_dir, 'bin', 'activate')
    
    # Create virtual environment if it doesn't exist
    if not os.path.exists(venv_dir):
        print("Creating virtual environment...")
        subprocess.run([sys.executable, '-m', 'venv', venv_dir], check=True)
    
    # Install requirements
    print("Installing dependencies...")
    req_file = os.path.join(base_dir, 'requirements.txt')
    subprocess.run([python_exe, '-m', 'pip', 'install', '-r', req_file, '--quiet'], check=True)
    
    # Run the Flask app
    print("\n" + "="*60)
    print("Starting Library Management System")
    print("="*60)
    print("\nFlask app running on http://127.0.0.1:5000")
    print("Press CTRL+C to stop the server\n")
    
    app_file = os.path.join(base_dir, 'app.py')
    subprocess.run([python_exe, app_file])

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nServer stopped.")
        sys.exit(0)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)
