pipeline {

    agent any

    stages {

        stage('Checkout') {
            steps {
                echo 'Repository checked out successfully.'
            }
        }

        stage('Setup Python Environment') {
            steps {
                sh '''
                    rm -rf .venv
                    python3 -m venv .venv
                    . .venv/bin/activate
                    python -m pip install --upgrade pip
                    pip install -r requirements.txt
                '''
            }
        }

        stage('Run Network Validation') {
            steps {
                sh '''
                    . .venv/bin/activate
                    python3 main.py
                '''
            }
        }
    }

    post {

        success {
            echo 'Network Validation completed successfully.'
        }

        failure {
            echo 'Network Validation failed.'
        }

        always {
            echo 'Pipeline execution finished.'
        }
    }
}
