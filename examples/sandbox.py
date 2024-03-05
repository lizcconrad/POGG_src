import yaml
from delphin import ace, mrs
from delphin.codecs import simplemrs
import GG.mrs_util
import pprint

# Load elements from global config
global_config = yaml.safe_load((open("../config_data/global_config.yml")))
grammar_location = global_config['ERG']

my_mrs = """[ TOP: h113
  INDEX: e110
  RELS: < [ unknown LBL: h112 ARG: x92 ARG0: e110 ]
          [ _on_p_loc LBL: h98 ARG0: e102 ARG1: x92 ARG2: x106 ]
          [ _the_q LBL: h109 ARG0: x106 RSTR: h107 BODY: h108 ]
          [ _left_n_of LBL: h101 ARG0: x106 ARG1: i100 ]
          [ def_explicit_q LBL: h98 ARG0: x92 RSTR: h96 BODY: h97 ]
          [ poss LBL: h94 ARG0: e91 ARG1: x92 ARG2: x87 ]
          [ compound LBL: h94 ARG0: e80 ARG1: x92 ARG2: x73 ]
          [ udef_q LBL: h79 ARG0: x73 RSTR: h77 BODY: h78 ]
          [ _left_n_of LBL: h75 ARG0: x73 ARG1: i74 ]
          [ _hand_n_1 LBL: h94 ARG0: x92 ]
          [ _the_q LBL: h90 ARG0: x87 RSTR: h88 BODY: h89 ]
          [ _player_n_of LBL: h86 ARG0: x87 ARG1: i85 ] >
  HCONS: < h107 qeq h101 h77 qeq h75 h88 qeq h86 h96 qeq h94 h113 qeq h112 > ]"""
my_mrs_obj = simplemrs.decode(my_mrs)

result_1 = """[ TOP: h0
  INDEX: e2 [ e SF: prop ]
  RELS: < [ unknown<0:34> LBL: h1 ARG: x4 [ x PERS: 3 NUM: sg IND: + ] ARG0: e2 ]
          [ _the_q<0:3> LBL: h5 ARG0: x6 [ x PERS: 3 NUM: sg IND: + ] RSTR: h7 BODY: h8 ]
          [ _player_n_of<4:10> LBL: h9 ARG0: x6 ARG1: i10 ]
          [ def_explicit_q<10:12> LBL: h11 ARG0: x4 RSTR: h12 BODY: h13 ]
          [ poss<10:12> LBL: h14 ARG0: e15 [ e SF: prop TENSE: untensed MOOD: indicative PROG: - PERF: - ] ARG1: x4 ARG2: x6 ]
          [ compound<13:22> LBL: h14 ARG0: e16 [ e SF: prop TENSE: untensed MOOD: indicative PROG: - PERF: - ] ARG1: x4 ARG2: x17 [ x IND: + ] ]
          [ udef_q<13:17> LBL: h18 ARG0: x17 RSTR: h19 BODY: h20 ]
          [ _left_n_of<13:17> LBL: h21 ARG0: x17 ARG1: i22 ]
          [ _hand_n_1<18:22> LBL: h14 ARG0: x4 ]
          [ _on_p_loc<23:25> LBL: h14 ARG0: e23 [ e SF: prop TENSE: untensed MOOD: indicative PROG: - PERF: - ] ARG1: x4 ARG2: x24 [ x PERS: 3 NUM: sg IND: + ] ]
          [ _the_q<26:29> LBL: h25 ARG0: x24 RSTR: h26 BODY: h27 ]
          [ _left_n_of<30:34> LBL: h28 ARG0: x24 ARG1: i29 ] >
  HCONS: < h0 qeq h1 h7 qeq h9 h12 qeq h14 h19 qeq h21 h26 qeq h28 > ]"""
erg_mrs_obj = simplemrs.decode(result_1)


var_dicts = GG.mrs_util.find_discrepancy(erg_mrs_obj, my_mrs_obj)
# pp = pprint.PrettyPrinter(depth=4)
# # pp.pprint(var_dicts[0][0])
# # pp.pprint(var_dicts[0][1])
#
# s1_var_dict = var_dicts[0][0]
# s1_pred_arg_dict = var_dicts[0][1]
#
# s2_var_dict = var_dicts[1][0]
# s2_pred_arg_dict = var_dicts[1][1]
#
# # for each variable in s1...
# for var in s1_var_dict:
#     # ... get each ARG it fills ...
#     # just a list of ARGs filled by the variable
#     target_equivalencies = set()
#
#     # dict of every variable the created (or other) SSEMENT has for the target ARGs
#     # ideally should end up with one key only, but if not, there's a missing equivalency
#     actual_equivalencies = {}
#     for pred in s1_var_dict[var]:
#         for arg in s1_var_dict[var][pred]:
#             pred_arg = "{}__{}".format(pred, arg)
#             target_equivalencies.add(pred_arg)
#
#             actual_var = s2_pred_arg_dict[pred][arg]
#             if actual_var not in actual_equivalencies:
#                 actual_equivalencies[actual_var] = set()
#                 actual_equivalencies[actual_var].add("{}__{}".format(pred, arg))
#             else:
#                 actual_equivalencies[actual_var].add("{}__{}".format(pred, arg))
#             # add any other equivalencies with actual_var
#             # this is technically redundant but this will catch those that are equivalent that *shouldn't* be
#             for pred2 in s2_var_dict[actual_var]:
#                 for arg2 in s2_var_dict[actual_var][pred2]:
#                     actual_equivalencies[actual_var].add("{}__{}".format(pred, arg))
#
#
#     # check set equivalency
#     if len(actual_equivalencies) == 1:
#         key = list(actual_equivalencies.keys())[0]
#         if target_equivalencies == actual_equivalencies[key]:
#             continue
#             # print("PASS...")
#             # print("Target SSEMENT equivalencies:{}\n".format(target_equivalencies))
#             # print("Composed SSEMENT equivalencies:{}\n".format(actual_equivalencies[key]))
#         else:
#             print("Composed SSEMENT has additional equivalencies...")
#             print("Target SSEMENT equivalencies:{}\n".format(target_equivalencies))
#             print("Composed SSEMENT equivalencies:{}\n".format(actual_equivalencies[key]))
#     else:
#         print("Composed SSEMENT doesn't contain appropriate equivalencies...")
#         print("Target SSEMENT equivalencies:{}\n".format(target_equivalencies))
#         print("Composed SSEMENT equivalencies:{}\n".format(actual_equivalencies))


    # check s2 for each of those ARGs...
    # make set ??? of variables for those ARGs in s2
    # if set is len(1) then it's fine ...
    # if not ... say these args are identical in s1 but not s2



# # ... TESTING ZONE ... ##
# with ace.ACEParser(grammar_location) as parser:
#     response = parser.interact("the player's left hand on the left")
#     for r in response.results():
#         mrs_obj = simplemrs.decode(r['mrs'])
#
#         # test isomorphic
#         mrs.is_isomorphic(mrs_obj, my_mrs_obj, properties=False)
#
#         var_dicts = GG.mrs_util.find_discrepancy(my_mrs_obj, mrs_obj)
#         pp = pprint.PrettyPrinter(depth=4)
#         # pp.pprint(var_dicts[0])
#         # pp.pprint(var_dicts[1])
#
#         mrs_string = simplemrs.encode(mrs_obj, indent=True)
#         print("{}\n".format(mrs_string))

