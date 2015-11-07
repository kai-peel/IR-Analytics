__author__ = 'kai'
import numpy as np


def main():
    #a = np.array([[1, 1], [3, 4], [2, 9]])
    #print np.std(a)
    #print np.std(a, axis=0)
    #print np.std(a, axis=1)
    r = np.histogram([10, 20, 10], bins=2)
    print r

if __name__ == '__main__':
    main()