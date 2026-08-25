pipeline {
    agent any

    options {
        skipDefaultCheckout(true)
        timestamps()
    }

    environment {
        DUT_HOST = '192.168.31.35'
        DUT_USER = 'pi3'
        DUT_REPO = '/home/pi3/projects/network-validation-framework'
        DUT_CREDENTIALS = 'pi3-dut-ssh'
    }

    parameters {
        choice(
            name: 'TEST_SUITE',
            choices: ['all', 'layer1'],
            description: 'Select validation test suite to execute on the Raspberry Pi'
        )
    }

    stages {

        stage('Verify DUT Connection') {
            steps {
                sshagent(credentials: [env.DUT_CREDENTIALS]) {
                    sh '''
                        ssh -o BatchMode=yes -o StrictHostKeyChecking=yes \
                            "$DUT_USER@$DUT_HOST" \
                            'hostname; whoami'
                    '''
                }
            }
        }

        stage('Run Validation on DUT') {
            steps {
                sshagent(credentials: [env.DUT_CREDENTIALS]) {
                    sh """
                        ssh -o BatchMode=yes -o StrictHostKeyChecking=yes \
                            "\$DUT_USER@\$DUT_HOST" \
                            "bash -s -- '${params.TEST_SUITE}'" <<'REMOTE_SCRIPT'

set -Eeuo pipefail

suite="\$1"

cd /home/pi3/projects/network-validation-framework

test -d .git

branch="\$(git branch --show-current)"

if [ "\$branch" != "feature/layer2-validation" ]; then
    echo "ERROR: Expected feature/layer2-validation, found \$branch"
    exit 2
fi

echo "Updating DUT repository from GitHub"

git pull --ff-only origin "\$branch"

echo "DUT: \$(hostname)"
echo "Repository: \$(pwd)"
echo "Branch: \$branch"

git log -1 --oneline
git status --short

python3 -m venv .venv

. .venv/bin/activate

python3 -m pip install --upgrade pip

python3 -m pip install -r requirements.txt

# Remove any previous JUnit report
rm -f reports/junit/network-validation.xml

# Execute selected validation suite
python3 main.py --suite "\$suite" 2>&1 | tee validation.log

REMOTE_SCRIPT
                    """
                }
            }
        }

        stage('Collect & Publish Test Results') {
            steps {
                sshagent(credentials: [env.DUT_CREDENTIALS]) {
                    sh '''
                        echo "Collecting JUnit test report from DUT"

                        mkdir -p reports/junit

                        scp -o BatchMode=yes -o StrictHostKeyChecking=yes \
                            "$DUT_USER@$DUT_HOST:$DUT_REPO/reports/junit/network-validation.xml" \
                            reports/junit/network-validation.xml
                    '''
                }

                echo 'Publishing JUnit test results'

                junit testResults: 'reports/junit/*.xml',
                      allowEmptyResults: false
            }
        }
    }

    post {

        always {
            sshagent(credentials: [env.DUT_CREDENTIALS]) {
                sh '''
                    echo "Collecting validation log from DUT"

                    scp -o BatchMode=yes -o StrictHostKeyChecking=yes \
                        "$DUT_USER@$DUT_HOST:$DUT_REPO/validation.log" \
                        validation.log || true
                '''
            }

            archiveArtifacts(
                artifacts: 'validation.log, reports/**, report/**, *.html, *.xml',
                allowEmptyArchive: true
            )
        }

        success {
            echo 'Network validation completed successfully on the Raspberry Pi.'
        }

        failure {
            echo 'Network validation failed on the Raspberry Pi. See validation.log and the console output.'
        }
    }
}
