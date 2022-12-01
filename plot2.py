import numpy as np
import matplotlib.pyplot as plt

plt.axis([0, 1000, 0, 1])

for i in range(1000):
    y = np.random.random()
    plt.scatter(i, y)
    plt.pause(0.05)

plt.show()