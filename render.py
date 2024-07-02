import numpy as np
import gym
from gym import spaces
import ipywidgets as widgets
from IPython.display import display

class GridRender:
    def __init__(self, grid_size, start, end, obstacles, state):
        self.grid_size = grid_size
        self.start = start
        self.end = end
        self.obstacles = obstacles
        self.state = state
        self.episode = 0
        self.cell_size = 40  # grid size
        
        # Canvas
        self.output = widgets.Output()
        self.episode_label = widgets.Label(f"Episode: {self.episode}")
        self.vbox = widgets.VBox([self.episode_label, self.output])
        display(self.vbox)
        
    def update_labels(self, episode):
        self.episode = episode 
        self.episode_label.value = f"Episode: {self.episode}"

    def render(self):
        with self.output:
            self.output.clear_output(wait=True)
            import matplotlib.pyplot as plt
            import matplotlib.patches as patches

            fig, ax = plt.subplots(figsize=(self.grid_size[1] * 0.4, self.grid_size[0] * 0.4))
            ax.set_xlim(0, self.grid_size[1])
            ax.set_ylim(0, self.grid_size[0])
            ax.set_xticks(np.arange(0, self.grid_size[1], 1))
            ax.set_yticks(np.arange(0, self.grid_size[0], 1))
            ax.grid(True)

            for i in range(self.grid_size[0]):
                for j in range(self.grid_size[1]):
                    color = "white"
                    if (i, j) in self.obstacles:
                        color = "black"
                    elif (i, j) == self.start:
                        color = "green"
                    elif (i, j) == self.end:
                        color = "red"
                    elif (i, j) == self.state:
                        color = "blue"
                    rect = patches.Rectangle((j, self.grid_size[0] - i - 1), 1, 1, linewidth=1, edgecolor='black', facecolor=color)
                    ax.add_patch(rect)
            
            plt.gca().invert_yaxis()
            plt.show()