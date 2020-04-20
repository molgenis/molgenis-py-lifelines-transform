# Transform LifeLines

This `lifelines-transform` Python package automates the (re)import of Lifelines data into Molgenis,
except for the *order* and *catolog_users* tables. It performs the following tasks:

* Download latest Lifelines csv files from a s3 bucket
* Transform csv files to the appropriate Molgenis tsv format
* Zip the transformed data
* Data is imported by uploading the zip file through the Molgenis REST API
* Table permissions are updated through Molgenis REST api

A [Kubernetes cronjob](https://rancher.molgenis.org:7777/p/c-rrz2w:p-dtpjq/workload/cronjob:dev-lifelines:lifelines-transform) is setup to run this script in a container every night.

## Usage

    # Show all running services/pods:
    kubectl get pods --namespace dev-lifelines

    # Show all cronjobs:
    kubectl get cronjobs --namespace dev-lifelines

    # Create a manual job to trigger the lifelines-transform script:
    kubectl create job manual-transform --from cronjob/lifelines-transform --namespace dev-lifelines

    # Delete it afterwards
    kubectl delete job manual-transform --namespace dev-lifelines

    # Info about the manual-transform job
    kubectl describe job manual-transform --namespace dev-lifelines

    # Show the log from the manual cronjob pod:
    kubectl logs manual-transform-bs7lx --namespace dev-lifelines

    # Create a Kubernetes secret:
    kubectl create secret generic transform-config --from-file=config.json --namespace dev-lifelines


# Development
Please note that the Lifelines s3 bucket only whitelists access from the Kubernetes cluster
and that the Molgenis upload only works without basic authentication in front. To test the
whole transfrom flow, you can spin up a Minio client(`minio/mc`) on the cluster.
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

 mirror Lifelines data to the Lifelines Minio service and port-forward the service to your local machine. The same can be done with the Molgenis backend:

    kubectl port-forward svc/dev-lifelines-molgenis 8080:8080 --namespace dev-lifelines
    kubectl port-forward svc/backend-lifelines-minio 9000:9000 --namespace backend-lifelines

To test the Lifelines S3 bucket download itself, last-minute debugging is to create a new pod (i.e. `ubuntu:eoan`), install some basic tooling, generate a ssh-key, add it your github account and checkout/run the project from there. Installation should be straightfoward.

You can manually create tagged Docker images and push them to the Nexus registry, and run it as pod on the cluster:

    # Password is in the fault
    docker login registry.molgenis.org
    docker build . --tag registry.molgenis.org/molgenis/lifelines-transform:dev
    docker push registry.molgenis.org/molgenis/lifelines-transform:dev
