# Catalog Transform

The catalog transform application runs periodically as a cronjob, importing S3 data
into Molgenis, except for the *order* and *catolog_users* tables.
It performs the following tasks:

* Download latest csv files from a s3 bucket
* Transform csv files to the appropriate Molgenis tsv format
* Zip the transformed data
* Send the zip to Molgenis REST api for import
* Update table permissions through Molgenis REST api

## Usage

Testing this transform requires a Molgenis stack. There is a docker-compose
config in *./docker* that allows this:

```bash
git clone git@github.com:molgenis/molgenis-py-lifelines-transform.git
cd molgenis-py-lifelines-transform/docker
cp config.json.example config.json
docker-compose up molgenis
# wait until Docker is done loading and indexing
# verify http://localhost whether Molgenis is running properly
# from another tab, go into the container:
docker-compose run transform bash
poetry shell
python lifelines_transform/main.py
```

## Development

### Kubernetes cheatsheet

```bash
# Show all running services/pods:
kubectl get pods --namespace lifelines-catalog-test

# Show all cronjobs:
kubectl get cronjobs --namespace lifelines-catalog-test

# Create a manual job to trigger the lifelines-transform script:
kubectl create job manual-transform --from cronjob/transform --namespace lifelines-catalog-test

# Delete it afterwards
kubectl delete job manual-transform --namespace lifelines-catalog-test

# Info about the manual-transform job
kubectl describe job manual-transform --namespace lifelines-catalog-test

# Show the log from the manual cronjob pod:
kubectl logs manual-transform-bs7lx --namespace lifelines-catalog-test

# Create a Kubernetes secret:
kubectl create secret generic transform-config --from-file=config.json --namespace lifelines-catalog-test
```

A [Kubernetes cronjob](https://rancher.molgenis.org:7777/p/c-rrz2w:p-dtpjq/workload/cronjob:lifelines-catalog-test:transform) is setup to run the transform in a
container every night.

### Backup data through Minio

To test the whole data flow, spin up a Minio client(`minio/mc`) on the cluster.
Open a shell to the pod and fill in *accessKey* and *secretKey* from the Vault and mirror:

```bash
# vi ~/.mc/config.json

"version": "9",
"hosts": {
    "molgenis": {
        "url": "http://backend-lifelines-minio.backend-lifelines.svc:9000",
        "accessKey": "molgenis",
        "secretKey": "molgenis",
        "api": "S3v4",
        "lookup": "auto"
    },
    "s3": {
        "url": "https://s3.eu-central-1.amazonaws.com",
        "accessKey": "",
        "secretKey": "",
        "api": "S3v4",
        "region": "eu-central-1",
        "lookup": "dns"
    }
}

mc mirror s3/ll-catalogue-a molgenis/backup
```

Then mirror the S3 bucket to the Kubernetes Minio service and port-forward the
service to your local machine. This allows you to retrieve data from the
Kubernetes Minio service and test the Molgenis upload; e.g.:

```bash
kubectl port-forward svc/dev-lifelines-molgenis 8080:8080 --namespace dev-lifelines
kubectl port-forward svc/backend-lifelines-minio 9000:9000 --namespace backend-lifelines
```

### Push Nexus & Docker.io

Versions are deployed as docker images on Nexus and Docker.io. Nexus is used
for deployment; Docker.io for production. Manually create tagged Docker images
with:

```bash
# Docker.io
docker build . --tag molgenis/molgenis-py-lifelines-transform:0.45.0
docker push molgenis/molgenis-py-lifelines-transform:0.45.0
docker push molgenis/molgenis-py-lifelines-transform:latest

# Nexus
docker login registry.molgenis.org
docker build . --tag registry.molgenis.org/molgenis/lifelines-transform:dev
docker push registry.molgenis.org/molgenis/lifelines-transform:dev
```
