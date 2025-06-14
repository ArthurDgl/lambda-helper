import lambdas
import copy
from pyvis.network import Network


class LambdaSolver:
    def __init__(self, expression, vis = False):
        self.start = lambdas.LambdaExpression(expression)
        self.to_process = [self.start]
        self.discovered = [str(self.start)]
        self.graph = {}
        self.solution = None
        self.vis = vis
        if vis:
            self.net = Network('1080px', '1920px')
            self.net.add_node(str(self.start), title=str(self.start), label=str(self.start), value=0, color="#7EFFA9")
    
    def solve(self):
        steps = 0
        result = False
        end = False
        while len(self.to_process) > 0:
            current = self.to_process.pop(0)
            current_key = str(current)
            self.graph[current_key] = []
            reductions = current.find_reductions()
            depth = 0
            if self.vis:
                depth = self.net.get_node(current_key)["value"]
            if len(reductions) == 0:
                self.solution = current
                result = True
                end = True
            for reduction in reductions:
                reduced = copy.deepcopy(current)
                reduced.apply_reduction(reduction)
                reduced_str = str(reduced)
                added = False
                if self.vis:
                    self.graph[current_key].append(reduced)
                if not end and reduced_str not in self.discovered:
                    self.discovered.append(str(reduced))
                    self.to_process.append(reduced)
                    if self.vis:
                        self.net.add_node(reduced_str, title=reduced_str, label=f"{depth+1}", value=depth+1)
                        added = True
                if self.vis and (added or reduced_str in self.net.node_map):
                    self.net.add_edge(current_key, reduced_str)
            steps += 1
            if not end and steps >= 10000:
                break
        if self.vis:
            if result:
                node = self.net.get_node(str(self.solution))
                node["label"] = str(self.solution)
                node["color"] = "#8133FF"
                self.net.get_node(str(self.start))["value"] = node["value"]
            self.net.show("lambda.html", notebook=False)
        return result

    '''
    Does not seem to aid performance
    '''
    def insert_by_length(self, lambda_expression):
        expression_length = str(lambda_expression)
        for i in range(len(self.to_process)):
            if expression_length < str(self.to_process[i]):
                self.to_process.insert(i, lambda_expression)
                return
        self.to_process.append(lambda_expression)