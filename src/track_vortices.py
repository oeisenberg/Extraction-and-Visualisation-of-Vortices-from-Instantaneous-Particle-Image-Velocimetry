from DataType import *
from copy import deepcopy
import math
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.tri as mtri
from skimage import measure
from skimage.draw import *

class tracker():
    def __init__(self, all_frames, min_path_len = 3, thresholds = [10, 2, 2, 5], weights = [1, 1, 0.7, 0.3]):
        self.all_frames = { i : all_frames[i] for i in range(0, len(all_frames) ) } 
        self.found_paths = {}
        self.found_paths_dbg = []
        self.minimum_path_length = min_path_len
        self.thresholds = thresholds
        self.weights = weights
        self.init_paths()
        self.paths_by_frame = {path[2]:path for path in self.found_paths}
        # self.make_pass(type='forward')
        # self.make_pass(type='backward')

    # First pass over the data set and frames
    def init_paths(self):
        # No longer automatically assumes a connection between feature i and canditate i+1
        # narrows inital pool to only in the direction the feature was moving in step i
        def get_possible_candidates(og_feature, frame):
            # if og_feature.u_signed < 0:
            #     u = {feature for feature in frame if frame[feature].x < og_feature.x}
            # elif og_feature.u_signed > 0:
            #     u = {feature for feature in frame if frame[feature].x > og_feature.x}
            # else:
            #     u = set(frame.keys())

            # if og_feature.v_signed < 0:
            #     v = {feature for feature in frame if frame[feature].y < og_feature.y}
            # elif og_feature.v_signed > 0:
            #     v = {feature for feature in frame if frame[feature].y > og_feature.y}
            # else:
            #     v = set(frame.keys())

            # candidate_keys = u.union(v)
            # return {key:frame[key] for key in candidate_keys}
            return frame

        # Calculates the correspondence value
        def correspondence(prediction, second_candidate):
            def test_distance(prediction, candidate, threshold):
                difference = math.sqrt(math.pow(prediction.x - candidate.x, 2) + \
                                        math.pow(prediction.y - candidate.y, 2))
                
                return 1 - (difference / threshold)
            def test_surface_area(prediction, candidate, threshold):
                difference = abs(prediction.size - candidate.size)

                difference = difference / max(prediction.size, candidate.size)

                return 1 - difference / threshold
            def test_position(prediction, candidate, threshold):
                difference_counter = 0

                if prediction.u_signed < 0:
                    if candidate.x < prediction.x:
                        difference_counter += 1
                elif prediction.u_signed > 0:
                    if candidate.x > prediction.x:
                        difference_counter += 1
                else:
                    if candidate.x == prediction.x:
                        difference_counter += 1

                if prediction.v_signed < 0:
                    if candidate.y < prediction.y:
                        difference_counter += 1
                elif prediction.v_signed > 0:
                    if candidate.y > prediction.y:
                        difference_counter += 1
                else:
                    if candidate.y == prediction.y:
                        difference_counter += 1

                if difference_counter == threshold:
                    return 1
                elif difference_counter == threshold-1:
                    return -1
                else:
                    return -1
            def test_velmag(prediction, candidate, threshold):
                difference = abs(prediction.vel_mag - candidate.vel_mag)

                difference = difference / max(prediction.vel_mag, candidate.vel_mag)

                return 1 - difference / threshold

            c_d = test_distance(prediction, second_candidate, self.thresholds[0])
            c_sa = test_surface_area(prediction, second_candidate, self.thresholds[1])
            c_p = test_position(prediction, second_candidate, self.thresholds[2])
            c_vm = test_velmag(prediction, second_candidate, self.thresholds[3])
            
            return sum(np.multiply([c_d, c_sa, c_p, c_vm], self.weights)) / sum(self.weights)

        # Continues searching for paths using DFS
        def continue_path(path, iFrame):
            if iFrame >= len(self.all_frames) or len(path) > len(self.all_frames):
                # no more frames
                return path

            frame = self.all_frames[iFrame]
            correspondences = [[candidate, correspondence(path.predictor, frame[candidate])] for candidate in frame if not frame[candidate].is_matched]
            potential_paths = [[correspondence[0], correspondence[1]] for correspondence in correspondences if correspondence[1] >= 0]

            if len(potential_paths) == 0:
                # end of path reached
                return path

            possible_branches = []
            for potential_candidate in potential_paths:
                new_path = deepcopy(path)
                new_path.addFeature(frame[potential_candidate[0]], potential_candidate[1])
                possible_branches.append(continue_path(new_path, iFrame+1))
            
            # choose best path to return 
            confidence_lvls = [path.confidence for path in possible_branches]
            maximum_c = max(confidence_lvls)
            max_idx = confidence_lvls.index(maximum_c)

            return possible_branches[max_idx]

        for iFrame in range(0, len(self.all_frames)-2):
            for feature in self.all_frames[iFrame]:
                if not self.all_frames[iFrame][feature].is_matched:
                    candidates = get_possible_candidates(self.all_frames[iFrame][feature], self.all_frames[iFrame+1])

                    for next_candidate in candidates:
                        prediction = Prediction(self.all_frames[iFrame][feature], self.all_frames[iFrame+1][next_candidate])

                        for second_candidate in self.all_frames[iFrame+2]:
                            c = correspondence(prediction, self.all_frames[iFrame+2][second_candidate])
                            
                            if c >= 0 and not self.all_frames[iFrame+1][next_candidate].is_matched and not self.all_frames[iFrame+2][second_candidate].is_matched:
                                # create a new path
                                init_features = [self.all_frames[iFrame][feature], self.all_frames[iFrame+1][next_candidate], self.all_frames[iFrame+2][second_candidate]]
                                path = Path(init_features, prediction, c, iFrame)
                                path = continue_path(path, iFrame+3)

                                if (len(path) > self.minimum_path_length):
                                    path.end(iFrame+len(path))

                                    self.found_paths_dbg.append(path)
                                    if self.found_paths.__contains__(path.Key):
                                        # only replace if higher confidence exists in the new path
                                        if self.found_paths[path.Key].confidence < path.confidence:
                                               self.found_paths[path.Key] = path
                                    else:
                                        self.found_paths[path.Key] = path

                                    for iframe in range(0, len(path)):
                                        self.all_frames[path.start+iframe][path.vortices[iframe].key].is_matched = True

    def make_pass(self, type='forward'):
        def _forward_pass():
            check_for_extensions()
            check_for_events()

        def _backward_pass():
            check_for_extensions(-1)
            check_for_events(-1)
            
        def check_for_extensions(step=1):
            for frame in self.paths_by_frame:
                if self.paths_by_frame.__contains__(frame + step):
                    # look to connect any paths
                    pass
                for path in self.paths_by_frame[frame]:
                    if frame == 0:
                        continue
                    for nodeKey in self.all_frames[frame + step]:
                        node = self.all_frames[frame + step][nodeKey]
                        # look to connect to unmatched nodes
                        if not node.is_matched:
                            pass

        def check_for_events(step=1):
            def add_event(type):
                pass
            
            def check_birthdeath(step):
                # if step equals 1, death
                for path in self.found_paths:
                    if self.found_paths[path].predictor.size <= 0:
                        if step == 1:
                            add_event('death')
                        else:
                            add_event('birth')

            def check_split_merge(step):
                # if step equals 1, split
                pass
            
            check_birthdeath(step)
            check_split_merge(step)

        if type == 'forward':
            _forward_pass()
        else:
            _backward_pass()
