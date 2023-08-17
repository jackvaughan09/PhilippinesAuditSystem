import logging
import os
import subprocess
import sys

logging.basicConfig(level=logging.WARNING)

# Get the path to the directory from the command line argument
phil_dir = os.path.abspath(os.sys.argv[1])

# Create the Images directory
os.makedirs(os.path.join(phil_dir, "Images"), exist_ok=True)

# Create the Extracted Directory
os.makedirs(os.path.join(phil_dir, "Extracted"), exist_ok=True)

# Create the Metadata directory
os.makedirs(os.path.join(phil_dir, "Metadata"), exist_ok=True)

# Create the year directories in Extracted
for year in range(2011, 2021):
    os.makedirs(os.path.join(phil_dir, "Extracted", str(year)), exist_ok=True)
    os.makedirs(
        os.path.join(phil_dir, "Extracted", str(year), "Complete"), exist_ok=True
    )
    os.makedirs(os.path.join(phil_dir, "Extracted", str(year), "Errors"), exist_ok=True)
    os.makedirs(
        os.path.join(phil_dir, "Extracted", str(year), "Errors", "Image_pdfs"),
        exist_ok=True,
    )
    os.makedirs(
        os.path.join(phil_dir, "Extracted", str(year), "Errors", "No_lattice"),
        exist_ok=True,
    )
    os.makedirs(
        os.path.join(phil_dir, "Extracted", str(year), "Errors", "Pageless"),
        exist_ok=True,
    )

# Create the year directories in Images
for year in range(2011, 2021):
    os.makedirs(os.path.join(phil_dir, "Images", str(year)), exist_ok=True)
    os.makedirs(os.path.join(phil_dir, "Images", str(year), "All"), exist_ok=True)
    os.makedirs(os.path.join(phil_dir, "Images", str(year), "Exclude"), exist_ok=True)
    os.makedirs(os.path.join(phil_dir, "Images", str(year), "Include"), exist_ok=True)
    os.makedirs(
        os.path.join(phil_dir, "Images", str(year), "False_positive"), exist_ok=True
    )
    os.makedirs(
        os.path.join(phil_dir, "Images", str(year), "False_negative"), exist_ok=True
    )

if not os.path.exists("./.venv"):
    # Create virtual environment
    subprocess.run(["python3", "-m", "venv", "./.venv"])

    # activate the virtual environment
    if sys.platform == "darwin":
        subprocess.run([".venv\\Scripts\\activate.bat"])
    elif sys.platform == "linux":
        subprocess.run(["source", ".venv/bin/activate"])
    elif "win" in sys.platform:
        subprocess.run([".venv\\Scripts\\activate.bat"])
    else:
        logging.error("OS not supported")
        sys.exit(1)

    # Install the requirements
    subprocess.run(["pip", "install", "-r", "requirements.txt"])

    # Install philaudit package
    subprocess.run(["pip", "install", "-e", "./philaudit/dist/philaudit-0.1.0.tar.gz"])
