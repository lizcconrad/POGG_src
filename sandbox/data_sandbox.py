import os
import yaml
import networkx as nx
from POGG.graph_util import write_graph_to_dot, find_root
import csv

# Load elements from global config
# global_config = yaml.safe_load((open("../config_data/global_config.yml")))
# outer folder with individual scenario/graph folders inside
#parent_data_dir = global_config['parent_data_directory']



# Load elements from local config
# TODO: hardcoded now, in the future can be adjusted to load each lexicon for each scenario
# data_directory = os.path.join(parent_data_dir, "ling575_presentation")
# local_config_path = os.path.join(data_directory, "local_config.yml")
# local_config = yaml.safe_load((open(local_config_path)))
# graph_directory = local_config['graph_directory']

# loop through parent directories
parent_data_dir = "/"
data_dirs = ['development', 'test', 'synthesized']
for dir in data_dirs:
    for subdir in os.listdir(os.path.join(parent_data_dir, dir)):
        subdir_path = os.path.join(parent_data_dir, dir, subdir)
        if os.path.isdir(subdir_path):

            # mkdir for depth_1 if needed
            if not os.path.exists("{}/depth_1".format(subdir_path)):
                os.makedirs("{}/depth_1".format(subdir_path))

            # make the .dot files for graphs of depth 1
            for filename in os.listdir(os.path.join(parent_data_dir, dir, subdir)):
                if ".dot" in filename:
                    split_file = os.path.splitext(filename)
                    print(filename)
                    graph_name = split_file[0]

                    subgraphs = []

                    graph = nx.drawing.nx_pydot.read_dot(os.path.join(subdir_path, filename))
                    try:
                        graph.remove_node("\\n")
                    except:
                        pass

                    # create a CSV file to store info for all depth_1 graphs for this "world"
                    # game_name, parent_node, child_node, edge_label, semantic_functor, lexicalization
                    with open(os.path.join(subdir_path, 'depth_1', '{}_depth_1s.csv'.format(subdir)), 'w',
                              newline='') as csvfile:
                        csvwriter = csv.writer(csvfile, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
                        csvwriter.writerow(
                            ['game_name', 'parent_node', 'child_node', 'edge_label', 'semantic_functor',
                             'lexicalization'])

                        nodes = list(graph.nodes)
                        for parent in nodes:
                            for child in graph.successors(parent):
                                property_edges = [(p, c, e) for p, c, e in graph.out_edges(parent, data=True) if p == parent and c == child]
                                for e in property_edges:
                                    subgraph = nx.DiGraph()
                                    subgraph.add_node(parent)
                                    subgraph.add_node(child)
                                    subgraph.add_edge(e[0], e[1], label=e[2]['label'])
                                    subgraphs.append(subgraph)

                                    # add info for this graph to the csv file
                                    csvwriter.writerow([subdir, parent, child, e[2]['label']])

                                # write to dot
                                write_graph_to_dot(subgraph, "{}/depth_1/{}_{}_{}_{}.dot".format(subdir_path, graph_name, parent, child, property_edges.index(e)))





# for each graph...
# for filename in os.listdir(graph_directory):
#     if os.path.isdir(os.path.join(graph_directory, filename)):
#         pass
#     else:
#         split_file = os.path.splitext(filename)
#         print(filename)
#         graph_name = split_file[0]
#
#         # mkdir for depth_1 if needed
#         if not os.path.exists("{}/depth_1".format(graph_directory)):
#             os.makedirs("{}/depth_1".format(graph_directory))
#
#         subgraphs = []
#
#         graph = nx.drawing.nx_pydot.read_dot(os.path.join(graph_directory, filename))
#         graph.remove_node("\\n")
#         nodes = list(graph.nodes)
#         for parent in nodes:
#             for child in graph.successors(parent):
#                 property_edges = [(p, c, e) for p, c, e in graph.out_edges(parent, data=True) if p == parent and c == child]
#                 for e in property_edges:
#                     subgraph = nx.DiGraph()
#                     subgraph.add_node(parent)
#                     subgraph.add_node(child)
#                     subgraph.add_edge(e[0], e[1], label=e[2]['label'])
#                     subgraphs.append(subgraph)
#
#                     # write to dot
#                     write_graph_to_dot(subgraph, "{}/depth_1/{}_{}_{}_{}.dot".format(graph_directory, graph_name, parent, child, property_edges.index(e)))
#

