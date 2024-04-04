import unittest

from project import *

class bdd_testing(unittest.testcase):

    def setUp(self):
        even_list = [2,4,6,8,10,12,14,16,18,20,22,24,26,28,30]
        self.even_bools = [True if i in even_list else False for i in range(32)]
        prime_list = [3, 5, 7, 11, 13, 17, 19, 23, 29, 31]
        self.prime_list = [True if i in prime_list else False for i in range(32)]

        self.graph = create_graph()

    

