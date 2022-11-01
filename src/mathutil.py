import numpy as np
import random
import matplotlib.pyplot as plt
from scipy.optimize import leastsq


def eq_fun(no_p, x):
    return x

np.seterr(all='raise') # strict mode
class FitFunction(object):
    parameter_count = 0
    best_parameters = []

    def __init__(self) -> None:
        raise NotImplementedError("FitFunction Not Implemented.")

    def do_fit(self, x, y):
        raise NotImplementedError("FitFunction.dofit Not Implemented.")

    def f(self, x):
        raise NotImplementedError("FitFunction.f Not Implemented.")


class LeastSQFunction(FitFunction):
    fun = eq_fun
    parameter_count = 0

    def __init__(self):
        raise NotImplementedError("LeastSQFunction Not Implemented.")

    def error(self, parameters, x, y):
        return self.fun(parameters, x) - y

    def do_fit(self, input_x, input_y):
        init_para = [random.random() for _ in range(self.parameter_count)]
        best_parameters = leastsq(
            self.error, init_para, args=(input_x, input_y))
        self.best_parameters = best_parameters[0]

    def f(self, x):
        return self.fun(self.best_parameters, x)

    def test(self, noise_rate=2):
        x = np.linspace(-100, 100, 100)
        raw_p = [random.random() for _ in range(self.parameter_count)]
        noise = np.random.randn(len(x))
        y = self.fun(raw_p, x) + noise * noise_rate
        self.do_fit(x, y)
        y_fitted = self.f(x)
        plt.plot(x, y, 'xr', label='Original')
        plt.plot(x, y_fitted, '-b', label='Fitted')
        plt.legend()
        plt.show()


class PolyFit(FitFunction):
    def __init__(self, deg):
        self.deg = deg
        self.parameter_count = deg + 1
        self.fun = lambda x: x
        self.best_parameters = []

    def do_fit(self, x, y):
        self.best_parameters = np.polyfit(x, y, self.deg)
        self.fun = np.poly1d(self.best_parameters)

    def f(self, x):
        return self.fun(x)

    def test(self, noise_rate=2):
        x = np.linspace(-100, 100, 100)
        raw_p = [random.random() for _ in range(self.parameter_count)]
        noise = np.random.randn(len(x))
        y = np.poly1d(raw_p)(x) + noise * noise_rate
        self.do_fit(x, y)
        y_fitted = self.f(x)
        plt.plot(x, y, 'xr', label='Original')
        plt.plot(x, y_fitted, '-b', label='Fitted')
        plt.legend()
        plt.show()


class LinearFuncSQ(LeastSQFunction):
    parameter_count = 2

    def __init__(self) -> None:
        def func(p, x):
            k, b = p
            return k * x + b
        self.fun = func


class QuadraticFuncSQ(LeastSQFunction):
    parameter_count = 3

    def __init__(self) -> None:
        def func(p, x):
            a, b, c = p
            return a * x * x + b * x + c
        self.fun = func


class ExponentialFuncSQ(LeastSQFunction):
    parameter_count = 1

    def __init__(self):
        def func(p, x):
            a = p[0]
            return a ** x
        self.fun = func

    def test(self, noise_rate=1):
        x = np.linspace(-1, 10, 100)
        raw_p = [np.abs(random.random()) * 1.5]
        noise = np.random.randn(len(x))
        y = self.fun(raw_p, x) + noise * noise_rate
        self.do_fit(x, y)
        y_fitted = self.f(x)
        plt.plot(x, y, 'xr', label='Original')
        plt.plot(x, y_fitted, '-b', label='Fitted')
        plt.legend()
        plt.show()


class InverseProportionalFunctionSQ(LeastSQFunction):
    parameter_count = 1

    def __init__(self):
        def func(p, x):
            a = p[0]
            return a / x
        self.fun = func

    def test(self, noise_rate=1):
        x = np.array([random.random() * 10 + 0.1 for _ in range(100)])
        x.sort()
        raw_p = [random.random() * 10 for _ in range(self.parameter_count)]
        noise = np.random.randn(len(x))
        y = self.fun(raw_p, x) + noise * noise_rate
        self.do_fit(x, y)
        x_range = np.linspace(min(x), max(x), 100)
        y_fitted = self.f(x_range)
        plt.plot(x, y, 'xr', label='Original')
        plt.plot(x_range, y_fitted, '-b', label='Fitted')
        plt.legend()
        plt.show()


unique_id = {
    "ad930572090434f024956f160be121e0": PolyFit,
    "fa5e3fcdb39bcd9157b809e3ca772214": LinearFuncSQ,
    "8bc00d0d94cb6b59d081fe37b346334a": QuadraticFuncSQ,
    "ad4fdb2b91c73cba3b0f4a1342dc587f": ExponentialFuncSQ,
    "3a91c05ee48915fffee93a85e99eefdf": InverseProportionalFunctionSQ,
}

uid_inv = {}
for key in unique_id:
    uid_inv[unique_id[key].__name__] = key

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        inp = int(sys.argv[1])
    else:
        inp = int(input("test type >> "))
    if inp == 0:
        least_linar_func_obj = LinearFuncSQ()
        least_linar_func_obj.test()
    elif inp == 1:
        poly_linar_func_obj = PolyFit(1)
        poly_linar_func_obj.test()
    elif inp == 2:
        least_quadratic_func_obj = QuadraticFuncSQ()
        least_quadratic_func_obj.test(100)
    elif inp == 3:
        poly_quaratic_func_obj = PolyFit(2)
        poly_quaratic_func_obj.test(100)
    elif inp == 4:
        least_exp_func_obj = ExponentialFuncSQ()
        least_exp_func_obj.test()
    elif inp == 5:
        print(unique_id, uid_inv)
    elif inp == 6:
        inverse_proportional_func_obj = InverseProportionalFunctionSQ()
        inverse_proportional_func_obj.test()
