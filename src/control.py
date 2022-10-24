import json
from src.mathutil import *
from matplotlib.figure import Figure
import numpy as np


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


class DataConfiuration:
    configuration = {
        "fitMod": "fa5e3fcdb39bcd9157b809e3ca772214",
        "nameDefinations": {
            "x-axis-label": "t",
            "y-axis-label": "v",
            "parameters": [
                "a", "v0"
            ]
        },
        "parameters_count": 2,
        "name": "速度时间图像"
    }
    parameters_count = 0
    fit_object = LinearFuncSQ
    labels = ["x", "y"]
    parameter_names = []
    name = "未命名"

    def __init__(self):
        pass

    def load_configration_content(self, conf_dict: dict):
        if type(conf_dict) == dict:
            if conf_dict.get("fitMod") is None:
                raise ValueError("fitMod is missing")
        self.load_from_configuration()

    def load_from_configuration(self):
        self.fit_object = unique_id.get(
            self.configuration["fitMod"], LinearFuncSQ
        )
        try:
            self.parameters_count = int(self.configuration["parameters_count"])
        except:
            self.parameters_count = 0
        self.name_definations = self.configuration["nameDefinations"]
        if type(self.name_definations) != dict:
            self.name_definations = {}
        self.labels = [
            self.name_definations.get("x-axis-label", "x"),
            self.name_definations.get("y-axis-label", "y")
        ]
        self.parameter_names = [None for _ in range(self.parameters_count)]
        parameter_names_conf = self.name_definations.get("parameters", [])
        if type(parameter_names_conf) != list:
            parameter_names_conf = []
        for i in range(len(parameter_names_conf)):
            self.parameter_names[i] = str(parameter_names_conf[i])
        self.name = self.configuration.get("name", "未命名")

    def save_to_configuration(self):
        result = {
            "fitMod": uid_inv[self.fit_object.__name__],
            "nameDefinations": {
                "x-axis-label": self.labels[0],
                "y-axis-label": self.labels[1],
                "parameters": self.parameter_names
            },
            "parameters_count": self.parameters_count,
            "name": self.name
        }
        return result


default_configuration = DataConfiuration()
default_configuration.load_configration_content({
    "fitMod": "fa5e3fcdb39bcd9157b809e3ca772214",
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


class FigureControl(object):
    fit: FitFunction

    def __init__(self):
        self.figure = Figure()
        self.plot = self.figure.add_subplot()
        self.update_configuration(default_configuration)
        self.data = []  # x,y pair

    def update_configuration(self, conf: DataConfiuration):
        self.configuration = conf
        self.fit = self.configuration.fit_object()
        self.parameters = [0 for _ in range(self.fit.parameter_count)]

    def first_run(self):
        self.plot.clear()
        self.plot.set_xlabel(self.configuration.labels[0])
        self.plot.set_ylabel(self.configuration.labels[1])

    def update(self):
        if len(self.data) < self.fit.parameter_count:
            print("More data required")  # todo : event handle
            return
        x = np.array([i[0] for i in self.data])
        y = np.array([i[1] for i in self.data])
        print(type(self.fit))
        x_range = np.linspace(min(x),max(x),100)
        y_fitted = self.fit.f(x_range)
        self.plot.clear()
        self.plot.plot(x, y, 'xr')
        self.plot.plot(x_range, y_fitted, '-b')
        self.plot.set_xlabel(self.configuration.labels[0])
        self.plot.set_ylabel(self.configuration.labels[1])


class GlobalVars:
    input_set = []
    configurations = []
    editing_configuration = default_configuration

    def __init__(self):
        configurations_json = json_read(".config") or []
        for item in configurations_json:
            d = DataConfiuration()
            d.load_configration_content(item)
            self.configurations.append(d)
        if len(self.configurations) == 0:
            self.configurations = [
                default_configuration
            ]
