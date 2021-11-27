import numpy as np
import math
from exceptions import InvalidNodeException
from convex_hull_algos import *

class Collective():
    def __init__(self, list_of_nodes=[]):
        def listToDict(node_xy_vals, list_of_nodes):
            dictionary = {tuple(node_xy_vals[i]) : list_of_nodes[i] for i in range(0, len(list_of_nodes))}
            return dictionary
        
        node_xy_vals = [[node.x , node.y] for node in list_of_nodes]
        self.nodes = listToDict(node_xy_vals, list_of_nodes)

    def addNode(self, node):
        self.nodes[tuple([node.x, node.y])] = node
    
    def addNodes(self, nodes):
        # assume input is of type dict
        self.nodes.update(nodes)

    def removeNode(self, node):
        try:
            del self.nodes[tuple([node.x, node.y])]
        except:
            pass

    def getAll(self, var):
        return [getattr(node, var) for node in self.nodes.values()]

    def addToAll(self, var, value):
        for key in list(self.nodes.keys()):
            node = self.nodes.get(key)
            node = self.updateNodeAttr(node, var, getattr(node, var) + value)
            self.nodes[key] = node

    def subtractFromAll(self, var, value):
        for key in list(self.nodes.keys()):
            node = self.nodes.get(key)
            node = self.updateNodeAttr(node, var, getattr(node, var) - value)
            self.nodes[key] = node

    def setNodeAttr(self, idx, var, value):
        keys = list(self.nodes.keys())
        key = keys[idx]
        node = self.nodes.get(key)
        setattr(node, var, value)
        self.nodes[key] = node

    def getNodeAttr(self, idx, var):
        return getattr(list(self.nodes.values())[idx], var)

    def updateNodeAttr(self, node, var, value):
        setattr(node, var, value)
        return node

    def key(self):
        return [self.x, self.y]

    # Allows for Collective().length()
    def length(self):
        return self.nodes.__len__()

    # Allows for len(Collective())
    def __len__(self):
        return self.nodes.__len__()

class Grid():
    def __init__(self, collective, unique_x, unique_y, x_idx, y_idx):
        self.x = unique_x
        self.y = unique_y
        self.x_idx = x_idx
        self.y_idx = y_idx

        all_nodes = list(collective.nodes.values())
        for iNode in range(0, np.size(all_nodes)):
            node = all_nodes[iNode]
            collective.setNodeAttr(iNode, 'x_idx', x_idx[iNode])
            collective.setNodeAttr(iNode, 'y_idx', y_idx[iNode])
        self.nodes = collective.nodes
        self.vortcies = Collective()
            
    def getNodeAt(self, x, y):
        # get idx X is at in self.x AND get idx Y is at in self.y
        key = tuple([x, y])
        new_node = self.nodes.get(key)
        if new_node == None:
            new_node = Node([x, y])
            new_node.x_idx = np.where(self.x == x)[0][0]
            new_node.y_idx = np.where(self.y == y)[0][0]
            return new_node

        return new_node

    def getNodeAtIdx(self, x, x_idx, y, y_idx):
        new_x_idx = np.where(self.x == x)[0][0] + x_idx
        new_y_idx = np.where(self.y == y)[0][0] + y_idx
        if new_x_idx < self.x_idx.min() or new_x_idx > self.x_idx.max() or \
            new_y_idx < self.y_idx.min() or new_y_idx > self.y_idx.max():
            # non existant, throw error
            raise InvalidNodeException
        return self.getNodeUsingIdx(self.x_idx[new_x_idx], self.y_idx[new_y_idx])

    def getNodeUsingIdx(self, x_idx, y_idx):
        # find where that idx is in x_idx AND find where that idx is in y_idx 
        x_locs = np.where(self.x_idx == x_idx)[0]
        y_locs = np.where(self.y_idx == y_idx)[0]
        return self.getNodeUsingLocs(self, x_locs, y_locs)

    def getNodeUsingLocs(self, x_locs, y_locs):
        node_idx = [np.where(x_locs == a) for a in y_locs][0]
        if (np.size(node_idx[0]) == 0):
            # non existant, throw error
            raise InvalidNodeException
        node_idx = node_idx[0][0]
        return list(self.nodes.values())[node_idx]

    def get_leftNode(self, node):
        return self.shift_x_axis(node, -1)

    def get_rightNode(self, node): 
        return self.shift_x_axis(node, 1)

    def get_upperNode(self, node):
        return self.shift_y_axis(node, 1)

    def get_lowerNode(self, node):
        return self.shift_y_axis(node, -1)

    def shift_x_axis(self, node, shift):
        x_locs = node.x_idx + shift
        if x_locs < 0: raise InvalidNodeException
        new_x = self.x[x_locs]
        return self.getNodeAt(new_x, node.y)
        
    def shift_y_axis(self, node, shift):
        y_locs = node.y_idx + shift
        if y_locs < 0: raise InvalidNodeException
        new_y = self.y[y_locs]
        return self.getNodeAt(node.x, new_y)

    def setNodeAsVortex(self, node):
        node.isVortex = True
        node.u = 0
        node.v = 0
        self.nodes[tuple([node.x, node.y])] = node

    def setNodesAsVortcies(self):
        keys = list(self.vortcies.nodes.keys())
        for key in keys:
            if self.nodes.__contains__(key):
                self.setNodeAsVortex(self.nodes[key])

    def containsNode(self, node):
        key = tuple([node.x, node.y])
        if self.nodes.__contains__(key):
            return True
        return False

    def addNode(self, node):
        self.nodes[tuple([node.x, node.y])] = node

class Node():
    def __init__(self, row_of_data):
        
        row_of_data.extend([0] * (19 - len(row_of_data)))

        self.x = float(row_of_data[0])
        self.y = float(row_of_data[1])
        self.z = float(row_of_data[2])
        self.u = float(row_of_data[3])
        self.v = float(row_of_data[4])
        self.w = float(row_of_data[5])
        self.velmag = float(row_of_data[6])
        self.flag = float(row_of_data[7])
        self.count = float(row_of_data[8])
        self.valid = float(row_of_data[9])
        self.snr = float(row_of_data[10])
        self.corr = float(row_of_data[11])
        self.dudx = float(row_of_data[12])
        self.dudy = float(row_of_data[13])
        self.dvdx = float(row_of_data[14])
        self.dvdy = float(row_of_data[15])
        self.vort_z = float(row_of_data[16]) # curl, self.dvdx - self.dudy
        self.shear_z = float(row_of_data[17]) # ..., dudy + dvdy
        self.nstrain = float(row_of_data[18]) # divergence, self.dudx + self.dvdy
        
        # Custom fields
        self.isVortex = False
        self.children = Collective()

    def addParent(self, parent_node):
        self.parent = parent_node

    def addChild(self, child_node):
        self.children.addNode(child_node)

    def adopt(self, node):
        for childKey in node.children.nodes:
            self.addChild(node.children.nodes[childKey])
        return self

    def key(self):
        return tuple([self.x, self.y])

class Vector():
    def __init__(self, x, y, z=1):
        self.x = x
        self.y = y
        self.z = z

    def dot(self, other):
        return self.x*other.x + self.y * other.y + self.z * other.z

    def cross(self, other):
        x = self.y * other.z - self.z * other.y
        y = self.z * other.x - self.x * other.z
        z = self.x * other.y - self.y * other.x
        return Vector(x, y, z)

    def magnitude(self):
        return math.sqrt(math.sqrt(math.pow(self.x,2) + math.pow(self.y,2)) + math.pow(self.z,2))

class Family():
    def __init__(self, parent):
        def sign_check(value):
            if value < 0.0: return -1
            if value > 0.0: return 1
            return 0
        def calc_bounding_surface():
            pass

        childern = parent.children.nodes
        parent_fields = list(parent.__dict__.keys())
        data = {k: np.array([]) for k in parent_fields}

        for field in parent_fields:
            if field == 'children':
                break
            data[field] = np.append(data[field], parent.__getattribute__(field))

        for child in childern:
            for field in parent_fields:
                if field == 'children':
                    break
                data[field] = np.append(data[field], childern[child].__getattribute__(field))
        
        self.nodes = data
        self.nodes['xy'] = list(zip(data['x'], data['y']))

        self.x = data['x'].mean()
        self.x_min = self.x - np.std(data['x'])
        self.x_max = self.x + np.std(data['x'])

        self.y = data['y'].mean()
        self.y_min = self.y - np.std(data['y'])
        self.y_max = self.y + np.std(data['y'])

        self.width = self.x_max - self.x_min
        self.height = self.y_max - self.y_min 

        self.surface_area = self.height * self.width    # Area
        self.vel_mag = self.nodes['velmag'].mean()      # VelMag
        
        self.size = len(data['x'])

        self.u = sign_check(self.nodes['u'].mean())     # Avg Dir
        self.v = sign_check(self.nodes['v'].mean())

        # bounding surface
        self.bounding_nodes = monotone_chain(self.nodes['xy']) # gift_wrapping(self.nodes['xy']), scipy_convexhull(self.nodes['xy'])

        self.is_matched = False
        self.PathKey = tuple([None, None, None])
        
    def __len__(self):
        return len(self.data.x)

class Path():
    def __init__(self, init_features, prediction, correspondance, startFrame):
        self.vortices = []
        self.vortices.extend(init_features)
        self.predictor = prediction
        self.predictor.update(2, init_features[2])
        self.corresondance = []
        self.corresondance.append(correspondance)
        self.start = startFrame
        self.Key = tuple([init_features[0].x, init_features[0].y, startFrame])
        self.confidence = self._calc_conf_idx()

    def addFeature(self, new_feature, corresondance):
        self.corresondance.append(corresondance)
        self.vortices.append(new_feature)
        self.predictor.update(len(self), new_feature)
        self.confidence = self._calc_conf_idx()

    def end(self, endFrame):
        self.end = endFrame
        self.length = len(self)

    def _calc_conf_idx(self):
        c_t = sum(self.corresondance)
        tau = 1 # growth factor, same as MinPathLength
        return 1 - pow(math.e, -c_t/tau)

    def __len__(self):
        return len(self.vortices)

class Prediction():
    def __init__(self, feature, candidate):
        fields = list(feature.__dict__.keys())

        for field in fields:
            if not field == 'PathKey' and not field == 'nodes' and not field == 'bounding_nodes' and \
                not field == 'is_matched':
                delta = getattr(candidate, field) - getattr(feature, field)
                setattr(self, field, getattr(candidate, field) + delta)

        self.fields = fields
        self.weight = 2

    def update(self, weight, candidate):
        for field in self.fields:
            if not field == 'PathKey' and not field == 'nodes' and not field == 'bounding_nodes' and \
                not field == 'is_matched':
                value = (getattr(self, field) * weight + getattr(candidate, field)) / (weight + 1)
                setattr(self, field, value)

    def isValid(self):
        if self.size <= 0 or self.surface_area <= 0:
            return False
        return True