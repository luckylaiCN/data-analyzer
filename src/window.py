from src.control import *
from src.mathutil import *

import tkinter as tk
from tkinter import ttk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


def empty_promise(_):
    print(f"<Promise return> {_}")
    return


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

    def do_submit(self,_=None):
        self.yield_promise(self.input_var.get())

    def do_cancel(self,_=None):
        self.yield_promise("", False)

    def setup(self):
        self.geometry("250x50")
        self.title("输入")
        self.input_var = tk.StringVar(master=self, value=self.value)
        self.input_box = tk.Entry(self, textvariable=self.input_var)
        self.submit = tk.Button(self, text="确定", command=self.do_submit)
        self.bind("<Return>",self.do_submit )
        self.cancel = tk.Button(self, text="取消", command=self.do_cancel)
        self.input_box.place(x=10, y=10)
        self.submit.place(x=160, y=5)
        self.cancel.place(x=200, y=5)
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
        self.list_raw = []
        for item in self.global_variables.editing_configuration.parameter_names:
            self.list_raw.append(item)
        self.list_var.set(self.list_raw)

    def setup(self):
        self.config(background="red", width=300, height=300)
        self.listbox_label = tk.Label(self, text="参数名称编辑")
        self.listbox = tk.Listbox(self, height=5)
        self.list_raw = []
        self.list_var = tk.StringVar(master=self, value=self.list_raw)
        for item in self.global_variables.editing_configuration.parameter_names:
            self.list_raw.append(item)
        self.list_var.set(self.list_raw)
        self.listbox.config(listvariable=self.list_var)
        self.listbox.bind("<Double-1>", self.update_handle)
        self.listbox_label.place(x=10, y=10)
        self.listbox.place(x=10, y=40)


class configurationFunctionArea(tk.Frame):
    def __init__(self, parent, global_variables):
        self.global_variables: GlobalVars = global_variables
        super().__init__(parent)
        self.place(x=0, y=70)
        self.setup()

    def setup(self):
        self.config(background="green", width=300, height=300)
        self.x_label_label = tk.Label(self, text="x轴标签")
        self.y_label_label = tk.Label(self, text="y轴标签")
        self.x_label_var = tk.StringVar(
            self, self.global_variables.editing_configuration.labels[0])
        self.y_label_var = tk.StringVar(
            self, self.global_variables.editing_configuration.labels[1])
        self.x_label_input = tk.Entry(self, textvariable=self.x_label_var)
        self.y_label_input = tk.Entry(self, textvariable=self.y_label_var)
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
        self.poly_deg_var = tk.IntVar(self,1)
        self.poly_deg_label = tk.Label(self,textvariable=self.poly_deg_var)
        self.left_button = tk.Button(self,text="降低维度",command=self.reduce_deg)
        self.right_button = tk.Button(self,text="增加维度",command=self.increase_deg)
        self.poly_deg_label.place(x=170,y=70)
        self.left_button.place(x=100,y=65)
        self.right_button.place(x=200,y=65)
        self.parameters_control = configurationParametersAliasArea(
            self, self.global_variables)
        self.parameters_control.place(x=0, y=100)

class configurationFunctionSQArea(configurationFunctionArea):
    def __init__(self, parent, global_variables):
        super().__init__(parent, global_variables)

    def extra(self):
        self.parameters_control = configurationParametersAliasArea(
            self, self.global_variables)
        self.parameters_control.place(x=0, y=100)


class ConfigurationWindow(tk.Tk):
    def __init__(self, global_variables):
        self.global_variables: GlobalVars = global_variables
        super().__init__()
        self.setup()

    def setup(self):
        self.title("数据类型设置")
        self.geometry("400x600")
        editing: DataConfiuration = self.global_variables.editing_configuration
        self.name_label = tk.Label(self, text="名称")
        self.name_input = tk.Entry(self)
        self.name_input.insert(0, editing.name)
        self.keys_list = list(uid_inv.keys())
        self.fit_label = tk.Label(self, text="拟合函数类型")
        self.fit_combobox = ttk.Combobox(
            self, values=self.keys_list, state="readonly")
        self.fit_combobox.bind("<<ComboboxSelected>>",
                               self.update_function_area)
        self.fit_combobox.current(self.keys_list.index(editing.fit_object.__name__))

        if editing.fit_object == PolyFit:
            self.function_area = configurationFunctionPolyArea(
            self, self.global_variables)
        else:
            self.function_area = configurationFunctionSQArea(
            self, self.global_variables)

        self.name_label.place(x=10, y=10)
        self.name_input.place(x=110, y=10)
        self.fit_label.place(x=10, y=40)
        self.fit_combobox.place(x=110, y=40)

    def update_function_area(self, eve):
        uid = uid_inv[self.keys_list[self.fit_combobox.current()]]
        self.function_area.destroy()
        self.global_variables.editing_configuration.change_fit_mod(unique_id[uid],1)
        if unique_id[uid] == PolyFit:
            self.function_area = configurationFunctionPolyArea(
            self, self.global_variables)
        else:
            self.function_area = configurationFunctionSQArea(
            self, self.global_variables)



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
        self.combo_box_label = tk.Label(self, text="数据类型")
        self.combo_box_label.place(x=20, y=20)
        self.combo_box = ttk.Combobox(self, width=20)
        all_confs = [i.name for i in self.global_variables.configurations]

        self.combo_box.config(
            values=(all_confs + ["新建数据类型"]), state="readonly")
        self.combo_box.current(0)
        self.combo_box.place(x=20, y=50)
        self.combo_box.bind("<<ComboboxSelected>>", self._eve_combo_box_change)

        self.conf_button = tk.Button(self,text="编辑",command=self.do_conf)
        self.conf_button.place(x=200,y=45)

    def do_conf(self):
        idx = self.combo_box.current()
        self.global_variables.editing_configuration = self.global_variables.configurations[idx]
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


    def bind_events(self, events):
        self.events = events[:]

    def _eve_combo_box_change(self, eve):
        if self.configuration_frame_flag:
            return
        length = len(self.combo_box["value"])
        if (self.combo_box.current() + 1) == length:
            self.combo_box.current(0)
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

    def change(self,conf):
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
