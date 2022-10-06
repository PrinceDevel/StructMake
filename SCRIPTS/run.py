import sys
import os
from builder import *
from clear_cache import clear as clear_cache

if __name__ == '__main__' :

    argc: int = len(sys.argv)
    argv: list = sys.argv

    struct: str = "struct.yaml"
    if argc > 1 and argv[1].endswith('.yaml') :
        struct = argv[1]

    if not os.path.exists(struct) :
        print(f'ERROR: {struct} file does not exist')
        exit()

    structure = LoadYAML(struct)
    workspace = ParseYAML(structure)
    BuildWorkspace(workspace)
    
    os.system(f'rm -r {os.getcwd()}/StructMake/__pycache__/')