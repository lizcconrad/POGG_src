from tabulate import tabulate


def node_evaluation(node_eval_info):
    node_table = []
    successful_nodes = 0
    included_nodes = 0
    for n in node_eval_info:
        n_info = node_eval_info[n]
        node_table.append([n, n_info['produced'][0], n_info['produced'][1],
                           n_info['included'][0], n_info['included'][1]])
        if n_info['produced'][0]:
            successful_nodes += 1
        if n_info['included'][0]:
            included_nodes += 1
    return tabulate(sorted(node_table, key=lambda x: x[0]),
                    headers=["Node", "MRS Produced", "Reason", "Included in MRS", "Reason"])


def edge_evaluation(edge_eval_info):
    edge_table = []
    successful_edges = 0
    included_edges = 0
    for e in edge_eval_info:
        e_info = edge_eval_info[e]
        edge_table.append([e, e_info['produced'][0], e_info['produced'][1],
                           e_info['included'][0], e_info['included'][1]])
        if e_info['produced'][0]:
            successful_edges += 1
        if e_info['included'][0]:
            included_edges += 1
    return tabulate(sorted(edge_table, key=lambda x: x[0]),
                    headers=["Edge", "MRS Composed", "Reason", "Included in MRS", "Reason"])


def evaluation_summary(eval_info):
    # count successful nodes
    successful_nodes = 0
    included_nodes = 0
    for n in eval_info['nodes']:
        if eval_info['nodes'][n]['produced'][0]:
            successful_nodes += 1
        if eval_info['nodes'][n]['included'][0]:
            included_nodes += 1

    # count successful edges
    successful_edges = 0
    included_edges = 0
    for e in eval_info['edges']:
        if eval_info['edges'][e]['produced'][0]:
            successful_edges += 1
        if eval_info['edges'][e]['included'][0]:
            included_edges += 1

    # node stats
    total_nodes = len(eval_info['nodes'])
    if total_nodes == 0:
        nodes_produced_coverage = 0
        nodes_included_coverage = 0
    else:
        nodes_produced_coverage = successful_nodes / total_nodes
        nodes_included_coverage = included_nodes / total_nodes
    # edge stats
    total_edges = len(eval_info['edges'])
    if total_edges == 0:
        edges_produced_coverage = 0
        edges_included_coverage = 0
    else:
        edges_produced_coverage = successful_edges / total_edges
        edges_included_coverage = included_edges / total_edges

    summary_table = [["Nodes", "Produced", successful_nodes, total_nodes, nodes_produced_coverage],
                     ["Nodes", "Included", included_nodes, total_nodes, nodes_included_coverage],
                     ["Edges", "Produced", successful_edges, total_edges, edges_produced_coverage],
                     ["Edges", "Included", included_edges, total_edges, edges_included_coverage]]

    return tabulate(summary_table, headers=["Graph Component", "Metric", "Successful", "Total", "Coverage"])
