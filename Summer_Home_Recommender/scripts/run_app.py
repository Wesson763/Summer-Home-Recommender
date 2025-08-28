"""
Simple script to run the Streamlit Summer Home Finder app
"""

import subprocess
import sys
import os

def main():
    # Get the directory where this script is located
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Path to the streamlit app
    app_path = os.path.join(script_dir, "..", "app", "main.py")
    
    print("Starting Summer Home Finder...")
    print("Open your browser to: http://localhost:8501")
    print("Press Ctrl+C to stop the application")
    print("-" * 50)
    
    try:
        # Add parent directory to Python path for app package resolution
        parent_dir = os.path.join(script_dir, "..")
        env = os.environ.copy()
        env['PYTHONPATH'] = parent_dir + os.pathsep + env.get('PYTHONPATH', '')
        
        # Run streamlit
        subprocess.run([
            sys.executable, "-m", "streamlit", "run", app_path,
            "--server.port", "8501",
            "--server.address", "localhost"
        ], env=env)
    except KeyboardInterrupt:
        print("\nApplication stopped by user")
    except Exception as e:
        print(f"Error running application: {e}")

if __name__ == "__main__":
    main()
