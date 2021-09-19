from graphviz import Digraph
from .gain_functions import shannon, gini
import uuid


class DecisionTree:

    def __init__(self, training_set, config):
        GAIN_FUNCTION = {"shannon": shannon, "gini": gini}
        self.gain_function = GAIN_FUNCTION[config["gain_function"].lower()]

        if not self.gain_function:
            raise Exception("Invalid gain function")
        self.training_set = training_set
        self.objective = config["objective"]
        self.tree = self.__generate_subtree(training_set, parent=None)

    def print(self):
        dot = Digraph()
        self.__add_node_rec(dot, self.tree)
        print(dot.source)

    def digraph(self):
        dot = Digraph()
        self.__add_node_rec(dot, self.tree)
        return dot

    def __add_node_rec(self, dot, node, parent=None):
        name = node.value
        dot.node(node.id, name)
        if parent is not None:
            dot.edge(parent.id, node.id)

        for child in node.children:
            self.__add_node_rec(dot, child, node)

    def __generate_subtree(self, data, parent):
        classes = list(data.keys())
        objective = self.objective

        # Case (1 and 2) dataset has all values the same
        if len(data[objective].unique()) == 1:
            return Node(data[objective].unique()[0], parent)

        # Case (3) attributes are empty
        if len(classes) == 1:
            return Node(str(data[objective].mode()[0]), parent)

        # remove objective class from classes so that only attributes remain
        classes.remove(objective)

        # Case (4) obtain root node
        # First calulate all possible gains
        gains_tuple = [(self.__gain(attr), attr) for attr in classes]
        # Choose attribute that maximizes Gain
        _, max_attr = max(gains_tuple)
        node = Node(max_attr, parent)
        children = []

        # for each posible value in the winner attribute
        for value in data[max_attr].unique():
            # Generate subset where max_attr is value and drop that column
            edge = Node(str(value), node)
            children.append(edge)
            new_data = data[data[max_attr] == value].drop(max_attr, axis=1)
            edge.children.append(self.__generate_subtree(new_data, parent=edge))

        node.children = children
        return node

    def __gain(self, attribute):
        """
        Gain(S, A) = H(S) - sum( (|S_v|/|S|) * H(S_v) )
        where S_v = subset of S for each value of attribute A

        Returns: float
        """
        data = self.training_set

        def sv(df, attr, val):
            # Subset of df where column attr has values val
            return df[df[attr] == val]

        # Array of subsets for each possible value of column attribute
        subsets = [sv(data, attribute, v) for v in data[attribute].unique()]

        # H(S)
        general_gain = self.gain_function(data[self.objective])

        sum_gains = 0
        for s_v in subsets:
            # frequency of value v for column attribute
            frequency = len(s_v) / len(data)
            # H(S_v)
            gain_v = self.gain_function(s_v[self.objective])
            sum_gains += frequency * gain_v

        return general_gain - sum_gains


class Node:
    def __init__(self, value, parent=None):
        self.value = value
        self.parent = parent
        self.children = []
        self.id = str(uuid.uuid4())

    @property
    def is_leaf(self):
        return len(self.children) == 0
