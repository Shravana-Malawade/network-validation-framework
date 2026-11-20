pipeline {
    agent any

    options {
        skipDefaultCheckout()
    }

    environment {
        VALIDATION_EMAIL_TO = 'shravanamalawade@gmail.com, sachin@nyxses.com '

    }

    stages {
        stage('Clear Previous Validation Output') {
            steps {
                // Remove exact generated paths before checkout so a setup
                // failure cannot publish a previous run's reports.
                sh '''
                    rm -f -- reports/junit.xml reports/results.json \
                        reports/summary.html reports/network_info.txt \
                        logs/framework.log \
                        reports/pcap/L4_TC_002.pcap reports/pcap/L4_TC_004.pcap
                '''
            }
        }

        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Setup Python Environment') {
            steps {
                sh '''
                    rm -rf .venv
                    python3 -m venv .venv
                    .venv/bin/python -m pip install --upgrade pip
                    .venv/bin/python -m pip install -r requirements.txt
                '''
            }
        }

        stage('Run Network Validation') {
            steps {
                script {
                    // Use recognized cause types. Free-text cause descriptions
                    // can include user or upstream job details.
                    def causes = currentBuild.getBuildCauses()
                    def labels = []
                    for (def cause : causes) {
                        def causeClass = cause['_class'].toString()
                        if (causeClass.endsWith('UserIdCause')) {
                            labels.add('Manual')
                        } else if (causeClass.endsWith('TimerTriggerCause')) {
                            labels.add('Scheduled')
                        } else if (causeClass.endsWith('SCMTriggerCause')) {
                            labels.add('SCM change')
                        } else if (causeClass.endsWith('UpstreamCause')) {
                            labels.add('Upstream build')
                        } else if (causeClass.endsWith('RemoteCause')) {
                            labels.add('Remote trigger')
                        } else {
                            labels.add('Jenkins trigger')
                        }
                    }
                    env.EMBITE_BUILD_TRIGGER = labels ? labels.unique().join(', ') : 'Unknown'

                    int validationExit = sh(
                        script: '.venv/bin/python -u main.py',
                        returnStatus: true
                    )

                    if (validationExit != 0) {
                        error("Network validation exited with code ${validationExit}. See the validation report.")
                    }

                    sh '''
                        test -s reports/pcap/L4_TC_002.pcap || {
                            echo 'Missing or empty capture for L4_TC_002'
                            exit 1
                        }
                        test -s reports/pcap/L4_TC_004.pcap || {
                            echo 'Missing or empty capture for L4_TC_004'
                            exit 1
                        }
                    '''
                }
            }
        }
    }

    post {
        always {
            script {
                if (fileExists('reports/junit.xml')) {
                    catchError(buildResult: 'FAILURE', catchInterruptions: false) {
                        junit testResults: 'reports/junit.xml', allowEmptyResults: true
                    }
                }

                catchError(buildResult: 'FAILURE', catchInterruptions: false) {
                    archiveArtifacts(
                        artifacts: 'reports/**,logs/framework.log',
                        allowEmptyArchive: true,
                        fingerprint: true
                    )
                }

                def validationStatus = 'UNAVAILABLE'
                def project = env.JOB_NAME
                def html = null

                if (fileExists('reports/results.json') &&
                    fileExists('reports/summary.html')) {
                    catchError(buildResult: 'FAILURE', catchInterruptions: false) {
                        def metadata = sh(
                            script: '''python3 -c '
import json
from pathlib import Path

report = json.loads(Path("reports/results.json").read_text(encoding="utf-8"))
print(report["run_status"])
print(" ".join(str(report["project"]).split()))
'
''',
                            returnStdout: true
                        ).trim().readLines()

                        validationStatus = metadata[0]
                        project = metadata[1]
                        html = readFile(file: 'reports/summary.html', encoding: 'UTF-8')
                    }
                }

                def buildStatus = currentBuild.currentResult
                def subject = "EmbITE | ${validationStatus} | ${project} | " +
                    "Network Validation | Storage Not Integrated | Build #${env.BUILD_NUMBER}"

                if (html != null) {
                    def body = html.replace(
                        '<body>',
                        "<body><p><strong>Jenkins build status</strong> ${buildStatus}</p>"
                    )
                    emailext(
                        to: env.VALIDATION_EMAIL_TO,
                        subject: subject,
                        mimeType: 'text/html',
                        body: body
                    )
                } else {
                    emailext(
                        to: env.VALIDATION_EMAIL_TO,
                        subject: subject,
                        mimeType: 'text/plain',
                        body: """Hello Team,

Jenkins build #${env.BUILD_NUMBER} finished with status ${buildStatus}.
The detailed network validation report is unavailable for this build.
Storage Validation: Not Integrated / Not Executed.

Build: ${env.BUILD_URL}
Console: ${env.BUILD_URL}console

Regards,
EmbITE Automation
NYXSES
"""
                    )
                }
            }
        }
    }
}
