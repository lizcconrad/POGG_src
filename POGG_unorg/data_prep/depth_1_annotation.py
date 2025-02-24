import os
import yaml
import networkx as nx
from POGG.mrs_algebra import config


### FUNCTIONS TO BE RELOCATED ###
# functions written for this task that need to find a home
def get_graphs(dir):
    """
    Get graphs from all .dot files in the given directory and read them in as NetworkX DiGraphs
    :param dir: directory to find .dot files in
    :return: list of graphs as read  from .dot files in the given directory
    :rtype: list(DiGraph)
    """
    graphs = []
    # make the .dot files for graphs of depth 1
    for filename in os.listdir(dir):
        if ".dot" in filename:
            graph = nx.drawing.nx_pydot.read_dot(os.path.join(dir, filename))
            try:
                graph.remove_node("\\n")
            except:
                pass
        graphs.append(graph)

    return graphs


# for each config...
config_parent = "/Users/lizcconrad/Documents/PhD/POGG/POGG_project/POGG_data/analysis/configs"
"""
config_files = []
for dirpath in os.walk(config_parent):
    for filename in dirpath[2]:
        if ".yml" in filename:
            config_files.append(filename)
             
"""
config_file_paths = [os.path.join(dirpath[0], filename) for dirpath in os.walk(config_parent) for filename in dirpath[2] if ".yml" in filename]

# TODO: just work with the first one for now...
config_file_paths = [config_file_paths[0]]



# for each config file...
for cf_file in config_file_paths:
    cf = yaml.safe_load((open(cf_file)))
    graph_directory = cf['graph_directory']
    depth1_graphs = get_graphs(graph_directory)

    # for each subgraph...



print(":3")


# build MRS
# record the following information...
# 1. parent node
# 2. child node
# 3. edge_label
# 4. comp_fxn used
# 5. comp_to_graph_relations classification
# 6. what holes does the parent have?
# 7. what holes does the child have?
# 8. what holes does the edge predicate, if introduced, have?
# 9. One possible lexicalization (constraining quantifiers to all be "the")


