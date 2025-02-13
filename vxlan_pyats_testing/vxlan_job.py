import os


# All run () must be inside a main function
def main(runtime):
    # Find the location of the script in relation to the job file
    testscript = os.path.join(os.path.dirname(__file__), 'vxlan_vni_test.py')
    # Execute the testscript
    runtime.tasks.run(testscript=testscript)
