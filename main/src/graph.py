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

    def is_connected(self):
        if len(self.graph) == 0:
            return False  
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
    
    # def get_faces(self):
    #     # находим базис циклов
    #     cycles = nx.cycle_basis(self.graph)

    #     def remove_composite_cycles(cycles):
    #         filtered = []
    #         for c in cycles:
    #             c_set = set(c)
    #             is_composite = False
    #             for other in cycles:
    #                 if c == other:
    #                     continue
    #                 if set(other).issubset(c_set) and len(other) < len(c):
    #                     is_composite = True
    #                     break
    #             if not is_composite:
    #                 filtered.append(c)
    #         return filtered 
        
    #     minimal_cycles = remove_composite_cycles(cycles)
        
    #     all_cycles = list(nx.simple_cycles(self.graph.to_directed())) 
    #     outer_face = max(all_cycles, key=len, default=[]) if all_cycles else []

    #     return minimal_cycles + [outer_face]


    def get_faces(self):
        """Возвращает список граней планарного графа."""
        if not self.is_planar():
            return []

        is_planar, embedding = nx.check_planarity(self.graph)
        if not is_planar:
            return []

        # Получаем координаты вершин 
        pos = nx.planar_layout(self.graph)
        import math
        neighbor_order = {}
        for u in embedding:
            # Сортируем соседей по углу относительно вершины u
            neighbors = sorted(
                embedding[u],
                key=lambda v: math.atan2(pos[v][1] - pos[u][1], pos[v][0] - pos[u][0])
            )
            neighbor_order[u] = {
                v: neighbors[(i + 1) % len(neighbors)]
                for i, v in enumerate(neighbors)
            }

        # Дальше обход граней
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

    def greenberg_condition(self):
        # проверка на планарность
        if not self.is_planar():
            return 'nonplanar'
        
        # проверка на связность
        if self.graph.number_of_nodes() < 3 or not self.is_connected():
            return False
        
        # проверка на наличие мостов
        if self.has_bridges():
            return False
        
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
        if total_sum == 0:
            return False

        target = total_sum // 2

        # преобразуем f_k в список пар (k, count) для удобства перебора
        items = list(f_k.items())
        n = len(items)

        # рекурсивная функция для перебора возможных f_k'
        def backtrack(pos, current_sum, selected):
            if current_sum == target:
                # проверяем, что для каждого k хотя бы одно из f_k' или f_k'' не ноль
                valid = all(selected.get(k, 0) > 0 or (f_k[k] - selected.get(k, 0)) > 0 for k in f_k)
                if valid:
                    return selected
                return None
            if pos >= n or current_sum > target:
                return None
            
            k, count = items[pos]
            max_take = min(count, (target - current_sum) // (k - 2)) if (k - 2) != 0 else 0

            # пробуем взять от 0 до max_take граней порядка k
            for take in range(max_take, -1, -1):
                if take == 0:
                    result = backtrack(pos + 1, current_sum, selected)
                else:
                    new_selected = selected.copy()
                    new_selected[k] = take
                    result = backtrack(pos + 1, current_sum + take * (k - 2), new_selected)
                if result is not None:
                    return result
            return None

        # перебор
        solution = backtrack(0, 0, {})

        if solution is not None:
            return True
        else:
            return False

    def is_hamiltonian(self):
        res = self.greenberg_condition()
        if res == 'nonplanar':
            return None
        return res

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
