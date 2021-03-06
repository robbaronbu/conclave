import conclave.dispatch
import conclave.lang as sal
from conclave.comp import dag_only
from conclave.utils import *
import conclave.partition as part
from conclave.codegen.scotch import ScotchCodeGen
from conclave.codegen.sharemind import SharemindCodeGen, SharemindCodeGenConfig
from conclave.codegen.spark import SparkCodeGen
from conclave.codegen.python import PythonCodeGen
from conclave import generate_code, CodeGenConfig
from conclave.dispatch import dispatch_all
from conclave.net import setup_peer
import sys


def testHybridJoinWorkflow():

    def protocol():

        # define inputs
        colsIn1 = [
            defCol("a", "INTEGER", [1]),
            defCol("b", "INTEGER", [1]),
        ]
        in1 = sal.create("in1", colsIn1, set([1]))
        proj1 = sal.project(in1, "proj1", ["a", "b"])

        colsIn2 = [
            defCol("c", "INTEGER", [1], [2]),
            defCol("d", "INTEGER", [2])
        ]
        in2 = sal.create("in2", colsIn2, set([2]))
        proj2 = sal.project(in2, "proj2", ["c", "d"])

        res = sal.join(proj1, proj2, "res", ["a"], ["c"])

        # open result to party 1
        sal.collect(res, 1)

        # return roots of dag
        return set([in1, in2])

    pid = int(sys.argv[1])
    size = sys.argv[2]

    workflow_name = "hybrid-join-" + str(pid)
    sm_cg_config = SharemindCodeGenConfig(
        workflow_name, "/mnt/shared", use_hdfs=False, use_docker=True)
    codegen_config = CodeGenConfig(
        workflow_name).with_sharemind_config(sm_cg_config)
    codegen_config.pid = pid
    codegen_config.code_path = "/mnt/shared/" + workflow_name
    codegen_config.input_path = "/mnt/shared/hybridjoin/" + size
    codegen_config.output_path = "/mnt/shared/hybridjoin/" + size

    jobqueue = generate_code(protocol, codegen_config, ["sharemind"], ["python"])
    sharemind_config = {
        "pid": pid,
        "parties": {
            1: {"host": "localhost", "port": 9001},
            2: {"host": "localhost", "port": 9002},
            3: {"host": "localhost", "port": 9003}
        }
    }
    sm_peer = setup_peer(sharemind_config)
    conclave.dispatch.dispatch_all(None, sm_peer, jobqueue)

if __name__ == "__main__":

    testHybridJoinWorkflow()
