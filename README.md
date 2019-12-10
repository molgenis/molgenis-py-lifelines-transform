# Transform LifeLines data

# Get source data
Source data will come from some s3 service.
Right now, get the download link and unzip the file.
The password is in the vault.
N.B. The variables csv has been updated by Trynke to add labels and fix names.

# Transform
It's probably easiest to create a virtualenv to run python.
```
python3 -m virtualenv env
```
This installs python into the `env` subdir.

```
source env/bin/activate
pip install .
```
This retrieves dependencies.

Now to run the transformation:
```
mkdir output
python scripts/transform.py
```

# Upload
To upload the data, zip the contents of the output directory.
Create a lifelines group if you haven't already and import the zipfile.

# Download
To download data+metadata from dev server:
```
 java -jar downloader-1.2.0.jar -o -f lifelines.zip -a admin -u https://backend-lifelines.test.molgenis.org/ -s 10000 lifelines_age_group lifelines_assessment lifelines_gender_group lifelines_section lifelines_sub_section lifelines_subsection_variable lifelines_tree lifelines_variable lifelines_variant lifelines_who_when lifelines_who
```

# issues
* age group indicators can all be null
* variable label can be longer than 255 characters
* what_when contains duplicates (but we dedupe them)
* a couple of subsections (17 and up) are listed as sections in the tree
* some of the who_when is not listed in the who

