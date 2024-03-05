# BUILDING LEXICON FROM FULL GRAPH
# ORGANIZED: N (MM/DD/YYYY)
# DOCUMENTED: N (MM/DD/YYYY)
import json
import os
from swiplserver import PrologMQI
from GG.graph_util import build_graph, select_subgraphs, write_graph_to_dot, write_graph_to_png, write_graph_to_svg
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
os.chdir("/Users/lizcconrad/Documents/PhD/GP2/GG_project/GG_data/test/")

# directory for current game
game_dir_name = "Scenario"

# build graph with all entities
graph = build_graph(result)

# build lexicon skeleton for scenario
lexicon_skeleton = build_lexicon_skeleton(graph)
with open("./{}/{}_lexicon.json".format(game_dir_name, game_dir_name), "w") as outfile:
    outfile.write(json.dumps(lexicon_skeleton, indent=4))
