# **phil**

> A dockerized environment, document convervsion system, and automated scraping tool for extracting policy audit text data from .doc/.docx & .pdf files 

## **INSTALLATION**

### For Windows Users

1. You'll need to start out by downloading git bash <https://git-scm.com/downloads>

2. Then ensure that you have WSL 2 on your machine.

   1. Check to see if you have it:

```powershell
# run this in powershell
wsl -l -v 

#output
NAME        STATE        VERSION
something   something       2 
```

   2. If this is not what you see, then you'll need to either upgrade or install wsl

      - If the wsl command failed, simply run  ```wsl --install```  in administrator powershell
  
      - If it didn't fail, but you have version 1, you'll need to upgrade.
        - **Start at step 3:** <https://learn.microsoft.com/en-us/windows/wsl/install-manual#step-4---download-the-linux-kernel-update-package>

## For Everyone

### 1. Install Docker

- <https://docs.docker.com/get-docker/>

### 2. Clone phil git repo

- in Git Bash (Windows) or your system terminal, run:
  > ```git clone https://www.github.com/hudnash/phil.git```
- if your system doesn't have bash (Very likely if you're on Windows), get Git Bash, install it
  - <https://git-scm.com/downloads>

### 3. Create a ```data/zip``` folder in your ```phil``` directory

- You can do this easily by running the following command while in the phil directory

```bash
mkdir data/zip
```

### 4. Add some zip files from the audit website to the 'zip' folder, you can find them here

[Phillipines Audit Website](
<https://www.coa.gov.ph/reports/annual-audit-reports/aar-local-government-units/#167-428-leyte>)

### 5. Run a matching version of phil.sh

- If you have an Intel or AMD processor run

```Bash/GitBash
sh x64phil.sh
```

- If you have an Apple Silicon chip or otherwise have an arm64 CPU, run

```Bash
sh arm64phil.sh
```
