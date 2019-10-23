pipeline {
    agent {
        kubernetes {
            label 'python-stretch'
        }
    }
    stages {
        stage('Prepare') {
            steps {
                script {
                    env.GIT_COMMIT = sh(script: 'git rev-parse HEAD', returnStdout: true).trim()
                }
                container('vault') {
                    script {
                        env.PYPI_USERNAME = sh(script: 'vault read -field=username secret/ops/account/pypi', returnStdout: true)
                        env.PYPI_PASSWORD = sh(script: 'vault read -field=password secret/ops/account/pypi', returnStdout: true)
                        env.GITHUB_TOKEN = sh(script: 'vault read -field=value secret/ops/token/github', returnStdout: true)
                        env.SONAR_TOKEN = sh(script: 'vault read -field=value secret/ops/token/sonar', returnStdout: true)
                    }
                }
                container('python') {
                    script {
                        sh "pip install bumpversion"
                        sh "pip install twine"
                    }
                }
            }
        }
        stage('Build: [ pull request ]') {
            when {
                changeRequest()
            }
            steps {
                container('python') {
                    sh "python setup.py test"
                    sh "pip install ."
                }
                container('sonar') {
                    sh "sonar-scanner -Dsonar.github.oauth=${env.GITHUB_TOKEN} -Dsonar.pullrequest.base=${CHANGE_TARGET} -Dsonar.pullrequest.branch=${BRANCH_NAME} -Dsonar.pullrequest.key=${env.CHANGE_ID} -Dsonar.pullrequest.provider=GitHub -Dsonar.pullrequest.github.repository=molgenis/molgenis-py-consensus"
                }
            }
        }
        stage('Build: [ master ]') {
            when {
                branch 'master'
            }
            steps {
                milestone 1
                container('python') {
                    sh "python setup.py test"
                    sh "pip install ."
                }
                container('sonar') {
                    sh "sonar-scanner"
                }
            }
        }
    }
}