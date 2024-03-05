# File that contains various common forms of composition, refer to the function names here in your lexicon file
# ORGANIZED: 01/04/2024
# DOCUMENTED: 01/04/2024
from GG.mrs_algebra import create_base_SSEMENT, op_scopal, op_non_scopal_lbl_shared, op_non_scopal_lbl_unshared
import GG.mrs_util
import re


# ENTITY FUNCTIONS
# Each of these simply passes the information to `mrs_algebra.create_base_SSEMENT`,
# but they serve as wrappers because the graph-to-MRS algorithm, and the user's lexicon,
# should only refer to things in composition_library, not the mrs_algebra directly.
def basic(predicate, variables={}, index_arg='ARG0'):
    return create_base_SSEMENT(predicate, variables, index_arg)


# index_arg=ARG1 by default, because the ARG1 of an adjective is the thing it modifies,
# which is typically what we want as the semantic index after composition with an adjective
def adjective_ssement(predicate, variables={}, index_arg='ARG1'):
    return create_base_SSEMENT(predicate, variables, index_arg)


# for adjectival properties that are represented in the graph as a boolean value
# the predicate to include in the MRS will depend on the boolean value
# returns TWO ssements that will be chosen from at the point of composition...
# also returns the composition function to be used...
def boolean_adjective_ssement(predicates, variables={}, index_arg='ARG1'):
    true_ssement = adjective_ssement(predicates[0], variables, index_arg)
    false_ssement = adjective_ssement(predicates[1], variables, index_arg)
    return true_ssement, false_ssement, adjective


# for verbal (passive participle) properties that are represented in the graph as a boolean value
# the predicate to include in the MRS will depend on the boolean value
# may appear as ["_unverb_v_1", "_verb_v_1"] OR [("_un-_a_neg, "_verb_v_1"), "_verb_v_1"]
# if the second one, have to apply the negation composition before creating the SSEMENT
# returns TWO ssements that will be chosen from at the point of composition...
# also returns the composition function to be used...
def boolean_pass_part_ssement(predicates, variables={}, index_arg='ARG0'):
    if type(predicates[0]) is list:
        prefix_ssement = basic(predicates[0][0], {}, 'ARG1')
        verbal_ssement = verb_ssement(predicates[0][1], variables, index_arg)
        # plug ARG1 of prefix with ARG0 of verbal, share labels
        true_ssement = prefix(prefix_ssement, verbal_ssement)
    else:
        true_ssement = verb_ssement(predicates[0], variables, index_arg)

    if type(predicates[1]) is list:
        prefix_ssement = basic(predicates[1][0])
        verbal_ssement = verb_ssement(predicates[1][1], variables, index_arg)
        # plug ARG1 of prefix with ARG0 of verbal, share labels
        false_ssement = prefix(prefix_ssement, verbal_ssement)
    else:
        false_ssement = verb_ssement(predicates[1], variables, index_arg)

    return true_ssement, false_ssement, passive_participle


def noun_ssement(predicate, variables={}, index_arg='ARG0'):
    return create_base_SSEMENT(predicate, variables, index_arg)


# index_arg=ARG1 by default, because the ARG1 of a preposition is the thing the preposition modifies,
# which is typically what we want as the semantic index after composition with a preposition
def preposition_ssement(predicate, variables={}, index_arg='ARG1'):
    return create_base_SSEMENT(predicate, variables, index_arg)


def pronoun_ssement(variables={}, index_arg='ARG0'):
    pron = create_base_SSEMENT('pron', variables, index_arg)
    pronoun_q = quant_ssement('pronoun_q')

    return op_scopal(pronoun_q, pron)


def quant_ssement(predicate, variables={}, index_arg='ARG0'):
    return create_base_SSEMENT(predicate, variables, index_arg)


def verb_ssement(predicate, variables={}, index_arg='ARG0'):
    return create_base_SSEMENT(predicate, variables, index_arg)


# COMPOSITION FUNCTIONS
def adjective(adj_ssement, nom_ssement):
    return op_non_scopal_lbl_shared(adj_ssement, nom_ssement, 'ARG1')


def boolean(boolean_ssements, nom_ssement, child_ssement):
    """
    Compose using a boolean property
    :param boolean_ssements: tuple of SSEMENTs, first is what to use if child_value is true, second if false
    :type boolean_ssements: (SSEMENT, SSEMENT)
    :param nom_ssement: SSEMENT being modified by boolean property
    :type nom_ssement: SSEMENT
    :param child_ssement: SSEMENT where predicate label *is* the boolean value...
    :type child_ssement: SSEMENT
    """
    if child_ssement.rels[0].predicate == '_true_a_of':
        chosen_bool = boolean_ssements[0]
    elif child_ssement.rels[0].predicate == '_false_a_of':
        chosen_bool = boolean_ssements[1]
    # if the child doesn't have a true/false predicate, raise an error for the purposes of evaluation
    # i *could* just return the nom, but this will incorrectly result in the evaluation saying the edge worked
    else:
        raise RuntimeError("Boolean property edge doesn't point to boolean value")

    # the third thing returned from boolean node functions is the appropriate composition function
    boolean_function = boolean_ssements[2]
    return boolean_function(chosen_bool, nom_ssement)




def compound(nonhead_ssement, head_ssement):
    udef = create_base_SSEMENT('udef_q')
    udef_nonhead = op_scopal(udef, nonhead_ssement)

    compound_ssement = create_base_SSEMENT('compound', {}, 'ARG1')
    compound_ARG2 = op_non_scopal_lbl_unshared(compound_ssement, udef_nonhead, 'ARG2')

    compound_final = op_non_scopal_lbl_shared(compound_ARG2, head_ssement, 'ARG1')
    return compound_final


def descriptor(descriptor_ssement, nom_ssement):
    """
    Used for properties whose value can be adjectival or verbal
    e.g. a "descriptor" may be "red" or "locked"
    For adjectives, the plugged hole is ARG1 but for verbal descriptors the plugged hole is ARG2
    :param descriptor_ssement: descriptor SSEMENT
    :type descriptor_ssement: SSEMENT
    :param nom_ssement: SSEMENT being described
    :type nom_ssement: SSEMENT
    :return:
    :rtype:
    """
    # TODO: what i can do is some sort of check to see if the index of the descriptor is eq to the ARG0 of some verb
    # TODO: but instead I'm just gonna check if it's a simple adjective and assume passive_participle otherwise
    # find the index of the descriptor
    descriptor_index = descriptor_ssement.index

    # get eq with descriptor_index if it exists
    eq_set = set([descriptor_index])
    if descriptor_ssement.eqs:
        for eq in descriptor_ssement.eqs:
            if descriptor_index in eq:
                eq_set.update(eq)

    # look for vrebal relation with ARG0 in the eq_set
    for r in descriptor_ssement.rels:
        # if the ARG0 is in the eq_set, then assume we have a verbal descriptor
        if r.args['ARG0'] in eq_set and re.match('_[A-z]+_v_', r.predicate):
            return passive_participle(descriptor_ssement, nom_ssement)

    # if it never succeeds, assume adjectival
    return adjective(descriptor_ssement, nom_ssement)


# the locked door
def passive_participle(v_ssement, nom_ssement):
    # need a new SSEMENT from the verb. the default behavior is that ARG0 is index.
    # this is appropriate for verbs, generally, but in this construction ARG2 is the index
    verb_index = v_ssement.index
    # it's possible that the verb's current index is eq to the fragment's index, so create a set of possibilities
    # this happens with things like "_un-_a_neg" + "_know_v_1" because the fragment's INDEX is ARG1 of the prefix
    # which is eq to the verb's ARG0, but the verb's ARG0 isn't the actual INDEX rn so we have to find it
    verb_index_set = set()
    verb_index_set.add(verb_index)
    if v_ssement.eqs:
        for eq in v_ssement.eqs:
            if verb_index in eq:
                for elem in eq:
                    verb_index_set.add(elem)

    # whether ARG2 or ARG1 needs to be the index
    # e.g. "the broken mirror" ... ARG2 of break is the mirror
    # but "the glowing mirror" ... ARG1 of glow is the mirror
    has_ARG2 = False
    verb_rel_index = None
    for i, r in enumerate(v_ssement.rels):
        if r.id in verb_index_set:
            verb_label = r.predicate
            verb_rel_index = i

            if 'ARG2' in r.args:
                has_ARG2 = True

            continue

    # if there is an ARG2, set that as the index
    if has_ARG2:
        part_ssement = GG.mrs_util.update_index(v_ssement, verb_label, 'ARG2')
        final = op_non_scopal_lbl_shared(part_ssement, nom_ssement, 'ARG2')
    else:
        # [e PROG: bool]
        # TODO: this is kinda ugly lol
        # this is an "ing" construction so the ARG0 has to be [e PROG: bool] so it's not forced to be a value of -
        # get variable of ARG0 of verb relation
        arg0_var = v_ssement.predications[verb_rel_index].args['ARG0']
        v_ssement.variables[arg0_var]["PROG"] = "bool"
        part_ssement = GG.mrs_util.update_index(v_ssement, verb_label, 'ARG1')
        final = op_non_scopal_lbl_shared(part_ssement, nom_ssement, 'ARG1')

    return final


def possessive(possessor_ssement, possessed_ssement):
    # check if possessor is quantified
    if not GG.mrs_util.check_if_quantified(possessor_ssement):
        quant_possessor = GG.mrs_util.wrap_with_quantifier(possessor_ssement)
    else:
        quant_possessor = possessor_ssement

    # mark possessed argument as INDEX
    poss_rel = basic('poss', {}, 'ARG1')
    # plug ARG1 with possessor
    poss_possessed_plugged = op_non_scopal_lbl_shared(poss_rel, possessed_ssement, 'ARG1')
    # plug ARG2 with possessed
    poss_possessor_plugged = op_non_scopal_lbl_unshared(poss_possessed_plugged, quant_possessor, 'ARG2')

    # final quantify now that both are plugged
    # TODO: I CAN'T DO THIS IN CASE OF FURTHER QUANTIFIERS !!!
    # def_explicit_q = quant_ssement('def_explicit_q')
    # quant_poss_possessed_plugged = quantify(def_explicit_q, poss_possessor_plugged)

    return poss_possessor_plugged


def possessive_old(possessor_ssement, possessed_ssement):
    # quantify the possessed
    quant_possessed = quantify(quant_ssement('def_explicit_q'), possessed_ssement)
    # check if possessor is quantified
    if not GG.mrs_util.check_if_quantified(possessor_ssement):
        quant_possessor = GG.mrs_util.wrap_with_quantifier(possessor_ssement)
    else:
        quant_possessor = possessor_ssement

    # mark possessed argument as INDEX
    poss_rel = basic('poss', {}, 'ARG1')
    # plug ARG1 with possessor
    poss_possessed_plugged = op_non_scopal_lbl_shared(poss_rel, quant_possessed, 'ARG1')
    poss_possessor_plugged = op_non_scopal_lbl_unshared(poss_possessed_plugged, quant_possessor, 'ARG2')
    return poss_possessor_plugged


def prefix(prefix_ssement, head_ssement):
    # append a prefix to a word and then set the holes of the resulting SSEMENT to be the holes of the head_ssement
    # TODO: basically the holes get lost because of the way I implemented the algebra ... I only pass on functor holes
    prefixed_ssement = op_non_scopal_lbl_shared(prefix_ssement, head_ssement, 'ARG1')
    # update holes... kinda cringe but whatever
    prefixed_ssement.holes = head_ssement.holes
    return prefixed_ssement


def preposition(prep_ssement, head_ssement, nonhead_ssement):
    # QUANTIFIER CHECK
    # TODO: take this out and put it somewhere, but for now, just do a check and quantify if it fails
    if not GG.mrs_util.check_if_quantified(nonhead_ssement):
        quant_nonhead_ssement = GG.mrs_util.wrap_with_quantifier(nonhead_ssement)
    else:
        quant_nonhead_ssement = nonhead_ssement

    preposition_ARG2 = op_non_scopal_lbl_unshared(prep_ssement, quant_nonhead_ssement, 'ARG2')
    preposition_ARG1 = op_non_scopal_lbl_shared(preposition_ARG2, head_ssement, 'ARG1')
    return preposition_ARG1


def quantify(quant_ssement, unquant_ssement):
    return op_scopal(quant_ssement, unquant_ssement)


# X is east of Y
def relative_direction(direction_ssement, figure_ssement, ground_ssement):
    # QUANTIFIER CHECK
    # TODO: take this out and put it somewhere, but for now, just do a check and quantify if it fails
    if not GG.mrs_util.check_if_quantified(ground_ssement):
        quant_ground_ssement = GG.mrs_util.wrap_with_quantifier(ground_ssement)
    else:
        quant_ground_ssement = ground_ssement

    # figure ssement must be unquantified
    # ground ssement must be quantified

    # create base SSEMENTs for direction and place_n
    place = create_base_SSEMENT('place_n')

    # plug ARG2 of the direction_ssement with ground_ssement (i.e. what figure_ssement is directionally relative to)
    direction_ARG2_plugged = op_non_scopal_lbl_unshared(direction_ssement, quant_ground_ssement, 'ARG2')

    # plug ARG1 of direction_ssement with place_n
    direction_place = op_non_scopal_lbl_shared(direction_ARG2_plugged, place, 'ARG1')

    # use implicit quantifier for SSEMENT thus far
    def_imp = create_base_SSEMENT('def_implicit_q')
    def_imp_direction_place = op_scopal(def_imp, direction_place)

    # create loc_nonsp SSEMENT and plug ARG1 with figure_ssement
    loc_nonsp = create_base_SSEMENT('loc_nonsp', {}, 'ARG1')
    loc_nonsp_ARG1_plugged = op_non_scopal_lbl_shared(loc_nonsp, figure_ssement, 'ARG1')

    # plug ARG2 of loc_nonsp with the direction+relative SSEMENT
    final_dir = op_non_scopal_lbl_unshared(loc_nonsp_ARG1_plugged, def_imp_direction_place, 'ARG2')

    return final_dir



