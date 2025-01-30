import os
import yaml
import networkx as nx
from delphin import ace
from delphin.codecs import simplemrs
from networkx import MultiDiGraph
from POGG.data_regularization import regularize_node, regularize_edge
from POGG.graph_to_mrs import load_lexicon, node_to_mrs, edge_to_mrs
from POGG.graph_util import find_root
from POGG.mrs_util import wrap_ssement

class POGGenerator:
    """
    Class to perform generation tasks from a graph or graph(s)
    """
    def __init__(self, yaml_files):
        config = {}
        for y in yaml_files:
            config.update(yaml.safe_load(open(y)))

        self.ERG_path = config['ERG']
        self.SEMI_path = config['SEMI']
        self.data_directory = config['data_directory']
        self.graph_directory = config['graph_directory']
        self.results_directory = config['results_directory']
        self.LEXICON = load_lexicon(config['LEXICON'])
        self.statistics = POGGStatistics()


    def read_graph(self, graph_path):
        if ".dot" in graph_path:
            graph_file = os.path.basename(graph_path)
            graph_name = graph_file.strip('.dot')
            graph = nx.drawing.nx_pydot.read_dot(graph_path)
            print(graph_name)
            return graph



    def graph_to_mrs_new(self, root, graph):
        """
        Convert a graph to MRS (SSEMENT)
        :param root: text on root node
        :type root: str
        :param graph: graph to compose MRS from
        :type graph: DiGraph
        :param variables: dict of variables and values, if you need to constrain them (e.g. NUM=sg)
        :type variables: dict
        :return: composed SEMENT
        :rtype: SEMENT
        """
        regularized_root = regularize_node(root)

        # add graph to POGGStatistics for this generator
        self.statistics.add_graph(graph)

        # 1. get MRS for root
        root_mrs = node_to_mrs(regularized_root, self.LEXICON, {})

        # 2. for each child ...
        new_composed_mrs = root_mrs
        for child in graph.successors(root):
            # TODO: if the root node or any child edge can't be produced, all children must be marked as disincluded
            # 3. recurse and get the full MRS for the child
            child_mrs = self.graph_to_mrs_new(child, graph)

            # 4. compose child_mrs with the root
            edge = graph.get_edge_data(root, child)
            regularized_edge = regularize_edge(edge[0]['label'])
            new_composed_mrs = edge_to_mrs(new_composed_mrs, child_mrs, regularized_edge, self.LEXICON)

        # 5. return the result
        return new_composed_mrs

    def generate_MRS_from_graph(self, graph):
        graph_mrs = self.graph_to_mrs_new(find_root(graph), graph)
        # TODO: THIS RETURNS A STRING... DO I WANT THAT?
        return wrap_ssement(graph_mrs)


    def generate_MRS_from_graphs(self, graphs):
        print("teehee")


    def generate_text_from_MRS_results(self, results):
        with ace.ACEGenerator(self.ERG_path, ['-r', 'root_frag']) as generator:
            for r in results:
                print("GENERATING FROM ... ")
                print(r)
                generator_response = generator.interact(r)
                print("GENERATED RESULTS ... ")
                for r in generator_response.results():
                    print(r.get('surface'))




class POGGStatistics:
    """
    Class to keep track of statistics while running generation tasks
    """
    def __init__(self):
        # tuple of graphs paired with their statistics
        self.graphs = list()

    def add_graph(self, graph):
        self.graphs.append(POGGGraph(graph))


class POGGGraph(MultiDiGraph):
    """
    POGGGraphs, created from a NetworkX graph and adds attributes to each node/edge for keeping track of statistics
    """
    def __init__(self, graph):
        # make empty graph
        super().__init__()
        # populate with incoming graph
        self._traverse_graph(find_root(graph), graph, 0, 0)

        self.did_generate_MRS = False
        self.did_generate_text = False
        self.generated_MRS = None
        self.generated_text = None
        self.results_count = 0

    # TODO: DEAL WITH CYCLES
    def _traverse_graph(self, root, graph, node_counter, edge_counter):
        # create POGGNodeStats for root
        root_node = POGGNode(root, "{}_{}".format(root, node_counter))
        # add to nodes list
        self.add_node(root_node)
        node_counter += 1

        # go through children
        for child in graph.successors(root):
            # create child POGGNodeStats object
            child_node = self._traverse_graph(child, graph, node_counter, edge_counter)

            # create POGGEdgeStats object
            edge = graph.get_edge_data(root, child)
            label = edge[0]['label']
            edge_object = POGGEdgeStats(label, "{}_{}".format(label, edge_counter), root_node, child_node)
            edge_counter += 1

            self.add_edge(root_node, child_node, edge_stats=edge_object)

        return root_node



class POGGGraphStats:
    """
    Class to keep track of statistics from generating from one graph
    """

    # TODO: DEAL WITH CYCLES
    def _traverse_graph(self, root, graph, node_counter, edge_counter):
        # create POGGNodeStats for root
        root_stats_obj = POGGNode(root, "{}_{}".format(root, node_counter))
        # add to nodes list
        self.nodes.append(root_stats_obj)
        node_counter += 1

        # go through children
        for child in graph.successors(root):
            # create child POGGNodeStats object
            child_stats_obj = self._traverse_graph(child, graph, node_counter, edge_counter)

            # create POGGEdgeStats object
            edge = graph.get_edge_data(root, child)
            label = edge[0]['label']
            edge_object = POGGEdgeStats(label, "{}_{}".format(label, edge_counter), root_stats_obj, child_stats_obj)
            edge_counter += 1

            self.edges.append(edge_object)

            # add (edge, child) tuples to root's children list
            root_stats_obj.children.append((edge_object, child_stats_obj))


        return root_stats_obj

    def __init__(self, graph):
        self.graph = graph
        self.did_generate_MRS = False
        self.did_generate_text = False
        self.generated_MRS = None
        self.generated_text = None
        self.results_count = 0
        self.nodes = list()
        self.edges = list()

        # establish POGGNodeStats and POGGEdgeStats objects in a structure that is isomorphic to the input graph 
        # self._traverse_graph(find_root(graph), graph, 0, 0)




class POGGNode:
    """
    Class to keep track of statistics from generating from one node
    """
    def __init__(self, node_name, node_id):
        pass
        self.node_id = node_id
        self.node_name = node_name
        self.did_generate_MRS = False
        self.did_get_included = False


class POGGEdgeStats:
    """
    Class to keep track of statistics from generating from one edge
    """
    def __init__(self, edge_name, edge_id, parent, child):
        self.edge_name = edge_name
        self.edge_id = edge_id
        self.parent = parent
        self.child = child
        self.did_generate_MRS = False
        self.did_generate_MRS = False