###########################
#   Transport Optimizer   #
###########################

import heapq

class Edge:
    def __init__(self, to, capacity, rev_index, owner_id=-1, lower=0):
        """
        Function Description:
            Initializes a single edge in a residual graph used in network flow algorithms.
            Each edge stores the endpoint, capacity, index of its reverse edge, ownership information,
            and any lower bound constraint.

        Attributes:
            - to: Destination node
            - capacity: Remaining capacity of the edge
            - rev_index: Index of the reverse edge in the adjacency list of the 'to' node
            - owner_id: Identifier for mapping this edge to a specific student-pickup connection
            - lower: Lower bound capacity for lower-bound flow problems

        Time Complexity:
            O(1)
            
        Aux Space Complexity:
            O(1)
        """
        self.to = to
        self.cap = capacity
        self.rev = rev_index
        self.owner = owner_id
        self.lower = lower


def add_edge(graph, from_node, to_node, capacity, owner_id=-1, lower=0):
    """
    Function Description:
        Adds a forward and backward (reverse) edge between two nodes in a residual graph.
        The reverse edge starts with capacity 0 and is used for backflow during augmentations.
        The function also supports lower-bound constraints by tracking the required minimum flow
        on each edge.

    Input:
        - graph: Adjacency list representation of the residual graph
        - from_node: Starting node of the edge
        - to_node: Destination node of the edge
        - capacity: Maximum flow allowed on this edge
        - owner_id: Identifier to trace this edge back to a student-pickup relation
        - lower: Lower bound on flow capacity for this edge

    Output:
        - None (modifies the graph in-place by appending edges)   

    Time Complexity:
        O(1)
        
    Aux Space Complexity:
        O(1)
    """
    graph[from_node].append(Edge(to_node, capacity, len(graph[to_node]), owner_id, lower))
    graph[to_node].append(Edge(from_node, 0, len(graph[from_node]) - 1, -1, 0))


def dijkstra(L, adjacency_list, source):
    """
    Function Description:
        Computes the shortest path distances from a single source node to all other nodes in a weighted graph
        using Dijkstra's algorithm with a binary heap (priority queue). It is used to determine which students
        can reach which pickup locations within the allowed maximum travel distance D.

    Input:
        - L: Number of locations in the city
        - adjacency_list: Graph as adjacency list with weight
        - source: Source node index

    Output:
        - distance: List of shortest distances from source to all nodes

    Time Complexity:
        O(R*log L), where R is the number of roads (edges) and L is the number of locations (nodes).

    Time Complexity Analysis:
        Initializing the distance array takes O(L) time. Each of the L nodes is inserted into and extracted
        from the priority queue at most once, and each operation takes O(log L) time. 
        For every extracted node, all of its outgoing edges (at most R total) are relaxed, resulting in
        O(R*log L) overall. The O(L) initialization term is dominated by O(R * log L), so the total time
        complexity is expressed as O(R * log L).

    Aux Space Complexity:
        O(L), where L is the number of locations (nodes)
    """
    distance = [10**30] * L
    distance[source] = 0
    priority_queue = [(0, source)]
    while priority_queue:
        current_distance, current_node = heapq.heappop(priority_queue)
        if current_distance != distance[current_node]:
            continue
        for neighbor, weight in adjacency_list[current_node]:
            new_distance = current_distance + weight
            if new_distance < distance[neighbor]:
                distance[neighbor] = new_distance
                heapq.heappush(priority_queue, (new_distance, neighbor))
    return distance


def dfs_augment(graph, current, sink, flow, visited):
    """
    Function Description:
        Depth-first search is used to find augmenting paths in the Ford-Fulkerson algorithm.
        It recursively attempts to push available flow until it reaches the sink or no path exists.

    Input:
        - graph: Residual graph
        - current: Current node
        - sink: Sink node
        - flow: Available flow amount to push
        - visited: Visitation state of each node

    Output:
        - Amount of flow successfully pushed through this path

    Time Complexity:
        O(V + E) in the worst case per DFS search, where V is the node and E is the edges

    Aux Space Complexity:
        O(V) for recursion stack and visited array, where V is the number of nodes in the graph
    """
    if current == sink:
        return flow
    visited[current] = True
    for edge in graph[current]:
        if edge.cap > 0 and not visited[edge.to]:
            pushed = dfs_augment(graph, edge.to, sink, min(flow, edge.cap), visited)
            if pushed > 0:
                edge.cap -= pushed
                graph[edge.to][edge.rev].cap += pushed
                return pushed
    return 0


def maxflow(graph, source, sink):
    """
    Function Description:
        It implements the Ford-Fulkerson maximum flow algorithm using repeated DFS augmentations.
        The algorithm repeatedly searches for augmenting paths from the source to the sink in the
        residual graph and pushes as much flow as possible along these paths until no more 
        augmenting paths exist. This function is used to compute the feasible circulation in the
        lower-bound flow network.

    Input:
        - graph: Residual graph
        - source: Source node
        - sink: Sink node

    Output:
        - Total maximum flow achieved from source to sink

    Time Complexity:
        O(E * f_max), where E is the number of edges in the residual graph and f_max is the toal
        maximum flow value pushed.

    Time Complexity Analysis:
        Each DFS-based augmentation explores at most all edges in the residual graph, taking O(E)
        time. Since each augmentation increases the total flow by at least one unit (assuming
        integer capacities), there can be at most f_max augmentations before reaching the
        maximum flow. Therefore, the total time complexity is O(E * f_max).
        
    Aux Space Complexity:
        O(V) for visited array per augmentation, where V is the number of nodes in the graph
    """
    total_flow = 0
    while True:
        visited = [False] * len(graph)
        pushed = dfs_augment(graph, source, sink, 10**18, visited)
        if pushed == 0:
            break
        total_flow += pushed
    return total_flow


def assign(L, roads, students, buses, D, T):
    """
    Function Description:
        Determines a feasible assignment of students to buses given the city's road network, pickup
        locations, minimum and maximum bus capacities, and an exact total number of students T to
        be transported. With each student only willing to travel up to a maximum distance D to reach 
        a pickup location.
        The function uses a max-flow algorithm with lower-bound flow constraints to enforce capacity
        and distance limits. It outputs a list indicating each student's assigned bus index, or None
        if no feasible assignment exists.

    Approach Description:
        1. I construct a city graph from the given road list and group all buses by their pickup 
           locations. Then, I compute the total mininmum and maximum bus capacities for each pickup
           location. For each pickup loation, i use Dijkstra's algorithm to determine which students
           can reach it within distance D. This constructs a biparte graph between students and 
           reachable pickup points.

        2. I build a flow network where:
            - Source -> each student (capacity 1 = per student)
            - Student -> reachable pickups (capacity = 1 for reachable pairs)
            - Pickup -> sink (capacity range [min, max] per location)
            - Sink -> source (enforces exactly T total students)

        3. I add a super-source and super-sink to check the flow feasibility under the lower bounds
           capacity constraints.

        4. I run Ford-Fulkerson DFS-based augmentations to check if the maximum feasible flow
           equals the total required demand.

        5. If the flow is feasible, I extract the student -> pickup assignments and then allocates 
           students to buses at each pickup while respecting the bus mininimum and maximum constraints.

    Input:
        - L : positive integer representing the number of locations in the city.
        - roads : list of tuples (u, v, w) representing bidirectional roads, where u is the starting
                  location, v is the ending location, and w is the length of the road.
        - students : list of integers where each element represent the student's home locations.
        - buses : list of tuples (e, f, g) where e is the pickup location of the bus, f is its minimum
                  capacity, and g is its maximum capacity.
        - D : positive integer representing the maximum distance a students is willing to travel to a 
              pickup points.
        - T : positive integer representung the exact number of students that must be transported.

    Output:
        - List of length that is equal to the number of students, where the i-th element indicates the
          bus index that student i is assigned to, or -1 if the student does not travel.
        - Returns None if no feasible assignment exists.

    Time Complexity:
        O(S*T + L + R*log(L)) worst case time complexity, where:
            S = number of students
            T = exact number of students required to be transported
            L = number of city locations
            R = number of roads
            P = number of pickup locations (bounded by a small constant <= 18)
            B = number of buses (bounded by a small constant multiple of S)

    Time Complexity Analysis:
        - Graph construction: 
            Building the city adjacency lise from the list of R roads takes O(L + R) time.
        
        - Reachability Analysis:
            For each pickup location, Dijkstra's algorithm is executed once to find students within
            distance D. Each Dijkstra run takes O(R*log(L) + L).
            Since the number of pickup locations P <= 18 (a fixed small constant), this step 
            contributes O(P*(R*log(L) + L)) = O(1*(R*log(L) + L)) = O(R*log(L) + L).

        - Flow Network:
            The flow network consists of O(S + P + 2) nodes and O(S*P) edges (each student connects
            To reachable pickups). As P is a constant, this reduces to O(S) nodes and O(S) edges,
            hence construction takes O(S) time.

        - Max Flow Computation:
            The Ford-Fulkerson method using DFS augmentations runs in O(E*f_max), where E = O(S)
            and f_max = O(T). Therefore, this contributes O(S*T) time.
        
        - Bus Distribution:
            Each student is assigned to a bus once, and each bus is processed once. This takes 
            O(S + B) = O(S), since B <= 18*S in the worst case but is practically bounded.        

        - Combining all these components yields a total worst case time complexity of
          O(L + R) + O(R*log(L) + L) + O(S) + O(S*T) + O(S) = O(S*T + L + R*log(L))

    Aux Space Complexity:
        O(S + L + R) worst case auxiliary space complexity, where
            S = number of students
            L = number of city locations
            R = number of roads
            P = number of pickup locations (bounded by a small constant <= 18)
            B = number of buses (bounded by a small constant multiple of S)

    Aux Space Complexity Analysis:
        - City graph:
            The adjacency list representation of the city graph requires O(L) for the list of
            locations and O(R) for storing all road connections, giving O(L + R) total.

        - Reachability matrix:
            The student-pickup reachability matrix has dimensions S*P, where P <= 18 is a 
            constant upper bound. Hence, this contributes O(S*P) = O(S*1) = O(S) space.

        - Flow network:
            The residual graph for the max-flow computation includes O(S) nodes (since P is constant) 
            and O(S) edges representing student-pickup and pickup-sink connections.
            This contributes to O(S) space overall.

        - Various arrays:
            The supporting arrays include:
                - Dijkstra's distance and priority queue arrays: O(L)
                - Flow circulation arrays: O(S)
                - Allocation and visited arrays: O(S)
                - Bus distribution arrays (min/max capacities): O(S)
                  The bus distribution arrays use O(B + S) space, but since B is bounded by the input
                  size and independent of S and L, this simplifies to O(1 + S) = O(S).
            This contributes to O(L + S) space overall.

        - Combining all these components gives a total auziliary space complexity of
          O(L + R) + O(S) + O(S) + O(L + S) = O(S + L + R)
    """

    # Build city graph from roads
    city_graph = [[] for _ in range(L)]
    for (u, v, w) in roads:
        city_graph[u].append((v, w))
        city_graph[v].append((u, w))

    num_students = len(students)
    num_buses = len(buses)

    # Group buses by their pickup locations
    buses_at_location = [[] for _ in range(L)]
    for bus_index in range(num_buses):
        pickup_point, min_capacity, max_capacity = buses[bus_index]
        buses_at_location[pickup_point].append(bus_index)

    # Compute total min/max capacity per pickup location
    min_capacity_sum = [0] * L
    max_capacity_sum = [0] * L
    for location in range(L):
        for bus_index in buses_at_location[location]:
            _, min_cap, max_cap = buses[bus_index]
            min_capacity_sum[location] += min_cap
            max_capacity_sum[location] += max_cap

    # Check if target T is less than total minimum capacity, if it is less return none as it is not valid
    total_min_all = sum(min_capacity_sum)
    if T < total_min_all:
        return None

    # Identify valid pickup locations
    pickup_locations = []
    pickup_index_of_location = [-1] * L
    for location in range(L):
        if len(buses_at_location[location]) > 0:
            pickup_index_of_location[location] = len(pickup_locations)
            pickup_locations.append(location)
    num_pickups = len(pickup_locations)
    if num_pickups == 0:
        return None

    # Determine which students can reach which pickup within distance D
    reachable = [[False] * num_pickups for _ in range(num_students)]
    for pickup_index, location in enumerate(pickup_locations):
        distance = dijkstra(L, city_graph, location)
        for student_index in range(num_students):
            if distance[students[student_index]] <= D:
                reachable[student_index][pickup_index] = True

    # Build the flow network
    node_students_start = 0
    node_pickups_start = num_students
    node_source = num_students + num_pickups
    node_sink = num_students + num_pickups + 1
    base_nodes = num_students + num_pickups + 2

    # Initialize lower-bound demands and residual graph
    demands = [0] * base_nodes
    residual_graph = [[] for _ in range(base_nodes + 10)]

    # Source -> students (each student can bea assigned at most once)
    for student_index in range(num_students):
        add_edge(residual_graph, node_source, node_students_start + student_index, 1)

    # Students -> reachable pickups edges, connect each student to all pickup points they can reach within D
    for student_index in range(num_students):
        for pickup_index in range(num_pickups):
            if reachable[student_index][pickup_index]:
                add_edge(
                    residual_graph,
                    node_students_start + student_index,
                    node_pickups_start + pickup_index,
                    1,
                    owner_id=student_index * num_pickups + pickup_index
                )

    # Pickup -> sink edges with lower/upper capacity bounds, 
    # each pickup must serve at least its total min capacity and cannot exceed its max capacity
    for pickup_index, location in enumerate(pickup_locations):
        from_node = node_pickups_start + pickup_index
        to_node = node_sink
        lower_bound = min_capacity_sum[location]
        upper_bound = max_capacity_sum[location]
        if upper_bound < lower_bound:
            return None
        add_edge(residual_graph, from_node, to_node, upper_bound - lower_bound, lower=lower_bound)
        demands[from_node] -= lower_bound
        demands[to_node] += lower_bound

    # Add edge sink -> sourc, enforcing exactly T students
    # This ensures total flow equals required total students transported.
    INF = 10**12
    lower_bound = T
    upper_bound = INF
    add_edge(residual_graph, node_sink, node_source, upper_bound - lower_bound, lower=lower_bound)
    demands[node_sink] -= lower_bound
    demands[node_source] += lower_bound

    # Add super-source and super-sink, 
    # it is used to check flow feasibility under lower bound circualtion constraints
    super_source = len(residual_graph) - 2
    super_sink = len(residual_graph) - 1
    total_positive_demand = 0
    for node in range(base_nodes):
        if demands[node] > 0:
            add_edge(residual_graph, super_source, node, demands[node])
            total_positive_demand += demands[node]
        elif demands[node] < 0:
            add_edge(residual_graph, node, super_sink, -demands[node])

    # Check feasibility with maxflow, run Ford-Fulkerson to verify if all demands can be satisfied
    flow = maxflow(residual_graph, super_source, super_sink)
    if flow != total_positive_demand:
        return None

    # Extract student -> pickup allocation
    # If edge has owner_id and zero remaining capacity, that student was matched to that pickup
    allocation = [-1] * num_students
    assigned_count_per_pickup = [0] * num_pickups
    for student_index in range(num_students):
        u = node_students_start + student_index
        for edge in residual_graph[u]:
            if edge.owner >= 0:
                pickup_index = edge.owner % num_pickups
                if edge.cap == 0:
                    allocation[student_index] = pickup_index
                    assigned_count_per_pickup[pickup_index] += 1
                    break

    # Validate that total assigned students == required total T
    if sum(assigned_count_per_pickup) != T:
        return None

    # Assign students at each pickup to specific buses while satisfying min/max capacities
    bus_loads = [0] * num_buses
    students_per_pickup = [[] for _ in range(num_pickups)]
    for student_index in range(num_students):
        pickup_index = allocation[student_index]
        if pickup_index >= 0:
            students_per_pickup[pickup_index].append(student_index)

    # Allocate students to buses at each pickup
    for pickup_index, location in enumerate(pickup_locations):
        bus_list = buses_at_location[location]
        num_buses_here = len(bus_list)

        # Case: No buses at this pickup
        if num_buses_here == 0:
            if assigned_count_per_pickup[pickup_index] != 0:
                return None
            else:
                continue

        # Record bus capacity ranges
        min_caps = [0] * num_buses_here
        max_caps = [0] * num_buses_here
        for idx in range(num_buses_here):
            bus_index = bus_list[idx]
            _, min_cap, max_cap = buses[bus_index]
            min_caps[idx] = min_cap
            max_caps[idx] = max_cap
            bus_loads[bus_index] = min_cap

        # Compute remaining capacity to fill after meeting minimums
        allocated = sum(min_caps)
        remaining = assigned_count_per_pickup[pickup_index] - allocated
        if remaining < 0:
            return None

        # Distribute remaining students greedily until capacities filled
        for idx in range(num_buses_here):
            if remaining <= 0:
                break
            bus_index = bus_list[idx]
            extra_capacity = max_caps[idx] - min_caps[idx]
            assign_now = min(remaining, extra_capacity)
            bus_loads[bus_index] += assign_now
            remaining -= assign_now
        if remaining != 0:
            return None

        # Assign students in order to their buses
        student_list = students_per_pickup[pickup_index]
        if len(student_list) != assigned_count_per_pickup[pickup_index]:
            return None

        ptr = 0
        for idx in range(num_buses_here):
            bus_index = bus_list[idx]
            total_for_bus = bus_loads[bus_index]
            for _ in range(total_for_bus):
                student_index = student_list[ptr]
                allocation[student_index] = bus_index
                ptr += 1

    # Ensure exactly T students are assigned to buses
    chosen_count = sum(1 for student_index in range(num_students) if allocation[student_index] != -1)
    if chosen_count != T:
        return None

    return allocation