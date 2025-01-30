import os.path
import networkx as nx
from sandbox.pogg_objects import POGGenerator, POGGGraph

global_yaml_path = "../config_data/global_config.yml"
local_yaml_path = "/Users/lizcconrad/Documents/PhD/POGG/POGG_project/POGG_data/synthesized/ling575_presentation/local_config.yml"

# make POGGProcess which contains all config information
p1 = POGGenerator([global_yaml_path, local_yaml_path])

graph = nx.drawing.nx_pydot.read_dot(os.path.join(p1.graph_directory, "graph1.dot"))

# result = p1.generate_MRS_from_graph(graph)
test = POGGGraph(graph)
print(":3")

# TODO: 01/31 ok this works but it's really inconvenient to access the nodes now bc they're objects not names so is there a way i can make the class more convenient? 


# just one result so make it a list
# p1.generate_text_from_MRS_results([result])



