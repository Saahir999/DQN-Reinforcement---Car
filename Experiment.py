import torch

# ten = torch.tensor([1,2,3,4,5,6], dtype=int)
# print(ten)
# ten = ten.unsqueeze(1)
# print(ten)

from torch import tensor

torch.manual_seed(0)

num_examples = 5
num_classes = 3
scores = torch.randn(5, 3)

# print of scores
scores: tensor([[1.5410, -0.2934, -2.1788],
                [0.5684, -1.0845, -1.3986],
                [0.4033, 0.8380, -0.7193],
                [-0.4033, -0.5966, 0.1820],
                [-0.8567, 1.1006, -1.0712]])


# y = torch.LongTensor([1, 2, 1, 0, 2])

# def test(index):
#     y = torch.LongTensor([index, 0, 0, 0, 0])
#
#     res = scores.gather(-1, y.view(-1, 1)).squeeze()
#     print(res)
#
#     res = scores.gather(0, y.view(-1, 1)).squeeze()
#     print(res)
#
#     res = scores.gather(1, y.view(-1, 1)).squeeze()
#     print(res)
#     print()
#
#
# test(0)
# test(1)
# test(2)
#
#
# class Test:
#     def __init__(self, sample):
#         print("INIT")
#         print(sample)
#
#     def doit(self, var):
#         print("var")
#
#
# T = Test("Hah")
# X = T("6")
#
#
# # Sol ->  __call__ magic method used

def unsq(index):
    scores.unsqueeze(index)
    print(scores)

print(scores)
for i in range(0, 3):
    unsq(i)

radars = [(92, 300), (20, 232), (30, 443), (76, 141), ]


def data():
    # input for AI, the angles do not matter to it since all points must be collision free in any case
    input = [0, 0, 0, 0, 0, 0]
    for i, radar in enumerate(radars):
        input[i] = int(radar[1])
    print(input)
    for i, radar in enumerate(radars):
        input.append(int(radar[0]))
    return input

print(data())

