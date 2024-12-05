# analysis_viz.py
# visualization/analysis_viz.py
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np


class DataVisualizer:
    def __init__(self, data_path):
        self.data = pd.read_csv(data_path)

    def plot_gaze_patterns(self):
        fig, axes = plt.subplots(3, 1, figsize=(12, 15))
        for i, posture in enumerate(['sit', 'stand', 'swivel']):
            posture_data = self.data[self.data['posture'] == posture]
            sns.scatterplot(data=posture_data, x='gaze_x', y='gaze_y',
                            hue='angle', ax=axes[i])
            axes[i].set_title(f'Gaze Patterns - {posture}')
        plt.tight_layout()
        return fig

    def plot_motion_summary(self):
        fig, axes = plt.subplots(2, 2, figsize=(15, 15))
        metrics = ['pitch', 'roll', 'yaw']
        for i, location in enumerate(['head', 'chest']):
            for j, metric in enumerate(metrics):
                sns.boxplot(data=self.data, x='posture', y=f'{location}_{metric}',
                            hue='angle', ax=axes[i][j])
        plt.tight_layout()
        return fig