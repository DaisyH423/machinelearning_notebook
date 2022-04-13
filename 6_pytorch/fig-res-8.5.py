import torch
import numpy as np
from torch import nn
from torch.autograd import Variable
import torch.nn.functional as F
import matplotlib.pyplot as plt
import matplotlib as mpl

plt.rcParams['font.sans-serif']=['SimHei']
plt.rcParams['axes.unicode_minus'] = False

#%matplotlib inline
np.random.seed(1)
m = 400 # 样本数量
N = int(m/2) # 每一类的点的个数
D = 2 # 维度
x = np.zeros((m, D))
y = np.zeros((m, 1), dtype='uint8') # label 向量， 0 表示红色， 1 表示蓝色
a = 4

criterion = nn.BCEWithLogitsLoss()

# 生成两类数据
for j in range(2):
    ix = range(N*j,N*(j+1))
    t = np.linspace(j*3.12,(j+1)*3.12,N) + np.random.randn(N)*0.2 # theta
    r = a*np.sin(4*t) + np.random.randn(N)*0.2 # radius
    x[ix] = np.c_[r*np.sin(t), r*np.cos(t)]
    y[ix] = j


def plot_decision_boundary(model, x, y):
    # Set min and max values and give it some padding
    x_min, x_max = x[:, 0].min() - 1, x[:, 0].max() + 1
    y_min, y_max = x[:, 1].min() - 1, x[:, 1].max() + 1 
    h = 0.01
    # Generate a grid of points with distance h between them
    xx, yy = np.meshgrid(np.arange(x_min, x_max, h), np.arange(y_min,y_max, h))    

    # Predict the function value for the whole grid .c_ 按行连接两个矩阵，左右相加。
    Z = model(np.c_[xx.ravel(), yy.ravel()])
    Z = Z.reshape(xx.shape)
    # Plot the contour and training examples
    plt.contourf(xx, yy, Z, cmap=plt.cm.Spectral)
    plt.ylabel("x2")
    plt.xlabel("x1")
    for i in range(m):
        if y[i] == 0:
            plt.scatter(x[i, 0], x[i, 1], marker='8',c=0, s=40, cmap=plt.cm.Spectral)
        else:
            plt.scatter(x[i, 0], x[i, 1], marker='^',c=1, s=40)

#尝试用逻辑回归解决
x = torch.from_numpy(x).float()
y = torch.from_numpy(y).float()


# Sequential
seq_net = nn.Sequential(
    nn.Linear(2, 4), # PyTorch 中的线性层， wx + b
    nn.Tanh(),
    nn.Linear(4, 1)
)

# 序列模块可以通过索引访问每一层
seq_net[0] # 第一层

# 打印出第一层的权重
w0 = seq_net[0].weight
print(w0)


# 通过 parameters 可以取得模型的参数
param = seq_net.parameters()
# 定义优化器
optim = torch.optim.SGD(param, 1.)

# 训练 10000 次
for e in range(10000):
    # 网络正向计算
    out = seq_net(Variable(x))
    # 计算误差
    loss = criterion(out, Variable(y))
    # 反向传播、 更新权重
    optim.zero_grad()
    loss.backward()
    optim.step()
    # 打印损失
    if (e + 1) % 1000 == 0:
        print('epoch: {}, loss: {}'.format(e+1, loss.item()))


def plot_seq(x):
    out = F.sigmoid(seq_net(Variable(torch.from_numpy(x).float()))).data.numpy()
    out = (out > 0.5) * 1
    return out

plot_decision_boundary(lambda x: plot_seq(x), x.numpy(), y.numpy())
mpl.rcParams['font.family'] = 'SimHei' 
plt.rcParams['axes.unicode_minus'] = False 

# plt.title('序列化网络')  
# plt.savefig('fig-res-8.5.pdf')
plt.title('模块定义网络')  
plt.savefig('fig-res-8.6.pdf')
plt.show()
torch.save(seq_net, 'save_seq_net.pth')