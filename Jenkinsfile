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

            emailext(
                to: 'shravanamalawade@gmail.com, sachin@nyxses.com',
                subject: "SUCCESS: Network Validation Build #${env.BUILD_NUMBER}",
                body: """Network Validation completed successfully.

Build Number: #${env.BUILD_NUMBER}
Job Name: ${env.JOB_NAME}
Result: ${currentBuild.currentResult}

JUnit Test Report: ${env.BUILD_URL}testReport/
Build Details: ${env.BUILD_URL}
""",
                attachmentsPattern: 'reports/junit.xml'
            )
        }

        failure {
            echo 'Network Validation failed.'

            emailext(
                to: 'shravanamalawade@gmail.com, sachin@nyxses.com',
                subject: "FAILURE: Network Validation Build #${env.BUILD_NUMBER}",
                body: """Network Validation failed.

Build Number: #${env.BUILD_NUMBER}
Job Name: ${env.JOB_NAME}
Result: ${currentBuild.currentResult}

JUnit Test Report: ${env.BUILD_URL}testReport/
Console Output: ${env.BUILD_URL}console
Build Details: ${env.BUILD_URL}
""",
                attachmentsPattern: 'reports/junit.xml'
            )
        }

        always {

            script {
                if (fileExists('reports/junit.xml')) {
                    junit(
                        testResults: 'reports/junit.xml',
                        allowEmptyResults: true
                    )
                } else {
                    echo 'JUnit report was not generated.'
                }
            }

            archiveArtifacts(
                artifacts: 'reports/**,logs/**',
                allowEmptyArchive: true,
                fingerprint: true
            )

            echo 'Pipeline execution finished.'
        }
    }
}
