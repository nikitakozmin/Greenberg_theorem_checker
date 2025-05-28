import networkx as nx
from itertools import combinations

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
    
    def remove_edge(self, start, end):
        start, end = start.strip(), end.strip()
        if self.graph.has_edge(start, end):
            self.graph.remove_edge(start, end)
            
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

    def is_biconnected(self):
        return nx.is_biconnected(self.graph)

    def has_separating_cycles(self):
        for node in self.graph.nodes:
            if self.graph.degree[node] == 2:
                neighbors = list(self.graph.neighbors(node))
                if not self.graph.has_edge(neighbors[0], neighbors[1]):
                    return True
        return False

    def get_faces(self):
        _, embedding = nx.check_planarity(self.graph)

        # получаем координаты вершин 
        pos = nx.planar_layout(self.graph)
        import math
        neighbor_order = {}
        for u in embedding:
            # сортируем соседей по углу относительно вершины u
            neighbors = sorted(
                embedding[u],
                key=lambda v: math.atan2(pos[v][1] - pos[u][1], pos[v][0] - pos[u][0])
            )
            neighbor_order[u] = {
                v: neighbors[(i + 1) % len(neighbors)]
                for i, v in enumerate(neighbors)
            }

        # обход граней
        faces = []
        visited_edges = set()

        for u in neighbor_order:
            for v in neighbor_order[u]:
                if (u, v) not in visited_edges:
                    face = []
                    current_u, current_v = u, v
                    while True:
                        face.append(current_u)
                        visited_edges.add((current_u, current_v))
                        next_v = neighbor_order[current_v][current_u]
                        current_u, current_v = current_v, next_v
                        if (current_u, current_v) == (u, v):
                            break
                    faces.append(face)

        return faces

    def greenberg_condition(self, mutable_params):
        # проверка на планарность
        if not self.is_planar():
            return 'nonplanar'
        
        # проверка на двусвязность
        if self.graph.number_of_nodes() < 3 or not self.is_biconnected():
            return 'nonbiconnected'
        
        # находим все грани
        faces = self.get_faces()
        if not faces:
            return False
       
        # считаем f_k (количество граней порядка k)
        f_k = {}
        for face in faces:
            k = len(face)
            if k >= 3:  # учитываем только грани с k >= 3
                f_k[k] = f_k.get(k, 0) + 1

        # вычисляем общую сумму S = sum f_k * (k - 2)
        total_sum = sum(f_k.get(k, 0) * (k - 2) for k in f_k)
        if total_sum == 0 or total_sum % 2 != 0:
            print(total_sum)
            return False

        target = total_sum // 2

        # преобразуем f_k в список пар (k, count) для удобства перебора

        n = len(faces)
        found = False

        # перебираем все возможные размеры подмножеств (от 1 до n-1)
        for r in range(1, n):
            # перебираем все комбинации из r граней
            for subset_indices in combinations(range(n), r):
                # вычисляем сумму (k-2) для выбранных граней
                current_sum = sum(len(faces[i]) - 2 for i in subset_indices)
                
                # если сумма совпала с целевой — проверяем условие
                if current_sum == target:
                    # получаем f'_k и f''_k
                    f_prime = [faces[i] for i in subset_indices]
                    f_double_prime = [faces[i] for i in range(n) if i not in subset_indices]

                    # проверяем, что в обоих группах есть хотя бы одна грань каждого порядка
                    # (если в исходном графе были грани порядка k, они должны быть в f'_k или f''_k)
                    orders_in_f_prime = {len(face) for face in f_prime}
                    orders_in_f_double_prime = {len(face) for face in f_double_prime}
                    all_orders = {len(face) for face in faces}

                    # если все orders покрыты хотя бы в одном из множеств — условие выполнено
                    if all_orders.issubset(orders_in_f_prime.union(orders_in_f_double_prime)):
                        found = True
        if found:
            mutable_params.append(f_prime)
            mutable_params.append(f_double_prime)

        return found

    def layout_planar_or_default(self):
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
