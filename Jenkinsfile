pipeline {
    agent {
        kubernetes {
            label 'python-stretch'
        }
    }
    environment {
        REPOSITORY = 'molgenis/molgenis-py-lifelines-transform'
        LOCAL_REPOSITORY = "${LOCAL_REGISTRY}/molgenis/lifelines-transform"
    }
    stages {
        stage('Prepare') {
            steps {
                script {
                    env.GIT_COMMIT = sh(script: 'git rev-parse HEAD', returnStdout: true).trim()
                }
                container('vault') {
                    script {
                        env.GITHUB_TOKEN = sh(script: 'vault read -field=value secret/ops/token/github', returnStdout: true)
                        env.NEXUS_AUTH = sh(script: 'vault read -field=base64 secret/ops/account/nexus', returnStdout: true)
                        env.DOCKERHUB_AUTH = sh(script: "vault read -field=value secret/gcc/token/dockerhub", returnStdout: true)
                        env.SONAR_TOKEN = sh(script: 'vault read -field=value secret/ops/token/sonar', returnStdout: true)
                    }
                }
                sh "git remote set-url origin https://${GITHUB_TOKEN}@github.com/${REPOSITORY}.git"
                sh "git fetch --tags"

                container('python') {
                    script {
                        sh "pip install poetry"
                        sh "poetry install -n"
                        sh "poetry run flake8"
                    }
                }
            }
        }
        stage('Build: [ pull request ]') {
            when {
                changeRequest()
            }
            steps {
                container('sonar') {
                    sh "sonar-scanner -Dsonar.github.oauth=${env.GITHUB_TOKEN} -Dsonar.pullrequest.base=${CHANGE_TARGET} -Dsonar.pullrequest.branch=${BRANCH_NAME} -Dsonar.pullrequest.key=${env.CHANGE_ID} -Dsonar.pullrequest.provider=GitHub -Dsonar.pullrequest.github.repository=molgenis/molgenis-py-consensus"
                }
            }
        }
        stage('Build container running the job [ PR ]') {
            when {
                changeRequest()
            }
            environment {
                TAG = "PR-${CHANGE_ID}-${BUILD_NUMBER}"
                DOCKER_CONFIG="/root/.docker"
            }
            steps {
                container (name: 'kaniko', shell: '/busybox/sh') {
                    sh "#!/busybox/sh\nmkdir -p ${DOCKER_CONFIG}"
                    sh "#!/busybox/sh\necho '{\"auths\": {\"registry.molgenis.org\": {\"auth\": \"${NEXUS_AUTH}\"}}}' > ${DOCKER_CONFIG}/config.json"
                    sh "#!/busybox/sh\n/kaniko/executor --context ${WORKSPACE} --destination ${LOCAL_REPOSITORY}:${TAG}"
                }
            }
        }
        stage('Release: [ master ]') {
            when {
                allOf {
                    branch 'master'
                    not {
                        changelog '.*\\[skip ci\\]$'
                    }
                }
            }
            steps {
                milestone 1
                container('sonar') {
                    sh "sonar-scanner"
                }
                container('python') {
                    sh "poetry run cz bump --yes"
                    script {
                        env.TAG = sh(script: 'poetry run version', returnStdout: true)
                    }
                }
            }
        }
        stage('Build container running the job [ master ]') {
            when {
                branch 'master'
            }
            environment {
                DOCKER_CONFIG="/root/.docker"
            }
            steps {
                container('python') {
                    script {
                        env.TAG = sh(script: 'poetry run version', returnStdout: true)
                    }
                }
                container (name: 'kaniko', shell: '/busybox/sh') {
                    sh "#!/busybox/sh\nmkdir -p ${DOCKER_CONFIG}"
                    sh "#!/busybox/sh\necho '{\"auths\": {\"https://index.docker.io/v1/\": {\"auth\": \"${DOCKERHUB_AUTH}\"}}}' > ${DOCKER_CONFIG}/config.json"
                    sh "#!/busybox/sh\n/kaniko/executor --context ${WORKSPACE} --destination ${REPOSITORY}:${TAG}"
                    sh "#!/busybox/sh\n/kaniko/executor --context ${WORKSPACE} --destination ${REPOSITORY}:latest"
                }
            }
        }
    }
}