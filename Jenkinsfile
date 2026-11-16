
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

        always {

            script {

                def summary = null

                if (fileExists('reports/junit.xml')) {

                    summary = junit(
                        testResults: 'reports/junit.xml',
                        allowEmptyResults: true
                    )

                    echo 'JUnit report published successfully.'

                } else {
                    echo 'JUnit report was not generated.'
                }

                archiveArtifacts(
                    artifacts: 'reports/**,logs/**',
                    allowEmptyArchive: true,
                    fingerprint: true
                )

                def total = summary ? summary.totalCount : 'N/A'
                def passed = summary ? summary.passCount : 'N/A'
                def failed = summary ? summary.failCount : 'N/A'
                def skipped = summary ? summary.skipCount : 'N/A'

                emailext(
                    to: 'shravanamalawade@gmail.com, sachin@nyxses.com',

                    subject: "${currentBuild.currentResult}: Network Validation Build #${env.BUILD_NUMBER}",

                    body: """Network Validation Build Report

Build Number : #${env.BUILD_NUMBER}
Job Name     : ${env.JOB_NAME}
Build Status : ${currentBuild.currentResult}

TEST SUMMARY
------------
Total Tests   : ${total}
Passed        : ${passed}
Failed        : ${failed}
Skipped       : ${skipped}

REPORTS
-------
JUnit Report : ${env.BUILD_URL}testReport/
Build Details: ${env.BUILD_URL}
Console Log  : ${env.BUILD_URL}console

The JUnit report and available framework logs are attached.
""",

                    attachmentsPattern: 'reports/junit.xml,logs/**',
                    attachLog: true
                )

                echo 'Build report email notification triggered.'
            }
        }
    }
}
