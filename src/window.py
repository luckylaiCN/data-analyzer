from src.control import *
from src.mathutil import *

import tkinter as tk
from tkinter import StringVar, ttk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


def empty_promise(_):
    print(f"<Promise return> {_}")
    return

class SubWindow(tk.Tk):
    events = []
    def __init__(self, global_variables):
        self.global_variables: GlobalVars = global_variables
        super().__init__()
        self.setup()

    def setup(self):
        raise NotImplementedError("TkModule not implemented.") 

    def bind_events(self,events):
        self.events = events[:]

class InputWindow(tk.Tk):
    def __init__(self, global_variables, default="", promise_function=empty_promise):
        self.global_variables: GlobalVars = global_variables
        self.value = default
        self.promise_function = promise_function

        super().__init__()

        self.setup()

    def yield_promise(self, response, status=True):
        self.promise_function((response, status))
        self.destroy()

    def do_submit(self, _=None):
        self.yield_promise(self.input_var.get())

    def do_cancel(self, _=None):
        self.yield_promise("", False)

    def setup(self):
        self.geometry("200x70")
        self.title("输入")

        self.input_var = tk.StringVar(master=self, value=self.value)
        self.input_box = ttk.Entry(self, textvariable=self.input_var,width=24)
        self.submit_button = ttk.Button(self, text="确定", command=self.do_submit)
        self.cancel_button = ttk.Button(self, text="取消", command=self.do_cancel)

        self.bind("<Return>", self.do_submit)

        self.input_box.place(x=10, y=10)
        self.submit_button.place(x=5, y=40)
        self.cancel_button.place(x=105, y=40)

        self.lift()


class configurationParametersAliasArea(tk.Frame):
    def __init__(self, parent, global_variables):
        self.global_variables: GlobalVars = global_variables
        self.promised = True
        super().__init__(parent)
        self.setup()

    def update_handle(self, eve):
        idxs = self.listbox.curselection()
        if not self.promised:
            return
        if len(idxs) == 1:
            idx = int(idxs[0])
            self.promised = False
            InputWindow(self.global_variables, self.list_raw[idx], (
                lambda resp: self.update_item(idx, resp)
            ))

    def update_item(self, index, resp):
        self.promised = True
        value, status = resp
        if not status:
            return
        if len(value) > 0:
            self.list_raw[index] = value
            self.list_var.set(self.list_raw)

    def update_all(self):
        self.list_raw = self.global_variables.editing_configuration.parameter_names[:]
        self.list_var.set(self.list_raw)

    def setup(self):
        self.config(width=300, height=300)
        self.list_raw = []
        self.list_var = tk.StringVar(master=self, value=self.list_raw)
        self.list_raw = self.global_variables.editing_configuration.parameter_names[:]
        self.list_var.set(self.list_raw)

        self.listbox_label = tk.Label(self, text="参数名称编辑")
        self.listbox_frame = tk.Frame(self, width=200, height=200)
        self.listbox = tk.Listbox(self.listbox_frame, height=5)
        self.scroll_bar = ttk.Scrollbar(
            self.listbox_frame, command=self.listbox.yview)

        self.listbox.config(listvariable=self.list_var,
                            yscrollcommand=self.scroll_bar.set)
        self.listbox.bind("<Double-1>", self.update_handle)

        self.listbox_label.place(x=10, y=10)
        self.listbox_frame.place(x=10, y=30)
        self.listbox.grid(column=0, row=0, sticky=(tk.N, tk.W, tk.E, tk.S))
        self.scroll_bar.grid(column=1, row=0, sticky=(tk.N, tk.S))
        self.listbox_frame.grid_columnconfigure(0, weight=1)
        self.listbox_frame.grid_rowconfigure(0, weight=1)


class configurationFunctionArea(tk.Frame):
    def __init__(self, parent, global_variables):
        self.global_variables: GlobalVars = global_variables
        super().__init__(parent)
        self.place(x=0, y=70)
        self.setup()

    def setup(self):
        self.config(width=300, height=250)
        self.x_label_label = tk.Label(self, text="x轴标签")
        self.y_label_label = tk.Label(self, text="y轴标签")
        self.x_label_var = tk.StringVar(
            self, self.global_variables.editing_configuration.labels[0])
        self.y_label_var = tk.StringVar(
            self, self.global_variables.editing_configuration.labels[1])
        self.x_label_input = ttk.Entry(self, textvariable=self.x_label_var)
        self.y_label_input = ttk.Entry(self, textvariable=self.y_label_var)

        self.x_label_label.place(x=10, y=10)
        self.y_label_label.place(x=10, y=40)
        self.x_label_input.place(x=110, y=10)
        self.y_label_input.place(x=110, y=40)

        self.extra()

    def extra(self):
        raise NotImplementedError(
            "configurationFunctionArea.extra not implemented.")


class configurationFunctionPolyArea(configurationFunctionArea):
    def __init__(self, parent, global_variables):
        super().__init__(parent, global_variables)

    def reduce_deg(self):
        if self.poly_deg_var.get() > 1:
            self.poly_deg_var.set(self.poly_deg_var.get()-1)
            self.global_variables.editing_configuration.reduce_deg_for_poly()
            self.parameters_control.update_all()

    def increase_deg(self):
        self.poly_deg_var.set(self.poly_deg_var.get()+1)
        self.global_variables.editing_configuration.increase_deg_for_poly()
        self.parameters_control.update_all()

    def extra(self):
        self.poly_deg_var = tk.IntVar(self, self.global_variables.editing_configuration.parameter_count)

        self.poly_deg_label = tk.Label(self, textvariable=self.poly_deg_var)
        self.left_button = ttk.Button(
            self, text="降低维度", command=self.reduce_deg)
        self.right_button = ttk.Button(
            self, text="增加维度", command=self.increase_deg)
        self.parameters_control = configurationParametersAliasArea(
            self, self.global_variables)

        self.poly_deg_label.place(x=140, y=70)
        self.left_button.place(x=10, y=70)
        self.right_button.place(x=200, y=70)
        self.parameters_control.place(x=0, y=100)


class configurationFunctionSQArea(configurationFunctionArea):
    def __init__(self, parent, global_variables):
        super().__init__(parent, global_variables)

    def extra(self):
        self.parameters_control = configurationParametersAliasArea(
            self, self.global_variables)
        self.parameters_control.place(x=0, y=100)


class ConfigurationWindow(SubWindow):
    def __init__(self, global_variables):
        super().__init__(global_variables)

    def setup(self):
        self.title("数据类型设置")
        self.geometry("300x400")
        editing: DataConfiuration = self.global_variables.editing_configuration
        self.name_var = StringVar(self,editing.name)
        self.keys_list = list(uid_inv.keys())

        self.name_label = tk.Label(self, text="名称")
        self.name_input = ttk.Entry(self,textvariable=self.name_var)
        self.fit_label = tk.Label(self, text="拟合函数类型")
        self.fit_combobox = ttk.Combobox(
            self, values=self.keys_list, state="readonly")
        self.submit_button = ttk.Button(self, text="确定",command=self.submit_change)
        self.cancel_button = ttk.Button(self, text="取消",command=self.discard_change)

        if editing.fit_object == PolyFit:
            self.function_area = configurationFunctionPolyArea(
                self, self.global_variables)
        else:
            self.function_area = configurationFunctionSQArea(
                self, self.global_variables)

        self.fit_combobox.bind("<<ComboboxSelected>>",
                               self.update_function_area)
        self.fit_combobox.current(
            self.keys_list.index(editing.fit_object.__name__))

        self.name_label.place(x=10, y=10)
        self.name_input.place(x=110, y=10)
        self.fit_label.place(x=10, y=40)
        self.fit_combobox.place(x=110, y=40)
        self.submit_button.place(x=100, y=350)
        self.cancel_button.place(x=200, y=350)

    def update_function_area(self, _):
        uid = uid_inv[self.keys_list[self.fit_combobox.current()]]
        self.function_area.destroy()
        self.global_variables.editing_configuration.change_fit_mode(
            unique_id[uid], 1)
        if unique_id[uid] == PolyFit:
            self.function_area = configurationFunctionPolyArea(
                self, self.global_variables)
        else:
            self.function_area = configurationFunctionSQArea(
                self, self.global_variables)

    def discard_change(self):
        self.destroy()

    def submit_change(self):
        self.global_variables.editing_configuration.name = self.name_var.get()
        self.global_variables.editing_configuration.parameter_names = self.function_area.parameters_control.list_raw[:]
        self.global_variables.editing_configuration.labels = [
            self.function_area.x_label_var.get(),
            self.function_area.y_label_var.get()
        ]
        if self.global_variables.editing_index == -1:
            self.global_variables.configurations.append(
                self.global_variables.editing_configuration
            )
        else:
            self.global_variables.configurations[self.global_variables.editing_index] = self.global_variables.editing_configuration
        self.destroy()


class DataWindow(SubWindow):
    def __init__(self, global_variables):
        super().__init__(global_variables)

    def setup(self):
        pass 

    def bind_events(self,events):
        self.events = events[:]

class ControlArea(tk.Frame):
    events = []

    def __init__(self, parent, global_variables):
        self.configuration_frame_flag = 0
        self.global_variables: GlobalVars = global_variables
        super().__init__(parent)
        self.place(x=0, y=0)
        self.setup()

    def setup(self):
        self.config(background="red", width=800, height=100)
        all_confs = [i.name for i in self.global_variables.configurations]

        self.combo_box_label = tk.Label(self, text="数据类型")
        
        self.combo_box = ttk.Combobox(self, width=20)
        self.conf_button = ttk.Button(self, text="编辑", command=self.do_conf)

        self.combo_box.config(
            values=(all_confs + ["新建数据类型"]), state="readonly")
        self.combo_box.current(0)
        self.combo_box.bind("<<ComboboxSelected>>", self._eve_combo_box_change)
        self.combo_box_label.place(x=20, y=20)
        self.combo_box.place(x=20, y=50)
        self.conf_button.place(x=200, y=50)

    def update_all(self):
        all_confs = [i.name for i in self.global_variables.configurations]
        self.combo_box.config(
            values=(all_confs + ["新建数据类型"]), state="readonly")
        self.combo_box.current(0)


    def do_conf(self):
        idx = self.combo_box.current()
        self.global_variables.editing_index = idx
        self.global_variables.editing_configuration = self.global_variables.configurations[
            idx]
        if self.configuration_frame_flag:
            return
        self.configuration_frame = ConfigurationWindow(
            self.global_variables)
        self.configuration_frame_flag = 1
        while self.configuration_frame_flag:
            self.configuration_frame.update()
            try:
                if not self.configuration_frame.winfo_exists():
                    self.configuration_frame_flag = 0
            except:
                self.configuration_frame_flag = 0
        self.update_all()

    def bind_events(self, events):
        self.events = events[:]

    def _eve_combo_box_change(self, _):
        if self.configuration_frame_flag:
            return
        length = len(self.combo_box["value"])
        if (self.combo_box.current() + 1) == length:
            self.global_variables.editing_index = -1
            self.combo_box.current(0)
            self.global_variables.editing_configuration = default_configuration.copy()
            self.configuration_frame = ConfigurationWindow(
                self.global_variables)
            self.configuration_frame_flag = 1
            while self.configuration_frame_flag:
                self.configuration_frame.update()
                try:
                    if not self.configuration_frame.winfo_exists():
                        self.configuration_frame_flag = 0
                except:
                    self.configuration_frame_flag = 0
            self.update_all()
        else:
            idx = self.combo_box.current()
            self.events[0](self.global_variables.configurations[idx])
       


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

    def change(self, conf):
        self.figure_control.update_configuration(conf)
        self.figure_control.first_run()
        self.canvas.draw()

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

        control.bind_events([
            figure.change
        ])


if __name__ == "__main__":
    window = App()
    window.mainloop()
