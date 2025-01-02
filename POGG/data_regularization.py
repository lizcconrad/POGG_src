# Functions to regularize data
# ORGANIZED: 01/04/2024
# DOCUMENTED: 01/04/2024
import re


# All of these functions assume Perplexity-like naming conventions.
# TODO: Future addition to let the user override these for their own data?

def regularize_node(node_text):
    """
    Regularize nodes to remove the number at the end.
    For example, idApple1 and idApple2 should map to the same ERG predicate label, so remove the number to get idApple
    :param node_text: node text
    :type node_text: str
    :return: trimmed node text
    :rtype: str
    """
    matched = re.match("(id[A-z]+)[0-9]+$", str(node_text))
    # if a match is found, just return the capture group
    if matched:
        return matched.group(1)
    # if not, it might just be a property, or it couldn't be regularized,
    # so just try to return it
    else:
        return str(node_text)


def regularize_edge(edge_text):
    """
    Regularize property to get just the property name, trimming the object its associated with
    For example, idObject1_prop_idProperty should return idProperty
    :param edge_text: edge text
    :type edge_text: str
    :return: trimmed edge text
    :rtype: str
    """
    matched = re.search("prop_([A-z]+)", str(edge_text))
    # if a match is found, just return the capture group
    if matched:
        return matched.group(1)
    # if not, it couldn't be regularized,
    # so just try to return it
    else:
        return str(edge_text)