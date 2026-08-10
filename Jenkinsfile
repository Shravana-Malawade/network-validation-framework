pipeline {
    agent any

    options {
        skipDefaultCheckout(true)
        timestamps()
    }

    parameters {
        choice(
            name: 'TEST_SUITE',
            choices: ['all', 'layer1'],
            description: 'Select validation test suite to execute'
        )
    }

    stages {
        stage('Checkout') {
            steps {
                checkout scm
                sh 'git log -1 --oneline'
            }
        }

        stage('Setup Python Environment') {
            steps {
                sh '''
                    python3 -m venv .venv
                    . .venv/bin/activate
                    python -m pip install --upgrade pip
                    pip install -r requirements.txt
                '''
            }
        }

        stage('Run Network Validation') {
            steps {
                sh """
                    . .venv/bin/activate
                    python3 main.py --suite ${params.TEST_SUITE} > validation.log 2>&1
                """
            }
        }

        stage('Publish Build Output') {
            steps {
                echo 'Saving validation output and any generated reports.'
            }
        }
    }

    post {
        always {
            archiveArtifacts artifacts: 'validation.log, reports/**/*, report/**/*, *.html, *.xml', allowEmptyArchive: true
        }

        success {
            echo 'Network Validation completed successfully.'
        }

        failure {
            echo 'Network Validation failed. Open validation.log under Build Artifacts for details.'
        }
    }
}
