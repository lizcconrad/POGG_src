import os
import yaml
from delphin import ace, mrs
from delphin.codecs import simplemrs
import POGG.mrs_util
from tabulate import tabulate

# Load elements from global config
global_config = yaml.safe_load((open("../config_data/global_config.yml")))
grammar_location = global_config['ERG']

error_analysis_path = "/POGG_data/development/Heal_TheTrees/results/error_analysis/"
error_analysis_filename = "uncountble_error.txt"

# type (a possible) desired string to input to ERG for parsing
desired_output = "the uncountable grass"

# PASTE BROKEN MRS HERE
composed_mrs_string = """
[ TOP: h15
  INDEX: e12
  RELS: < [ unknown LBL: h14 ARG: x8 ARG0: e12 ]
          [ def_udef_a_q LBL: h11 ARG0: x8 RSTR: h9 BODY: h10 ]
          [ _un-_a_neg LBL: h1 ARG0: i5 ARG1: x8 ]
          [ _countable_a_1 LBL: h1 ARG0: e2 ARG1: x8 ]
          [ _grass_n_1 LBL: h1 ARG0: x8 ] >
  HCONS: < h9 qeq h1 h15 qeq h14 > ]
"""
composed_mrs_obj = simplemrs.decode(composed_mrs_string)


with open(os.path.join(error_analysis_path, error_analysis_filename), 'w') as error_analysis_file:
    error_analysis_file.write("MRS WITH ERROR:\n{}\n".format(composed_mrs_string))

    # attempt generation
    # results = POGG.mrs_util.generate(composed_mrs_string)
    # error_analysis_file.write("GENERATED RESULTS ... \n")
    # for r in results:
    #     error_analysis_file.write(r.get('surface') + "\n")

    error_analysis_file.write("\nDESIRED STRING: {}\n".format(desired_output))
    # parse desired string with ERG
    with ace.ACEParser(grammar_location) as parser:
        response = parser.interact(desired_output)
        for i, r in enumerate(response.results()):
            target_mrs_obj = simplemrs.decode(r['mrs'])

            # find discrepancies between result and broken mrs
            error_analysis_file.write("------------------------------------------------------------------------------\n")
            error_analysis_file.write("TARGET SSEMENT #{}:\n{}\n\n".format(i, simplemrs.encode(target_mrs_obj, indent=True)))
            POGG.mrs_util.find_discrepancy(target_mrs_obj, composed_mrs_obj, error_analysis_file)
            error_analysis_file.write("------------------------------------------------------------------------------\n")


