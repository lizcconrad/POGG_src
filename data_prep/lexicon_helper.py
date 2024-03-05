# Given a full set of entities, properties, and relationships, build a lexicon skeleton
# ORGANIZED: 01/30/2024
# DOCUMENTED: 01/30/2024
import networkx as nx
from GG.data_regularization import regularize_node, regularize_edge


def build_lexicon_skeleton(graph):
    lexicon_skeleton = {
        "entityTypes": {},
        "propertyValues": {},
        "properties": {}
    }

    # add all node values to lexicon
    node_type_dict = nx.get_node_attributes(graph, "node_type")

    # lists to store entityTypes and propertyValues for sorting purposes
    entityTypes = []
    propertyValues = []

    for node in list(graph.nodes):
        regularized_node = regularize_node(node)
        if node_type_dict[node] == "entity_node":
            entityTypes.append(regularized_node)
        else:
            propertyValues.append(regularized_node)

    # add all edge values to lexicon
    # TODO: this gets the label but i need the type because relationships look different in the lexicon
    property_edges = []
    relationship_edges = []
    for edge in list(graph.edges):
        edge_data = graph.get_edge_data(edge[0], edge[1])
        regularized_edge = regularize_edge(edge_data['label'])
        # if property, assume it's simple and just add it to the properties section
        if edge_data['edge_type'] == 'property':
            property_edges.append(regularized_edge)
            lexicon_skeleton["properties"][regularized_edge] = ""
        else:
            relationship_edges.append(regularized_edge)

    # sort lists
    entityTypes = sorted(entityTypes)
    propertyValues = sorted(propertyValues)
    property_edges = sorted(property_edges)
    relationship_edges = sorted(relationship_edges)

    # put it all into the lexicon_skeleton
    relationship_skeleton = {
        "composition": "",
        "property_predicate": {
            "predicate_type": "",
            "predicate_label": ""
        }
    }
    for e in entityTypes:
        lexicon_skeleton["entityTypes"][e] = ""
    for p in propertyValues:
        lexicon_skeleton["propertyValues"][p] = ""
    for pe in property_edges:
        lexicon_skeleton["properties"][pe] = ""
    for re in relationship_edges:
        lexicon_skeleton["properties"][re] = relationship_skeleton

    return lexicon_skeleton


