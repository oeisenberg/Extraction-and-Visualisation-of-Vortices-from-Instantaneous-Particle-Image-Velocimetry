import math
import numpy as np
import pandas as pd
from DataType import *
from pandas import DataFrame
from queue import Queue

def Holman(data):
    def assign_velocity_direction_labels(data):
        def calcAngle(x, y):
            dotProd = np.dot([x, y], [1, 0])
            input_magnitude = (x ** 2 + y ** 2) ** 0.5
            angle = math.degrees(math.acos((dotProd/input_magnitude)))
            if y < 0: angle = -angle
            return angle
        def calcDirRange(angle):
            if angle < 0:
                angle = 360 + angle
            sector = np.ceil(angle / direction_range)
            assert sector >= 1
            return sector

        labelled_data = np.zeros(np.shape(data)[0])
        possible_direction_ranges = 4
        direction_range = 360 / possible_direction_ranges

        # Labelling is ANTI-clockwise from 1
        idx_x = 0
        for idx in range(0, np.shape(data)[0]):
            labelled_data[idx_x] = calcDirRange(calcAngle(data[idx, 3], data[idx,4]))
            idx_x = idx_x + 1
        return labelled_data

    labelled_data = assign_velocity_direction_labels(data)
    print(labelled_data)
    # topilogical clean up?
        # loop through x = 1:-1 & y = 1:-1
        # for each vertex check if false id'd else categorise as a vortex
    pass
def Jiang(data):
    def get_nonZero_neighbour(data, node, y_increment, x_increment):
        while(node.u == 0 and node.v == 0): 
            node = data.shift_x_axis(node, x_increment)
            node = data.shift_y_axis(node, y_increment)
        return node

    def isVortex(data, node):
        try:
            # if neighbour is 0 keep searching until non/boarder reached.
            left_node = data.get_leftNode(node)
            right_node = data.get_rightNode(node)
            upper_node = data.get_upperNode(node)
            lowerNode = data.get_lowerNode(node)
            if((get_nonZero_neighbour(data, left_node, 0, -1).v + get_nonZero_neighbour(data, right_node, 0, 1).v == 0) and \
                (get_nonZero_neighbour(data, upper_node, 1, 0).u + get_nonZero_neighbour(data, lowerNode, -1, 0).u == 0)):
                if (left_node.v + upper_node.u != 0):
                    return True
        except:
            return False
        return False

    def id_vortcies(data):
        # for each data point in the grid, 
        # call is vortex on that point
        # set to vortex core if true, append to seperate list?
        for y in data.y:
            for x in data.x:
                try:
                    node = data.getNodeAt(x, y)
                    if not data.containsNode(node):
                        data.addNode(node)
                    if isVortex(data, node):
                        data.vortcies.addNode(node)
                    
                except:
                    pass
        return data

    def change_frameOfReference(data):
        u_avg = np.average(data.getAll('u'))
        v_avg = np.average(data.getAll('v'))
        data.subtractFromAll('u', u_avg)
        data.subtractFromAll('v', v_avg)
        return data

    def id_algo(data):
        def label_data(data):
            def sign_check(value):
                if value < 0.0: return -1
                if value > 0.0: return 1
                return 0
            for iVelocity in range(0, data.length()):
                data.setNodeAttr(iVelocity, 'u', sign_check(data.getNodeAttr(iVelocity, 'u')))
                data.setNodeAttr(iVelocity, 'v', sign_check(data.getNodeAttr(iVelocity, 'v')))
            return data
        def reformatData(data): 
            x_vals, x_idx = np.unique(data.getAll('x'), return_inverse=True)
            y_vals, y_idx = np.unique(data.getAll('y'), return_inverse=True)
            return Grid(data, x_vals, y_vals, x_idx, y_idx)

        labelled_data = label_data(data)
        labelled_data = reformatData(labelled_data)
        labelled_data = id_vortcies(labelled_data)
        return labelled_data

    def gwth_algo(data):
        def BFS(data, grown_vortcies, init_vortex, visited):
            def checkNode(data, vortex, grown_vortcies, frontier, visited, init_vortex):
                if not visited.nodes.__contains__(tuple([vortex.x, vortex.y])): #faster, using hashtables
                    if (isVortex(data, vortex)):
                        init_vortex.addChild(vortex)
                        data.vortcies.addNode(init_vortex)
                        data.vortcies.removeNode(vortex)
                        data.all_nodes.addNode(vortex)
                        data.all_nodes.addNode(init_vortex)
                        frontier.put(vortex)
                    visited.addNode(vortex)
                return frontier, visited

            visited.addNode(init_vortex)
            frontier = Queue(maxsize=0)
            frontier.put(init_vortex)
            while(not frontier.empty()):
                vortex = frontier.get()
                # check all four neighbours - if vortex add to frontier
                left_node = data.get_leftNode(vortex)
                right_node = data.get_rightNode(vortex)
                upper_node = data.get_upperNode(vortex)
                lowerNode = data.get_lowerNode(vortex)
                frontier, visited = checkNode(data, left_node, grown_vortcies, frontier, visited, init_vortex)            
                frontier, visited = checkNode(data, right_node, grown_vortcies, frontier, visited, init_vortex)
                frontier, visited = checkNode(data, upper_node, grown_vortcies, frontier, visited, init_vortex)
                frontier, visited = checkNode(data, lowerNode, grown_vortcies, frontier, visited, init_vortex)
            return visited, data

        grown_vortcies = Collective()
        visited = Collective()
        for key in list(data.vortcies.nodes.keys()):
            visited, data = BFS(data, grown_vortcies, data.nodes[key], visited)

        return data

    data = change_frameOfReference(data)
    data = id_algo(data)
    data.setNodesAsVortcies()
    data.all_nodes = Collective()
    data = gwth_algo(data)
    data.all_nodes.addNodes(data.vortcies.nodes) # adding ID'd childless vortcies
    data.setNodesAsVortcies()

    return data.vortcies.nodes, data.all_nodes