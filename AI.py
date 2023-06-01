# experience replay to be able to refer to important experiences which occur only once in life
# Deep Q learning
# Interaction is WAD keys

import os
import random
import torch
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim


class ExperienceReplay:

    def __init__(self, size):
        self.size = size

        # memory is list of tuples containing error and the memory
        self.memory = []

    def add_to_memory(self, memory_inst):
        r"""

        :param memory_inst: has the previous state, previous reward, current state and previous action and the (error?)
        :return:
        """

        self.memory.append(memory_inst)

        # if self.size > len(self.memory):
        # implement deletion logic
        # todo select experience with least "surprise" or divergence from actual. i.e. the error is lowest

    def get_exp_replay(self, batch_size):
        samples = zip(*random.sample(self.memory, batch_size))
        return map(lambda x: torch.cat(x, 0), samples)


class Network(nn.Module):
    r"""
    Network represents one layer structure ???

    input_size is the number of inputs being fed to brain/NN
    output_size is the number of outputs of the NN

    There are 6 inputs or radars
    In this case there are only 3 actions - accel or turn in either direction
    """

    def __init__(self, input_size, output_size):
        super(Network, self).__init__()
        self.input_size = input_size
        self.output_size = output_size
        self.full_connect_input_hidden1 = nn.Linear(input_size, 10)
        self.full_connect_hidden_output = nn.Linear(10, output_size)
        # full here means all inputs connected to all hidden layer neurons
        # FCNN implies a linear connection of all neurons to the neurons of th next layer

    def forward(self, state):
        r"""
        forward(self, state) will determine the activation function; in this case a non linear transformation applied
        -> on the linear transformation of input through use of weights

            The activation function for hidden layer is RELU and the activation for output layer is linear

            Later Softmax is intended to be used to get the best output with some stochasticity in choice for better
            learning possibilities
        """
        hidden = F.relu(self.full_connect_input_hidden1(state))
        output_q_values = self.full_connect_hidden_output(hidden)
        return output_q_values


class DeepQLearn:

    def __init__(self, input_size, output_size, gamma):
        r"""
        memory for exp replay
        gamma is time discounting
        reward_window is list of last n rewards to get a mean of them to evaluate performance
            last action
            last reward
            last state
        """

        self.gamma = gamma
        self.reward_window = []
        self.model = Network(input_size, output_size)
        self.memory = ExperienceReplay(100000)
        self.optimizer = optim.Adam(self.model.parameters(), lr=0.001)
        # optimizer is responsible for updating weights of the model
        # Adaptive moments is used instead of stochastic gradient descent to allow for variable learning rates
        # initial rate matters as it affects output before being changed

        self.last_state = torch.Tensor(input_size).unsqueeze(0)
        self.last_action = 0
        # Indice of array storing degrees by which to rotate car

        self.last_reward = 0

    def select_action(self, state):
        # Using softmax to calculate the probability of the best choice
        # depending on Q values and randomly selecting at times for a
        # better path in long term than in higher q value in short term
        probs = F.softmax(self.model.forward(state) * 3)
        # 7 to magnify the pre softmax q values to give more
        # weight to higher q value when softmax uses natural number
        # exponents

        action = probs.multinomial(num_samples=1)

        # 2 dim reference in 1 dim
        # [x, y] is [y][x]
        return action.data[0, 0]

    def learn(self, batch_state, batch_next_state, batch_reward, batch_action):
        outputs = self.model(batch_state).gather(1, batch_action.unsqueeze(1)).squeeze(1)
        # nth (n=1) position of each batch of output of self.model which predicts Q values for batch_state as input
        # internally the magic method allowing calling of an object also calls feed forward
        # batch state 1th index is now populated by batch_action
        # 1 is fake dimension for tensor format -> vector segregation needs that dim
        # TODO-> Look at input and find tensor format for forward and backward transformation

        next_outputs = self.model(batch_next_state).detach().max(1)[0]
        # action is specified by index 1 here
        # The next states are recorded at 0th index so

        target = batch_reward + self.gamma * next_outputs

        temporal_difference_loss = F.huber_loss(outputs, target)

        self.optimizer.zero_grad()
        # https://stackoverflow.com/questions/48001598/why-do-we-need-to-call-zero-grad-in-pytorch

        temporal_difference_loss.backward(retain_graph=True)

        self.optimizer.step()
        # Add batch gradient changes to global changes and actually
        # change weights acc to gradients determined by this mini batch

    def update(self, reward, observation):

        new_state = torch.Tensor(observation).float().unsqueeze(0)

        # self.select_action called
        action = self.select_action(new_state)

        self.memory.add_to_memory(
            (self.last_state, new_state, torch.LongTensor([int(self.last_action)]), torch.Tensor([self.last_reward])))

        if len(self.memory.memory) > 100:
            batch_state, batch_next_state, batch_action, batch_reward = self.memory.get_exp_replay(100)

            # self.learn called
            self.learn(batch_state, batch_next_state, batch_reward, batch_action)

        self.last_action = action
        self.last_state = new_state
        self.last_reward = reward
        self.reward_window.append(reward)
        if len(self.reward_window) > 1000:
            del self.reward_window[0]
        return action

    def score(self):
        return sum(self.reward_window) / (len(self.reward_window) + 1.)

    def save(self):
        torch.save({'state_dict': self.model.state_dict(),
                    'optimizer': self.optimizer.state_dict(),
                    }, 'last_brain.pth')

    def load(self, name):
        if os.path.isfile(name):
            print("=> loading checkpoint... ")
            checkpoint = torch.load(name)
            self.model.load_state_dict(checkpoint['state_dict'])
            self.optimizer.load_state_dict(checkpoint['optimizer'])
            print("done !")
        else:
            print("no checkpoint found...")
