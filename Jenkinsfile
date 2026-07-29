pipeline {

    agent any

    stages {

        stage('Checkout') {
            steps {
                echo 'Repository checked out successfully.'
            }
        }

        stage('Run Network Validation') {
            steps {
                sh '''
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
    }
}
