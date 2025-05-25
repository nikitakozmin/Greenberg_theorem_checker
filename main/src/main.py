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
        self.vertex_removal_mode = False
        self.edge_removal_mode = False

        # Настройка размеров окна
        # Настройка размеров окна
        self.master.geometry("1000x800")
        self.master.minsize(600, 500)
        
        self.setup_ui()
    
    def setup_ui(self):
        """Настройка пользовательского интерфейса с адаптивной панелью"""
        # Главный фрейм
        main_frame = tk.Frame(self.master)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Панель управления с увеличенной высотой и возможностью прокрутки
        control_frame = tk.Frame(main_frame, bg="lightgray", padx=5, pady=8, height=80)
        control_frame.pack(side=tk.TOP, fill=tk.X)
        control_frame.pack_propagate(False)  # Фиксируем высоту
        
        # Фрейм для кнопок с прокруткой
        button_container = tk.Frame(control_frame)
        button_container.pack(fill=tk.BOTH, expand=True)
        
        # Горизонтальный скроллбар для кнопок
        scrollbar = tk.Scrollbar(button_container, orient=tk.HORIZONTAL)
        scrollbar.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Холст для кнопок
        self.button_canvas = tk.Canvas(button_container, 
                                     height=60, 
                                     xscrollcommand=scrollbar.set,
                                     bg="lightgray",
                                     highlightthickness=0)
        self.button_canvas.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.button_canvas.xview)
        
        # Фрейм для кнопок внутри холста
        self.button_frame = tk.Frame(self.button_canvas, bg="lightgray")
        self.button_canvas.create_window((0,0), 
                                       window=self.button_frame, 
                                       anchor="nw",
                                       tags="button_frame")
        
        # Кнопки управления
        buttons = [
            ("Задать кол-во вершин", self.set_vertex_count, "lightblue"),
            ("Сгенерировать ребра", self.generate_graph, "lightblue"),
            ("Добавить ребро", self.toggle_edge_mode, "lightgreen"),
            ("Удалить вершину", self.toggle_vertex_removal_mode, "salmon"),
            ("Удалить ребро", self.toggle_edge_removal_mode, "orange"),
            ("Проверить граф", self.check_hamiltonian, "lightyellow"),
            ("Очистить всё", self.clear_graphs, "pink"),
            ("Справка", self.show_help, "white")
        ]
        
        for text, command, color in buttons:
            btn = tk.Button(self.button_frame, 
                          text=text, 
                          command=command,
                          bg=color,
                          padx=10,
                          pady=5,
                          font=('Arial', 10),
                          relief=tk.RAISED,
                          bd=2)
            btn.pack(side=tk.LEFT, padx=5, pady=5)
        
        # Обновление размера фрейма кнопок
        self.button_frame.update_idletasks()
        self.button_canvas.config(scrollregion=self.button_canvas.bbox("all"))
        self.button_canvas.bind("<Configure>", self.on_canvas_configure)
        
        # Холст для графа
        canvas_container = tk.Frame(main_frame)
        canvas_container.pack(fill=tk.BOTH, expand=True)
        
        self.canvas = tk.Canvas(canvas_container, bg="white")
        
        # Вертикальный скроллбар для холста
        v_scroll = tk.Scrollbar(canvas_container, orient=tk.VERTICAL, command=self.canvas.yview)
        h_scroll = tk.Scrollbar(canvas_container, orient=tk.HORIZONTAL, command=self.canvas.xview)
        self.canvas.configure(yscrollcommand=v_scroll.set, xscrollcommand=h_scroll.set)
        
        v_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        h_scroll.pack(side=tk.BOTTOM, fill=tk.X)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Обработчики событий
        self.canvas.bind("<Button-1>", self.on_canvas_click)
        self.canvas.bind("<B1-Motion>", self.on_vertex_drag)
        self.master.bind("<Configure>", self.on_window_resize)
    
    def on_canvas_configure(self, event):
        """Обновление области прокрутки для кнопок"""
        self.button_canvas.itemconfig("button_frame", width=event.width)
        self.button_canvas.config(scrollregion=self.button_canvas.bbox("all"))
    
    def on_window_resize(self, event):
        """Обработчик изменения размера окна"""
        self.button_canvas.config(scrollregion=self.button_canvas.bbox("all"))
        self.redraw_graph()

    def show_help_window(self, help_text):
        help_win = tk.Toplevel()
        help_win.title("Справка")
        help_win.geometry("400x400") 

        scrollbar = tk.Scrollbar(help_win)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        text = tk.Text(help_win, wrap=tk.WORD, yscrollcommand=scrollbar.set)
        text.pack(expand=True, fill=tk.BOTH)
        text.insert(tk.END, help_text)
        text.config(state=tk.DISABLED)

        scrollbar.config(command=text.yview)

    def show_help(self):
        """Показать справку"""
        help_text = (
            "Инструкция по использованию:\n\n"
            "1. Задайте количество вершин\n"
            "2. Сгенерируйте ребра или создайте их вручную\n"
            "3. Используйте инструменты:\n"
            "   - Добавить ребро: клик на 2 вершины\n"
            "   - Удалить вершину: клик на вершину\n"
            "   - Удалить ребро: клик на 2 вершины\n"
            "4. Проверьте граф на гамильтоновость\n\n"
            "Теорема Гринберга проверяет планарные графы\n"
            "на наличие гамильтонова цикла."
        )
        self.show_help_window(help_text)

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

    def toggle_vertex_removal_mode(self):
        """Переключение режима удаления вершин"""
        self.vertex_removal_mode = not self.vertex_removal_mode
        self.edge_creation_mode = False
        self.edge_removal_mode = False
        self.update_cursor()

    def toggle_edge_removal_mode(self):
        """Переключение режима удаления рёбер"""
        self.edge_removal_mode = not self.edge_removal_mode
        self.edge_creation_mode = False
        self.vertex_removal_mode = False
        self.update_cursor()

    def remove_vertex(self, vertex):
        """Удаление вершины из графа"""
        if vertex in self.vertex_positions:
            self.graph.remove_vertex(vertex)
            del self.vertex_positions[vertex]
            self.redraw_graph()
            return True
        return False
    
    def remove_edge(self, u, v):
        """Удаление ребра между вершинами"""
        if u in self.vertex_positions and v in self.vertex_positions:
            if self.graph.has_edge(u, v):
                self.graph.remove_edge(u, v)
                self.redraw_graph()
                return True
        return False
    
    def update_cursor(self):
        """Обновление курсора в зависимости от режима"""
        if self.edge_creation_mode:
            self.master.config(cursor="cross")
        elif self.vertex_removal_mode:
            self.master.config(cursor="pirate")
        elif self.edge_removal_mode:
            self.master.config(cursor="X_cursor")
        else:
            self.master.config(cursor="")

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
            if self.vertex_removal_mode:
                self.remove_vertex(clicked_vertex)
                return
            elif self.edge_removal_mode:
                if self.selected_vertex is None:
                    self.selected_vertex = clicked_vertex
                else:
                    self.remove_edge(self.selected_vertex, clicked_vertex)
                    self.selected_vertex = None
                self.redraw_graph()
                return
            elif self.edge_creation_mode:
                if self.selected_vertex is None:
                    self.selected_vertex = clicked_vertex
                else:
                    self.add_edge(self.selected_vertex, clicked_vertex)
                    self.selected_vertex = None
                self.redraw_graph()
                return
            else:
                self.selected_vertex = clicked_vertex
                self.redraw_graph()
        else:
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

        # Добавляем подпись сверху
        self.canvas.create_text(
            self.canvas.winfo_width() // 2, 20,  
            text="Плоский граф текущего графа. Чтобы вернуться, нажмите на экран.",
            fill="black",
            font=("Arial", 12, "bold"),
            anchor="n",  # привязка к верхнему центру текста
            width=self.canvas.winfo_width() - 40  # чтобы текст переносился и не выходил за края
        )
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
            messagebox.showinfo("Результат", "Граф может быть гамильтонов (по теореме Гринберга)")
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

    def clear_graphs(self):
        """Очистка холста, графа и вершин"""
        self.clear_canvas()
        self.vertex_count = 0


def main():
    root = tk.Tk()
    app = GraphGUI(root)
    root.mainloop()

if __name__ == "__main__":
    import math
    main()
