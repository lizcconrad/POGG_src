import os
import yaml
import networkx as nx
import POGG.graph_to_mrs
import POGG.mrs_util
import POGG.graph_util
import POGG.evaluation

# Load elements from global config
global_config = yaml.safe_load((open("../config_data/global_config.yml")))
# outer folder with individual scenario/graph folders inside
parent_data_dir = global_config['parent_data_directory']

# Load elements from local config
# TODO: hardcoded now, in the future can be adjusted to load each lexicon for each scenario
data_directory = os.path.join(parent_data_dir, "ling575_presentation")
local_config_path = os.path.join(data_directory, "local_config.yml")
local_config = yaml.safe_load((open(local_config_path)))
graph_directory = local_config['graph_directory']
results_directory = local_config['results_directory']
lexicon = POGG.graph_to_mrs.load_lexicon(local_config['LEXICON'])

# make results directory if needed
if not os.path.exists(results_directory):
    os.makedirs(results_directory)


# for each graph...
for filename in os.listdir(graph_directory):
    split_file = os.path.splitext(filename)
    print(filename)
    # only process if it's an actual .dot file
    if ".dot" in filename:
        graph_name = split_file[0]
        graph = nx.drawing.nx_pydot.read_dot(os.path.join(graph_directory, filename))

        # TODO: might want to deal with this better in the future...
        # if there's a cycle, skip it entirely
        try:
            nx.find_cycle(graph)
            continue
        except nx.NetworkXNoCycle:
            pass

        root = POGG.graph_util.find_root(graph)

        conversion_results = POGG.graph_to_mrs.graph_to_mrs(root, graph, lexicon)
        graphmrs = conversion_results[0]

        mrs_string = POGG.mrs_util.wrap_SEMENT(graphmrs)

        if mrs_string != "":
            results = POGG.mrs_util.generate(mrs_string)
            print([r['surface'] for r in results])
