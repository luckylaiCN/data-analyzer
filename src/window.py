from src.control import *
from src.mathutil import *

import tkinter as tk
from tkinter import ttk
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
        raise NotImplementedError("SubWindow Not Implemented.")

    def bind_events(self, events):
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
        self.input_box = ttk.Entry(self, textvariable=self.input_var, width=24)
        self.submit_button = ttk.Button(
            self, text="确定", command=self.do_submit)
        self.cancel_button = ttk.Button(
            self, text="取消", command=self.do_cancel)

        self.bind("<Return>", self.do_submit)

        self.input_box.place(x=10, y=10)
        self.submit_button.place(x=5, y=40)
        self.cancel_button.place(x=105, y=40)

        self.lift()


class ConfigurationParametersAliasArea(tk.Frame):
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


class ConfigurationFunctionArea(tk.Frame):
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
            "configurationFunctionArea.extra Not Implemented.")


class ConfigurationFunctionPolyArea(ConfigurationFunctionArea):
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
        self.poly_deg_var = tk.IntVar(
            self, self.global_variables.editing_configuration.deg)

        self.poly_deg_label = tk.Label(self, textvariable=self.poly_deg_var)
        self.left_button = ttk.Button(
            self, text="降低维度", command=self.reduce_deg)
        self.right_button = ttk.Button(
            self, text="增加维度", command=self.increase_deg)
        self.parameters_control = ConfigurationParametersAliasArea(
            self, self.global_variables)

        self.poly_deg_label.place(x=140, y=70)
        self.left_button.place(x=10, y=70)
        self.right_button.place(x=200, y=70)
        self.parameters_control.place(x=0, y=100)


class ConfigurationFunctionSQArea(ConfigurationFunctionArea):
    def __init__(self, parent, global_variables):
        super().__init__(parent, global_variables)

    def extra(self):
        self.parameters_control = ConfigurationParametersAliasArea(
            self, self.global_variables)
        self.parameters_control.place(x=0, y=100)


class ConfigurationWindow(SubWindow):
    def __init__(self, global_variables):
        super().__init__(global_variables)

    def setup(self):
        self.title("数据类型设置")
        self.geometry("300x400")
        editing: DataConfiuration = self.global_variables.editing_configuration
        self.name_var = tk.StringVar(self, editing.name)
        self.keys_list = list(uid_inv.keys())

        self.name_label = tk.Label(self, text="名称")
        self.name_input = ttk.Entry(self, textvariable=self.name_var)
        self.fit_label = tk.Label(self, text="拟合函数类型")
        self.fit_combobox = ttk.Combobox(
            self, values=self.keys_list, state="readonly")
        self.submit_button = ttk.Button(
            self, text="确定", command=self.submit_change)
        self.cancel_button = ttk.Button(
            self, text="取消", command=self.discard_change)

        if editing.fit_object == PolyFit:
            self.function_area = ConfigurationFunctionPolyArea(
                self, self.global_variables)
        else:
            self.function_area = ConfigurationFunctionSQArea(
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
            self.function_area = ConfigurationFunctionPolyArea(
                self, self.global_variables)
        else:
            self.function_area = ConfigurationFunctionSQArea(
                self, self.global_variables)

    def discard_change(self):
        self.destroy()

    def submit_change(self):
        self.global_variables.editing_configuration.name = self.name_var.get()
        self.global_variables.editing_configuration.parameter_names = self.function_area.parameters_control.list_raw[
            :]
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
        self.destruoy()


class DataInputArea(tk.Frame):
    data_index = -1
    data = []
    stated = []
    events = []
    activated = 0

    def __init__(self, parent, global_variables):
        self.global_variables: GlobalVars = global_variables
        super().__init__(parent)
        self.place(x=410, y=40)
        self.setup()

    def get_xy(self):
        x = 0
        y = 0
        try:
            x = float(self.x_var.get())
        except:
            pass
        try:
            y = float(self.y_var.get())
        except:
            pass
        return (x, y)

    def save_index(self):
        if self.data_index >= 0:
            self.data[self.data_index] = self.get_xy()

    def append_to_end(self):
        self.data.append((0, 0))
        self.data_index = len(self.data) - 1
        self.events[0]()
        self.activate()

    def activate(self):
        if self.activated:
            return
        self.activated = 1
        for item in self.stated:
            item.config(state="normal")

    def deactivate(self):
        if not self.activated:
            return
        self.activated = 0
        for item in self.stated:
            item.config(state="disabled")

    def go_to_next(self):
        # no update requirements for listbox
        if len(self.data) == self.data_index + 1:
            self.data.append((0, 0))
        self.data_index += 1

    def update_to_index(self, index):
        self.data_index = index
        self.activate()
        self.x_var.set(str(self.data[index][0]))
        self.y_var.set(str(self.data[index][1]))
        print("call")

    def bind_events(self, events):
        self.events = events[:]

    def setup(self):
        self.config(background="red", height=240, width=160)
        using_configuration = self.global_variables.configurations[
            self.global_variables.using_index]
        self.data = self.global_variables.data[:]
        self.x_var = tk.StringVar(self)
        self.y_var = tk.StringVar(self)

        self.x_label = tk.Label(self, text=using_configuration.labels[0])
        self.y_label = tk.Label(self, text=using_configuration.labels[1])
        self.x_input = tk.Entry(
            self, textvariable=self.x_var, state="disabled")
        self.y_input = tk.Entry(
            self, textvariable=self.y_var, state="disabled")

        self.append_button = ttk.Button(
            self, text="新建", command=self.append_to_end)
        self.save_and_next_button = ttk.Button(
            self, text="保存并下一个", state="disabled")
        self.submit_button = ttk.Button(self, text="保存", state="disabled")
        self.delete_button = ttk.Button(self, text="删除", state="disabled")

        self.stated = [
            self.x_input, self.y_input, self.save_and_next_button, self.submit_button, self.delete_button
        ]

        self.x_label.place(x=0, y=0)
        self.x_input.place(x=20, y=0)
        self.y_label.place(x=0, y=30)
        self.y_input.place(x=20, y=30)
        self.save_and_next_button.place(x=0, y=70)
        self.append_button.place(x=0, y=100)
        self.submit_button.place(x=0, y=130)
        self.delete_button.place(x=0, y=160)


class DataListBoxArea(tk.Frame):
    events = []

    def __init__(self, parent, global_variables):
        self.global_variables: GlobalVars = global_variables
        super().__init__(parent)
        self.place(x=10, y=40)
        self.setup()

    def update_list(self):
        self.data_raw = []
        for d in self.events[1]:
            x, y = d
            self.data_raw.append("(%.4f,%.4f)" %(x,y))
        self.data_var.set(self.data_raw)

    def handle_change(self, _=None):
        idxs = self.data_listbox.curselection()
        if len(idxs) == 1:
            idx = int(idxs[0])
            self.events[0](idx)

    def setup(self):
        self.config(background="red", height=250, width=400)
        self.data_raw = []
        self.data_var = tk.StringVar(self, self.data_raw)
        self.data_listbox = tk.Listbox(
            self, listvariable=self.data_var, width=50, height=13)
        self.scroll_bar = ttk.Scrollbar(self, command=self.data_listbox.yview)
        self.data_listbox.config(yscrollcommand=self.scroll_bar.set)
        self.data_listbox.bind("<Double-1>",self.handle_change)

        self.data_listbox.grid(
            column=0, row=0, sticky=(tk.N, tk.W, tk.E, tk.S))
        self.scroll_bar.grid(column=1, row=0, sticky=(tk.N, tk.S))
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

    def bind_events(self, events):
        self.events = events[:]


class DataWindow(SubWindow):
    def __init__(self, global_variables):
        super().__init__(global_variables)

    def setup(self):
        self.geometry("600x300")
        self.title("编辑数据")
        self.edition_label = tk.Label(self, text="实验数据")
        self.edition_listbox_frame = DataListBoxArea(
            self, self.global_variables)
        self.edition_input_frame = DataInputArea(self, self.global_variables)

        self.edition_listbox_frame.bind_events(
            [self.edition_input_frame.update_to_index,self.edition_input_frame.data])
        self.edition_input_frame.bind_events(
            [self.edition_listbox_frame.update_list])

        self.edition_label.place(x=10, y=10)

    def bind_events(self, events):
        self.events = events[:]


class ControlArea(tk.Frame):
    events = []
    data_window_flag = 0
    configuration_window_flag = 0

    def __init__(self, parent, global_variables):
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
        self.data_label = tk.Label(self, text="实验数据")
        self.data_button = ttk.Button(
            self, text="编辑数据", command=self.create_data_window)

        self.combo_box.config(
            values=(all_confs + ["新建数据类型"]), state="readonly")
        self.combo_box.current(0)
        self.combo_box.bind("<<ComboboxSelected>>", self.on_combo_box_change)
        self.combo_box_label.place(x=20, y=20)
        self.combo_box.place(x=20, y=50)
        self.conf_button.place(x=200, y=50)
        self.data_label.place(x=400, y=20)
        self.data_button.place(x=400, y=50)

    def create_data_window(self):
        if self.data_window_flag:
            return
        self.data_window_flag = 1

        self.data_window = DataWindow(self.global_variables)

        while self.data_window_flag:
            self.data_window.update()
            try:
                if not self.data_window.winfo_exists():
                    self.data_window_flag = 0
            except:
                self.data_window_flag = 0

    def update_all(self):
        all_confs = [i.name for i in self.global_variables.configurations]
        self.combo_box.config(
            values=(all_confs + ["新建数据类型"]), state="readonly")

    def do_conf(self):
        idx = self.combo_box.current()
        self.global_variables.editing_index = idx
        self.global_variables.editing_configuration = self.global_variables.configurations[
            idx]
        if self.configuration_window_flag:
            return
        self.configuration_window = ConfigurationWindow(
            self.global_variables)
        self.configuration_window_flag = 1
        while self.configuration_window_flag:
            self.configuration_window.update()
            try:
                if not self.configuration_window.winfo_exists():
                    self.configuration_window_flag = 0
            except:
                self.configuration_window_flag = 0
        self.update_all()
        self.combo_box.current(idx)

    def bind_events(self, events):
        self.events = events[:]

    def on_combo_box_change(self, _):
        if self.configuration_window_flag:
            return
        length = len(self.combo_box["value"])
        if (self.combo_box.current() + 1) == length:
            self.global_variables.editing_index = -1
            self.combo_box.current(0)
            self.global_variables.editing_configuration = new_configuration.copy()
            self.configuration_window = ConfigurationWindow(
                self.global_variables)
            self.configuration_window_flag = 1
            while self.configuration_window_flag:
                self.configuration_window.update()
                try:
                    if not self.configuration_window.winfo_exists():
                        self.configuration_window_flag = 0
                except:
                    self.configuration_window_flag = 0
            self.update_all()
        else:
            idx = self.combo_box.current()
            self.global_variables.using_index = idx
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

        self.lift()


if __name__ == "__main__":
    window = App()
    window.mainloop()
