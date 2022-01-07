from _typeshed import Self
import random

from numpy import bitwise_and
from Node import Node
from EvolutionStep import EvolutionStep
from Connection import Connection


class Genome:
    def __init__(self, inputs_num, outputs_num):
        self.inputs_num = inputs_num
        self.outputs_num = outputs_num
        self.layers_num = 2
        self.next_node_num = 0
        self.bias_node = 0  # initialize bias at 0
        self.next_connection_num = 0  # initialize connection numbers at 0
        self.nodes = []  # list of nodes
        self.genes = []  # list of connections
        self.network_ordered = []  # list of nodes, ordered by when the neural network processes through them
        self.evolution_history = []  # list of evolutionSteps that shows how the unique genome structure
        # has evolved over time

        for i in range(inputs_num):
            new_input = Node(self.next_node_num)
            new_input.layer = 0
            self.next_node_num += 1
            self.nodes.append(new_input)

        for i in range(outputs_num):
            new_output = Node(self.next_node_num)
            new_output.layer = 1
            self.next_node_num += 1
            self.nodes.append(new_output)

        bias = Node(self.next_node_num)
        self.next_node_num += 1
        bias.layer = 0
        self.nodes.append(bias)
        
        
    # mutation method 1. Add node to the nueral net
    def add_node(innovation_history_list):
        #if no connections exist, create one 
        if len(Self.genes) == 0:
            Self.add_connection(Self, innovation_history_list)
            return
        # 
        randomConnectionIndex = int(random.uniform(0, len(Self.genes)))
        
        #cant remove bias node - check and re randomize if case
        while(Self.genes[randomConnectionIndex].from_node.id == Self.bias):
            randomConnectionIndex = int(random.uniform(0, len(Self.genes)))
        
        Self.genes[randomConnectionIndex].enabled = False
        
        newNodeNumber = Self.next_node_num
        Self.nodes.append(Node(newNodeNumber))
        Self.next_node_num += 1
        
        # for connection bw a to b 
        connectionInnovationNumber = Self.get_innov_num(Self, innovation_history_list,
                                                    Self.genes[randomConnectionIndex].from_node,
                                                    Self.get_node(newNodeNumber))
        Self.genes.append(Connection(Self.genes[randomConnectionIndex].from_node, Self.get_node(newNodeNumber), 1, connectionInnovationNumber))
        
        # for connection bw b to c
        connectionInnovationNumber = Self.get_innov_num(Self, innovation_history_list, 
                                                        Self.get_node(newNodeNumber), 
                                                        Self.genes[randomConnectionIndex].to_node)
        Self.genes.append(Connection(Self.get_node(newNodeNumber), 
                                     Self.genes[randomConnectionIndex].to_node, 
                                     Self.genes[randomConnectionIndex].weight,
                                     connectionInnovationNumber))
        Self.get_node(newNodeNumber).layer = Self.genes[randomConnectionIndex].from_node.layer + 1
        
        #get innovation number for bias connection
        connectionInnovationNumber = Self.get_innov_num(Self, innovation_history_list, 
                                                        Self.get_node(Self.bias_node), 
                                                        Self.get_node(newNodeNumber))
        # insert connection to bias node 
        Self.genes.append(Connection(Self.get_node(Self.bias_node), Self.get_node(newNodeNumber), 
                                     0, connectionInnovationNumber))
        
        
        if Self.get_node(newNodeNumber).layer == Self.genes[randomConnectionIndex].to_node.layer:
            for i in range (len(Self.nodes) - 1):
                if Self.nodes[i].layer >= Self.get_node(newNodeNumber):
                    Self.nodes[i].layer += 1
            Self.layers += 1

        Self.connect_nodes()
        return
    # return the node pos with the matching ID or returns none
    def get_node(searchID):
        for i in len(Self.nodes):
            if Self.nodes[i].id == searchID:
                return Self.nodes[i]
        return None
                
        

    def connect_nodes(self):

        for i in range(len(self.nodes)):
            self.nodes[i].output_connections.clear()

        for i in range(len(self.genes)):
            self.genes[i].node_from.outputLink.add(self.genes[i])

    def add_connection(self, innovation_history_list):
        if self.is_full():
            print("Network full. Add connection failed.")
            return

        from_index = int(random.uniform(0, len(self.nodes)))
        to_index = int(random.uniform(0, len(self.nodes)))

        while from_index == to_index or self.cannot_connect(from_index, to_index):
            from_index = int(random.uniform(0, len(self.nodes)))
            to_index = int(random.uniform(0, len(self.nodes)))

        from_node = self.genes[from_index]
        to_node = self.genes[to_index]

        connection_innov_num = self.get_innov_num(from_node, to_node)
        self.genes.append(Connection(from_node, to_node, random.uniform(-1, 1), connection_innov_num))  # may error
        self.connect_nodes()

    def is_full(self):
        max_possible = 0
        node_count_per_layer = []
        for i in range(len(self.nodes)):
            node_count_per_layer[self.nodes[i].layer] += 1

        for i in range(self.layers_num - 1):
            nodes_in_next = 0
            for j in range(i + 1, self.layers_num):
                nodes_in_next += node_count_per_layer[j]

            max_possible += nodes_in_next * node_count_per_layer[i]

        return max_possible == len(self.genes)

    def cannot_connect(self, to_index, from_index):
        if self.nodes[to_index].layer <= self.nodes[from_index].layer:
            return True  # if same layer or to is behind from
        if self.nodes[from_index].is_connected(self.nodes[to_index]):
            return True
        return False

    def get_innov_num(self, from_node, to_node):
        is_new = True
        connection_innovation_num = self.next_connection_num

        for i in range(len(self.evolution_history)):
            if self.evolution_history[i].equals(self, from_node, to_node):
                is_new = False
                connection_innovation_num = self.evolution_history[i].innovation_num
                break

        if is_new:
            self.record_new_evolution(from_node.id, to_node.id, connection_innovation_num)
            self.next_connection_num += 1

        return connection_innovation_num

    def record_new_evolution(self, from_node_id, to_node_id, connection_innov_num):
        innovation_num_list = []
        for i in range(len(self.genes)):
            innovation_num_list.append(self.genes[i].innovation_num)
        new_evolution = EvolutionStep(from_node_id, to_node_id, connection_innov_num, innovation_num_list)
        self.evolution_history.append(new_evolution)
