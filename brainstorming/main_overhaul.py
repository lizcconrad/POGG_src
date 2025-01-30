# sample variables
graphs = []

# sample functions
def make_output_files():
    pass

routines = {
    "build_mrs": {},
    "evaluate": {},
    "depth1_analysis": {}
}

# list of functions that need to be run per different elements of the process
# comes as tuple: (fxn_name, when)
# fxn_name: fxn to be run
# when: before or after ... before or after what...?
routine_dict = {
    "per_graph": [],
    "per_node": [],
    "per_edge": []
}

for graph in graphs:
    make_output_files()