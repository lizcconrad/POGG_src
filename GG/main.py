import os
import yaml
import networkx as nx
import GG.graph_to_mrs
import GG.mrs_util
import GG.graph_util
import GG.evaluation
from tabulate import tabulate

# Load elements from global config
global_config = yaml.safe_load((open("../config_data/global_config.yml")))
# outer folder with individual scenario/graph folders inside
parent_data_dir = global_config['parent_data_directory']

# Load elements from local config
# TODO: hardcoded now, in the future can be adjusted to load each lexicon for each scenario
data_directory = os.path.join(parent_data_dir, "Scenario")
local_config_path = os.path.join(data_directory, "local_config.yml")
local_config = yaml.safe_load((open(local_config_path)))
graph_directory = local_config['graph_directory']
results_directory = local_config['results_directory']
lexicon = GG.graph_to_mrs.load_lexicon(local_config['LEXICON'])

# make results directory if needed
if not os.path.exists(results_directory):
    os.makedirs(results_directory)


# for summary stats at end
full_eval_info = {
    'nodes': {},
    'edges': {}
}
node_counter = 0
edge_counter = 0

# stores # of results per graph, and reason for 0 if 0
# e.g. {
#   graph_0: [26, "Succesfully generated"],
#   graph_1: [0, "MRS not produced"],
#   graph_2: [0, "ERG did not generate]
# }
generation_info = {}

# for each graph...
for filename in os.listdir(graph_directory):
    split_file = os.path.splitext(filename)
    print(filename)
    graph_name = split_file[0]
    if split_file[-1].lower() == '.dot':
        results_filename = os.path.join(results_directory, graph_name + ".txt")

        with open(results_filename, 'w') as results_file:
            results_file.write(os.path.join(graph_directory, filename) + "\n")

            graph = nx.drawing.nx_pydot.read_dot(os.path.join(graph_directory, filename))

            # TODO: might want to deal with this better in the future...
            # if there's a cycle, skip it entirely
            try:
                nx.find_cycle(graph)
                generation_info[graph_name] = [0, "Graph contains cycles"]
                results_file.write("Graph contains cycles")
                continue
            except nx.NetworkXNoCycle:
                pass

            root = GG.graph_util.find_root(graph)

            conversion_results = GG.graph_to_mrs.graph_to_mrs(root, graph, lexicon)
            graphmrs = conversion_results[0]
            eval_info = conversion_results[1]

            # update full_eval_info
            for n in eval_info['nodes']:
                new_node_name = "{}_{}".format(graph_name, n)
                full_eval_info['nodes'][new_node_name] = eval_info['nodes'][n]

            for e in eval_info['edges']:
                new_edge_name = "{}_{}".format(graph_name, e)
                full_eval_info['edges'][new_edge_name] = eval_info['edges'][e]

            mrs_string = GG.mrs_util.wrap_ssement(graphmrs)
            results_file.write(mrs_string + "\n")

            results = []
            if mrs_string == "":
                generation_info[graph_name] = [0, "MRS not produced"]
            else:
                results = GG.mrs_util.generate(mrs_string)

                results_file.write("GENERATED RESULTS ... \n")
                for r in results:
                    results_file.write(r.get('surface') + "\n")

                if len(results) == 0:
                    generation_info[graph_name] = [0, "ERG did not generate"]
                else:
                    generation_info[graph_name] = [len(results), "Successfully generated"]

            results_file.write("\nTOTAL RESULTS: {}".format(len(results)))

            results_file.write("\n\n")
            results_file.write(GG.evaluation.node_evaluation(eval_info['nodes']))
            results_file.write("\n\n")
            results_file.write(GG.evaluation.edge_evaluation(eval_info['edges']))
            results_file.write("\n\n")
            results_file.write(GG.evaluation.evaluation_summary(eval_info))


with open(os.path.join(results_directory,"evaluation_summary.txt"), 'w') as summary_file:
    summary_file.write("EVALUATION SUMMARY\n\n")
    # total results per graph
    generation_table = []
    graphs_generated_from = 0
    for g in generation_info:
        g_info = generation_info[g]
        generation_table.append([g, str(g_info[0]), g_info[1]])
        if g_info[0] > 0:
            graphs_generated_from += 1

    total_graphs = len(generation_info)
    graph_coverage = graphs_generated_from / total_graphs
    coverage_table = [[str(graphs_generated_from), str(total_graphs), str(graph_coverage)]]

    summary_file.write(tabulate(coverage_table, headers=["Graphs Generated From", "Total Graphs", "Graph Coverage"]))
    summary_file.write("\n\n")
    summary_file.write(tabulate(sorted(generation_table, key=lambda x: x[0]), headers=["Graph Name", "Results", "Reason"]))
    summary_file.write("\n\n")

    # total node/edge coverage
    summary_table = GG.evaluation.evaluation_summary(full_eval_info)
    summary_file.write(GG.evaluation.evaluation_summary(full_eval_info))

    # node/edge information
    summary_file.write("\n\n")
    summary_file.write(GG.evaluation.node_evaluation(full_eval_info['nodes']))
    summary_file.write("\n\n")
    summary_file.write(GG.evaluation.edge_evaluation(full_eval_info['edges']))

