import numpy as np

def get_coors_at(dd_list, idx):
    return [dd_list[0][idx], dd_list[1][idx]]

# 2D cross product, pq and pr vectors
def orientation(p, q, r): 
        # val = (q[1] - p[1]) * (r[0] - q[0]) - (q[0] - p[0]) * (r[1]  - q[1]) 
        val = (q[0] - p[0]) * (r[1] - p[1]) - (q[1] - p[1]) * (r[0] - p[0])
        if val == 0:
            # Colinear
            return 0
        elif val > 0: 
            # Clockwise 
            return 1
        else: 
            # Anti-clockwise
            return 2

# Algorithm taken and adapted from:
# https://en.wikipedia.org/wiki/Gift_wrapping_algorithm
# https://www.geeksforgeeks.org/convex-hull-set-1-jarviss-algorithm-or-wrapping/
def gift_wrapping(set_of_nodes):
    def get_left_node(set_of_nodes):
        # If points are colinear, pick the first point
        min_value = sorted(set_of_nodes)[0]
        left_node_x_idx = np.where([x == min_value[0] and y == min_value[1] for x, y in set_of_nodes])[0][0]
        return left_node_x_idx
    
    if len(set_of_nodes[0]) < 3:
        return set_of_nodes
        
    node_on_hull = get_left_node(set_of_nodes)
    nodes_on_convex_hull = []
    endpoint = node_on_hull 
    q = 0
    while True:
        nodes_on_convex_hull.append(get_coors_at(set_of_nodes, endpoint))

        q = (endpoint+1) % len(set_of_nodes[0])
        for i in range(0, len(set_of_nodes[0])):
            if orientation(get_coors_at(set_of_nodes, endpoint), get_coors_at(set_of_nodes, i), get_coors_at(set_of_nodes, q)) == 2:
                q = i
        endpoint = q
        if get_coors_at(set_of_nodes, endpoint) == nodes_on_convex_hull[0]:
            break
    return nodes_on_convex_hull

# Algorithm taken and adapted from:
# https://en.wikipedia.org/wiki/Graham_scan
#
# Basic idea when sorted on x-coordinate instead of angle and computed
# in two steps is known as Andrew's monotone chain algo.
def graham_scan(set_of_nodes):
    def get_left_node(set_of_nodes):
        min_value = sorted(set_of_nodes)[0]
        left_node_xy_idx = np.where([x == min_value[0] and y == min_value[1] for x, y in set_of_nodes])[0][0] # take the first
        return left_node_xy_idx
    
    # Function for returning the item one entry below the top of stack,
    # without changing it
    def next_to_top(stack):
        p = stack.top()
        stack.pop()
        res = stack.top()
        stack.push(p)
        return res

    # sort points by polar angle with P0, if several points have the same polar angle then only keep the farthest
    
    # for point in points:
    #     # pop the last point from the stack if we turn clockwise to reach this point
    #     while count stack > 1 and ccw(next_to_top(stack), top(stack), point) < 0:
    #         pop stack
    #     push point to stack
    # end

    set_of_nodes.sort()

    if len(set_of_nodes) < 3:
        return set_of_nodes

    stack = []
    left_idx = get_left_node(set_of_nodes)
    # sort points by polar angle with P0, if several points have the same polar angle then only keep the farthest

    # for node in set_of_nodes:
    #     stack.pop()
    #     while stack.count > 1 and ccw(next_to_top(stack), stack.top(), node) < 0:
    #         stack.pop()
    #     stack.append(node)
    # return stack

# Algorithm taken and adapted from:
# https://en.wikibooks.org/wiki/Algorithm_Implementation/Geometry/Convex_hull/Monotone_chain#Python
def monotone_chain(set_of_nodes):
    # sort by x then by y

    # Input: a list P of points in the plane.

    # Precondition: There must be at least 3 points.

    # Sort the points of P by x-coordinate (in case of a tie, sort by y-coordinate).

    # Initialize U and L as empty lists.
    # The lists will hold the vertices of upper and lower hulls respectively.

    # for i = 1, 2, ..., n:
    #     while L contains at least two points and the sequence of last two points
    #             of L and the point P[i] does not make a counter-clockwise turn:
    #         remove the last point from L
    #     append P[i] to L

    # for i = n, n-1, ..., 1:
    #     while U contains at least two points and the sequence of last two points
    #             of U and the point P[i] does not make a counter-clockwise turn:
    #         remove the last point from U
    #     append P[i] to U

    # Remove the last point of each list (it's the same as the first point of the other list).
    # Concatenate L and U to obtain the convex hull of P.
    # Points in the result will be listed in counter-clockwise order.
    
    set_of_nodes.sort()

    if len(set_of_nodes) <= 1:
        return set_of_nodes

    # Upper
    upper = []
    for node in reversed(set_of_nodes):
        while len(upper) >= 2 and orientation(upper[-2], upper[-1], node) == (2 or 0):
            upper.pop()
        upper.append(node)

    # Lower
    lower = []
    for node in set_of_nodes:
        while len(lower) >= 2 and orientation(lower[-2], lower[-1], node) == (2 or 0):
            lower.pop()
        lower.append(node)

    return lower[:-1] + upper[:-1]