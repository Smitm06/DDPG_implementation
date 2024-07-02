import torch
import torch.nn as nn
import torch.optim as optim

import numpy as np

import random
from collections import deque

# Define Actor and Critic networks
class Actor(nn.Module):
    def __init__(self, state_dim, action_dim):
        super(Actor, self).__init__()
        self.layer1 = nn.Linear(state_dim, 128)
        self.layer2 = nn.Linear(128, 128)
        self.layer3 = nn.Linear(128, action_dim)
    
    def forward(self, state):
        x = torch.relu(self.layer1(state))
        x = torch.relu(self.layer2(x))
        x = torch.softmax(self.layer3(x), dim=-1)
        return x

class Critic(nn.Module):
    def __init__(self, state_dim, action_dim):
        super(Critic, self).__init__()
        self.layer1 = nn.Linear(state_dim + action_dim, 128)
        self.layer2 = nn.Linear(128, 128)
        self.layer3 = nn.Linear(128, 1)
    
    def forward(self, state, action):
        x = torch.cat([state, action], 1)
        x = torch.relu(self.layer1(x))
        x = torch.relu(self.layer2(x))
        x = self.layer3(x)
        return x

class DDPGAgent:
    def __init__(self, state_dim, action_dim, max_action, device):
        self.actor = Actor(state_dim, action_dim).to(device)
        self.actor_target = Actor(state_dim, action_dim).to(device)
        self.actor_target.load_state_dict(self.actor.state_dict())
        self.actor_optimizer = optim.Adam(self.actor.parameters(), lr=1e-3)
        
        self.critic = Critic(state_dim, action_dim).to(device)
        self.critic_target = Critic(state_dim, action_dim).to(device)
        self.critic_target.load_state_dict(self.critic.state_dict())
        self.critic_optimizer = optim.Adam(self.critic.parameters(), lr=1e-3)
        
        self.max_action = max_action
        self.replay_buffer = deque(maxlen=100000)
        self.batch_size = 64
        self.discount = 0.99
        self.tau = 0.005
        self.epsilon = 0.2  # Exploration rate
        self.device = device    
        
    def select_action(self, state, explore=True):
        state = torch.FloatTensor(state.reshape(1, -1)).to(self.device)
        if explore and np.random.rand() < self.epsilon:
            action = np.random.randint(0, 4)  # Random action
        else:
            action_probs = self.actor(state).cpu().data.numpy().flatten()
            action = np.random.choice(np.arange(len(action_probs)), p=action_probs)
        return action

    def train(self):
        if len(self.replay_buffer) < self.batch_size:
            return
        
        batch = random.sample(self.replay_buffer, self.batch_size)
        state, next_state, action, reward, done = zip(*batch)
        
        state = torch.FloatTensor(np.array(state)).to(self.device)
        next_state = torch.FloatTensor(np.array(next_state)).to(self.device)
        action = torch.LongTensor(action).to(self.device).unsqueeze(1)
        reward = torch.FloatTensor(reward).to(self.device).unsqueeze(1)
        done = torch.FloatTensor(done).to(self.device).unsqueeze(1)
        
        # One-hot encode actions
        action_one_hot = torch.zeros(self.batch_size, self.actor.layer3.out_features).to(self.device)
        action_one_hot.scatter_(1, action, 1)
        
        # Compute target Q value
        with torch.no_grad():
            next_action_probs = self.actor_target(next_state)
            next_action = next_action_probs.argmax(dim=1, keepdim=True)
            next_action_one_hot = torch.zeros(self.batch_size, self.actor.layer3.out_features).to(self.device)
            next_action_one_hot.scatter_(1, next_action, 1)
            target_q = self.critic_target(next_state, next_action_one_hot)
            target_q = reward + ((1 - done) * self.discount * target_q)
        
        # Get current Q estimate
        current_q = self.critic(state, action_one_hot.float())
        
        # Compute critic loss
        critic_loss = nn.MSELoss()(current_q, target_q)
        
        # Optimize the critic
        self.critic_optimizer.zero_grad()
        critic_loss.backward()
        self.critic_optimizer.step()
        
        # Compute actor loss
        action_probs = self.actor(state)
        action = action_probs.argmax(dim=1, keepdim=True)
        action_one_hot = torch.zeros(self.batch_size, self.actor.layer3.out_features).to(self.device)
        action_one_hot.scatter_(1, action, 1)
        actor_loss = -self.critic(state, action_one_hot.float()).mean()
        
        # Optimize the actor
        self.actor_optimizer.zero_grad()
        actor_loss.backward()
        self.actor_optimizer.step()
        
        # Soft update target networks
        for param, target_param in zip(self.critic.parameters(), self.critic_target.parameters()):
            target_param.data.copy_(self.tau * param.data + (1 - self.tau) * target_param.data)
        
        for param, target_param in zip(self.actor.parameters(), self.actor_target.parameters()):
            target_param.data.copy_(self.tau * param.data + (1 - self.tau) * target_param.data)
    
    def add_to_replay_buffer(self, state, next_state, action, reward, done):
        self.replay_buffer.append((state, next_state, action, reward, done))