import matplotlib.pyplot as plt
import numpy as np
from IPython.core.display_functions import display
from IPython.display import clear_output
from ipywidgets import IntSlider, interactive, FloatSlider, Output


class PoissonProcessSimulator:
    def __init__(self):
        self.interval = IntSlider(value=100, min=20, max=150, step=1, description="Time")
        self.param = FloatSlider(value=1, min=0.1, max=2, step=0.1, description="λ")

        self.interactive_plot = interactive(
            self.update_plot,
            interval=self.interval,
            param=self.param,
        )

    @staticmethod
    def simulate_process(interval: int, param: float):
        segments = []
        number = 0
        while True:
            number += 1
            start_time = 0 if not segments else segments[-1][0][1]
            end_time = start_time + np.random.exponential(param)
            if end_time > interval:
                break

            segments.append([(start_time, end_time), (number, number)])
        return segments

    def update_plot(self, interval: int, param: float):
        clear_output(wait=True)
        output_plot = Output()
        with output_plot:
            plt.figure(figsize=(10, 6))
            for data in self.simulate_process(interval, param):
                plt.plot(*data)

            plt.xlabel('Time')
            plt.ylabel('N')
            plt.title(f'Poisson Process λ = {param}')
            plt.show()
        display(output_plot)


if __name__ == "__main__":
    simulator = PoissonProcessSimulator()
    display(simulator.interactive_plot)
