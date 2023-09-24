# Flow

Date Created: August 3, 2023 11:50 PM
Status: To Do

# Philippines Audit System

The Philippines Audit System (PAS) is a 3-stage document-data extraction software package developed to study “infraction-level” corruption in provincial, municipal, and city governments. This repo contains all of the production code used to engineer the target dataset. The `convert` module, however, should be unnecessary for replication.

Raw data (.zip file reports) for the project can be found on the [Republic of Philippines Commision on Audit website](https://www.coa.gov.ph/reports/annual-audit-reports/aar-local-government-units), but we recommend using the `PhilAuditStorage` drive link found in the Prerequisites section to obtain the PDF-converted data in an organized file structure.

## Table of Contents

- Background
- Prerequisites
- Installation
- Use
- FAQ

---

## Prerequisites:

- Download [PhilAuditStorage](https://drive.google.com/drive/folders/1zu_lqh7zdRF4CUtX18iJmJUIAE9DZVkI?usp=drive_link) — public drive where converted, organized data is kept.
    - Take note of the path (where you install it), it will be important later! Eg. `/Users/me/Downloads/philauditstorage`
- Download [Model Weights](https://drive.google.com/file/d/1U6Y3EqmA5PciAt79YlpTReOYkxrsP4ZW/view?usp=drive_link)
- As much local device space as you can afford. **Each year will require ~50GBs on their intial runs,** though that size *can be cut in half* after running model predictions and clearing the `/Image/year/All` folders.

---

## Installation

- Clone Repo

```python
git clone https://github.com/jackvaughan09/PhilippinesAuditSystem.git
```

1. Inside of repo run:
    
    ```bash
    python3 scripts/setup.py path/to/philauditstorage
    ```
    
    - creates the necessary directory structure inside of `philauditstorage` for all subsequent script executions (uses `mkdir -p` equivalent, i.e. will not overwrite existing directories with the same name)
    - if this is your first time running `setup.py`, it will create and activate a virtual environment before installing the pip dependencies.

`Setup.py` is designed such that subsequent runs will not overwrite the created directory paths (unless deleted) or the virtual environment, so you can run this whenever you need without worry.

---

## Use

1. Generate metadata for a single year:
    
    ```bash
    python3 scripts/generate_metadata.py path/to/philauditstorage/year
    
    # Example
    python3 scripts/generate_metadata.py /Users/me/Documents/PhilAuditStorage/2015
    ```
    
    - After completing this step, there will be a file titled `20XX_metadata.csv` in the directory `path/to/philauditstorage/Metadata/`
    
    > The metadata files are *critical* for the operation of the software package and should not be edited manually unless you know exactly what you’re doing.
    > 
2. PDF to image
    
    ```bash
    python3 scripts/generate_images.py /path/to/philauditstorage/year
    
    # Example
    python3 scripts/generate_images.py /Users/me/Documents/PhilAuditStorage/2015
    ```
    
    > Be prepared with a significant amount of storage on your local device before attempting the PDF to image conversion for a year. There will be upwards of 50,000 `.png` images created! (~30GB)
    > 
3. Create predictions
    - Rather than using the usual `/path/to/pas/year` path as we’ve been doing, we’ll actually be using the `/path/to/pas/Images/year` directory created during `setup.py`
    - You’ll also need the path to the model weights downloaded [above.](https://drive.google.com/file/d/1U6Y3EqmA5PciAt79YlpTReOYkxrsP4ZW/view?usp=drive_link)
    
    ```bash
    python3 scripts/sort.py /path/to/philauditstorage/Images/year path/to/weights.ckpt
    
    # Example
    python3 scripts/sort.py /Users/me/Documents/PhilAuditStorage/Images/2015 \
        /Users/me/PhilRepo/weights.ckpt
    ```
    
    > During this step, images are **COPIED** from the `Images/year/All` folder into `Images/year/Include` or `Images/year/Exclude` based on the detection model predictions. We stress the *copying* because, again, this requires a significant amount of local device storage.
    > 
4. Manually sort predictions to obtain ground truth labels
    
    
5. Map sorted images back to pdfs
    
    ```bash
    python3.8 scripts/map_images_to_pdfs.py /path/to/philauditstorage/year
    ```
    
6.  Extraction
    
    ```bash
    python3.8 scripts/extract.py /path/to/philauditstorage/year
    ```