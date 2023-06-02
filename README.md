# DQN-Reinforcement---Car
A self driving car implemented based on Deep Q Learning using PyTorch

## How-To Use
The first click will be the start point and the second click will be the endpoint
The intention is to toggle the goal when endpoint is reached and vice versa so the Agent goes back and forth

## Parameters and Structure
1. Activation function was ReLu
2. Optimization was performed using Adaptive moments since Create Path.py was used to generate many paths to train over sufficient data
3. Learning rate was 0.001 kept low initially since no progressive rewards were placed so inefficient reward gain would not be highlighted initially
4. Gamma or discounting was 0.8
5. 1 hidden layer
6. Inputs are lines of view of driver in a car
7. Non-prioritized experience replay
8. Hitbox of the car is 4 blue dots at the vertices



![image](https://github.com/Saahir999/DQN-Reinforcement---Car/assets/77979559/a83a2983-d972-477d-9639-a0958d4b4c95)



9. Best Q value chosen using softmax
10. Output is moving forward or turning in either direction -> 3 outputs to choose from

#TODO
 - [ ] using one track to train and testing learning on others
 - [ ] using multiple tracks to train and test
 - ✅ Dynamic start and endpoint
 - [ ] Prioritized experience replay with priority on the basis of higher error and latest experience also being considered
 - [ ] implement jerk to give variable accel with opposing jerk similar to velocity for better simulation (?)
 - [ ] implement greater goals like a destination and checkpoint rewards
 - ✅ feed self.angle -- greater Error
 - [ ] give penalty for turning 
 - [ ] pass differential change in radar angle as input
 - [ ] lower degree of rotation per decision
 - ✅ make rewards cumulative
 - ✅ make some radars more important by rewarding based on their inputs
