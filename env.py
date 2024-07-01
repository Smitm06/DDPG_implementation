import gym
from gym import spaces
import numpy as np
from render import GridRender
class GridWorldEnv(gym.Env):
    def __init__(self, grid_size, start, end, obstacles):
        super(GridWorldEnv, self).__init__()
        self.grid_size = grid_size
        self.start = start
        self.end = end
        self.obstacles = obstacles
        self.state = start

        
        self.action_space = spaces.Discrete(4)  # 4 actions: up, down, left, right
        self.observation_space = spaces.Box(low=0, high=max(grid_size), shape=(2,), dtype=int)
        
        self.renderer = GridRender(grid_size, start, end, obstacles, self.state)

    def reset(self, episode):
        self.state = self.start
        self.renderer.update_labels(episode)
        return np.array(self.state, dtype=int)

    def step(self, action):
        x, y = self.state
        if action == 0 and y < self.grid_size[1] - 1:  # Up
            y += 1
        elif action == 1 and y > 0:  # Down
            y -= 1
        elif action == 2 and x > 0:  # Left
            x -= 1
        elif action == 3 and x < self.grid_size[0] - 1:  # Right
            x += 1

        next_state = (x, y)

        # Calculate reward
        current_distance = abs(x - self.end[0]) + abs(y - self.end[1])
        new_distance = abs(x - self.end[0]) + abs(y - self.end[1])  

        # Calculate reward
        if next_state in self.obstacles:
            reward = -1  
            done = True
        elif next_state == self.end:
            reward = 10 
            done = True
        else:
            if new_distance > current_distance:
                reward = -1 
            else:
                reward = -0.1  
            done = False
    
        self.state = next_state
        return np.array(self.state, dtype=int), reward, done, {}

    def render(self):
        self.renderer.state = self.state  # Update the current state in the renderer
        self.renderer.render() 