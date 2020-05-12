# Transform LifeLines

The Lifelines transform runs periodically as a cronjob, importing Lifelines data
into Molgenis, except for the *order* and *catolog_users* tables.
It performs the following tasks:

* Download latest Lifelines csv files from a s3 bucket
* Transform csv files to the appropriate Molgenis tsv format
* Zip the transformed data
* Send the zip to Molgenis REST api for import
* Update table permissions through Molgenis REST api

## Development

### Kubernetes

There are 2 Kubernetes namespaces: **lifelines-catalog-test**, **lifelines-catalog-accept**

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

A [Kubernetes cronjob](https://rancher.molgenis.org:7777/p/c-rrz2w:p-dtpjq/workload/cronjob:lifelines-catalog-test:transform)
is setup to run the transform in a container every night.

#### Mirror to Minio server

To test the whole transfrom flow, spin up a Minio client(`minio/mc`) on the cluster.
Open a shell to the pod and fill in *accessKey* and *secretKey* from the Vault and mirror:

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

    mc mirror s3/ll-catalogue-a molgenis/fleur

Mirror Lifelines data to the Lifelines Minio service and port-forward the service
to your local machine. The same can be done with the Molgenis backend:

    kubectl port-forward svc/dev-lifelines-molgenis 8080:8080 --namespace dev-lifelines
    kubectl port-forward svc/backend-lifelines-minio 9000:9000 --namespace backend-lifelines

#### Push to Nexus / Docker.io

Versions are deployed as docker images on Nexus and Docker.io. Nexus is used
for deployment; Docker.io for production. Manually create tagged Docker images
with:

    # Docker.io
    docker build . --tag molgenis/molgenis-py-lifelines-transform:0.45.0
    docker push molgenis/molgenis-py-lifelines-transform:0.45.0
    docker push molgenis/molgenis-py-lifelines-transform:latest

    # Nexus
    docker login registry.molgenis.org
    docker build . --tag registry.molgenis.org/molgenis/lifelines-transform:dev
    docker push registry.molgenis.org/molgenis/lifelines-transform:dev
