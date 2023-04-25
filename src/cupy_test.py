import numpy as np
import cupy as cp

if __name__ == '__main__':
    arr1 = np.array([1, 2, 3])
    arr2 = cp.array(arr1)
    print('numpy', np.sum(arr1))
    print('cupy', cp.sum(arr2))