# Contains functions for building graphs and writing them to files
# ORGANIZED: 01/30/2024
# DOCUMENTED: 01/30/2024
import networkx as nx
import random


# TODO: Needs to be generalized for data shapes beyond the perplexity data
def build_graph(entities):
    """
    build a graph out of a list of entities where nodes are entities and property values,
    and edges are relationships between entities and property names

    Data shape:
    {'Entity': 'idGlowingGrass1',
        'Properties': [
            {'args': ['idGlowingGrass1_prop_idColor', 'green'], 'functor': ','}
        ],
        'Relationships': [
            {'args': ['idGlowingGrass1', {'args': ['isTouching', 'idGlowingArea1'
        ], 'functor': ','}],
    'functor': ','}]}

    :param entities: list of entities to build a graph from
    :type entities: list
    """
    # if entities is not already a list, make it one
    if not isinstance(entities, list):
        entities = [entities]

    # create the graph
    graph = nx.DiGraph()

    for entity in entities:
        # add a node for the entity ...
        entity_name = entity['Entity']
        graph.add_node(entity_name, node_type="entity_node")

        # TODO: again, weird
        # skip if for some reason entity_name is None
        if entity_name is None or entity_name == "":
            continue

        # add nodes/edges for each property ...
        properties = entity['Properties']
        for prop in properties:
            prop_name = prop['args'][0]
            prop_value = prop['args'][1]

            # sometimes prop_value is a list... if so, just convert the list to a comma separated string?
            # TODO: this should be handled better...
            if isinstance(prop_value, list):
                new_prop_value = ""
                for v in prop_value[:-1]:
                    new_prop_value += "{}, ".format(v)
                new_prop_value += prop_value[-1]
                prop_value = new_prop_value

            # TODO: not sure about this solution either
            # if the prop_value is multiple words, put quotes around it
            # (because some characters like : are illegal in nodes without quotes)
            if " " in str(prop_value) or ":" in str(prop_value):
                prop_value = '"{}"'.format(prop_value)

            # TODO: again, weird
            # skip if for some reason prop_value is None
            if prop_value is None or prop_value == "":
                continue

            graph.add_node(prop_value, node_type="property_node")
            graph.add_edge(entity_name, prop_value, label=prop_name, edge_type="property")

        # add edges for relationships between entities...
        relationships = entity['Relationships']
        for rel in relationships:
            rel_name = rel['args'][1]['args'][0]
            other_entity = rel['args'][1]['args'][1]

            graph.add_node(other_entity, node_type="entity_node")
            graph.add_edge(entity_name, other_entity, label=rel_name, edge_type="relationship")

    return graph


def write_graph_to_dot(graph, filepath):
    """
    write the graph to a .dot file
    :param graph:
    :type graph: DiGraph
    :param filepath:
    :type filepath: str
    """
    nx.nx_pydot.write_dot(graph, filepath)


def write_graph_to_png(graph, filepath):
    """
    write the graph to a .png file
    :param graph:
    :type graph: DiGraph
    :param filepath:
    :type filepath: str
    """
    png_graph = nx.drawing.nx_pydot.to_pydot(graph)
    png_graph.write_png(filepath)


def write_graph_to_svg(graph, filepath):
    """
    write the graph to a .svg file
    :param graph:
    :type graph: DiGraph
    :param filepath:
    :type filepath: str
    """
    png_graph = nx.drawing.nx_pydot.to_pydot(graph)
    png_graph.write_svg(filepath)


def _select_property_edges(graph, entity, maximum=None):
    """
    Select edges of a graph associated with properties (i.e. edges whose value for "edge_type" is "property")
    for a given entity
    :param graph: Graph (with possibly many entities) to select edges from
    :type graph: DiGraph
    :param entity: The specific entity to find property edges for
    :type entity: str
    :param maximum: Maximum number of property edges to return
    :type maximum: int
    :return: list of edges
    :rtype: list
    """
    property_edges = [(parent, child, edge) for parent, child, edge in graph.out_edges(entity, data=True) if
                      edge["edge_type"] == "property"]

    if max is None or len(property_edges) <= maximum:
        return property_edges
    else:
        return random.sample(property_edges, maximum)


def _select_relationship_edges(graph, entity, maximum=None):
    """
    Select edges of a graph associated with properties (i.e. edges whose value for "edge_type" is "relationship")
    for a given entity
    :param graph: Graph (with possibly many entities) to select edges from
    :type graph: DiGraph
    :param entity: The specific entity to find relationship edges for
    :type entity: str
    :param maximum: Maximum number of relationship edges to return
    :type maximum: int
    :return: list of edges
    :rtype: list
    """
    relationship_edges = [(parent, child, edge) for parent, child, edge in graph.out_edges(entity, data=True) if
                          edge["edge_type"] == "relationship"]

    if max is None or len(relationship_edges) <= maximum:
        return relationship_edges
    else:
        return random.sample(relationship_edges, maximum)


def select_subgraphs(graph):
    """
    Given a grpah with all entities you want to generate subgraphs for,
    select subgraphs with a random # of properties and relationships for each entity
    return the dict with the entity name as the key and the subgraph as the value

    The graph must include all information about relevant entities (as opposed to just information about one entity
    and its relationships to other entities) or the function won't be able to get properties of the related entities.

    Example: if the graph contains properties about a Box and its relationship to a Ball, if the graph does not
    also contain the information about the Ball, and just that it's related to the Box, then a subgraph with properties
    about the ball can't be selected
    :param graph: graph with all entities included
    :type graph:
    :return: dict of subgraphs (entity name as key, subgraph as value)
    :rtype: dict
    """

    subgraphs_dict = {}

    # for each entity in the graph...
    node_type_dict = nx.get_node_attributes(graph, "node_type")
    for entity in list(graph.nodes()):
        if node_type_dict[entity] == "entity_node":
            subgraph = nx.DiGraph()

            # add the primary entity, mark it as root
            subgraph.add_node(entity, node_type="entity_node", root="root")

            # get property_edges for entity (maximum 3 properties)
            # get all properties from an entity, as many have 0
            # if more than 3 limit it to 3
            property_edges = _select_property_edges(graph, entity, 3)

            # get relationship_edges for entity (maximum 2)
            # random # of relationships 0-2, as all entities have many relationships
            relationship_count = random.randrange(3)
            relationship_edges = _select_relationship_edges(graph, entity, relationship_count)

            # get property_edges and relationship_edges for related entities
            child_property_edges = []
            child_relationship_edges = []
            for r_edge in relationship_edges:
                child_entity = r_edge[1]
                # get 2 properties of child if possible
                child_property_edges.extend(_select_property_edges(graph, child_entity, 2))

                # get up to 1 relationship for the child_entity
                if random.getrandbits(1):
                    child_relationship_edges.extend(_select_relationship_edges(graph, child_entity, 1))

            # extend the property_edges and relationship_edges lists
            property_edges.extend(child_property_edges)
            relationship_edges.extend(child_relationship_edges)

            all_edges = property_edges + relationship_edges
            for e in all_edges:
                subgraph.add_edge(e[0], e[1], label=e[2]['label'], edge_type=e[2]['edge_type'])

            subgraphs_dict[entity] = subgraph

    return subgraphs_dict


def find_root(graph):
    """
    Find the root of a given graph. First check for "root" attribute, otherwise do topological sort,
    otherwise can't be guessed
    :param graph: graph to find root in
    :type graph: DiGraph
    """
    # attempt to use 'root' attribute
    root_node_list = [node for node, attrs in graph.nodes(data=True)
                    if 'root' in attrs.keys() and attrs['root'] == 'root']
    if len(root_node_list) > 0:
        return root_node_list[0]
    # try topological sort (only works if there are no cycles)
    try:
        root_node_list = list(nx.topological_sort(graph))
        if root_node_list[0] == "\\n":
            return root_node_list[1]
        else:
            return root_node_list[0]
    except nx.NetworkXUnfeasible:
        pass
    # try finding node with no in-degree=0 (could have random detached node that works, so this is not a great guess)
    root_node_list = [node for node, indegree in graph.in_degree() if indegree == 0]
    if len(root_node_list) > 0:
        if root_node_list[0] == "\\n":
            return root_node_list[1]
        else:
            return root_node_list[0]
    # couldn't find root
    return None


