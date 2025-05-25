import networkx as nx

class GraphNX:
    def __init__(self):
        self.graph = nx.Graph()

    def add_vertex(self, vertex):
        vertex = vertex.strip()
        self.graph.add_node(vertex)

    def add_edge(self, start, end, weight=1):
        start, end = start.strip(), end.strip()
        if start == end:
            return  # петли не допускаются
        self.graph.add_edge(start, end, weight=weight)

    def remove_vertex(self, vertex):
        self.graph.remove_node(vertex)

    def get_vertices(self):
        return list(self.graph.nodes)

    def get_edges(self):
        return [(u, v, d['weight']) for u, v, d in self.graph.edges(data=True)]

    def has_edge(self, start, end):
        for s, e, _ in self.get_edges():
            if (s == start and e == end) or (s == end and e == start):
                return True
        return False

    def is_planar(self):
        return nx.check_planarity(self.graph)[0]

    def is_connected(self):
        return nx.is_connected(self.graph)

    def is_biconnected(self):
        return nx.is_biconnected(self.graph)

    def has_bridges(self):
        return len(list(nx.bridges(self.graph))) > 0

    def has_separating_cycles(self):
        for node in self.graph.nodes:
            if self.graph.degree[node] == 2:
                neighbors = list(self.graph.neighbors(node))
                if not self.graph.has_edge(neighbors[0], neighbors[1]):
                    return True
        return False

    def greenberg_condition(self):
        if not self.is_planar():
            return 'nonplanar'  # возвращаем явно, что граф непланарный

        n = self.graph.number_of_nodes()
        if n < 3 or not self.is_connected():
            return True

        degrees = dict(self.graph.degree)
        if any(deg < 2 for deg in degrees.values()):
            return True

        if all(deg >= n / 2 for deg in degrees.values()):
            return False

        for u in self.graph.nodes:
            for v in self.graph.nodes:
                if u != v and not self.graph.has_edge(u, v):
                    if degrees[u] + degrees[v] >= n:
                        return False

        if not self.is_biconnected():
            return True
        if self.graph.number_of_edges() > 3 * n - 6:
            return True
        if self.has_bridges():
            return True
        if self.has_separating_cycles():
            return True

        return False

    def is_hamiltonian(self):
        res = self.greenberg_condition()
        if res == 'nonplanar':
            return None
        return not res

    def layout_planar_or_default(self):
        """Возвращает словарь позиций вершин.
        Если граф планарный, то использует планарный embedding.
        Иначе — spring layout (force-directed)."""
        is_planar, embedding = nx.check_planarity(self.graph)
        if is_planar:
            # планарное расположение из embedding
            pos = nx.combinatorial_embedding_to_pos(embedding)
            return pos, True
        else:
            pos = nx.spring_layout(self.graph)
            return pos, False
        
    def print_graph_state(self):
        print("\nТекущие вершины графа:")
        for node in self.graph.nodes:
            print(f"{node}: {list(self.graph[node].items())}")
