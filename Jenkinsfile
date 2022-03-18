pipeline {
    agent {
        kubernetes {
            // the shared pod template defined on the Jenkins server config
            inheritFrom 'shared'
            // pod template defined in molgenis/molgenis-jenkins-pipeline repository
            yaml libraryResource("pod-templates/python.yaml")
        }
    }
    environment {
        POETRY_CACHE_DIR = '/usr/src/app/.cache'
        REPOSITORY = 'molgenis/molgenis-py-lifelines-transform'
        LOCAL_REPOSITORY = "${LOCAL_REGISTRY}/molgenis/lifelines-transform"
    }
    stages {
        stage('Prepare') {
            when {
                allOf {
                    not {
                        changelog '.*\\[skip ci\\]$'
                    }
                }
            }
            steps {
                container('vault') {
                    script {
                        env.GITHUB_TOKEN = sh(script: 'vault read -field=value secret/ops/token/github', returnStdout: true)
                        env.NEXUS_AUTH = sh(script: 'vault read -field=base64 secret/ops/account/nexus', returnStdout: true)
                        env.SONAR_TOKEN = sh(script: 'vault read -field=value secret/ops/token/sonar', returnStdout: true)
                        env.DOCKERHUB_AUTH = sh(script: 'vault read -field=value secret/gcc/token/dockerhub', returnStdout: true)
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
        stage('Build [pull request]') {
            when {
                changeRequest()
            }
            environment {
                TAG = "PR-${CHANGE_ID}-${BUILD_NUMBER}"
                DOCKER_CONFIG="/root/.docker"
            }
            steps {
                container('sonar') {
                    sh "sonar-scanner -Dsonar.github.oauth=${env.GITHUB_TOKEN} -Dsonar.pullrequest.base=${CHANGE_TARGET} -Dsonar.pullrequest.branch=${BRANCH_NAME} -Dsonar.pullrequest.key=${env.CHANGE_ID} -Dsonar.pullrequest.provider=GitHub -Dsonar.pullrequest.github.repository=molgenis/molgenis-py-consensus"
                }
                container (name: 'kaniko', shell: '/busybox/sh') {
                    sh "#!/busybox/sh\nmkdir -p ${DOCKER_CONFIG}"
                    sh "#!/busybox/sh\necho '{\"auths\": {\"registry.molgenis.org\": {\"auth\": \"${NEXUS_AUTH}\"}, \"https://index.docker.io/v1/\": {\"auth\": \"${DOCKERHUB_AUTH}\"}, \"registry.hub.docker.com\": {\"auth\": \"${DOCKERHUB_AUTH}\"}}}' > ${DOCKER_CONFIG}/config.json"
                    sh "#!/busybox/sh\n/kaniko/executor --context ${WORKSPACE} --destination ${LOCAL_REPOSITORY}:${TAG}"
                }
            }
        }
        stage('Release: [master]') {
            when {
                allOf {
                    branch 'master'
                    not {
                        changelog '.*\\[skip ci\\]$'
                    }
                }
            }
            environment {
                GIT_AUTHOR_EMAIL = 'molgenis+ci@gmail.com'
                GIT_AUTHOR_NAME = 'molgenis-jenkins'
                GIT_COMMITTER_EMAIL = 'molgenis+ci@gmail.com'
                GIT_COMMITTER_NAME = 'molgenis-jenkins'
                DOCKER_CONFIG = '/root/.docker'
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
                container (name: 'kaniko', shell: '/busybox/sh') {
                    sh "#!/busybox/sh\nmkdir -p ${DOCKER_CONFIG}"
                    sh "#!/busybox/sh\necho '{\"auths\": {\"registry.molgenis.org\": {\"auth\": \"${NEXUS_AUTH}\"}, \"https://index.docker.io/v1/\": {\"auth\": \"${DOCKERHUB_AUTH}\"}, \"registry.hub.docker.com\": {\"auth\": \"${DOCKERHUB_AUTH}\"}}}' > ${DOCKER_CONFIG}/config.json"
                    sh "#!/busybox/sh\n/kaniko/executor --context ${WORKSPACE} --destination ${REPOSITORY}:${TAG}"
                    sh "#!/busybox/sh\n/kaniko/executor --context ${WORKSPACE} --destination ${REPOSITORY}:latest"
                }
            }
            post {
                success {
                    container('python') {
                        sh "git push origin master --tags"
                    }
                    hubotSend(message: 'Build success', status:'INFO', site: 'slack-pr-app-team')
                }
                failure {
                    hubotSend(message: 'Build failed', status:'ERROR', site: 'slack-pr-app-team')
                }
            }
        }
    }
}
