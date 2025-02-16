import os
import yaml
import networkx as nx
import POGG.graph_to_mrs
import POGG.mrs_util
import POGG.graph_util
from tabulate import tabulate

# Load elements from global config
global_config = yaml.safe_load((open("../config_data/global_config.yml")))
# outer folder with individual scenario/graph folders inside
parent_data_dir = global_config['parent_data_directory']

# Load elements from local config
# TODO: hardcoded now, in the future can be adjusted to load each lexicon for each scenario
data_directory = os.path.join(parent_data_dir, "micrograph")
local_config_path = os.path.join(data_directory, "local_config.yml")
local_config = yaml.safe_load((open(local_config_path)))
graph_directory = local_config['graph_directory']
lexicon = POGG.graph_to_mrs.load_lexicon(local_config['LEXICON'])


# for each graph...
total_total_nodes = 0
total_successful_nodes = 0
total_included_nodes = 0
total_total_edges = 0
total_successful_edges = 0
total_included_edges = 0
for filename in os.listdir(graph_directory):
    if os.path.splitext(filename)[-1].lower() == '.dot':
        print(os.path.join(graph_directory, filename))
        graph = nx.drawing.nx_pydot.read_dot(os.path.join(graph_directory, filename))

        root = POGG.graph_util.find_root(graph)

        conversion_results = POGG.graph_to_mrs.graph_to_mrs(root, graph, lexicon)
        graphmrs = conversion_results[0]
        eval_info = conversion_results[1]

        mrs_string = POGG.mrs_util.wrap_SEMENT(graphmrs)
        print(mrs_string)

        results = POGG.mrs_util.generate(mrs_string)

        print("GENERATED RESULTS ... ")
        for r in results:
            print(r.get('surface'))

        # evaluation information
        print("EVALUATION ... ")
        node_table = []
        successful_nodes = 0
        included_nodes = 0
        for n in eval_info['nodes']:
            n_info = eval_info['nodes'][n]
            node_table.append([n, n_info['produced'][0], n_info['produced'][1],
                               n_info['included'][0], n_info['included'][1]])
            if n_info['produced'][0]:
                successful_nodes += 1
                total_successful_nodes += 1
            if n_info['included'][0]:
                included_nodes += 1
                total_included_nodes += 1
        print(tabulate(node_table, headers=["Node", "MRS Produced", "Reason", "Included in MRS", "Reason"]))

        edge_table = []
        successful_edges = 0
        included_edges = 0
        for e in eval_info['edges']:
            e_info = eval_info['edges'][e]
            edge_table.append([e, e_info['produced'][0], e_info['produced'][1],
                               e_info['included'][0], e_info['included'][1]])
            if e_info['produced'][0]:
                successful_edges += 1
                total_successful_edges += 1
            if e_info['included'][0]:
                included_edges += 1
                total_included_edges += 1
        print("\n\n")
        print(tabulate(edge_table, headers=["Edge", "MRS Composed", "Reason", "Included in MRS", "Reason"]))

        # node stats
        total_nodes = len(eval_info['nodes'])
        nodes_produced_coverage = successful_nodes / total_nodes
        nodes_included_coverage = included_nodes / total_nodes
        total_total_nodes += total_nodes
        # edge stats
        total_edges = len(eval_info['edges'])
        if total_edges == 0:
            edges_produced_coverage = 0
            edges_included_coverage = 0
        else:
            edges_produced_coverage = successful_edges / total_edges
            edges_included_coverage = included_edges / total_edges
        total_total_edges += total_edges

        summary_table = [["Nodes", "Produced", successful_nodes, total_nodes, nodes_produced_coverage],
                        ["Nodes", "Included", included_nodes, total_nodes, nodes_included_coverage],
                        ["Edges", "Produced", successful_edges, total_edges, edges_produced_coverage],
                        ["Edges", "Included", included_edges, total_edges, edges_included_coverage]]
        print("\n\n")
        print(tabulate(summary_table, headers=["Graph Component", "Metric", "Successful", "Total", "Coverage"]))


total_nodes_produced_coverage = total_successful_nodes / total_total_nodes
total_edges_produced_coverage = total_successful_edges / total_total_edges
total_nodes_included_coverage = total_included_nodes / total_total_nodes
total_edges_included_coverage = total_included_edges / total_total_edges
full_summary_table = [["Nodes", "Produced", total_successful_nodes, total_total_nodes, total_nodes_produced_coverage],
                    ["Nodes", "Included", total_included_nodes, total_total_nodes, total_nodes_included_coverage],
                    ["Edges", "Produced", total_successful_edges, total_total_edges, total_edges_produced_coverage],
                    ["Edges", "Included", total_included_edges, total_total_edges, total_edges_included_coverage]]
print("\n\n")
print(tabulate(full_summary_table, headers=["Graph Component", "Metric", "Successful", "Total", "Coverage"]))
