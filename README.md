# DQN-Reinforcement---Car
A self driving car implemented based on Deep Q Learning using PyTorch

1. Activation function was ReLu
2. Optimization was performed using Adaptive moments since Create Path.py was used to generate many paths to train over sufficient data
3. Learning rate was 0.001 kept low initially since no progressive rewards were placed so inefficient reward gain would not be highlighted initially
4. Gamma or discounting was 0.8
5. 1 hidden layer
6. Inputs are lines of view of driver in a car
7. Non-prioritized experience replay
![image](https://github.com/Saahir999/DQN-Reinforcement---Car/assets/77979559/a83a2983-d972-477d-9639-a0958d4b4c95)

7. Q value chosen using softmax
8. Output is moving forward or turning in either direction -> 3 outputs to choose from

#TODO
1. using one track to train and testing learning on others
2. using multiple tracks to train and test
3. Dynamic start and endpoint
4. Prioritized experience replay with priority on the basis of higher error and latest experince also being considered
5. implement jerk to give variable accel with opposing jerk similar to velocity for better simulation (?)
6. implement greater goals like a destination and checkpoint rewards
7. feed self.angle 
8. give penalty for turning 
9. pass differential change in radar
10. lower degree of rotation per decision
11. make rewards cumulative
12. make some radars more important by rewarding based on their inputs
