# CONVERTING GRAPH TO MRS
# ORGANIZED: 01/04/2024
# DOCUMENTED: 01/04/2024
import json
import re
import random
import POGG.composition_library
import POGG.data_regularization

# TODO: graph selection? based on complexity? offload to graph_util.py perhaps

# dict of composition functions and their composition types
# VALUES:
#   PARENT_HOLE: parent (hole) -> hole (plug) ... photos --(of)--> cake
#   PARENT_PLUG: parent (plug) -> child (hole) ... apple --(color)--> red
#   EDGE_PRED_PARENT_CHILD: parent (ARG1) -> child (ARG2) + edge predicate ... cookie --(on)--> plate
COMPOSITION_TYPES = json.load(open("../config_data/comp_to_graph_relations.json"))


def load_lexicon(lexicon_filename):
    """
    Load the lexicon given a filename
    :param lexicon_filename: filename fo the lexicon
    :type lexicon_filename: str
    :return: lexicon in json format
    :rtype: dict
    """
    lexicon_file = open(lexicon_filename)
    lexicon = json.load(lexicon_file)
    return lexicon


def guess_pos_and_create_ssement(pred_label, variables={}):
    """
    Given a predicate label, guess the part of speech and then generate the basic SSEMENT
    :param pred_label: predicate label
    :type pred_label: str
    :param variables: dict of variables and values, if you need to constrain them (e.g. NUM=sg)
    :type variables: dict
    :return: basic SSEMENT
    :rtype: SSEMENT
    """
    # noun
    if re.match('_[A-z]+_n_[0-z]+$', pred_label):
        return POGG.composition_library.noun_ssement(pred_label, variables)
    # adjective
    elif re.match('_[A-z\-]+_a_[0-z]+$', pred_label):
        return POGG.composition_library.adjective_ssement(pred_label, variables)
    # verb
    elif re.match('_[A-z]+_v_[0-z]$', pred_label):
        return POGG.composition_library.verb_ssement(pred_label, variables)
    # quantifier
    elif re.match('_[A-z]+_q$', pred_label):
        return POGG.composition_library.quant_ssement(pred_label, variables)
    # preposition
    elif re.match('_[A-z]+_p(_loc)*$', pred_label):
        return POGG.composition_library.preposition_ssement(pred_label, variables)
    # if no guess, do basic_ssement, assuming ARG0 as INDEX
    else:
        return POGG.composition_library.basic(pred_label, variables)


def parent_hole_composition(parent, child, edge_rule):
    """
    Parent MRS has a hole plugged by the child, edge introduces no predicate
    ex. photos of cupcakes
    :param parent: parent SSEMENT
    :type parent: SSEMENT
    :param child: child SSEMENT
    :type child: SSEMENT
    :param edge_rule: edge text
    :type edge_rule: str
    :return: composed SSEMENT
    :rtype: SSEMENT
    """
    # get the composition rule from the lexicon via the edge name
    comp_rule = getattr(POGG.composition_library, edge_rule)
    # when the child is the plug, the parent is the functor, so it goes first
    # e.g. adjective(adj, nom)
    return comp_rule(parent, child)


def parent_plug_composition(parent, child, edge_rule):
    """
    Parent MRS has is the plug for the hole in the child MRS, edge introduces no predicate
    ex. red apple
    :param parent: parent SSEMENT
    :type parent: SSEMENT
    :param child: child SSEMENT
    :type child: SSEMENT
    :param edge_rule: edge text
    :type edge_rule: str
    :return: composed SSEMENT
    :rtype: SSEMENT
    """
    # get the composition rule from the lexicon via the edge name
    comp_rule = getattr(POGG.composition_library, edge_rule)
    # when the parent is the plug, the child is the functor, so it goes first
    # e.g. adjective(adj, nom)
    return comp_rule(child, parent)


def edge_predicate(parent, child, edge_json):
    """
    Edge introduces its own predicate, parent serves as ARG1, child serves as ARG2
    :param parent: parent SSEMENT
    :type parent: SSEMENT
    :param child: child SSEMENT
    :type child: SSEMENT
    :param edge_json: json containing edge information
    :type edge_json: dict
    :return: composed SSEMENT
    :rtype: SSEMENT
    """
    # if an edge introduces a predicate, then the json info for the edge will look like this:
    # {edge}: {
    #   "composition": {...},
    #   {predicate_type}: {...}
    # so the edge_pred being introduced is whatever the value of that second property is
    # and the composition rule is the value of the "composition" property
    comp_rule_name = edge_json["composition"]
    comp_rule = getattr(POGG.composition_library, comp_rule_name)
    # edge pred information
    edge_pred = edge_json["property_predicate"]["predicate_label"]
    edge_ssement_type = edge_json["property_predicate"]["predicate_type"]
    edge_ssement_rule = getattr(POGG.composition_library, edge_ssement_type)
    edge_ssement = edge_ssement_rule(edge_pred)
    return comp_rule(edge_ssement, parent, child)


def head_first_node(head, nonhead, comp_name):
    comp_rule = getattr(POGG.composition_library, comp_name)
    return comp_rule(head, nonhead)


def head_second_node(head, nonhead, comp_name):
    comp_rule = getattr(POGG.composition_library, comp_name)
    return comp_rule(nonhead, head)


def node_to_mrs(node, lexicon, variables={}):
    """
        Create MRS for individual node
        :param node: node text
        :type node: str
        :param lexicon: lexicon with node to ERG predicate label mappings
        :type lexicon: dict
        :param variables: dict of variables and values, if you need to constrain them (e.g. NUM=sg)
        :type variables: dict
        :return: SSEMENT for the node
        :rtype: SSEMENT
        """
    # get ERG predicate
    # might involve compounds or synonyms

    # see if it's a node that's categorized as an entityType
    # TODO: bro this is sooooo bad oh my god, FIX LATER FR
    # ... it's possibly a recursive call, in which case node is already a dict ...
    # ... or if it LOOKS like an ERG predicate ...
    if isinstance(node, dict) or re.match("^_?[0-z-]+_[0-z]+_[0-z]+$", node):
        node_json = node
    else:
        try:
            node_json = lexicon['entityTypes'][node]
        except KeyError:
            # see if it's a propertyValue
            try:
                node_json = lexicon['propertyValues'][node]
            except KeyError:
                raise KeyError("Can't find '{}' as a key in the lexicon".format(node))

    # if it's just a string, return the ssement for the pred label
    if node_json == "":
        raise ValueError("'{}' has no value in the lexicon".format(node))
    elif isinstance(node_json, str):
        return guess_pos_and_create_ssement(node_json, variables)
    else:
        # recursively get MRS for head and nonhead
        head_mrs = node_to_mrs(node_json['predicates']['head'], lexicon)
        nonhead_mrs = node_to_mrs(node_json['predicates']['modifier'], lexicon)

        # otherwise it's a compositional node, so get rule name for composition
        comp_rule_name = node_json['composition']

        try:
            composition_types = COMPOSITION_TYPES[comp_rule_name]
        except KeyError:
            raise KeyError("Can't find '{}' as a key in comp_to_graph_relations.json")

        try:
            if 'HEAD_FIRST_NODE' in composition_types:
                return head_first_node(head_mrs, nonhead_mrs, comp_rule_name)
            elif 'HEAD_SECOND_NODE' in composition_types:
                return head_second_node(head_mrs, nonhead_mrs, comp_rule_name)
            else:
                raise ValueError("No legitimate composition type for {}".format(comp_rule_name))
        except RuntimeError as error:
            raise error


def edge_to_mrs(parent, child, edge, lexicon):
    """
    Compose MRS between parent and child, considering any semantic contribution made by the edge
    :param parent: parent SSEMENT
    :type parent: SSEMENT
    :param child: child SSEMENT
    :type child: SSEMENT
    :param edge: edge text
    :type edge: str
    :param lexicon: lexicon with node to ERG predicate label mappings
    :type lexicon: dict
    :return: composed SSEMENT
    :rtype: SSEMENT
    """
    try:
        edge_json = lexicon['properties'][edge]
    except:
        raise KeyError("Can't find '{}' as a key in the lexicon".format(edge))

    # assume edge name in lexicon is direct composition type
    # e.g. "idColor": "adjective"
    # otherwise, get the "composition" value
    if edge_json == '':
        raise ValueError("'{}' has no value in lexicon".format(edge))
    if isinstance(edge_json, str):
        edge_composition = edge_json
    else:
        edge_composition = lexicon['properties'][edge]['composition']

    try:
        composition_types = COMPOSITION_TYPES[edge_composition]
    except:
        raise KeyError("Can't find '{}' as a key in comp_to_graph_relations.json")

    try:
        if 'PARENT_HOLE' in composition_types:
            return parent_hole_composition(parent, child, edge_json)
        elif 'PARENT_PLUG' in composition_types:
            return parent_plug_composition(parent, child, edge_json)
        elif 'EDGE_PRED_PARENT_CHILD' in composition_types:
            return edge_predicate(parent, child, edge_json)
        else:
            raise ValueError("No legitimate composition type for {}".format(edge_composition))
    except RuntimeError as error:
        raise error


def graph_to_mrs(root, graph, lexicon, node_count=0, edge_count=0):
    """
    Convert a graph to MRS (SSEMENT)
    :param root: text on root node
    :type root: str
    :param graph: graph to compose MRS from
    :type graph: DiGraph
    :param lexicon: lexicon with node to ERG predicate label mappings
    :type lexicon: dict
    :param node_count: counter for naming nodes in the evaluation dictionary
    :type node_count: int
    :param edge_count: counter for naming edges in the evaluation dictionary
    :type edge_count: int
    :param variables: dict of variables and values, if you need to constrain them (e.g. NUM=sg)
    :type variables: dict
    :return: tuple of composed SSEMENT and eval information
    :rtype: tuple
    """

    '''eval info should look like...
        {
            nodes: {
                'idApple': {
                    'produced': (True, "MRS produced"),
                    'included': (True "Included in MRS"),
                },
                'red': {
                    'produced': (True, "MRS produced"),
                    'included': (True, "Included in MRS")
                },
                'idTable': {
                    'produced': (False, "Not in lexicon"),
                    'included': (False, "Not in lexicon")
                },
                'wooden': {
                    'produced': (True, "MRS produced")
                    'included': (False, "Child of failed node")
                }
            },
            edges: {
                'color': {
                    'produced': (True, "MRS composed"),
                    'included': (True, Included in MRS)
                },
                'onTopOf': {
                    'produced': (False, "Inbound of failed node"),
                    'included': (False, "Inbound of failed node")
                },
                'material': {
                    'produced': (False, "Outbound of failed node"),
                    'included': (False, "Outbound of failed node")
                }
            }
        }
    '''

    regularized_root = POGG.data_regularization.regularize_node(root)
    # the node/edge names have to be stored in eval with a counter
    node_count += 1
    # this is because two separate nodes/edges with the same key should be counted as separate instances
    eval_node_name = "{}_{}".format(regularized_root, node_count)

    # eval_info for the root
    eval_info = {
        'nodes': {
            eval_node_name: {
                'produced': None,
                'included': None
            }
        },
        'edges': {}
    }

    # 1. get MRS for root
    root_mrs = None
    try:
        root_mrs = node_to_mrs(regularized_root, lexicon, {})
        eval_info['nodes'][eval_node_name]['produced'] = (True, "MRS fragment produced")
        eval_info['nodes'][eval_node_name]['included'] = (True, "Included in MRS")
    except (KeyError, ValueError) as error:
        # node is not in lexicon
        eval_info['nodes'][eval_node_name]['produced'] = (False, error)
        eval_info['nodes'][eval_node_name]['included'] = (False, error)


    # 2. for each child ...
    new_composed_mrs = root_mrs
    for child in graph.successors(root):
        # if the root node or any child edge can't be produced, all children must be marked as disincluded
        inclusion_failure = False
        # 3. recurse and get the full MRS for the child
        child_conversion_result = graph_to_mrs(child, graph, lexicon, node_count, edge_count)
        child_mrs = child_conversion_result[0]
        child_eval_info = child_conversion_result[1]
        node_count = child_conversion_result[2]
        edge_count = child_conversion_result[3]

        # 4. compose child_mrs with the root
        edge = graph.get_edge_data(root, child)
        edge_count += 1
        regularized_edge = POGG.data_regularization.regularize_edge(edge[0]['label'])

        eval_edge_name = "{}_{}".format(regularized_edge, edge_count)
        eval_info['edges'][eval_edge_name] = {
            'produced': None,
            'included': None
        }

        if new_composed_mrs is None:
            inclusion_failure = 'node'
            eval_info['edges'][eval_edge_name]['produced'] = (False, "Outbound from failed node")
            eval_info['edges'][eval_edge_name]['included'] = (False, "Outbound from failed node")
        elif child_mrs is None:
            eval_info['edges'][eval_edge_name]['produced'] = (False, "Inbound to failed node")
            eval_info['edges'][eval_edge_name]['included'] = (False, "Inbound to failed node")
        else:
            try:
                new_composed_mrs = edge_to_mrs(new_composed_mrs, child_mrs, regularized_edge, lexicon)
                eval_info['edges'][eval_edge_name]['produced'] = (True, "MRS composed")
                eval_info['edges'][eval_edge_name]['included'] = (True, "Included in MRS")
            except (KeyError, ValueError, RuntimeError) as error:
                inclusion_failure = 'edge'
                eval_info['edges'][eval_edge_name]['produced'] = (False, error)
                eval_info['edges'][eval_edge_name]['included'] = (False, error)

        if inclusion_failure:
            # update child_eval_info to set every node/edge to false
            for n in child_eval_info['nodes']:
                if child_eval_info['nodes'][n]['included'][0]:
                    child_eval_info['nodes'][n]['included'] = (False, "Descends from failed {}".format(inclusion_failure))
            for e in child_eval_info['edges']:
                if child_eval_info['edges'][e]['included'][0]:
                    child_eval_info['edges'][e]['included'] = (False, "Descends from failed {}".format(inclusion_failure))

        # merge child_eval_info with current eval_info
        eval_info['nodes'] = {**eval_info['nodes'], **child_eval_info['nodes']}
        eval_info['edges'] = {**eval_info['edges'], **child_eval_info['edges']}

    # 5. return the result
    # i.e. the MRS up to this point, evaluation information, and the count of included nodes/edges in the MRS
    # add the root_increment here, so it's only accounted for once
    return new_composed_mrs, eval_info, node_count, edge_count

# def graph_to_mrs_new(root, graph, lexicon):
#     """
#     Convert a graph to MRS (SSEMENT)
#     :param root: text on root node
#     :type root: str
#     :param graph: graph to compose MRS from
#     :type graph: DiGraph
#     :param lexicon: lexicon with node to ERG predicate label mappings
#     :type lexicon: dict
#     :param node_count: counter for naming nodes in the evaluation dictionary
#     :type node_count: int
#     :param edge_count: counter for naming edges in the evaluation dictionary
#     :type edge_count: int
#     :param variables: dict of variables and values, if you need to constrain them (e.g. NUM=sg)
#     :type variables: dict
#     :return: tuple of composed SSEMENT and eval information
#     :rtype: tuple
#     """
#     regularized_root = POGG.data_regularization.regularize_node(root)
#
#     # 1. get MRS for root
#     root_mrs = node_to_mrs(regularized_root, lexicon, {})
#
#     # 2. for each child ...
#     new_composed_mrs = root_mrs
#     for child in graph.successors(root):
#         # if the root node or any child edge can't be produced, all children must be marked as disincluded
#         inclusion_failure = False
#         # 3. recurse and get the full MRS for the child
#         child_mrs = graph_to_mrs_new(child, graph, lexicon)
#
#         # 4. compose child_mrs with the root
#         edge = graph.get_edge_data(root, child)
#         regularized_edge = POGG.data_regularization.regularize_edge(edge[0]['label'])
#         new_composed_mrs = edge_to_mrs(new_composed_mrs, child_mrs, regularized_edge, lexicon)
#
#
#     # 5. return the result
#     # i.e. the MRS up to this point, evaluation information, and the count of included nodes/edges in the MRS
#     # add the root_increment here, so it's only accounted for once
#     return new_composed_mrs
