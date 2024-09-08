import math
import tkinter as tk
from tkinter import ttk, messagebox

import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


class Main(tk.Frame):
    def __init__(self, root):
        super().__init__(root)
        self.init_main()

    def init_main(self):
        toolbar = tk.Frame(bg="#f0f0f0", bd=2)
        toolbar.pack(side=tk.TOP, fill=tk.X)
        ttk.Label(toolbar, text="Количество опытов").grid(row=1, column=0)
        self.edit1 = ttk.Entry(toolbar)
        btn_add = ttk.Button(toolbar, text="Добавить в таблицу")
        btn_add.grid(row=1, column=3, columnspan=1)
        btn_add.bind('<Button-1>', lambda event: self.edit1_change(self.edit1.get()))
        self.edit1.grid(row=1, column=1)
        self.edit1.bind("<KeyRelease>")
        self.tree = ttk.Treeview(self, columns=("№ Опыта", "Значение"), show="headings")
        self.tree.heading("№ Опыта", text="№ Опыта")
        self.tree.heading("Значение", text="Значение")
        self.tree.grid(row=0, column=0, columnspan=4)
        ttk.Button(self, text="Ввести значение", command=self.open_dialog).grid(row=2, column=0, columnspan=1)

        ttk.Button(self, text="Вычислить", command=self.button1_click).grid(row=2, column=1, columnspan=1)

        self.labels = {}
        self.edits = {}
        for i, text in enumerate(["Оценка математического ожидания", "Среднее квадратичное отклонение", "Дисперсия",
                                  "Варьирование X", "Формула Стерджесса"]):
            self.labels[text] = ttk.Label(self, text=text)
            self.labels[text].grid(row=3 + i, column=0)
            self.edits[text] = ttk.Entry(self)
            self.edits[text].grid(row=3 + i, column=1)
        self.mo = 0
        self.d = 0
        self.xi = []
        self.ni = []
        self.f = []
        self.g = []
        self.x_min = 0
        self.x_max = 0
        self.chart = plt.Figure(figsize=(6, 4))
        self.chart_canvas = FigureCanvasTkAgg(self.chart, self)
        self.chart_canvas.get_tk_widget().grid(row=0, column=4, rowspan=10)

    def edit1_change(self, event):
        try:
            n = int(self.edit1.get())
            if n > 1:
                for i in range(n):
                    self.tree.insert("", "end", values=(i + 1, '-'))

            else:
                messagebox.showwarning("Warning", "Введите количество опытов больше нуля")
        except ValueError:
            pass

    def button1_click(self):
        # Оценка математического ожидания
        values = [float(self.tree.item(child)["values"][1]) for child in self.tree.get_children()]
        with open('values.txt', 'w') as f:
            for item in values:
                f.write("%s\n" % item)
        self.mo = sum(values) / len(values)
        self.edits["Оценка математического ожидания"].delete(0, tk.END)
        self.edits["Оценка математического ожидания"].insert(0, str(self.mo))

        # Среднее квадратичное отклонение, Дисперсия
        self.d = sum((x - self.mo) ** 2 for x in values) / (len(values) - 1)
        self.edits["Среднее квадратичное отклонение"].delete(0, tk.END)
        self.edits["Среднее квадратичное отклонение"].insert(0, str(math.sqrt(self.d)))
        self.edits["Дисперсия"].delete(0, tk.END)
        self.edits["Дисперсия"].insert(0, str(self.d))

        # Варьирование X
        values.sort()
        self.x_min, self.x_max = values[0], values[-1]
        self.edits["Варьирование X"].delete(0, tk.END)
        self.edits["Варьирование X"].insert(0, str(self.x_max - self.x_min))

        # Формула Стерджесса
        dx = (self.x_max - self.x_min) / (1 + 3.22 * math.log(len(values)))
        self.edits["Формула Стерджесса"].delete(0, tk.END)
        self.edits["Формула Стерджесса"].insert(0, str(dx))

        # Вычисление xi, ni, f, и g
        self.xi = [self.x_min + i * dx for i in range(len(values) + 1)]
        self.ni = [sum(1 for v in values if (v < x and v >= (x - dx))) for x in self.xi[1:]]
        self.g = [n / len(values) for n in self.ni]
        self.f = [0] + [sum(self.ni[:i + 1]) / len(values) for i in range(len(self.ni))]

        # Графики
        self.chart.clear()
        ax = self.chart.add_subplot(111)
        ax.plot(self.xi, self.f, color='red', label='Статистическая функция')
        ax.bar(self.xi[:-1], self.g, width=dx, alpha=0.5, color='blue', label='Гистограмма')
        ax.legend()
        self.chart_canvas.draw()

    def open_dialog(self):
        Child()

    def records(self, values):
        self.tree.set(self.tree.selection()[0], '#2', value=values)


class Child(tk.Toplevel):
    def __init__(self):
        super().__init__(root)
        self.init_child()
        self.view = app

    def init_child(self):
        self.title("Добавить значение")
        self.geometry("300x120+300+200")
        self.resizable(False, False)
        label_values = tk.Label(self, text='Значение:')
        label_values.place(x=50, y=40)
        self.entry_values = ttk.Entry(self)
        self.entry_values.place(x=120, y=40)
        self.grab_set()
        self.focus_set()
        btn_ok = ttk.Button(self, text='Добавить', command=self.destroy)
        btn_ok.place(x=180, y=80)
        btn_ok.bind('<Button-1>', lambda event: self.view.records(self.entry_values.get()))


if __name__ == "__main__":
    root = tk.Tk()
    app = Main(root)
    app.pack()
    root.title("ОЦЕНКА ЧИСЛОВЫХ ХАРАКТЕРИСТИК СЛУЧАЙНЫХ ВЕЛИЧИН")
    root.geometry("1000x450+300+200")
    root.resizable(False, False)
    root.mainloop()
