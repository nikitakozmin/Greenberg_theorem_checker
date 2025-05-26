import networkx as nx
import planarity
from collections import defaultdict
from networkx import PlanarEmbedding

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
    
    def get_faces(self):
        """Возвращает список граней планарного графа."""
        if not hasattr(self, '_faces_cache'):
            if not self.is_planar():
                self._faces_cache = []
                return []

            # Получаем планарное вложение
            is_planar, embedding = nx.check_planarity(self.graph)
            if not is_planar:
                self._faces_cache = []
                return []

            # Создаем словарь для хранения порядка соседей
            neighbor_order = defaultdict(dict)
            for u in embedding:
                neighbors = list(embedding[u])
                for i, v in enumerate(neighbors):
                    next_v = neighbors[(i + 1) % len(neighbors)]
                    neighbor_order[u][v] = next_v

            # Находим все грани
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
                            
                            # Получаем следующую вершину в порядке обхода
                            next_v = neighbor_order[current_v][current_u]
                            current_u, current_v = current_v, next_v
                            
                            if (current_u, current_v) == (u, v):
                                break
                        
                        faces.append(face)

            self._faces_cache = faces

        return self._faces_cache

    def greenberg_condition(self):
        """Проверяет условие Гринберга для планарного графа."""
        if not self.is_planar(): # проверка планарности
            return 'nonplanar'

        if self.graph.number_of_nodes() < 3 or not self.is_connected():  # проверка связности и корректного кол-ва вершин
            return False
        
        faces = self.get_faces()
        if len(faces) < 1:
            return False  
        
        V, E, F = len(self.graph.nodes), len(self.graph.edges), len(faces)
        if V - E + F != 2: # проверка формулы эйлера
            return False

        try:
            # пытаемся найти вершины на выпуклой оболочке
            pos = nx.planar_layout(self.graph)
            if len(pos) < 3:
                external_face = max(faces, key=len)
            else:
                from scipy.spatial import ConvexHull
                points = list(pos.values())
                hull = ConvexHull(points)
                hull_vertices = set(hull.vertices)
                
                # ищем грань с максимальным числом вершин на оболочке
                max_hull_count = -1
                external_face = faces[0]
                for face in faces:
                    hull_count = sum(1 for v in range(len(face)) 
                                if list(pos.keys()).index(face[v]) in hull_vertices)
                    if hull_count > max_hull_count:
                        max_hull_count = hull_count
                        external_face = face
                        
        except Exception as e:
            print(f"Ошибка при определении внешней грани: {e}")
            external_face = max(faces, key=len)

        internal_faces = [f for f in faces if f != external_face]

        # Вычисляем суммы (k-2)
        sum_internal = sum(len(face) - 2 for face in internal_faces)
        sum_external = len(external_face) - 2

        return sum_internal == sum_external

    def is_hamiltonian(self):
        """Проверяет, может ли граф быть гамильтоновым на основе условия Гринберга."""
        res = self.greenberg_condition()
        if res == 'nonplanar':
            return None
        return res

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
