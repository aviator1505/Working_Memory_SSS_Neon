# real_time_viz.py
# visualization/real_time_viz.py
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import time
import numpy as np


class ExperimentVisualizer:
    def __init__(self, experiment):
        self.exp = experiment
        self.fig = plt.figure(figsize=(15, 10))
        self.setup_plots()
        self.time_window = 5.0
        self.history = self._initialize_history()

    def setup_plots(self):
        gs = self.fig.add_gridspec(3, 2)
        self.gaze_ax = self.fig.add_subplot(gs[0, 0])
        self.head_ax = self.fig.add_subplot(gs[0, 1])
        self.chest_ax = self.fig.add_subplot(gs[1, :])
        self.mobile_ax = self.fig.add_subplot(gs[2, :])

    def _initialize_history(self):
        return {
            'times': {loc: [] for loc in ['gaze', 'head', 'chest', 'mobile']},
            'data': {loc: defaultdict(list) for loc in ['gaze', 'head', 'chest', 'mobile']}
        }

    def update(self, frame):
        current_time = time.time()
        self._update_data()
        self._update_plots(current_time)

    def _update_data(self):
        for location, queue in self.exp.data_queues.items():
            while not queue.empty():
                data = queue.get()
                self.history['times'][location].append(data['timestamp'])
                for key, value in data.items():
                    if key != 'timestamp':
                        self.history['data'][location][key].append(value)

    def _update_plots(self, current_time):
        self._plot_gaze(current_time)
        self._plot_head_motion(current_time)
        self._plot_body_motion(current_time)

    def start(self):
        self.anim = FuncAnimation(self.fig, self.update, interval=100)
        plt.show()