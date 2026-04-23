# main.py
import subprocess
import sys

# This allows you to run 'python main.py' locally to start streamlit
if __name__ == "__main__":
    subprocess.run(["streamlit", "run", "app.py"])