import os.path
import networkx as nx
from delphin.codecs import simplemrs
import POGG.composition_library
from POGG.mrs_util import wrap_SEMENT
from sandbox.pogg_objects import POGGenerator, POGGGraph

global_yaml_path = "../config_data/global_config.yml"
local_yaml_path = "/Users/lizcconrad/Documents/PhD/POGG/POGG_project/POGG_data/synthesized/ling575_presentation/local_config.yml"

# make POGGProcess which contains all config information
p1 = POGGenerator([global_yaml_path, local_yaml_path])

graph = nx.drawing.nx_pydot.read_dot(os.path.join(p1.graph_directory, "graph1.dot"))

# result = p1.generate_MRS_from_graph(graph)
test = POGGGraph(graph)

yip = test.get_nodes_by_name("apple")[0]
pee = test.get_nodes_by_name("red")[0]
apple_mrs = p1.node_to_mrs(yip)
red_mrs = p1.node_to_mrs(pee)

red_apple = POGG.composition_library.adjective_phrase(p1.LEXICON.edges['color'], apple_mrs, red_mrs)

you = POGG.composition_library.pronoun(p1.LEXICON.nodes['you'])
print(":3")

# pee = test.get_node_by_id("apple_n0")
# poo = test.get_edges_by_name("color")
# pa = test.get_edge_by_id("color_e0")
# print(":3")
# TODO: 01/31 ok this works but it's really inconvenient to access the nodes now bc they're objects not names so is there a way i can make the class more convenient?


# just one result so make it a list
# wrap
you_wrapped = wrap_SEMENT(you)

p1.generate_text_from_MRS_results([you_wrapped])



