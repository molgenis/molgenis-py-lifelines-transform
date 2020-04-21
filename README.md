# Transform LifeLines

This `lifelines-transform` Python package automates the (re)import of Lifelines
data into Molgenis, except for the *order* and *catolog_users* tables.
It performs the following tasks:

* Download latest Lifelines csv files from a s3 bucket
* Transform csv files to the appropriate Molgenis tsv format
* Zip the transformed data
* Send the zip to Molgenis REST api for import
* Update table permissions through Molgenis REST api

## Development

### Kubernetes

There are 2 Kubernetes namespaces: **lifelines-test**, **lifelines-accept**

    # Show all running services/pods:
    kubectl get pods --namespace lifelines-test

    # Show all cronjobs:
    kubectl get cronjobs --namespace lifelines-test

    # Create a manual job to trigger the lifelines-transform script:
    kubectl create job manual-transform --from cronjob/lifelines-transform --namespace lifelines-test

    # Delete it afterwards
    kubectl delete job manual-transform --namespace lifelines-test

    # Info about the manual-transform job
    kubectl describe job manual-transform --namespace lifelines-test

    # Show the log from the manual cronjob pod:
    kubectl logs manual-transform-bs7lx --namespace lifelines-test

    # Create a Kubernetes secret:
    kubectl create secret generic transform-config --from-file=config.json --namespace lifelines-test

A [Kubernetes cronjob](https://rancher.molgenis.org:7777/p/c-rrz2w:p-dtpjq/workload/cronjob:lifelines-catalog-test:transform) is setup to run the transform in a container
every night.

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

#### Manually push to Nexus

You can manually create tagged Docker images and push them to the Nexus registry,
and run it as pod on the cluster:

    # Password is in the fault
    docker login registry.molgenis.org
    docker build . --tag registry.molgenis.org/molgenis/lifelines-transform:dev
    docker push registry.molgenis.org/molgenis/lifelines-transform:dev
