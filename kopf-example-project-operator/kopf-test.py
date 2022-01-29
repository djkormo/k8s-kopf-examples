import time
import shlex
import subprocess
from kopf.testing import KopfRunner

def test_operator():
    with KopfRunner(['run', '--namespace project-operator', '--verbose', 'app/kopf_operator.py']) as runner:
        # do something while the operator is running.

        subprocess.run("kubectl apply -f test/project.yaml", shell=True, check=True)
        time.sleep(30)  # give it some time to react and to sleep and to retry

        subprocess.run("kubectl delete -f test/project.yaml", shell=True, check=True)
        time.sleep(30)  # give it some time to react

    assert runner.exit_code == 0
    assert runner.exception is None
    assert 'And here we are!' in runner.stdout
    assert 'Deleted, really deleted' in runner.stdout
# run test    
test_operator()    