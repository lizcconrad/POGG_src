import re
import POGG.semantic_constructions.base

# for adjectival properties that are represented in the graph as a boolean value
# the predicate to include in the MRS will depend on the boolean value
# returns TWO SEMENTs that will be chosen from at the point of composition...
# also returns the composition function to be used...
def boolean_adjective_SEMENT(predicates, variables={}, index_arg='ARG1'):
    true_SEMENT = POGG.semantic_constructions.base.adjective_SEMENT(predicates[0], variables, index_arg)
    false_SEMENT = POGG.semantic_constructions.base.adjective_SEMENT(predicates[1], variables, index_arg)
    return true_SEMENT, false_SEMENT, POGG.semantic_constructions.base.adjective


# for verbal (passive participle) properties that are represented in the graph as a boolean value
# the predicate to include in the MRS will depend on the boolean value
# may appear as ["_unverb_v_1", "_verb_v_1"] OR [("_un-_a_neg, "_verb_v_1"), "_verb_v_1"]
# if the second one, have to apply the negation composition before creating the SEMENT
# returns TWO SEMENTs that will be chosen from at the point of composition...
# also returns the composition function to be used...
def boolean_pass_part_SEMENT(predicates, variables={}, index_arg='ARG0'):
    if type(predicates[0]) is list:
        prefix_SEMENT = POGG.semantic_constructions.base.basic(predicates[0][0], {}, 'ARG1')
        verbal_SEMENT = POGG.semantic_constructions.base.verb_SEMENT(predicates[0][1], variables, index_arg)
        # plug ARG1 of prefix with ARG0 of verbal, share labels
        true_SEMENT = POGG.semantic_constructions.base.prefix(prefix_SEMENT, verbal_SEMENT)
    else:
        true_SEMENT = POGG.semantic_constructions.base.verb_SEMENT(predicates[0], variables, index_arg)

    if type(predicates[1]) is list:
        # TODO: this needs to set 'ARG1' as the index arg... i forgot to so it's gg
        prefix_SEMENT = POGG.semantic_constructions.base.basic(predicates[1][0])
        verbal_SEMENT = POGG.semantic_constructions.base.verb_SEMENT(predicates[1][1], variables, index_arg)
        # plug ARG1 of prefix with ARG0 of verbal, share labels
        false_SEMENT = POGG.semantic_constructions.base.prefix(prefix_SEMENT, verbal_SEMENT)
    else:
        false_SEMENT = POGG.semantic_constructions.base.verb_SEMENT(predicates[1], variables, index_arg)

    return true_SEMENT, false_SEMENT, POGG.semantic_constructions.base.passive_participle


def boolean(boolean_SEMENTs, nom_SEMENT, child_SEMENT):
    """
    Compose using a boolean property
    :param boolean_SEMENTs: tuple of SEMENTs, first is what to use if child_value is true, second if false
    :type boolean_SEMENTs: (SEMENT, SEMENT)
    :param nom_SEMENT: SEMENT being modified by boolean property
    :type nom_SEMENT: SEMENT
    :param child_SEMENT: SEMENT where predicate label *is* the boolean value...
    :type child_SEMENT: SEMENT
    """
    if child_SEMENT.rels[0].predicate == '_true_a_of':
        chosen_bool = boolean_SEMENTs[0]
    elif child_SEMENT.rels[0].predicate == '_false_a_of':
        chosen_bool = boolean_SEMENTs[1]
    # if the child doesn't have a true/false predicate, raise an error for the purposes of evaluation
    # i *could* just return the nom, but this will incorrectly result in the evaluation saying the edge worked
    else:
        raise RuntimeError("Boolean property edge doesn't point to boolean value")

    # the third thing returned from boolean node functions is the appropriate composition function
    boolean_function = boolean_SEMENTs[2]
    return boolean_function(chosen_bool, nom_SEMENT)


def descriptor(descriptor_SEMENT, nom_SEMENT):
    """
    Used for properties whose value can be adjectival or verbal
    e.g. a "descriptor" may be "red" or "locked"
    For adjectives, the plugged hole is ARG1 but for verbal descriptors the plugged hole is ARG2
    :param descriptor_SEMENT: descriptor SEMENT
    :type descriptor_SEMENT: SEMENT
    :param nom_SEMENT: SEMENT being described
    :type nom_SEMENT: SEMENT
    :return:
    :rtype:
    """
    # TODO: what i can do is some sort of check to see if the index of the descriptor is eq to the ARG0 of some verb
    # TODO: but instead I'm just gonna check if it's a simple adjective and assume passive_participle otherwise
    # find the index of the descriptor
    descriptor_index = descriptor_SEMENT.index

    # get eq with descriptor_index if it exists
    eq_set = set([descriptor_index])
    if descriptor_SEMENT.eqs:
        for eq in descriptor_SEMENT.eqs:
            if descriptor_index in eq:
                eq_set.update(eq)

    # look for vrebal relation with ARG0 in the eq_set
    for r in descriptor_SEMENT.rels:
        # if the ARG0 is in the eq_set, then assume we have a verbal descriptor
        if r.args['ARG0'] in eq_set and re.match('_[A-z]+_v_', r.predicate):
            return POGG.semantic_constructions.base.passive_participle(descriptor_SEMENT, nom_SEMENT)

    # if it never succeeds, assume adjectival
    return POGG.semantic_constructions.base.adjective(descriptor_SEMENT, nom_SEMENT)