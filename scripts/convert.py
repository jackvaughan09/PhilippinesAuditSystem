import subprocess
import sys

if __name__ == "__main__":
    root = sys.argv[1]  # path/to/PhilAuditStorage/Year
    subprocess.run(["python3", "./scripts/generate_metadata.py", root])
    subprocess.run(["python3", "./scripts/generate_images.py", root])
