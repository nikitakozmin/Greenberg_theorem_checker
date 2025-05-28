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
        self.vertex_create_mode = False

        # Настройка размеров окна
        self.master.geometry("1000x600")
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
            ("Сгенерировать ребра", self.graph_edge_generation, "lightblue"),
            ("Проверить граф", self.check_hamiltonian, "lightgoldenrod"),
            ("Перемещение вершин", self.reset_modes, "white"),
            ("Добавление вершин", self.toggle_vertex_mode, "lightgreen"),
            ("Добавление ребер", self.toggle_edge_mode, "lightgreen"),
            ("Удаление вершин", self.toggle_vertex_removal_mode, "pink"),
            ("Удаление ребер", self.toggle_edge_removal_mode, "pink"),
            ("Очистить всё", self.clear_graphs, "salmon"),
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
        self.button_canvas.bind("<Configure>", self.on_button_canvas_configure)
        
        # Холст для графа
        canvas_container = tk.Frame(main_frame)
        canvas_container.pack(fill=tk.BOTH, expand=True)
        
        self.canvas = tk.Canvas(canvas_container, bg="white")
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Обработчики событий
        self.canvas.bind("<Button-1>", self.on_canvas_click)
        self.canvas.bind("<B1-Motion>", self.on_vertex_drag)
    
    def on_button_canvas_configure(self, event):
        """Обновление области прокрутки для кнопок"""
        # Рассчитываем необходимую ширину для всех кнопок
        required_width = self.button_frame.winfo_reqwidth()

        # Устанавливаем ширину фрейма как максимальную из:
        # - реальной ширины всех кнопок
        # - текущей доступной ширины холста
        new_width = max(required_width, event.width)
        self.button_canvas.itemconfig("button_frame", width=new_width)

        # Обновляем область прокрутки
        self.button_canvas.config(scrollregion=self.button_canvas.bbox("all"))

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
            "2. Сгенерируйте ребра\n"
            "3. Можете использовать инструменты:\n"
            "   - Перемещение вершин (по умолчанию): \n"
            "            перетаскивание курсором\n"
            "   - Добавление вершин: клик на холст\n"
            "   - Добавление ребер: клик на 2 вершины\n"
            "   - Удаление вершин: клик на вершину\n"
            "   - Удаление ребер: клик на 2 вершины\n"
            "4. Проверьте граф на гамильтоновость\n\n"
            "Теорема Гринберга проверяет планарные графы\n"
            "на наличие гамильтонова цикла."
        )
        self.show_help_window(help_text)
    
    def toggle_edge_mode(self):
        """Переключение режима создания рёбер"""
        self.reset_modes()  
        self.edge_creation_mode = True 
        self.master.config(cursor="cross")

    def toggle_vertex_mode(self):
        """Переключение режима создания вершин"""
        self.reset_modes()  
        self.vertex_create_mode = True 
        self.master.config(cursor="plus")

    def add_vertex_at(self, x, y):
        """Добавляет вершину в указанные координаты"""
        # Генерируем уникальное имя вершины
        used_indices = [int(name[1:]) for name in self.vertex_positions.keys() if name.startswith("V")]
        new_index = max(used_indices) + 1 if used_indices else 1
        vertex_name = f"V{new_index}"
        
        # Проверяем границы холста
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()
        
        x = max(self.vertex_radius, min(x, canvas_width - self.vertex_radius))
        y = max(self.vertex_radius, min(y, canvas_height - self.vertex_radius))
        
        # Добавляем вершину
        self.vertex_positions[vertex_name] = (x, y)
        self.graph.add_vertex(vertex_name)
        self.vertex_count += 1
        self.redraw_graph()
    
    def toggle_vertex_removal_mode(self):
        """Переключение режима удаления вершин"""
        self.reset_modes()
        self.vertex_removal_mode = True
        self.master.config(cursor="pirate")

    def toggle_edge_removal_mode(self):
        """Переключение режима удаления рёбер"""
        self.reset_modes()
        self.edge_removal_mode = True
        self.master.config(cursor="X_cursor")
        
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
    
    def clear_edges(self):
        """Удаление всех ребер"""
        for u, v, i in self.graph.get_edges():
            for i in range(i):
                self.remove_edge(u, v)
        self.redraw_graph()
    
    def reset_modes(self):
        """Сброс всех режимов и курсора"""
        self.edge_creation_mode = False
        self.vertex_removal_mode = False
        self.edge_removal_mode = False
        self.vertex_create_mode = False
        self.selected_vertex = None
        self.master.config(cursor="")
        self.redraw_graph()

    def set_vertex_count(self):
        """Запрос количества вершин у пользователя"""
        self.reset_modes()
        count = simpledialog.askinteger("Количество вершин", 
                                      "Введите количество вершин (2-50):", 
                                      parent=self.master, 
                                      minvalue=2, 
                                      maxvalue=50)
        if count:
            self.vertex_count = count
            self.clear_canvas()
            self.circular_draw_vertices()
    
    def circular_draw_vertices(self):
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
        # Координаты с учётом прокрутки
        x = self.canvas.canvasx(event.x)
        y = self.canvas.canvasy(event.y)
        
        if self.vertex_create_mode:
            self.add_vertex_at(x, y)
            return
        
        if not self.vertex_positions:
            return
        
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
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()
        
        x = max(self.vertex_radius, min(x, canvas_width - self.vertex_radius))
        y = max(self.vertex_radius, min(y, canvas_height - self.vertex_radius))
        
        # Обновляем позицию вершины
        self.vertex_positions[self.selected_vertex] = (x, y)
        self.redraw_graph()
    
    def add_edge(self, start, end):
        """Добавление ребра в граф"""
        self.graph.add_edge(start, end)  
        self.redraw_graph()

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
            
        # Добавляем подпись сверху
        self.canvas.create_text(
            self.canvas.winfo_width() // 2, 20,  
            text="Плоский граф текущего графа. Чтобы вернуться, нажмите на экран.",
            fill="red",
            font=("Arial", 12, "bold"),
            anchor="n",  # привязка к верхнему центру текста
            width=self.canvas.winfo_width() - 40  # чтобы текст переносился и не выходил за края
        )

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
            
            outline = "red" if vertex == self.selected_vertex else "black"
            width = 2 if vertex == self.selected_vertex else 1
            
            if vertex == self.selected_vertex:
                outline = "red"
                width = 2
            
            self.canvas.create_oval(x-self.vertex_radius, y-self.vertex_radius,
                              x+self.vertex_radius, y+self.vertex_radius,
                              fill="lightblue", outline=outline, width=width)
            self.canvas.create_text(x, y, text=vertex, font=("Arial", 12))
        
    def graph_edge_generation(self):
        """Генерация случайного графа"""
        self.reset_modes()
        if not self.vertex_count:
            messagebox.showwarning("Ошибка", "Сначала задайте количество вершин!")
            return
            
        density = simpledialog.askfloat("Плотность графа", 
                                      "Введите плотность графа (0.0-1.0):",
                                      parent=self.master,
                                      minvalue=0,
                                      maxvalue=1.0)
        if density is None:
            return
        
        self.clear_edges()
        
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
        self.reset_modes()
        if not self.graph.get_vertices():
            messagebox.showwarning("Ошибка", "Граф пуст!")
            return
        
        mutable_params = []
        result = self.graph.greenberg_condition(mutable_params)
        
        if result == True:
            messagebox.showinfo("Результат", f"Граф может быть гамильтонов (по теореме Гринберга)\nf'_k: {mutable_params[0]}\nf''k: {mutable_params[1]}")
            self.redraw_planar_graph()
        elif result == False:
            messagebox.showinfo("Результат", "Граф не гамильтонов (по теореме Гринберга)")
        elif result == 'nonplanar':
            messagebox.showinfo("Результат", "Граф непланарный, теорема Гринберга не применима, гамильтоновость неизвестна")
        elif result == 'nonbiconnected':
            messagebox.showinfo("Результат", "Граф не двусвязный, теорема Гринберга не применима, гамильтоновости нет")
        else:
            messagebox.showwarning("Ошибка", "Неожиданный результат")

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
        self.reset_modes()
        self.clear_canvas()
        self.vertex_count = 0


def main():
    root = tk.Tk()
    app = GraphGUI(root)
    root.mainloop()

if __name__ == "__main__":
    import math
    main()
