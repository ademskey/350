
import unittest
from project import *
'''
Testing for the project code. This tests graph create, even and prime set creation, and BDD's created.
Checks the assignment PDF test questions as well as Question 3.
'''

class testing_bdd(unittest.TestCase):
    def setUp(self):
        # Set the letters to be used for bool variables (y for prime, x for even)
        self.y = 'y'  
        self.x = 'x'

        # Generate the EVEN and PRIME sets
        self.even_list = make_even_list()
        self.prime_list = make_prime_list()

        # Ged BDD's for Graph, EVEN, PRIME sets
        self.graph = create_graph()  # Create the graph matrix from the lists of bdd variables (uses the %32 logic for edges in the graph)
        self.prime_set_bdd = node_set_to_bdd(self.prime_list, 'y') # Convert the prime list to a BDD
        self.even_set_bdd = node_set_to_bdd(self.even_list, 'x')  # Convert the even list to a BDD

        # Create the RR
        self.rr = graph_to_expressions(self.graph)  # Create the expressions from the graph made in setup
        self.rr = combine_expressions(self.rr)       # Combine the expressions to a single expression RR = BDD grom graph

        # Create RR2 and RR2star RR2 = RR o RR
        self.rr2 = rr_to_rr2(self.rr)                 # Create the rr2 from the rr
        self.rr2star = transitive_closure(self.rr2)   # Create the rr2star from the rr2
        # RR2star = reachability in positive and even # of steps

    def test_create_graph(self):
        # Check if the graph is created correctly
        self.assertEqual(len(self.graph), 32)
        self.assertEqual(len(graph[0]), 32)

        # Check if the graph has correct edge
        self.assertTrue(graph[3][0])

    def test_EVENS(self):
        # Check if 14 is an even number (should be true)
        self.assertTrue(find_node(self.even_set_bdd, 14, 'x'))

        # Check if 13 is an even number (should be false)
        self.assertFalse(find_node(self.even_set_bdd, 13, 'x'))

    def test_PRIMES(self): 
        # Check if 7 is a prime number (should be true)
        self.assertTrue(find_node(self.prime_set_bdd, 7, 'y'))

        # Check if 2 is a prime number (should be false)
        self.assertFalse(find_node(self.prime_set_bdd, 2, 'y'))

    def test_RR(self):
        # Turn the given graph into a BDD
        rr = graph_to_expressions(self.graph)
        rr = combine_expressions(rr)

        # Search BDD for RR with edge 27, 3 (should be true)
        self.assertTrue(search_bdd(self.rr, 27, 3))

        # Search BDD for RR with edge 16, 20 (should be false)
        self.assertFalse(search_bdd(self.rr, 16, 20))
    
    def test_RR2(self):
        # Search BDD for RR2 with edge 27, 6 (shold be true)
        self.assertTrue(search_bdd(self.rr2, 27, 6))

        # Search BDD for RR2 with edge 27, 9 (should be false)
        self.assertFalse(search_bdd(self.rr2, 27, 9))

    '''
    3.A. Graded on correctness and clarity, No explicit graph search.
    Every finite set can be coded as a BDD. Please write a Python program to decide whether the following is true:
    (StatementA) for each node u in [prime], there is a node v in [even] such that u can reach v
    in a positive even number of steps.
    '''
    def test_question3_statement_A(self):
        # !!! STEP 1: Graph BDD, RR, RR2, and RR2star have been created in the setup (Other tests for EVEN, PRIME, RR, RR2) !!!

        # for each node u in [prime], there is a node v in [even] such that u can reach v in a positive even number of steps.
        # Vu. (prime(u) -> exists(v).(even(v) ^ RR2star(u,v)))
        # where U = xx1-xx5            # where V = yy1-yy5
            
        # Bannana Step! Find if there is a node in the prime set that can reach a node in the even set in an even number of steps
        even_nodes_steps = self.even_set_bdd & self.rr2star # AND operator between evenbdd & rr2star
        vars_y = set_bddvars(self.y, 5)

        # Bad Apple Step! Eliminate existential quantifiers over YY1-YY5
        some_v = even_nodes_steps.smoothing(vars_y)  # some_v becomes nodes smoothed out over the set of Y variables 

        # Fish Step! PRIME BDD implies Bad Apple
        # logical equivalent of -> ("if then") == (~A | B) (Philosiphy 201)
        if_prime_then_v = ~self.prime_set_bdd | some_v  # eliminate universal quantifier by negating and ORing

        # Result Step! For all (XX1-XX5)Fish 
        # eliminate universal quantifier
        vars_x = set_bddvars(self.x, 5)  

         # For every == ~Exists~ (Math 216)
        # ~(~Exists in XX1-XX5) ~BDD over X variables == ~(~BDD over X variables).smoothing(X variables)
        result = ~((~if_prime_then_v).smoothing(vars_x))

        self.assertTrue(result) # Check if the result is true

if __name__ == '__main__':
    unittest.main()