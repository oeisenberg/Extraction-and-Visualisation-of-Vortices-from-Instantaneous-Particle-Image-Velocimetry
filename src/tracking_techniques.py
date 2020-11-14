import numpy as np
import math

from Utility import *
from DataType import *
from statistics import mean
from sklearn.neighbors import KNeighborsClassifier

import matplotlib.pyplot as plt

# clean up of childless points by, if possible, 
# assigning to nearby 'families'
def preprocess_data(vortcies, all_nodes):
    def knn_classifier(vortcies, all_nodes):
        def adopt(vortcies, all_nodes, family_idx):
            all_node_keys = list(all_nodes.keys())
            to_remove = []
            for iNode in range(0, len(all_nodes)):     
                node_key = all_node_keys[iNode]
                family = family_idx[iNode]
                if not node_key == vortcies[list(vortcies.keys())[family]].key():
                    parent = vortcies[list(vortcies.keys())[family]]
                    child = all_nodes[node_key]
                    parent.addChild(child)
                    child.addParent(parent)
                    if node_key in vortcies: # child ?
                        to_remove.append(node_key) # child
            for node_key in to_remove: 
                # child reclassified therefore can be removed.
                child = vortcies[node_key]
                new_parent = child.parent.adopt(child)
                vortcies[new_parent.key()] = new_parent
                del vortcies[node_key]
                
            return vortcies
        def make_predictions(distances, vortex_keys, indices, familiy_labels):
            node_idx = 0
            predictions = []
            families = [familiy_labels[idx] for idx in indices]
            for nn_distances in distances:
                to_remove = [d > 10 for d in nn_distances] # threshold is 10
                family_values = [d for (d, remove) in zip(families[node_idx], to_remove) if not remove]
                family = int(min(family_values, key=lambda x:abs(x-mean(family_values)))) # Find closest pos fam value
                node_idx += 1
                predictions.append(family)
            return predictions

        vortex_keys = list(all_nodes.keys())
        familiy_labels = np.empty(len(vortex_keys))
        counter = 0
        for vortex_key in vortcies:
            family_locs = [vortex_keys.index(iChild) for iChild in list(vortcies[vortex_key].children.nodes)]
            family_locs.append(vortex_keys.index(vortex_key))
            familiy_labels[family_locs] = counter
            counter = counter + 1

        neigh = KNeighborsClassifier(n_neighbors = 10, weights = 'distance')
        neigh.fit(vortex_keys, familiy_labels)
        distance, indices = neigh.kneighbors(vortex_keys)
        family_idxs = make_predictions(distance, list(vortcies.keys()), indices, familiy_labels)
        
        return adopt(vortcies, all_nodes, family_idxs)
    def calc_family_properties(vortcies):
        families = []
        for parent in vortcies:
            families.append(Family(vortcies[parent]))
        return {tuple([f.x, f.y]) : f for f in families}

    if len(vortcies) > 0:
        vortcies = knn_classifier(vortcies, all_nodes)
        families = calc_family_properties(vortcies)

    return vortcies, families
    
def Silver_And_Wang(features):
    for iTimestep in range(0, len(features)-1):
        currentStep = features[iTimestep]
        nextStep = features[iTimestep+1]
        # oct trees?
        # https://github.com/jcummings2/pyoctree/blob/master/octree.py

def Samtaney(features):
    def find_match(current_vortex, next_step):
        # look for direct match first
        vortex = next_step.get(current_vortex)
        if not vortex == None:
            return current_vortex

        # look for closest match
        next_keys = list(next_step.keys())
        distances = [math.sqrt(math.pow(k[0]-current_vortex[0],2) + math.pow(k[1]-current_vortex[1],2)) for k in next_keys] 
        idx = distances.index(min(distances))
        return next_keys[idx]
    def test_overlap(current_vortex, closet_vortex):
        OVERLAP_THRESHOLD = 0

        current_vortex_nodes = current_vortex.nodes['xy']
        closet_vortex_nodes = closet_vortex.nodes['xy']
        nodes = current_vortex_nodes
        nodes.extend(closet_vortex_nodes)
        difference = len(nodes) - len(set(nodes))

        if difference > OVERLAP_THRESHOLD:
            # overlap, as no duplicates in OG node lists
            return True
        return False
    def test_surface_area(current_vortex, closet_vortex):
        SURFACE_AREA_THRESHOLD = 1

        difference = closet_vortex.size - current_vortex.size

        difference = difference / max(closet_vortex.size, current_vortex.size)

        if abs(difference) <= SURFACE_AREA_THRESHOLD: # Samataney states, number of nodes is enough
            return True
        return False
    def test_position(current_vortex, closet_vortex):
        DISTANCE_THRESHOLD = 5 

        difference = math.sqrt(math.pow(closet_vortex.x - current_vortex.x, 2) + \
                                math.pow(closet_vortex.y - current_vortex.y, 2))
        
        if difference <= DISTANCE_THRESHOLD:
            return True
        return False
    def test_bounding_suface(current_vortex, closet_vortex):
        pass
    def tag_matches(current_step, next_step, overlap=True, position=True, surface_area=True):
        if overlap and position and surface_area:
                # tag, remove from list
                matched_curr_t.append(tuple([vortex, closet_vortex_key]))
                new_curr_dict = dict(current_step)
                new_next_dict = dict(next_step)
                del new_curr_dict[vortex]
                del new_next_dict[closet_vortex_key]
                current_step = new_curr_dict
                next_step = new_next_dict
        return current_step, next_step

    matched = []
    for iTimestep in range(0, len(features)-1):
        current_step = features[iTimestep]
        next_step = features[iTimestep+1]
        matched_curr_t = []

        for vortex in current_step:
            if len(next_step) == 0:
                break

            closet_vortex_key = find_match(vortex, next_step)
            closet_vortex = next_step[closet_vortex_key]
            current_vortex = current_step[vortex]
             
            # test Bounding surface
            position = test_position(current_vortex, closet_vortex)
            # overlap = test_overlap(current_vortex, closet_vortex)
            surface_a = test_surface_area(current_vortex, closet_vortex)

            current_step, next_step = tag_matches(current_step, next_step, position=position, surface_area=surface_a)
            

        matched.append(matched_curr_t)

    # From the remainaing, check for bifurcation and amalgamation

    return matched
        
def Reinder(all_frames):
    def start_paths(all_frames):
        def correspondence(prediction, second_candidate):
            def test_surface_area(prediction, closet_vortex):
                SURFACE_AREA_THRESHOLD = 1

                # difference = abs(prediction.surface_area - closet_vortex.surface_area)
                difference = abs(prediction.size - closet_vortex.size)

                # difference = difference / max(prediction.surface_area, prediction.surface_area)
                difference = difference / max(prediction.size, prediction.size)

                return 1 - difference / SURFACE_AREA_THRESHOLD
            def test_position(prediction, candidate):
                DISTANCE_THRESHOLD = 20 

                difference = math.sqrt(math.pow(prediction.x - candidate.x, 2) + \
                                        math.pow(prediction.y - candidate.y, 2))
                
                return 1 - (difference / DISTANCE_THRESHOLD)

            if not prediction.isValid():
                return -1

            POSITION_WIEGHT = 1
            SURFACE_AREA_WIEGHT = 1
            WEIGHTS = [POSITION_WIEGHT] #, SURFACE_AREA_WIEGHT]

            C_pos = test_position(prediction, second_candidate)
            C_sa = test_surface_area(prediction, second_candidate)
            Corr_factors = [C_pos] #, C_sa]

            return sum(np.multiply(Corr_factors, WEIGHTS)) / sum(WEIGHTS)
        def compare_path_conf(pathA, pathB, ):
            a_value = pathA.confidence
            b_value = pathB.confidence

            if a_value == b_value:
                return 0
            elif a_value > b_value:
                return 1 # cont with path A
            else:
                return 2 # stop with path B
        def continue_path(path, fnd_paths, all_frames, iframe):
            if len(all_frames) - 1 < iframe:
                return path

            try:
                frame = all_frames[iframe]
                for candidate in frame:
                    c = correspondence(prediction, frame[candidate])
                    if c >= 0:
                        if not frame[candidate].is_matched or (frame[candidate].is_matched and compare_path_conf(path, fnd_paths[frame[candidate].PathKey]) == 1):
                            all_frames[iframe][candidate].is_matched = True
                            all_frames[iframe][candidate].PathKey = path.Key
                            path.addFeature(frame[candidate], c)
                            path = continue_path(path, fnd_paths, all_frames, iframe+1)
                            return path
            except:
                return path
            return path
        def rm_path(paths, all_frames, path):
            iVortex = 0
            for vortex in path.vortices:
                all_frames[iVortex][tuple([vortex.x, vortex.y])].is_matched = False
                all_frames[iVortex][tuple([vortex.x, vortex.y])].PathKey = tuple([None, None, None])
                iVortex += 1
            del paths[path.Key]
            return all_frames
        def calc_confidence_lvls(og_path, fnd_paths, path_keys, all_frames):
            # compare path strength to path_keys elements
            keys = []
            confidence_levels = []
            for path_key in path_keys:
                try:
                    keys.append(fnd_paths[path_key])
                except:
                    keys.append(tuple([None, None, None]))
            for path in keys:
                try:
                    confidence_levels.append(path.confidence)
                except:
                    confidence_levels.append(float('-inf'))
            confidence_levels.append(og_path.confidence)
            most_confident = max(confidence_levels)
            idx = confidence_levels.index(most_confident)
            # remove paths that are not == idx
            for iPath in range(0, len(confidence_levels)-1):
                if not iPath == idx:
                    if fnd_paths.__contains__(path_keys[iPath]):
                        # remove lower conf paths that conflict
                        all_frames = rm_path(fnd_paths, all_frames, fnd_paths[path_keys[iPath]])
            return idx, confidence_levels
        def gen_path_keys(all_frames, iFrame, feature, next_candidate, second_candidate):
            path_keys = set([all_frames[iFrame][feature].PathKey, all_frames[iFrame+1][next_candidate].PathKey, all_frames[iFrame + 2][second_candidate].PathKey])
            try:
                path_keys.remove(tuple([None, None, None]))
            except:
                pass
            path_keys = list(path_keys)
            return path_keys

        fnd_paths = {}
        MinPathLength = 0
        iFrame = 0
        for frame in all_frames:
            if len(all_frames) > iFrame + 2:
                next_frame = all_frames[iFrame + 1]
                second_frame = all_frames[iFrame + 2]
                for feature in frame:
                    if not frame[feature].is_matched:
                        for next_candidate in next_frame:
                            # assume connection between feature i and candidate i+1
                            prediction = Prediction(frame[feature], next_frame[next_candidate])
                            for second_candidate in second_frame:
                                c = correspondence(prediction, second_frame[second_candidate])
                                if c >= 0: 
                                    # create new path
                                    init_features = [frame[feature], next_frame[next_candidate], second_frame[second_candidate]]
                                    path = Path(init_features, prediction, c, iFrame)

                                    path_keys = gen_path_keys(all_frames, iFrame, feature, next_candidate, second_candidate)
                                    idx, confidence_levels = calc_confidence_lvls(path, fnd_paths, path_keys, all_frames)

                                    if idx < len(confidence_levels)-1:
                                        # path already exists
                                        pass
                                    else:

                                        path = continue_path(path, fnd_paths, all_frames, iFrame+3)
                                        pathKey = path.Key

                                        if (len(path) > MinPathLength):
                                            # add path to graph
                                            path.end(iFrame+len(path))

                                            fnd_paths[pathKey] = path
                                            
                                            all_frames[iFrame][feature].is_matched = True
                                            all_frames[iFrame + 1][next_candidate].is_matched = True
                                            all_frames[iFrame + 2][second_candidate].is_matched = True

                                            all_frames[iFrame][feature].PathKey = path.Key
                                            all_frames[iFrame + 1][next_candidate].PathKey = path.Key
                                            all_frames[iFrame + 2][second_candidate].PathKey = path.Key


            iFrame += 1
        return fnd_paths
    
    paths = start_paths(all_frames)
    return paths


# For demo purposes only
data = loadData(parent='data', filename='all.features')
Reinder(data)
