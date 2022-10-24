from src.control import *
from src.mathutil import *

import tkinter as tk
from tkinter import ttk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


class configurationFunctionArea(tk.Frame):
    def __init__(self, parent, global_variables):
        self.global_variables = global_variables
        super().__init__(parent)
        self.place(x=0, y=70)
        self.setup()

    def setup(self):
        self.config(background="green", width=300, height=300)

class configurationFunctionPolyArea(configurationFunctionArea):
    def __init__(self, parent, global_variables):
        super().__init__(parent, global_variables)

    def setup(self):
        self.config(background="green", width=300, height=300)
        



class ConfigurationWindow(tk.Tk):
    def __init__(self, global_variables):
        self.global_variables: GlobalVars = global_variables
        super().__init__()
        self.setup()

    def setup(self):
        self.title("数据类型设置")
        self.geometry("400x300")
        editing: DataConfiuration = self.global_variables.editing_configuration
        self.name_label = tk.Label(self, text="名称")
        self.name_input = tk.Entry(self)
        self.name_input.insert(0, editing.name)

        self.fit_label = tk.Label(self, text="拟合函数类型")
        self.fit_combobox = ttk.Combobox(
            self, values=list(uid_inv.keys()), state="readonly")
        self.fit_combobox.bind("<<ComboboxSelected>>",
                               self.update_function_area)
        self.fit_combobox.current(0)

        self.function_area = configurationFunctionPolyArea(self, self.global_variables)

        self.name_label.place(x=10, y=10)
        self.name_input.place(x=110, y=10)
        self.fit_label.place(x=10, y=40)
        self.fit_combobox.place(x=110, y=40)

    def update_function_area(self, eve):
        print(eve)


class ControlArea(tk.Frame):
    def __init__(self, parent, global_variables):
        self.configuration_frame_flag = 0
        self.global_variables: GlobalVars = global_variables
        super().__init__(parent)
        self.place(x=0, y=0)
        self.setup()

    def setup(self):
        self.config(background="red", width=800, height=100)
        self.combo_box_label = tk.Label(self, text="数据类型")
        self.combo_box_label.place(x=20, y=20)
        self.combo_box = ttk.Combobox(self, width=20)
        all_confs = [i.name for i in self.global_variables.configurations]

        self.combo_box.config(
            values=(all_confs + ["新建数据类型"]), state="readonly")
        self.combo_box.current(0)
        self.combo_box.place(x=20, y=50)
        self.combo_box.bind("<<ComboboxSelected>>", self._eve_combo_box_change)

    def bind_events(self, events):
        pass

    def _eve_combo_box_change(self, eve):
        if self.configuration_frame_flag:
            return
        length = len(self.combo_box["value"])
        if (self.combo_box.current() + 1) == length:
            self.combo_box.current(0)
            self.configuration_frame = ConfigurationWindow(self.global_variables)
            self.configuration_frame.lift()
            self.configuration_frame.attributes("-topmost", True)
            self.configuration_frame_flag = 1
            while self.configuration_frame_flag:
                self.configuration_frame.update()
                try:
                    if not self.configuration_frame.winfo_exists():
                        self.configuration_frame_flag = 0
                except:
                    self.configuration_frame_flag = 0


class FigureArea(tk.Frame):
    def __init__(self, parent, global_variables):
        self.global_variables = global_variables
        super().__init__(parent)
        self.place(x=0, y=100)
        self.setup()

    def setup(self):
        self.config(background="green", width=500, height=500)
        self.figure_control = FigureControl()
        self.canvas = FigureCanvasTkAgg(self.figure_control.figure, self)
        self.figure_control.first_run()
        self.canvas.draw()
        self.canvas.get_tk_widget().pack()

    def update(self):
        self.figure_control.update()
        self.canvas.draw()


class App(tk.Tk):
    def __init__(self,) -> None:
        self.global_variables = GlobalVars()
        super().__init__()
        self.setup()

    def setup(self):
        self.geometry("800x600")
        self.title("实验数据处理分析系统")
        control = ControlArea(self, self.global_variables)
        figure = FigureArea(self, self.global_variables)


if __name__ == "__main__":
    window = App()
    window.mainloop()
