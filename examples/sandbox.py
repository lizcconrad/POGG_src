import yaml
from delphin import ace, mrs
from delphin.codecs import simplemrs
# import POGG.mrs_util
import pprint

# Load elements from global config
global_config = yaml.safe_load((open("../config_data/global_config.yml")))
grammar_location = global_config['ERG']

# PARSER SANDBOX
# with ace.ACEParser(grammar_location) as parser, ace.ACEGenerator(grammar_location, ['-r', 'root_frag']) as generator:
#     parser_response = parser.interact("the locked box of cookies")
#     for r in parser_response.results():
#         mrs_obj = simplemrs.decode(r['mrs'])
#         print(simplemrs.encode(mrs_obj, indent=True))



locked_box = """[ TOP: h0
  INDEX: e2 [ e SF: prop ]
  RELS: < [ unknown<0:14> LBL: h1 ARG: x4 [ x PERS: 3 NUM: sg IND: + ] ARG0: e2 ]
          [ _the_q<0:3> LBL: h5 ARG0: x4 RSTR: h6 BODY: h7 ]
          [ _lock_v_cause<4:10> LBL: h8 ARG0: e9 [ e SF: prop TENSE: untensed MOOD: indicative PROG: bool PERF: - ] ARG1: i10 ARG2: x4 ]
          [ _box_n_of<11:14> LBL: h8 ARG0: x4 ARG1: i11 ] >
  HCONS: < h0 qeq h1 h6 qeq h8 >
  ICONS: < e9 topic x4 > ]"""

locked_box_of_cookies = """[ TOP: h0
  INDEX: e2 [ e SF: prop ]
  RELS: < [ unknown<0:25> LBL: h1 ARG: x4 [ x PERS: 3 NUM: sg IND: + ] ARG0: e2 ]
          [ _the_q<0:3> LBL: h5 ARG0: x4 RSTR: h6 BODY: h7 ]
          [ _lock_v_cause<4:10> LBL: h8 ARG0: e9 [ e SF: prop TENSE: untensed MOOD: indicative PROG: bool PERF: - ] ARG1: i10 ARG2: x4 ]
          [ _box_n_of<11:14> LBL: h8 ARG0: x4 ARG1: x11 [ x PERS: 3 NUM: pl IND: + ] ]
          [ udef_q<18:25> LBL: h12 ARG0: x11 RSTR: h13 BODY: h14 ]
          [ _cookie_n_1<18:25> LBL: h15 ARG0: x11 ] >
  HCONS: < h0 qeq h1 h6 qeq h8 h13 qeq h15 >
  ICONS: < e9 topic x4 > ]"""

tbd = """[ TOP: h0
  INDEX: e2 [ e SF: prop ]
  RELS: < [ unknown<0:25> LBL: h1 ARG: x4 [ x PERS: 3 NUM: sg IND: + ] ARG0: e2 ]
          [ _the_q<0:3> LBL: h5 ARG0: x4 RSTR: h6 BODY: h7 ]
          [ _lock_v_cause<4:10> LBL: h8 ARG0: e9 [ e SF: prop TENSE: untensed MOOD: indicative PROG: bool PERF: - ] ARG1: x11 ARG2: x4 ]
          [ _box_n_of<11:14> LBL: h8 ARG0: x4 ARG1: i12 [ x PERS: 3 NUM: pl IND: + ] ]
          [ udef_q<18:25> LBL: h12 ARG0: x11 RSTR: h13 BODY: h14 ]
          [ _cookie_n_1<18:25> LBL: h15 ARG0: x11 ] >
  HCONS: < h0 qeq h1 h6 qeq h8 h13 qeq h15 >
  ICONS: < e9 topic x4 > ]"""



generate_from = [locked_box, locked_box_of_cookies, tbd]

# GENERATOR SANDBOX
with ace.ACEGenerator(grammar_location, ['-r', 'root_frag']) as generator:
        for g in generate_from:
            print("GENERATING FROM ... ")
            print(g)
            generator_response = generator.interact(g)
            print("GENERATED RESULTS ... ")
            for r in generator_response.results():
                print(r.get('surface'))


# # PARSE & GENERATE SANDBOX
# with ace.ACEParser(grammar_location) as parser, ace.ACEGenerator(grammar_location, ['-r', 'root_frag']) as generator:
#     parser_response = parser.interact("the locked box")
#     for r in parser_response.results():
#         mrs_obj = simplemrs.decode(r['mrs'])
#         print(simplemrs.encode(mrs_obj, indent=True))
#     generator_response = generator.interact(simplemrs.encode(mrs_obj, indent=True))
#     print("GENERATED RESULTS ... ")
#     for r in generator_response.results():
#         print(r.get('surface'))






