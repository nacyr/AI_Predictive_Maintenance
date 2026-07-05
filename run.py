import os
import subprocess

project_root = os.path.dirname(os.path.abspath(__file__))

subprocess.run(
    [
        "streamlit",
        "run",
        "app/dashboard.py"
    ],
    cwd=project_root
)