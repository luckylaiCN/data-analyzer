import json
from src.mathutil import *
from matplotlib.figure import Figure
import numpy as np

MIT_LICENSE_STR = """MIT License

Copyright (c) 2022 Lucky Lai

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

# MIT License 的全文，用于About窗口的文字说明


def json_read(filepath):
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            result = json.load(f)
    except:
        result = None
    return result


def json_write(filepath, obj):
    try:
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(obj, f)
        return True
    except:
        return False


class DataConfiuration: # 神奇的拟合属性配置
    configuration = {
        "fitMode": "fa5e3fcdb39bcd9157b809e3ca772214",
        "nameDefinations": {
            "x-axis-label": "x",
            "y-axis-label": "y",
            "parameters": [
                "a0", "a1"
            ]
        },
        "parameters_count": 2,
        "name": "未命名"
    }
    parameter_count = 0
    fit_object = LinearFuncSQ
    labels = ["x", "y"]
    parameter_names = []
    name = "未命名"
    deg = 1

    def __init__(self):
        pass

    def load_configuration_content(self, conf_dict: dict):
        if type(conf_dict) == dict:
            if conf_dict.get("fitMode") is None:
                raise ValueError("fitMode is missing")
        self.configuration = conf_dict.copy()
        self.load_from_configuration()

    def load_from_configuration(self):
        self.fit_object = unique_id.get(
            self.configuration["fitMode"], LinearFuncSQ
        )
        try:
            self.parameter_count = int(self.configuration["parameters_count"])
        except:
            self.parameter_count = 0
        self.name_definations = self.configuration["nameDefinations"]
        if type(self.name_definations) != dict:
            self.name_definations = {}
        self.labels = [
            self.name_definations.get("x-axis-label", "x"),
            self.name_definations.get("y-axis-label", "y")
        ]
        self.parameter_names = [
            f"a{idx}" for idx in range(self.parameter_count)]
        parameter_names_conf = self.name_definations.get("parameters", [])
        if type(parameter_names_conf) != list:
            parameter_names_conf = []
        for i in range(len(parameter_names_conf)):
            self.parameter_names[i] = str(parameter_names_conf[i])
        self.name = self.configuration.get("name", "未命名")

    def save_to_configuration(self):
        result = {
            "fitMode": uid_inv[self.fit_object.__name__],
            "nameDefinations": {
                "x-axis-label": self.labels[0],
                "y-axis-label": self.labels[1],
                "parameters": self.parameter_names
            },
            "parameters_count": self.parameter_count,
            "name": self.name
        }
        return result

    def change_fit_mode(self, fitMode, deg=None):
        self.fit_object = fitMode
        if fitMode.parameter_count == 0:
            self.deg = deg or 1
            self.parameter_count = self.deg + 1
        else:
            self.parameter_count = fitMode.parameter_count
        self.parameter_names = [
            f"a{idx}" for idx in range(self.parameter_count)]

    def reduce_deg_for_poly(self):
        self.parameter_count -= 1
        self.deg -= 1
        self.parameter_names.pop()

    def increase_deg_for_poly(self):
        self.parameter_count += 1
        self.deg += 1
        self.parameter_names.append(
            f"a{self.parameter_count-1}"
        )

    def copy(self):
        new = DataConfiuration()
        new.load_configuration_content(
            self.save_to_configuration()
        )
        return new


default_configuration = DataConfiuration()
default_configuration.load_configuration_content({
    "fitMode": "fa5e3fcdb39bcd9157b809e3ca772214",
    "nameDefinations": {
        "x-axis-label": "t",
        "y-axis-label": "v",
        "parameters": [
                        "a", "v0"
        ]
    },
    "parameters_count": 2,
    "name": "速度时间图像"
})

default_configuration2 = DataConfiuration()
default_configuration2.load_configuration_content({
    "fitMode": "fa5e3fcdb39bcd9157b809e3ca772214",
    "nameDefinations": {
        "x-axis-label": "I",
        "y-axis-label": "U",
        "parameters": [
                        "-r", "E"
        ]
    },
    "parameters_count": 2,
    "name": "电池内阻电动势性质图像"
})

new_configuration = DataConfiuration()
new_configuration.load_configuration_content({
    "fitMode": "fa5e3fcdb39bcd9157b809e3ca772214",
    "nameDefinations": {
        "x-axis-label": "x",
        "y-axis-label": "y",
        "parameters": [
            "a0", "a1"
        ]
    },
    "parameters_count": 2,
    "name": "未命名"
})


class FigureControl(object): # 图像控制
    fit: FitFunction
    events = []

    def __init__(self):
        self.figure = Figure()
        self.plot = self.figure.add_subplot()
        self.update_configuration(default_configuration)
        self.data = []  # x,y pair

    def update_configuration(self, conf: DataConfiuration):
        self.configuration = conf
        if conf.fit_object == PolyFit:
            self.fit: FitFunction = PolyFit(conf.deg)
        else:
            self.fit: FitFunction = self.configuration.fit_object()
        self.parameters = [0 for _ in range(self.fit.parameter_count)]

    def first_run(self):
        self.plot.clear()
        self.plot.set_xlabel(self.configuration.labels[0])
        self.plot.set_ylabel(self.configuration.labels[1])

    def update(self):
        if len(self.data) < self.fit.parameter_count:
            self.raise_error(f"拟合所需要的数据量不足。请输入至少{self.fit.parameter_count}项数据")
            return
        x = np.array([i[0] for i in self.data])
        y = np.array([i[1] for i in self.data])
        if type(self.fit) == InverseProportionalFunctionSQ:
            x_range = np.linspace(min(x), max(x), 100) # div0 异常的处理
        else:
            x_range = np.linspace(min(min(x),0), max(x), 100) # 因为神奇的要求把x压到0去
        try:
            self.fit.do_fit(x,y)
            y_fitted = self.fit.f(x_range)
        except Exception as e:
            self.raise_error(f"Exception Caught:\n{e}")
            return
        
        self.plot.clear()
        self.plot.plot(x, y, 'xr')
        self.plot.plot(x_range, y_fitted, '-b')
        self.plot.set_xlabel(self.configuration.labels[0])
        self.plot.set_ylabel(self.configuration.labels[1])
        self.plot.grid(axis="both")

    def raise_error(self,message):
        self.events[0](message)

    def bind_events(self,events):
        self.events = events[:]


class GlobalVars: # tk下的全局变量
    input_set = []
    configurations = []
    editing_configuration = default_configuration.copy()
    editing_index = -1
    using_index = 0
    data = []

    def __init__(self):
        configurations_json = json_read(".config") or []
        for item in configurations_json:
            d = DataConfiuration()
            d.load_configuration_content(item)
            self.configurations.append(d)
        if len(self.configurations) == 0:
            self.configurations = [
                default_configuration.copy(),
                default_configuration2.copy()
            ]

    def save_config(self):
        configurations_json = []
        for item in self.configurations:
            configurations_json.append(item.save_to_configuration())

        json_write(".config",configurations_json)
