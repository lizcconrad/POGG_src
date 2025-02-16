import POGG.semantic_constructions.base


# TODO: 02/07 ... create correct fxns here and also make like a "gen" vs "dataset specific" comp lib

# find the right function to create the SEMENT fragment for a node
def node_composition(node_lex_entry):
    # get fxn in composition library
    comp_fxn = getattr(POGG.composition_library, node_lex_entry.composition)
    return comp_fxn(node_lex_entry)


# Functions to create SEMENTs from scratch
def adjective(lex_entry):
    return POGG.semantic_constructions.semantic_constructions.adjective_SEMENT(lex_entry.pred_label)

def noun(lex_entry):
    return POGG.semantic_constructions.semantic_constructions.noun_SEMENT(lex_entry.pred_label)

def preposition(lex_entry):
    return POGG.semantic_constructions.semantic_constructions.preposition_SEMENT(lex_entry.pred_label)

def pronoun(lex_entry):
    var_dict = {}
    if hasattr(lex_entry, "person"):
        var_dict['PERS'] = lex_entry.person
    if hasattr(lex_entry, "number"):
        var_dict['NUM'] = lex_entry.number
    if hasattr(lex_entry, "gender"):
        var_dict['GEND'] = lex_entry.gender
    return POGG.semantic_constructions.semantic_constructions.pronoun_SEMENT(variables=var_dict)

def verb(lex_entry):
    return POGG.semantic_constructions.semantic_constructions.verb_SEMENT(lex_entry.pred_label)

def quantifier(lex_entry):
    return POGG.semantic_constructions.semantic_constructions.quant_SEMENT(lex_entry.pred_label)


# Functions to combine SEMENTs
def adjective_phrase(lex_entry, parent_sement, child_sement):
    if lex_entry.parent_role == "HEAD" and lex_entry.child_role == "MODIFIER":
        argument_sement = parent_sement
        functor_sement = child_sement
    elif lex_entry.parent_role == "MODIFIER" and lex_entry.child_role == "HEAD":
        argument_sement = child_sement
        functor_sement = parent_sement
    else:
        raise ValueError("""The lexical entry for '{}' must specify parent_role and child_role.
            For adjective_phrase, one must be HEAD and one must be MODIFIER.
            Current values:
            \tparent_role: {}
            \tchild_role: {}""".format(lex_entry.lex_id, lex_entry.parent_role, lex_entry.child_role))

    return POGG.semantic_constructions.semantic_constructions.adjective(functor_sement, argument_sement)
