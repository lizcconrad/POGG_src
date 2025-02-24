# contains helper functions for composing MRS and generating from MRS
# ORGANIZED: 01/30/2024
# DOCUMENTED: 01/30/2024
import yaml
from delphin import ace, mrs
from delphin.codecs import simplemrs
import POGG.mrs_algebra
import copy
from tabulate import tabulate
import re


def _make_rels_list(s):
    rels_list = list()
    for r in s.rels:
        rels_list.append(r.predicate)
    return sorted(rels_list)


def _make_var_dicts(s):
    """
    Create two dictionaries for a given SEMENT. One where the top level keys are the variables,
    and another where the top level keys are the predicate labels. These will be used to find discrepancies between
    non-isomorphic SEMENTs
    :param s: Given SEMENT
    :type s: SEMENT
    :return: two dictionaries with structure shown below
    :rtype: dict, dict
    """

    # var_dict looks like...
    # have to add lbl to key in case of multiple relations with the same pred label
    """
    {
        'x4': {
            'unknown__h1': [ARG],
            '_the_q__h5': [ARG0],
            '_white_a_1__h8': [ARG1],
            '_cat_n_1__h8: [ARG0]
        }
    }
    """
    var_dict = {}

    # pred_arg_dict looks like...
    # have to add lbl to key in case of multiple relations with the same pred label
    """
    {
        '_white_a_1__h8': {
            'predicate_label': '_white_a_1'
            'LBL': 'h8',
            'ARG0': 'e9',
            'ARG1': 'x4'
        }
    }
    """
    pred_arg_dict = {}

    # TOP
    var_dict[s.top] = {'TOP': ['TOP']}
    pred_arg_dict['TOP'] = {'predicate_label': 'TOP', 'TOP': s.top}
    # INDEX
    var_dict[s.index] = {'INDEX': ['INDEX']}
    pred_arg_dict['INDEX'] = {'predicate_label': 'INDEX', 'INDEX': s.index}
    # vars in RELS
    rel_counter = 0
    for r in s.rels:
        # { '_white_a_1': {}}
        pred_key = "{}__{}-{}".format(r.predicate, r.label, r.id)
        if pred_key not in pred_arg_dict:
            pred_arg_dict[pred_key] = {}
            pred_arg_dict[pred_key]['predicate_label'] = r.predicate


        # add LBL
        pred_arg_dict[pred_key]['LBL'] = r.label
        if r.label in var_dict:
            if pred_key in var_dict[r.label]:
                var_dict[r.label][pred_key].append('LBL')
            else:
                var_dict[r.label][pred_key] = ['LBL']
        else:
            var_dict[r.label] = {}
            var_dict[r.label][pred_key] = ['LBL']

        for arg in r.args:
            # a = 'ARG1'
            # arg_var_val = 'x1'
            arg_val = r.args[arg]

            # {'_white_a_1__h8': {'ARG1': 'x1'}}
            pred_arg_dict[pred_key][arg] = arg_val

            if arg_val in var_dict:
                if pred_key in var_dict[arg_val]:
                    # {'x1': {'_white_a_1': ['ARG1']}}
                    var_dict[arg_val][pred_key].append(arg)
                else:
                    var_dict[arg_val][pred_key] = [arg]
            else:
                var_dict[arg_val] = {pred_key: [arg]}

        rel_counter += 1
    return var_dict, pred_arg_dict


def _get_var_equivalencies(s_dicts):
    s_var_dict = s_dicts[0]
    s_pred_arg_dict = s_dicts[1]

    # for each variable in s1...
    all_equivalencies = list()
    all_regularized_equivalencies = list()
    for var in s_var_dict:
        current_equivalencies = list()
        current_regularized_equivalencies = list()

        # get equivalencies for s
        for pred in s_var_dict[var]:
            regularized_pred = s_pred_arg_dict[pred]['predicate_label']
            if re.search("_q$", regularized_pred):
                regularized_pred = 'abstract_q'

            for arg in s_var_dict[var][pred]:
                pred_arg = "{}__{}".format(pred, arg)
                regularized_pred_arg = "{}__{}".format(regularized_pred, arg)
                current_equivalencies.append(pred_arg)
                current_regularized_equivalencies.append(regularized_pred_arg)

        all_equivalencies.append(sorted(current_equivalencies))
        all_regularized_equivalencies.append(sorted(current_regularized_equivalencies))

    return all_equivalencies, all_regularized_equivalencies


def _check_var_equivalencies(s1_dicts, s2_dicts):
    s1_var_dict = s1_dicts[0]
    s1_pred_arg_dict = s1_dicts[1]

    s2_var_dict = s2_dicts[0]
    s2_pred_arg_dict = s2_dicts[1]

    # for each variable in s1...
    for var in s1_var_dict:
        # ... get each ARG it fills ...
        # just a list of ARGs filled by the variable
        target_equivalencies = list()
        target_regularized_equivalencies = list()

        actual_equivalencies = list()
        actual_regularized_equivalencies = list()

        # dict of every variable the created (or other) SEMENT has for the target ARGs
        # ideally should end up with one key only, but if not, there's a missing equivalency
        # PARALLEL LISTS...


        # get equivalencies for s1
        for pred in s1_var_dict[var]:
            regularized_pred = s1_pred_arg_dict[pred]['predicate_label']
            if re.search("_q$", regularized_pred):
                regularized_pred = 'abstract_q'

            for arg in s1_var_dict[var][pred]:
                pred_arg = "{}__{}".format(pred, arg)
                regularized_pred_arg = "{}__{}".format(regularized_pred, arg)
                target_equivalencies.append(pred_arg)
                target_regularized_equivalencies.append(regularized_pred_arg)

                # for each variable in s1...
                for var in s1_var_dict:
                    # ... get each ARG it fills ...
                    # just a list of ARGs filled by the variable


                    actual_equivalencies = list()
                    actual_regularized_equivalencies = list()

                    # dict of every variable the created (or other) SEMENT has for the target ARGs
                    # ideally should end up with one key only, but if not, there's a missing equivalency
                    # PARALLEL LISTS...

                    # get equivalencies for s1
                    for pred in s1_var_dict[var]:
                        regularized_pred = s1_pred_arg_dict[pred]['predicate_label']
                        if re.search("_q$", regularized_pred):
                            regularized_pred = 'abstract_q'

                        for arg in s1_var_dict[var][pred]:
                            pred_arg = "{}__{}".format(pred, arg)
                            regularized_pred_arg = "{}__{}".format(regularized_pred, arg)
                            target_equivalencies.append(pred_arg)
                            target_regularized_equivalencies.append(regularized_pred_arg)

            # TARGET_EQUIVALENCIES ESTABLISHED...


            # # look for candidates in s2_pred_arg_dict
            # for cand_pred in s2_pred_arg_dict:
            #     if s2_pred_arg_dict[cand_pred]['predicate_label'] == regularized_pred:
            #         cand_var = s2_pred_arg_dict[cand_pred][arg]
            #
            #         # if cand_var already in current_equivalencies, skip
            #         if cand_var in current_equivalencies:
            #             continue
            #
            #         for pred2 in s2_var_dict[cand_var]:
            #             regularized_pred2 = s2_pred_arg_dict[pred2]['predicate_label']
            #             for arg2 in s2_var_dict[cand_var][pred2]:
            #                 current_equivalencies[cand_var].add("{}__{}".format(pred2, arg2))
            #                 current_regularized_equivalencies[cand_var].add("{}__{}".format(regularized_pred2, arg2))
            #         candidate_actual_equivalencies.append(current_equivalencies)
            #         candidate_regularized_actual_equivalencies.append(current_regularized_equivalencies)


                # FOR EVERY POSSIBLE RELATION THAT *COULD* BE A MATCH...
                # if i find a match, then assume it's correct and add as normal and skip other candidates
                # if i *dont* find a match

                # actual_var = s2_pred_arg_dict[pred][arg]
                # if actual_var not in actual_equivalencies:
                #     actual_equivalencies[actual_var] = set()
                #     actual_equivalencies[actual_var].add("{}__{}".format(pred, arg))
                # else:
                #     actual_equivalencies[actual_var].add("{}__{}".format(pred, arg))
                # # add any other equivalencies with actual_var
                # # this is technically redundant but this will catch those that are equivalent that *shouldn't* be
                # for pred2 in s2_var_dict[actual_var]:
                #     for arg2 in s2_var_dict[actual_var][pred2]:
                #         actual_equivalencies[actual_var].add("{}__{}".format(pred2, arg2))

        # # check set equivalency
        # if len(actual_equivalencies) == 1:
        #     key = list(actual_equivalencies.keys())[0]
        #     if target_equivalencies == actual_equivalencies[key]:
        #         continue
        #     else:
        #         print("Composed SEMENT has additional equivalencies...")
        #         print("Target SEMENT equivalencies:{}".format(sorted(list(target_equivalencies))))
        #         print("Composed SEMENT equivalencies:{}\n".format(sorted(list(actual_equivalencies[key]))))
        # else:
        #     print("Composed SEMENT doesn't contain appropriate equivalencies...")
        #     print("Target SEMENT equivalencies:{}".format(sorted(list(target_equivalencies))))
        #     print("Composed SEMENT variables:{}\n".format(actual_equivalencies))


def _make_hcon_list(s, s_var_dict, s_pred_arg_dict):
    # TODO: make these into tuples for comparison i guess idk ... god ... puking
    full_hcons = list()
    regularized_hcons = list()

    for hcon in s.hcons:
        hi_var = hcon.hi
        lo_var = hcon.lo
        rel = hcon.relation

        hi_string_full = ""
        hi_string_reg = ""
        for pred in sorted(list(s_var_dict[hi_var].keys())):
            regularized_pred = s_pred_arg_dict[pred]['predicate_label']
            if re.search("_q$", regularized_pred):
                regularized_pred = 'abstract_q'

            hi_string_full += "__{}_".format(pred)
            hi_string_reg += "__{}_".format(regularized_pred)
            for arg in sorted(list(s_var_dict[hi_var][pred])):
                hi_string_full += "_{}".format(arg)
                hi_string_reg += "_{}".format(arg)

        lo_string_full = ""
        lo_string_reg = ""
        for pred in sorted(list(s_var_dict[lo_var].keys())):
            regularized_pred = s_pred_arg_dict[pred]['predicate_label']
            if re.search("_q$", regularized_pred):
                regularized_pred = 'abstract_q'

            lo_string_full += "__{}_".format(pred)
            lo_string_reg += "__{}_".format(regularized_pred)
            for arg in sorted(list(s_var_dict[lo_var][pred])):
                lo_string_full += "_{}".format(arg)
                lo_string_reg += "_{}".format(arg)

        hcon_tuple_full = (hi_string_full, rel, lo_string_full)
        hcon_tuple_reg = (hi_string_reg, rel, lo_string_reg)

        full_hcons.append(hcon_tuple_full)
        regularized_hcons.append(hcon_tuple_reg)

    return full_hcons, regularized_hcons



def find_discrepancy(s1, s2, file):
    # check if isomorphic
    if mrs.is_isomorphic(s1, s2, properties=False):
        file.write("SEMENTs are isomorphic!\n")
        return False

    # s1_string = simplemrs.encode(s1, indent=True)
    # s2_string = simplemrs.encode(s2, indent=True)
    # file.write("TARGET SEMENT:\n{}\n\n".format(s1_string))
    # file.write("COMPOSED SEMENT:\n{}\n\n".format(s2_string))

    # check for same RELS ...
    s1_rels = _make_rels_list(s1)
    s2_rels = _make_rels_list(s2)

    if _make_rels_list(s1) != _make_rels_list(s2):
        s1_mutable_rels = copy.copy(s1_rels)
        s2_mutable_rels = copy.copy(s2_rels)

        for rel in s1_rels:
            s1_ind = s1_mutable_rels.index(rel)
            if rel in s2_mutable_rels:
                s2_ind = s2_mutable_rels.index(rel)

                # remove from s1 and s2 lists because a match was found
                s1_mutable_rels.pop(s1_ind)
                s2_mutable_rels.pop(s2_ind)
            elif re.search("_q$", rel):
                # if the rel from s1 ends in _q, just pop any quantifier out of s2
                # TODO: not the best but just assuming if the MRSs have the same # of quantifiers they have same RELs
                q_index_list = [i for i, item in enumerate(s2_mutable_rels) if re.search('_q$', item)]
                # just get the first one it found
                try:
                    q_index = q_index_list[0]
                    s2_mutable_rels.pop(q_index)
                    s1_mutable_rels.pop(s1_ind)
                except:
                    pass

        if len(s2_mutable_rels) > 0 or len(s1_mutable_rels) > 0:
            file.write("SEMENTs don't contain the same RELs\n")
            file.write("Extra Target RELs: {}\n\n".format(s1_mutable_rels))
            file.write("Extra Composed RELs: {}\n\n".format(s2_mutable_rels))
            return True

    # make var dicts
    s1_dicts = _make_var_dicts(s1)
    s2_dicts = _make_var_dicts(s2)

    # check variable equivalencies...
    # _check_var_equivalencies(s1_dicts, s2_dicts)
    s1_full_equivs, s1_reg_equivs = _get_var_equivalencies(s1_dicts)
    s2_full_equivs, s2_reg_equivs = _get_var_equivalencies(s2_dicts)

    s1_mutable_full_equivs = copy.copy(s1_full_equivs)
    s1_mutable_reg_equivs = copy.copy(s1_reg_equivs)
    s2_mutable_full_equivs = copy.copy(s2_full_equivs)
    s2_mutable_reg_equivs = copy.copy(s2_reg_equivs)

    for reg_equiv in s1_reg_equivs:
        s1_ind = s1_mutable_reg_equivs.index(reg_equiv)
        if reg_equiv in s2_mutable_reg_equivs:
            s2_ind = s2_mutable_reg_equivs.index(reg_equiv)

            # remove from s1 and s2 lists because a match was found
            s1_mutable_full_equivs.pop(s1_ind)
            s1_mutable_reg_equivs.pop(s1_ind)
            s2_mutable_full_equivs.pop(s2_ind)
            s2_mutable_reg_equivs.pop(s2_ind)

    # print equivalencies not found in both
    file.write("Equivalencies in TARGET SEMENT not found in COMPOSED SEMENT:\n")
    for i, equiv in enumerate(s1_mutable_full_equivs):
        equiv_table = []
        for j, equiv_elem in enumerate(equiv):
            # get regularized equiv_element in parallel
            reg_equiv_elem = s1_mutable_reg_equivs[i][j]
            equiv_table.append([reg_equiv_elem, equiv_elem])
        file.write("{}\n\n".format(tabulate(equiv_table, headers=["REGULARIZED", "FULL"])))

    file.write("\nEquivalencies in COMPOSED SEMENT not found in TARGET SEMENT:\n")
    for i, equiv in enumerate(s2_mutable_full_equivs):
        equiv_table = []
        for j, equiv_elem in enumerate(equiv):
            # get regularized equiv_element in parallel
            reg_equiv_elem = s2_mutable_reg_equivs[i][j]
            equiv_table.append([reg_equiv_elem, equiv_elem])
        file.write("{}\n\n".format(tabulate(equiv_table, headers=["REGULARIZED", "FULL"])))


    # check qeq equivalencies...
    # pass in SEMENT to access HCONS and the var_dict to convert the qeqs to readable format
    s1_full_hcons, s1_reg_hcons = _make_hcon_list(s1, s1_dicts[0], s1_dicts[1])
    s2_full_hcons, s2_reg_hcons = _make_hcon_list(s2, s2_dicts[0], s2_dicts[1])

    s1_mutable_full_hcons = copy.copy(s1_full_hcons)
    s1_mutable_reg_hcons = copy.copy(s1_reg_hcons)
    s2_mutable_full_hcons = copy.copy(s2_full_hcons)
    s2_mutable_reg_hcons = copy.copy(s2_reg_hcons)

    for reg_hcon in s1_reg_hcons:
        s1_ind = s1_mutable_reg_hcons.index(reg_hcon)
        if reg_hcon in s2_reg_hcons:
            s2_ind = s2_mutable_reg_hcons.index(reg_hcon)

            # remove from s1 and s2 lists because a match was found
            s1_mutable_full_hcons.pop(s1_ind)
            s1_mutable_reg_hcons.pop(s1_ind)
            s2_mutable_full_hcons.pop(s2_ind)
            s2_mutable_reg_hcons.pop(s2_ind)

    # print equivalencies not found in both
    file.write("\n\nHCONs in TARGET SEMENT not found in COMPOSED SEMENT:\n")
    for i in range(len(s1_mutable_full_hcons)):
        file.write("\tREGULARIZED: {} ={}= {}\n".format(s1_mutable_reg_hcons[i][0], s1_mutable_reg_hcons[i][1],
                                                 s1_mutable_reg_hcons[i][2]))
        file.write("\tFULL: {} ={}= {}\n\n".format(s1_mutable_full_hcons[i][0], s1_mutable_full_hcons[i][1],
                                          s1_mutable_full_hcons[i][2]))

    file.write("\nHCONs in COMPOSED SEMENT not found in TARGET SEMENT:\n")
    for i in range(len(s2_mutable_full_hcons)):
        file.write("\tREGULARIZED: {} ={}= {}\n".format(s2_mutable_reg_hcons[i][0], s2_mutable_reg_hcons[i][1],
                                                 s2_mutable_reg_hcons[i][2]))
        file.write("\tFULL: {} ={}= {}\n\n".format(s2_mutable_full_hcons[i][0], s2_mutable_full_hcons[i][1],
                                          s2_mutable_full_hcons[i][2]))

    return True


def check_if_quantified(check_SEMENT):
    """
    Check if the given SEMENT is quantified (assumes generation is occurring on referring expressions)
    :param check_SEMENT: SEMENT to be checked
    :type check_SEMENT: SEMENT
    :return: quantified SEMENT (may be unchanged from given)
    :rtype: SEMENT
    """
    # if the INDEX (or something eq to INDEX) is not the ARG0 of something with RSTR, gg
    index = check_SEMENT.index
    index_set = set()
    index_set.add(index)
    # go through eqs to find variables eq to index
    if check_SEMENT.eqs is not None:
        for eq in check_SEMENT.eqs:
            if index in eq:
                for elem in eq:
                    index_set.add(elem)

    for rel in check_SEMENT.rels:
        if rel.args['ARG0'] in index_set and 'RSTR' in rel.args:
            return True
    return False


def wrap_with_quantifier(unquant_SEMENT):
    """
    Wrap the given SEMENT in a quantifier
    :param unquant_SEMENT: unquantified SEMENT
    :type unquant_SEMENT: SEMENT
    :return: quantified SEMENT
    :rtype: SEMENT
    """
    # just using 'the' for now
    quant = POGG.mrs_algebra.create_base_SEMENT('def_udef_a_q')
    return POGG.mrs_algebra.op_scopal(quant, unquant_SEMENT)


def update_index(SEMENT, index_rel, index_arg):
    """
    Given a SEMENT, the relation that has the ARG that serves as the index,
    and the index ARG, update the SEMENT's index

    Example: a verbal SEMENT whose index is the ARG0 of the verb relation may need to be updated so the ARG2 of
    the verb is the INDEX in the case of a passive participle modifier
    :param SEMENT: SEMENT to update
    :type SEMENT: SEMENT
    :param index_rel: predicate label for the relation which contains the new index
    :type index_rel: str
    :param index_arg: ARG that serves as index
    :type index_arg: str
    :return: updated SEMENT
    :rtype: SEMENT
    """
    for r in SEMENT.rels:
        if r.predicate == index_rel:
            new_index = r.args[index_arg]

    SEMENT.index = new_index
    return SEMENT


def group_equalities(eqs):
    """
    Group equalities from a list of EQs into lists as opposed to individual equalities
    That is, if x1=x2 and x2=x3 create a list [x1, x2, x3] such that they're in an equality "group"
    :param eqs: List of eqs
    :type eqs: list
    :return: new_sets, list of EQ groups
    :rtype: list
    """
    new_sets = []
    # as long as there are eqs still not covered
    while eqs:
        # pop one eq off the list
        current_eq = eqs.pop()
        # flag for whether a new group is needed
        need_new = True
        # for every set in the list of new_sets,
        # THIS DOESN'T WORK BECAUSE (x1,x2) makes new set, (x3,x4) makes new set
        # BUT WHAT IF (x2,x3)
        # so...
        # which new sets are the eq members found in
        new_sets_found_in = []
        for i, new_set in enumerate(new_sets):
            # if either member is in the new_set, update the set so that it's the union of both
            if current_eq[0] in new_set or current_eq[1] in new_set:
                # append new_set and index as tuple for popping
                new_sets_found_in.append(new_set)
                # and therefore we don't need to create a new set because we found a candidate group
                need_new = False

        # if need_new, start a new group
        if need_new:
            new_sets.append(set(current_eq))
        # else, unionize all sets it was found in and pop extras from new_sets
        else:
            updated_new_set = set()
            # update the set
            for new_set in new_sets_found_in:
                updated_new_set.update(new_set)
                new_sets.remove(new_set)
            updated_new_set.update(current_eq)
            new_sets.append(updated_new_set)


        # for i, new_set in enumerate(new_sets):
        #     # if either member is in the new_set, update the set so that it's the union of both
        #     if current_eq[0] in new_set or current_eq[1] in new_set:
        #         new_sets[i] = new_set.union(set(current_eq))
        #         # and therefore we don't need to create a new set because we found the right group
        #         need_new = False


    return new_sets


def get_most_specified_variable(eq_vars):
    """
    Get the most "specific" variable to serve as the representative for the EQ set
    That is, a variable of type x is more specific than one of type i, according to the ERG hierarchy
    :param eq_vars: list of variables that are equivalent
    :type eq_vars: list
    :return: most specific variable
    :rtype: str
    """
    # this isn't going to check for incompatibilities, I'm assuming those have been handled already
    types = {
        'u': 0,
        'i': 1,
        'p': 1,
        'e': 2,
        'x': 2,
        'h': 2
    }

    most_spec_var = eq_vars[0]
    for var in eq_vars:
        # type is the first char in the string
        # if the type of the current var is more specific than the already chosen one,
        # update the chosen one
        if types[var[0]] > types[most_spec_var[0]]:
            most_spec_var = var
    return most_spec_var


def overwrite_eqs(final_SEMENT):
    """
    Create a new SEMENT where the EQs have been overwritten to one representative value
    :param final_SEMENT: final SEMENT from composition
    :type final_SEMENT: SEMENT
    :return: new SEMENT with overwritten EQs
    :rtype: SEMENT
    """

    # will be progressively collecting a new list of SEPs, HCONS, and EQs, so start with those from the final_SEMENT
    # where final_SEMENT is the SEMENT that comes out after composition is complete
    current_SEMENT = final_SEMENT
    current_seps = current_SEMENT.rels
    current_variables = current_SEMENT.variables
    current_hcons = current_SEMENT.hcons
    # group the equalities so if x1=x2 and x2=x3 there's a list of [x1, x2, x3] with all variables that are equivalent
    grouped_eqs = group_equalities(current_SEMENT.eqs)

    for eq in grouped_eqs:
        # need to get the more specific variable of the pair
        chosen_var = get_most_specified_variable(list(eq))

        # check the top
        if current_SEMENT.top in eq:
            newest_top = chosen_var
        else:
            newest_top = current_SEMENT.top
        # check the ltop
        if current_SEMENT.ltop in eq:
            newest_ltop = chosen_var
        else:
            newest_ltop = current_SEMENT.ltop
        # check the index
        if current_SEMENT.index in eq:
            newest_index = chosen_var
        else:
            newest_index = current_SEMENT.index

        # check the rels
        new_seps = []
        for r in current_seps:
            if r.label in eq:
                new_r_label = chosen_var
            else:
                new_r_label = r.label
            new_r_args = {}
            for arg in r.args:
                if r.args[arg] in eq:
                    new_r_args[arg] = chosen_var
                else:
                    new_r_args[arg] = r.args[arg]
            new_seps.append(POGG.mrs_algebra.SEP(r.predicate, new_r_label, new_r_args))


        # update the SEP list with the current ones
        current_seps = new_seps

        # update the variable dictionary
        new_variables = {}
        for var in current_variables:
            if var in eq:
                new_variables[chosen_var] = {}
                # update the new property dictionary with properties from every var in the eq group
                for e in eq:
                    new_variables[chosen_var].update(current_variables[e])
            else:
                new_variables[var] = current_variables[var]
        current_variables = new_variables

        # check the hcons...
        new_hcons = []
        for hcon in current_hcons:
            # is there any chance that the hi of an hcon will be one member of an eq
            # and the lo could be another member of the eq? so both need to be checked/changed?
            # idk but i'm scared so
            if hcon.hi in eq:
                new_hi = chosen_var
            else:
                new_hi = hcon.hi
            if hcon.lo in eq:
                new_lo = chosen_var
            else:
                new_lo = hcon.lo
            new_hcons.append(mrs.HCons(new_hi, 'qeq', new_lo))

        current_hcons = new_hcons

        # check the icons...???

    # build new overwritten SEMENT
    # eqs list is gone
    return POGG.mrs_algebra.SEMENT(newest_top, newest_ltop, newest_index, current_seps, current_variables, current_SEMENT.holes, None, new_hcons)


def wrap_and_generate_to_console(final_SEMENT):
    """
    Wraps a refex with the "unknown" predicate, which the ERG requires for generation, then performs the generation
    :param final_SEMENT: SEMENT to wrap
    :type final_SEMENT: SEMENT
    """
    # quantify if not already quantified
    if check_if_quantified(final_SEMENT):
        quant_final_SEMENT = final_SEMENT
    else:
        quant_final_SEMENT = wrap_with_quantifier(final_SEMENT)

    # wrap with 'unknown' and overwrite EQs
    unknown = POGG.mrs_algebra.create_base_SEMENT('unknown')
    wrapped_SEMENT = POGG.mrs_algebra.op_final(unknown, quant_final_SEMENT, POGG.mrs_algebra.VAR_LABELER.get_var_name('h'))
    generate_from = overwrite_eqs(wrapped_SEMENT)

    generate_mrs_string = simplemrs.encode(generate_from, indent=True)

    config = yaml.safe_load((open("../config_data/global_config.yml")))

    with ace.ACEGenerator(config['ERG'], ['-r', 'root_frag']) as generator:
        print(generate_mrs_string)
        response = generator.interact(generate_mrs_string)
        print("GENERATED RESULTS ... ")
        for r in response.results():
            print(r.get('surface'))


def wrap_and_generate_to_file(final_SEMENT, filename):
    """
    Wraps a refex with the "unknown" predicate, which the ERG requires for generation, then performs the generation
    :param final_SEMENT: SEMENT to wrap
    :type final_SEMENT: SEMENT
    """
    # quantify if not already quantified
    if check_if_quantified(final_SEMENT):
        quant_final_SEMENT = final_SEMENT
    else:
        quant_final_SEMENT = wrap_with_quantifier(final_SEMENT)

    # wrap with 'unknown' and overwrite EQs
    unknown = POGG.mrs_algebra.create_base_SEMENT('unknown')
    wrapped_SEMENT = POGG.mrs_algebra.op_final(unknown, quant_final_SEMENT, POGG.mrs_algebra.VAR_LABELER.get_var_name('h'))
    generate_from = overwrite_eqs(wrapped_SEMENT)

    generate_mrs_string = simplemrs.encode(generate_from, indent=True)

    config = yaml.safe_load((open("../config_data/global_config.yml")))

    with ace.ACEGenerator(config['ERG'], ['-r', 'root_frag']) as generator:
        with open(filename, 'a') as file:
            file.write(generate_mrs_string + "\n")
            response = generator.interact(generate_mrs_string)
            file.write("GENERATED RESULTS ... \n")
            for r in response.results():
                file.write(r.get('surface') + "\n")


def wrap_SEMENT(final_SEMENT):
    """
    Wraps a refex with the "unknown" predicate, which the ERG requires for generation
    :param final_SEMENT: SEMENT to wrap
    :type final_SEMENT: SEMENT
    :return: new wrapped SEMENT
    :rtype: str
    """
    # if the SEMENT is empty, i.e. the conversion fully failed, return empty string
    if final_SEMENT is None:
        return ""

    # quantify if not already quantified
    if check_if_quantified(final_SEMENT):
        quant_final_SEMENT = final_SEMENT
    else:
        quant_final_SEMENT = wrap_with_quantifier(final_SEMENT)

    # wrap with 'unknown' and overwrite EQs
    unknown = POGG.mrs_algebra.create_base_SEMENT('unknown')
    wrapped_SEMENT = POGG.mrs_algebra.op_final(unknown, quant_final_SEMENT, POGG.mrs_algebra.VAR_LABELER.get_var_name('h'))
    generate_from = overwrite_eqs(wrapped_SEMENT)

    generate_mrs_string = simplemrs.encode(generate_from, indent=True)

    return generate_mrs_string



def generate(wrapped_mrs_string):
    """
    Generate from a given MRS and return the results
    :param wrapped_mrs_string: MRS string to generate from
    :type wrapped_mrs_string: str
    :return: results from response object
    :rtype: list
    """
    config = yaml.safe_load((open("../config_data/global_config.yml")))

    with ace.ACEGenerator(config['ERG'], ['-r', 'root_frag']) as generator:
        response = generator.interact(wrapped_mrs_string)
        return response.results()
