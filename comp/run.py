import os
import subprocess
import sys

def main():
    print("Starting Memory Architecture Simulator...")
    # Get the directory of this script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    app_path = os.path.join(script_dir, "ui", "app.py")
    
    # Run streamlit
    subprocess.run([sys.executable, "-m", "streamlit", "run", app_path])

if __name__ == "__main__":
    main()
