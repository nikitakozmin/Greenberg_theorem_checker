import tkinter as tk
from tkinter import messagebox, simpledialog
import random
import math
from graph import GraphNX

class GraphGUI:
    def __init__(self, master):
        self.master = master
        self.master.title("Проверка графа на гамильтоновость")
        self.graph = GraphNX()
        self.vertex_count = 0
        self.canvas = None
        self.vertex_radius = 20
        self.vertex_positions = {}
        self.selected_vertex = None
        self.edge_creation_mode = False
        
        # Настройка размеров окна
        self.master.geometry("900x700")
        self.master.minsize(800, 600)
        
        self.setup_ui()
    
    def setup_ui(self):
        """Настройка пользовательского интерфейса"""
        # Главный фрейм с панелью управления и холстом
        main_frame = tk.Frame(self.master)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Панель управления
        control_frame = tk.Frame(main_frame, bg="lightgray", padx=5, pady=5)
        control_frame.pack(side=tk.TOP, fill=tk.X)
        
        # Кнопки управления
        tk.Button(control_frame, text="Задать количество вершин", 
                 command=self.set_vertex_count).pack(side=tk.LEFT, padx=5)
        tk.Button(control_frame, text="Сгенерировать граф", 
                 command=self.generate_graph).pack(side=tk.LEFT, padx=5)
        tk.Button(control_frame, text="Режим создания рёбер", 
                 command=self.toggle_edge_mode, bg="lightgreen").pack(side=tk.LEFT, padx=5)
        tk.Button(control_frame, text="Проверить на гамильтоновость", 
                 command=self.check_hamiltonian).pack(side=tk.LEFT, padx=5)
        tk.Button(control_frame, text="Очистить", 
                 command=self.clear_canvas).pack(side=tk.LEFT, padx=5)
        
        # Холст для рисования графа с прокруткой
        canvas_frame = tk.Frame(main_frame)
        canvas_frame.pack(fill=tk.BOTH, expand=True)
        
        self.canvas = tk.Canvas(canvas_frame, width=800, height=600, bg="white", 
                               scrollregion=(0, 0, 1200, 1200))
        
        # Добавляем прокрутку
        h_scroll = tk.Scrollbar(canvas_frame, orient=tk.HORIZONTAL, command=self.canvas.xview)
        v_scroll = tk.Scrollbar(canvas_frame, orient=tk.VERTICAL, command=self.canvas.yview)
        self.canvas.configure(xscrollcommand=h_scroll.set, yscrollcommand=v_scroll.set)
        
        h_scroll.pack(side=tk.BOTTOM, fill=tk.X)
        v_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Обработчики событий
        self.canvas.bind("<Button-1>", self.on_canvas_click)
        self.canvas.bind("<B1-Motion>", self.on_vertex_drag)
        self.canvas.bind("<Configure>", self.on_canvas_resize)
    
    def on_canvas_resize(self, event):
        """Обработчик изменения размера холста"""
        self.redraw_graph()
    
    def toggle_edge_mode(self):
        """Переключение режима создания рёбер"""
        self.edge_creation_mode = not self.edge_creation_mode
        if self.edge_creation_mode:
            self.master.config(cursor="cross")
        else:
            self.master.config(cursor="")
            self.selected_vertex = None
            self.redraw_graph()
    
    def set_vertex_count(self):
        """Запрос количества вершин у пользователя"""
        count = simpledialog.askinteger("Количество вершин", 
                                      "Введите количество вершин (2-50):", 
                                      parent=self.master, 
                                      minvalue=2, 
                                      maxvalue=50)
        if count:
            self.vertex_count = count
            self.clear_canvas()
            self.draw_vertices()
    
    def draw_vertices(self):
        """Отрисовка вершин на холсте с учётом границ"""
        if not self.vertex_count:
            return
        
        self.vertex_positions = {}
        canvas_width = self.canvas.winfo_width() - 2 * self.vertex_radius
        canvas_height = self.canvas.winfo_height() - 2 * self.vertex_radius
        
        # Если холст ещё не отобразился, используем стандартные размеры
        if canvas_width <= 0:
            canvas_width = 800 - 2 * self.vertex_radius
        if canvas_height <= 0:
            canvas_height = 600 - 2 * self.vertex_radius
        
        center_x, center_y = canvas_width // 2, canvas_height // 2
        radius = min(center_x - 50, center_y - 50, 
                    max(50, min(canvas_width, canvas_height) // 3))
        
        for i in range(self.vertex_count):
            angle = 2 * math.pi * i / self.vertex_count
            x = center_x + radius * math.cos(angle)
            y = center_y + radius * math.sin(angle)
            
            # Убедимся, что вершина не выходит за границы
            x = max(self.vertex_radius, min(x, canvas_width - self.vertex_radius))
            y = max(self.vertex_radius, min(y, canvas_height - self.vertex_radius))
            
            vertex = f"V{i+1}"
            self.vertex_positions[vertex] = (x, y)
            self.graph.add_vertex(vertex)
        
        self.redraw_graph()
    
    def on_canvas_click(self, event):
        """Обработчик клика на холсте"""
        if not self.vertex_positions:
            return
        
        # Координаты с учётом прокрутки
        x = self.canvas.canvasx(event.x)
        y = self.canvas.canvasy(event.y)
        
        # Проверяем, кликнули ли на вершину
        clicked_vertex = None
        for vertex, (vx, vy) in self.vertex_positions.items():
            if ((x - vx)**2 + (y - vy)**2) <= self.vertex_radius**2:
                clicked_vertex = vertex
                break
        
        if clicked_vertex:
            if self.edge_creation_mode:
                if self.selected_vertex is None:
                    # Выбираем первую вершину
                    self.selected_vertex = clicked_vertex
                    self.redraw_graph()
                else:
                    # Создаём ребро между выбранными вершинами
                    if self.selected_vertex != clicked_vertex:
                        self.add_edge(self.selected_vertex, clicked_vertex)
                    # Снимаем выделение
                    self.selected_vertex = None
                    self.redraw_graph()
            else:
                # Просто выделяем вершину для перемещения
                self.selected_vertex = clicked_vertex
                self.redraw_graph()
        elif not self.edge_creation_mode and self.selected_vertex:
            # Снимаем выделение, если кликнули не на вершину
            self.selected_vertex = None
            self.redraw_graph()
    
    def on_vertex_drag(self, event):
        """Перемещение вершины при перетаскивании"""
        if not self.selected_vertex or self.edge_creation_mode:
            return
        
        # Координаты с учётом прокрутки
        x = self.canvas.canvasx(event.x)
        y = self.canvas.canvasy(event.y)
        
        # Убедимся, что вершина не выходит за границы
        canvas_width = self.canvas.winfo_width() - self.vertex_radius
        canvas_height = self.canvas.winfo_height() - self.vertex_radius
        
        x = max(self.vertex_radius, min(x, canvas_width - self.vertex_radius))
        y = max(self.vertex_radius, min(y, canvas_height - self.vertex_radius))
        
        # Обновляем позицию вершины
        self.vertex_positions[self.selected_vertex] = (x, y)
        self.redraw_graph()
    
    def add_edge(self, start, end):
        """Добавление ребра в граф"""
        self.graph.add_edge(start, end)
    
    
    def redraw_planar_graph(self):
        """Перерисовка графа с учётом планарности"""
        self.canvas.delete("all")

        pos, is_planar = self.graph.layout_planar_or_default()

        # Масштабируем координаты под размеры холста
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()

        # Найдём минимальные и максимальные координаты из pos
        xs = [x for x, y in pos.values()]
        ys = [y for x, y in pos.values()]
        min_x, max_x = min(xs), max(xs)
        min_y, max_y = min(ys), max(ys)

        # Функция нормализации координат под размеры холста с отступами
        def scale_coord(x, y):
            margin = 40
            scaled_x = margin + (x - min_x) / (max_x - min_x) * (canvas_width - 2 * margin)
            scaled_y = margin + (y - min_y) / (max_y - min_y) * (canvas_height - 2 * margin)
            return scaled_x, scaled_y

        scaled_pos = {v: scale_coord(x, y) for v, (x, y) in pos.items()}

        # Рисуем рёбра
        for start, end, _ in self.graph.get_edges():
            x1, y1 = scaled_pos[start]
            x2, y2 = scaled_pos[end]
            self.canvas.create_line(x1, y1, x2, y2, width=2, fill="black")

        # Рисуем вершины
        for vertex, (x, y) in scaled_pos.items():
            color = "lightblue" if is_planar else "lightcoral"  # цвет зависит от планарности
            outline = "black"
            width = 1
            if vertex == self.selected_vertex:
                outline = "red"
                width = 2
            r = self.vertex_radius
            self.canvas.create_oval(x - r, y - r, x + r, y + r, fill=color, outline=outline, width=width)
            self.canvas.create_text(x, y, text=vertex, font=("Arial", 12))

        # Обновляем область прокрутки
        self.update_scrollregion()


    def redraw_graph(self):
        """Перерисовка всего графа"""
        self.canvas.delete("all")
        
        # Рисуем рёбра
        for start, end, _ in self.graph.get_edges():
            x1, y1 = self.vertex_positions[start]
            x2, y2 = self.vertex_positions[end]
            self.canvas.create_line(x1, y1, x2, y2, width=2, fill="black")
        
        # Рисуем вершины
        for vertex, (x, y) in self.vertex_positions.items():
            color = "lightblue"
            outline = "black"
            width = 1
            
            if vertex == self.selected_vertex:
                outline = "red"
                width = 2
            
            self.canvas.create_oval(x-self.vertex_radius, y-self.vertex_radius,
                                   x+self.vertex_radius, y+self.vertex_radius,
                                   fill=color, outline=outline, width=width)
            self.canvas.create_text(x, y, text=vertex, font=("Arial", 12))
        
        # Обновляем область прокрутки
        self.update_scrollregion()
    
    def update_scrollregion(self):
        """Обновление области прокрутки холста"""
        if not self.vertex_positions:
            return
        
        # Находим границы всех элементов
        min_x = min(x for x, y in self.vertex_positions.values()) - self.vertex_radius
        min_y = min(y for x, y in self.vertex_positions.values()) - self.vertex_radius
        max_x = max(x for x, y in self.vertex_positions.values()) + self.vertex_radius
        max_y = max(y for x, y in self.vertex_positions.values()) + self.vertex_radius
        
        # Добавляем отступы
        padding = 50
        self.canvas.config(scrollregion=(min_x - padding, min_y - padding,
                          max_x + padding, max_y + padding))
    
    def generate_graph(self):
        """Генерация случайного графа"""
        if not self.vertex_count:
            messagebox.showwarning("Ошибка", "Сначала задайте количество вершин!")
            return
            
        density = simpledialog.askfloat("Плотность графа", 
                                      "Введите плотность графа (0.1-1.0):",
                                      parent=self.master,
                                      minvalue=0.1,
                                      maxvalue=1.0)
        if density is None:
            return
            
        self.clear_canvas()
        self.draw_vertices()
        
        # Генерация рёбер
        vertices = list(self.vertex_positions.keys())
        max_edges = len(vertices) * (len(vertices) - 1) // 2
        target_edges = int(density * max_edges)
        
        # Добавляем рёбра случайным образом
        added_edges = 0
        while added_edges < target_edges:
            v1, v2 = random.sample(vertices, 2)
            if v1 != v2 and not self.graph.has_edge(v1, v2):
                self.add_edge(v1, v2)
                added_edges += 1
        
        self.redraw_graph()
    
    def check_hamiltonian(self):
        """Проверка графа на гамильтоновость"""
        if not self.graph.get_vertices():
            messagebox.showwarning("Ошибка", "Граф пуст!")
            return
            
        result = self.graph.is_hamiltonian()
        
        if result is True:
            messagebox.showinfo("Результат", "Граф гамильтонов (по теореме Гринберга)")
            self.redraw_planar_graph()
        elif result is False:
            messagebox.showinfo("Результат", "Граф не гамильтонов (по теореме Гринберга)")
        else:
            messagebox.showinfo("Результат", "Граф непланарный, теорема Гринберга не применима, гамильтоновость неизвестна")

    def clear_canvas(self):
        """Очистка холста и графа"""
        self.canvas.delete("all")
        self.graph = GraphNX()
        self.vertex_positions = {}
        self.selected_vertex = None
        self.edge_creation_mode = False
        self.master.config(cursor="")

def main():
    root = tk.Tk()
    app = GraphGUI(root)
    root.mainloop()

if __name__ == "__main__":
    import math
    main()