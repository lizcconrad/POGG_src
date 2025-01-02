# CONVERTING (PERPLEXITY) DATA TO GRAPHS
# ORGANIZED: N (MM/DD/YYYY)
# DOCUMENTED: N (MM/DD/YYYY)
import json
import os
from swiplserver import PrologMQI
from POGG.graph_util import build_graph, select_subgraphs, write_graph_to_dot, write_graph_to_png, write_graph_to_svg
from lexicon_helper import build_lexicon_skeleton


# set working directory to the directory with the Perplexity data
os.chdir("/Users/lizcconrad/Documents/PhD/GP2/Adventure/NLTK")

# open Prolog thread
with PrologMQI() as mqi:
    with mqi.create_thread() as prolog_thread:
        # consult Debug.pl
        prolog_thread.query("['Debug_GG.pl']")

        # get all entities with property and relationship data
        result = prolog_thread.query("getEntityData(Entity, Properties, Relationships).")


# go back to current working directory
os.chdir("//test/")

# directory for current game
game_dir_name = "Scenario"


# mkdirs
if not os.path.exists("./{}".format(game_dir_name)):
    os.makedirs("./{}".format(game_dir_name))
if not os.path.exists("./{}/full_graphs".format(game_dir_name)):
    os.makedirs("./{}/full_graphs".format(game_dir_name))
    os.makedirs("./{}/subgraphs".format(game_dir_name))
    os.makedirs("./{}/full_graphs/dot".format(game_dir_name))
    os.makedirs("./{}/full_graphs/png".format(game_dir_name))
    os.makedirs("./{}/full_graphs/svg".format(game_dir_name))
    os.makedirs("./{}/subgraphs/dot".format(game_dir_name))
    os.makedirs("./{}/subgraphs/png".format(game_dir_name))
    os.makedirs("./{}/subgraphs/svg".format(game_dir_name))


# build graph with all entities
graph = build_graph(result)

# build lexicon skeleton for scenario
lexicon_skeleton = build_lexicon_skeleton(graph)
with open("./{}/{}_lexicon.json".format(game_dir_name, game_dir_name), "w") as outfile:
    outfile.write(json.dumps(lexicon_skeleton, indent=4))


# get subgraphs for each entity
subgraphs = select_subgraphs(graph)

write_graph_to_dot(graph, "{}/{}_entities.dot".format(game_dir_name, game_dir_name))
# write_graph_to_png(graph, "{}/{}_entities.png".format(game_dir_name, game_dir_name))
# write_graph_to_svg(graph, "{}/{}_entities.svg".format(game_dir_name, game_dir_name))

# then also build one FULL graph for each entity
for e in result:
    #  get entity name for file naming
    name = e['Entity']

    # build graph and save to dot and png
    g = build_graph([e])
    write_graph_to_dot(g, "{}/full_graphs/dot/{}.dot".format(game_dir_name, name))
    write_graph_to_png(g, "{}/full_graphs/png/{}.png".format(game_dir_name, name))
    write_graph_to_svg(g, "{}/full_graphs/svg/{}.svg".format(game_dir_name, name))


for s in subgraphs:
    write_graph_to_dot(subgraphs[s], "{}/subgraphs/dot/{}_subgraph.dot".format(game_dir_name, s))
    write_graph_to_png(subgraphs[s], "{}/subgraphs/png/{}_subgraph.png".format(game_dir_name, s))
    write_graph_to_svg(subgraphs[s], "{}/subgraphs/svg/{}_subgraph.svg".format(game_dir_name, s))