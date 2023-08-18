# Philippines Audit System

The Philippines Audit System (PAS) is a 3-stage document-data extraction software package developed to study “infraction level” corruption in municipal and city governments. This repo contains all of the production code used in conducting the research, however, `convert` should be unnecessary for replication (more on this below). Raw data (.zip file reports) for the project can be found on the [RoP Commision on Audit website](https://www.coa.gov.ph/reports/annual-audit-reports/aar-local-government-units).

## Table of Contents

- Prerequisites
- Installation
- Use

---

## Prerequisites

PAS is a **Dockerized** application, so you need to download [Docker](https://docs.docker.com/get-started/). Doing this allows us operating system independence and consistent packaging requirements… what truly a wonderful tool!

- Helpful links for doing so:
  - [Official Docker guide](https://docs.docker.com/get-docker/)
  - [Mac install link](https://docs.docker.com/desktop/install/mac-install/)
  - [Windows install link](https://docs.docker.com/desktop/install/windows-install/)
- Download [PhilAuditStorage](https://drive.google.com/drive/folders/1zu_lqh7zdRF4CUtX18iJmJUIAE9DZVkI?usp=drive_link) — public drive where converted, organized data is kept.
  - Take note of the path (where you install it), it will be important later! Eg. `/Users/me/Downloads/philauditstorage`
- Download [Model Weights](https://drive.google.com/file/d/1U6Y3EqmA5PciAt79YlpTReOYkxrsP4ZW/view?usp=drive_link)

## Installation

- Clone Repo

```python
git clone https://github.com/jackvaughan09/PhilippinesAuditSystem.git
```

1. Inside of repo run:

    ```bash
    python3.8 scripts/setup.py path/to/philauditstorage
    ```

    - creates the necessary directory structure inside of `philauditstorage` for all subsequent script executions (uses `mkdir -p` equivalent, i.e. will not overwrite existing directories with the same name)
    - if this is your first time running `setup.py`, it will create and activate a virtual environment before installing the pip dependencies.*
2. Generate metadata for a single year:

    ```bash
    python3.8 scripts/generate_metadata.py path/to/philauditstorage/year
    ```

    - After completing this step, there will be a file titled `20XX_metadata.csv` in the directory `path/to/philauditstorage/Metadata/`

3. PDF to image

    ```bash
    python3.8 scripts/generate_images.py /path/to/philauditstorage/year
    
    # Example
    python3 scripts/generate_images.py /Users/me/Documents/PhilAuditStorage/2015
    ```

4. Create predictions

    ```bash
    python3.8 scripts/sort.py /path/to/philauditstorage/Images/year path/to/weights.ckpt
    
    # Example
    python3 scripts/sort.py /Users/me/Documents/PhilAuditStorage/Images/2015 \
        /Users/me/PhilRepo/weights.ckpt
    ```

5. Manually sort predictions to obtain ground truth labels
6. Map sorted images back to pdfs

    ```bash
    python3.8 scripts/map_images_to_pdfs.py /path/to/philauditstorage/year
    ```

7. Extraction

    ```bash
    python3.8 scripts/extract.py /path/to/philauditstorage/year
    ```
