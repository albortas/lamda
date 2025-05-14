import numpy as np

a = np.array([[1, 2, 3],
              [4, 5, 6],
              [7, 8, 9]])

b = np.array([[10, 11, 12, 13],
              [15, 16, 17, 18],
              [20, 21, 22, 23]])


c = a + b[:, 0, np.newaxis] 
d = c @ np.array([1,2,3])
e = d * 0.5
#print(b[:, 0, np.newaxis])
print(c)
print(d)
print(e)
