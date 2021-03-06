import logging

import torch

from supernets.implementation.EdgeCostEvaluator import EdgeCostEvaluator
from supernets.interface.NetworkBlock import NetworkBlock

logger = logging.getLogger(__name__)


class ComputationCostEvaluator(EdgeCostEvaluator):
    def init_costs(self, model):
        device = next(model.parameters()).device
        with torch.no_grad():
            input_var = (torch.ones(1, *model.input_size).to(device),)
            graph = model.net

            self.costs = torch.Tensor(graph.number_of_nodes())

            #todo: Not final
            graph.node[model.in_nodes[0]]['input'] = [*input_var]
            for node in model.traversal_order:
                cur_node = graph.node[node]
                input_var = model.format_input(cur_node['input'])

                out = cur_node['module'](input_var)

                if isinstance(cur_node['module'], NetworkBlock):
                    cost = cur_node['module'].get_flop_cost(input_var)
                else:
                    logger.warning('Node {} isn\'t a Netwrok block'.format(node))

                self.costs[self.node_index[node]] = cost
                cur_node['input'] = []

                for succ in graph.successors(node):
                    if 'input' not in graph.node[succ]:
                        graph.node[succ]['input'] = []
                    graph.node[succ]['input'].append(out)
