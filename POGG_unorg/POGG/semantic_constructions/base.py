# File that contains various common forms of composition, refer to the function names here in your lexicon file
# ORGANIZED: 01/04/2024
# DOCUMENTED: 01/04/2024
import POGG.mrs_algebra
import POGG.mrs_util
import re


# ENTITY FUNCTIONS
# Each of these simply passes the information to `mrs_algebra.POGG.mrs_algebra.create_base_SEMENT`,
# but they serve as wrappers because the graph-to-MRS algorithm, and the user's lexicon,
# should only refer to things in composition_library, not the mrs_algebra directly.
def basic(predicate, variables={}, index_arg='ARG0'):
    return POGG.mrs_algebra.create_base_SEMENT(predicate, variables, index_arg)


# index_arg=ARG1 by default, because the ARG1 of an adjective is the thing it modifies,
# which is typically what we want as the semantic index after composition with an adjective
def adjective_SEMENT(predicate, variables={}, index_arg='ARG1'):
    return POGG.mrs_algebra.create_base_SEMENT(predicate, variables, index_arg)


def noun_SEMENT(predicate, variables={}, index_arg='ARG0'):
    return POGG.mrs_algebra.create_base_SEMENT(predicate, variables, index_arg)


# index_arg=ARG1 by default, because the ARG1 of a preposition is the thing the preposition modifies,
# which is typically what we want as the semantic index after composition with a preposition
def preposition_SEMENT(predicate, variables={}, index_arg='ARG1'):
    return POGG.mrs_algebra.create_base_SEMENT(predicate, variables, index_arg)


def pronoun_SEMENT(variables={}, index_arg='ARG0'):
    pron = POGG.mrs_algebra.create_base_SEMENT('pron', variables, index_arg)
    pronoun_q = quant_SEMENT('pronoun_q')

    return POGG.mrs_algebra.op_scopal(pronoun_q, pron)


def quant_SEMENT(predicate, variables={}, index_arg='ARG0'):
    return POGG.mrs_algebra.create_base_SEMENT(predicate, variables, index_arg)


def verb_SEMENT(predicate, variables={}, index_arg='ARG0'):
    return POGG.mrs_algebra.create_base_SEMENT(predicate, variables, index_arg)


# COMPOSITION FUNCTIONS
def adjective(adj_SEMENT, nom_SEMENT):
    return POGG.mrs_algebra.op_non_scopal_lbl_shared(adj_SEMENT, nom_SEMENT, 'ARG1')



def compound(nonhead_SEMENT, head_SEMENT):
    udef = POGG.mrs_algebra.create_base_SEMENT('udef_q')
    udef_nonhead = POGG.mrs_algebra.op_scopal(udef, nonhead_SEMENT)

    compound_SEMENT = POGG.mrs_algebra.create_base_SEMENT('compound', {}, 'ARG1')
    compound_ARG2 = POGG.mrs_algebra.op_non_scopal_lbl_unshared(compound_SEMENT, udef_nonhead, 'ARG2')

    compound_final = POGG.mrs_algebra.op_non_scopal_lbl_shared(compound_ARG2, head_SEMENT, 'ARG1')
    return compound_final


# the locked door
def passive_participle(v_SEMENT, nom_SEMENT):
    # need a new SEMENT from the verb. the default behavior is that ARG0 is index.
    # this is appropriate for verbs, generally, but in this construction ARG2 is the index
    verb_index = v_SEMENT.index
    # it's possible that the verb's current index is eq to the fragment's index, so create a set of possibilities
    # this happens with things like "_un-_a_neg" + "_know_v_1" because the fragment's INDEX is ARG1 of the prefix
    # which is eq to the verb's ARG0, but the verb's ARG0 isn't the actual INDEX rn so we have to find it
    verb_index_set = set()
    verb_index_set.add(verb_index)
    if v_SEMENT.eqs:
        for eq in v_SEMENT.eqs:
            if verb_index in eq:
                for elem in eq:
                    verb_index_set.add(elem)

    # whether ARG2 or ARG1 needs to be the index
    # e.g. "the broken mirror" ... ARG2 of break is the mirror
    # but "the glowing mirror" ... ARG1 of glow is the mirror
    has_ARG2 = False
    verb_rel_index = None
    for i, r in enumerate(v_SEMENT.rels):
        if r.id in verb_index_set:
            verb_label = r.predicate
            verb_rel_index = i

            if 'ARG2' in r.args:
                has_ARG2 = True

            continue

    # if there is an ARG2, set that as the index
    if has_ARG2:
        part_SEMENT = POGG.mrs_util.update_index(v_SEMENT, verb_label, 'ARG2')
        final = POGG.mrs_algebra.op_non_scopal_lbl_shared(part_SEMENT, nom_SEMENT, 'ARG2')
    else:
        # [e PROG: bool]
        # TODO: this is kinda ugly lol
        # this is an "ing" construction so the ARG0 has to be [e PROG: bool] so it's not forced to be a value of -
        # get variable of ARG0 of verb relation
        arg0_var = v_SEMENT.predications[verb_rel_index].args['ARG0']
        v_SEMENT.variables[arg0_var]["PROG"] = "bool"
        part_SEMENT = POGG.mrs_util.update_index(v_SEMENT, verb_label, 'ARG1')
        final = POGG.mrs_algebra.op_non_scopal_lbl_shared(part_SEMENT, nom_SEMENT, 'ARG1')

    return final


def possessive(possessor_SEMENT, possessed_SEMENT):
    # check if possessor is quantified
    if not POGG.mrs_util.check_if_quantified(possessor_SEMENT):
        quant_possessor = POGG.mrs_util.wrap_with_quantifier(possessor_SEMENT)
    else:
        quant_possessor = possessor_SEMENT

    # mark possessed argument as INDEX
    poss_rel = basic('poss', {}, 'ARG1')
    # plug ARG1 with possessor
    poss_possessed_plugged = POGG.mrs_algebra.op_non_scopal_lbl_shared(poss_rel, possessed_SEMENT, 'ARG1')
    # plug ARG2 with possessed
    poss_possessor_plugged = POGG.mrs_algebra.op_non_scopal_lbl_unshared(poss_possessed_plugged, quant_possessor, 'ARG2')

    # final quantify now that both are plugged
    # TODO: I CAN'T DO THIS IN CASE OF FURTHER QUANTIFIERS !!!
    # def_explicit_q = quant_SEMENT('def_explicit_q')
    # quant_poss_possessed_plugged = quantify(def_explicit_q, poss_possessor_plugged)

    return poss_possessor_plugged



def prefix(prefix_SEMENT, head_SEMENT):
    # append a prefix to a word and then set the holes of the resulting SEMENT to be the holes of the head_SEMENT
    # TODO: basically the holes get lost because of the way I implemented the algebra ... I only pass on functor holes
    prefixed_SEMENT = POGG.mrs_algebra.op_non_scopal_lbl_shared(prefix_SEMENT, head_SEMENT, 'ARG1')
    # update holes... kinda cringe but whatever
    prefixed_SEMENT.holes = head_SEMENT.holes
    return prefixed_SEMENT


def preposition(prep_SEMENT, head_SEMENT, nonhead_SEMENT):
    # QUANTIFIER CHECK
    # TODO: take this out and put it somewhere, but for now, just do a check and quantify if it fails
    if not POGG.mrs_util.check_if_quantified(nonhead_SEMENT):
        quant_nonhead_SEMENT = POGG.mrs_util.wrap_with_quantifier(nonhead_SEMENT)
    else:
        quant_nonhead_SEMENT = nonhead_SEMENT

    preposition_ARG2 = POGG.mrs_algebra.op_non_scopal_lbl_unshared(prep_SEMENT, quant_nonhead_SEMENT, 'ARG2')
    preposition_ARG1 = POGG.mrs_algebra.op_non_scopal_lbl_shared(preposition_ARG2, head_SEMENT, 'ARG1')
    return preposition_ARG1


def quantify(quant_SEMENT, unquant_SEMENT):
    return POGG.mrs_algebra.op_scopal(quant_SEMENT, unquant_SEMENT)


# X is east of Y
def relative_direction(direction_SEMENT, figure_SEMENT, ground_SEMENT):
    # QUANTIFIER CHECK
    # TODO: take this out and put it somewhere, but for now, just do a check and quantify if it fails
    if not POGG.mrs_util.check_if_quantified(ground_SEMENT):
        quant_ground_SEMENT = POGG.mrs_util.wrap_with_quantifier(ground_SEMENT)
    else:
        quant_ground_SEMENT = ground_SEMENT

    # figure SEMENT must be unquantified
    # ground SEMENT must be quantified

    # create base SEMENTs for direction and place_n
    place = POGG.mrs_algebra.create_base_SEMENT('place_n')

    # plug ARG2 of the direction_SEMENT with ground_SEMENT (i.e. what figure_SEMENT is directionally relative to)
    direction_ARG2_plugged = POGG.mrs_algebra.op_non_scopal_lbl_unshared(direction_SEMENT, quant_ground_SEMENT, 'ARG2')

    # plug ARG1 of direction_SEMENT with place_n
    direction_place = POGG.mrs_algebra.op_non_scopal_lbl_shared(direction_ARG2_plugged, place, 'ARG1')

    # use implicit quantifier for SEMENT thus far
    def_imp = POGG.mrs_algebra.create_base_SEMENT('def_implicit_q')
    def_imp_direction_place = POGG.mrs_algebra.op_scopal(def_imp, direction_place)

    # create loc_nonsp SEMENT and plug ARG1 with figure_SEMENT
    loc_nonsp = POGG.mrs_algebra.create_base_SEMENT('loc_nonsp', {}, 'ARG1')
    loc_nonsp_ARG1_plugged = POGG.mrs_algebra.op_non_scopal_lbl_shared(loc_nonsp, figure_SEMENT, 'ARG1')

    # plug ARG2 of loc_nonsp with the direction+relative SEMENT
    final_dir = POGG.mrs_algebra.op_non_scopal_lbl_unshared(loc_nonsp_ARG1_plugged, def_imp_direction_place, 'ARG2')

    return final_dir



