import subprocess
from io import StringIO

def get_node_output(input_str: str) -> str:
    p = subprocess.Popen(['node', '-e', 'console.log(%s)' % input_str], stdin=subprocess.PIPE, stdout=subprocess.PIPE)
    stdout, stderr = p.communicate()
    return stdout.decode().strip()