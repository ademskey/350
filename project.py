
from pyeda.inter import *
from pyeda.boolalg.bdd import *

'''
PROJECT FLOW:
create bdd-vars/bool-vars to represend graph nodes/edges -> create and write formulas/expressions -> convert formulas/expressions to bdd -> Operations on BDDs

Operations on BDDs:
define RR2 = RR o RR to be boolean formula in 10 vars -> 

'''
## Generate variables for use in graph conversion to BDD ###########################################################################
'''
This function takes a string variable (Either X or Y for the later PRIME and EVEN sets) 
and an integer length as input (5 for XX1-XX5 or YY1-YY5) then returns a list of BDD variables.
'''
# Define the variables X and Y for XX1-XX5 and YY1-YY5 sets (later used in PRIME and EVEN)
letter_x = 'x'
letter_y = 'y'

def set_bddvars(letter: str, length: int):  
    vars_x = []
    for i in range(length):
        var_name = f"{letter * 2}" + str(i)
        var = bddvar(var_name)
        vars_x.append(var)
    return vars_x

# generate lists of vars xx0...xx5 & yy0...yy5 with set_bddvar function
vars_x = set_bddvars(letter_x, 5)
vars_y = set_bddvars(letter_y, 5)

def make_even_list() -> list[bool]:
    even_list = []
    for i in range(32):
        if i % 2 == 0:
            even_list.append(True)
        else:
            even_list.append(False)
    return even_list


def make_prime_list() -> list[bool]:
    prime_list = [3, 5, 7, 11, 13, 17, 19, 23, 29, 31]
    result = []
    for i in range(32):
        if i in prime_list:
            result.append(True)
        else:
            result.append(False)
    return result

# Generate graph for translation to BDD ########################################################
'''
This function takes a list of BDD variables as input and then returns a BDD graph matrix.
True or False represent an edge between two nodes in the graph.
'''
def create_graph() -> list[list[bool]]:
    graph_matrix = [[False] * 32 for _ in range(32)] #set all index to false initially

    for j in range(32):
        for i in range(32):
            if (i + 3) % 32 == j % 32 or (i + 8) % 32 == j % 32:
                graph_matrix[j][i] = True
    return graph_matrix

graph = create_graph() # Create the graph matrix


# Convert graph to Expressions ###########################################################################
'''
This function uses below functions and a loop to take a boolean graph matrix as input and then
returns a list of expressions to convert to bdd.
'''
def graph_to_expressions(graph: list[list[bool]]) -> list[Expression]:
    edge_list = []
    for j in range(32):
        for i in range(32):
            if graph[j][i]:
                node_x = node_to_binexpr(i, letter_x)
                node_y = node_to_binexpr(j, letter_y)
                edge_list.append(node_x & node_y)

    return edge_list

'''
This function takes a node from edge list and transforms it into a boolean expression. 
ex. xx1 ^ ~xx2 ^ xx3 ...
'''
# Expression = Boolean expression
def node_to_binexpr(nodenum: int, letter: str) -> Expression:

    nodenum_bin = format(nodenum, 'b').rjust(5, '0') # Convert the node number to binary and fill with 0s right justified
    expr_strs = []  # List for strings of names of nodes

    for i in range(5):
        node_name = f"{2 * letter}{i}"  # Generate node name like 'Xx0'
        if int(nodenum_bin[i]):
            expr_strs.append(node_name)
        else:
            expr_strs.append(f"~{node_name}")

    expression = expr(" & ".join(expr_strs))  # Create the expression using logical AND operator
    return expression

expressions = graph_to_expressions(graph) # Create the BDD graph

## Convert Expressions to BDD ###########################################################################
'''
This function takes list of expressions generated from the graph and then combines them into a single expression to represent the BDD
'''
def combine_expressions(expr_list: list[Expression]) -> Expression:

    full_expr = expr_list[0]  # Initialize the expression with the first expression in the list
    for node in expr_list[1:]:
        full_expr |= node  # Combine the expressions using logical OR operator

    return expr2bdd(full_expr)  # Convert the expression to BDD

bdd = combine_expressions(expressions) # Combine the expressions to create the BDD

'''
This function takes a list of nodes and a letter as input and then returns a BDD that represents the nodes.
'''
# Will use this in assignment to convert PRIME and EVEN sets into a BDD
# Brings in the letter (X/Y) and the node list (manipulated as T/F) to create the BDD (~xx0 & xx1 & ~xx2 ... ~yy0 & yy1 & ~yy2 ...)
def node_set_to_bdd(node_list: list[bool], letter: str) -> BinaryDecisionDiagram:
    bin_expr_list = []
    for node_id in range(len(node_list)):  #Loop through the list of nodes and append to the binairy expressions list a created bin expression using node and letter
        if node_list[node_id]:
            bin_expr_list.append(node_to_binexpr(node_id, letter))
    return combine_expressions(bin_expr_list)  # Combine the expressions to create the BDD


## Change the reachability of the BDD ###################################################################
'''
This function takes two BDDs as input and then returns a new BDD that represents the reachability of the second BDD from the first BDD.
Essentially an implementatino of the Z set (assumed initialy unreached) where it is used as a middleman between x and y sets.
'''
def extend_reachability(rr1: BinaryDecisionDiagram, rr2: BinaryDecisionDiagram) -> BinaryDecisionDiagram:
    # define BDD variables for z
    vars_z = set_bddvars('z', 5)

    # define BDDs from x to z, then z to y
    step1 = rr1.compose({vars_x[idx]: vars_z[idx] for idx in range(5)})
    step2 = rr2.compose({vars_y[idx]: vars_z[idx] for idx in range(5)})

    # combine steps and eliminate existiential quantifier
    return (step1 & step2).smoothing(vars_z)

'''
This function computes rr2 by performing reachability step on itself
'''
def rr_to_rr2(rr: BinaryDecisionDiagram) -> BinaryDecisionDiagram:
    return  extend_reachability(rr, rr)

'''
The function accepts a bdd (rr) and iteratively extends the reachability of nodes in the graph represented 
by the input BDD rr until reaching a fixed point where no further extension is possible, indicating that the 
transitive closure has been achieved.
'''

## Utilization of the Transitive closure property ################################################
'''
 transitive closure property ensures that if there is a path from X to node Z, and from Z to Y, 
 then there's also path from x - y. This function iteratively extends the reachability of nodes 
 until no further extensions are possible, capturing all transitive relationships in the BDD
'''

def transitive_closure(rr: BinaryDecisionDiagram) -> bool:
    converging_bdd = rr  #initialie new bdd

    while True: #infinite loop until break
        new_bdd = bdd or extend_reachability(converging_bdd, rr)
        if new_bdd.equivalent(converging_bdd):  #If no futrhure iterations are possible,
            break
        converging_bdd = new_bdd # Update converging BDD for next iteration

    return converging_bdd


## Search BDD's for Nodes and edges ###################################################################
'''
This function takes a BDD and a node as input and then returns a boolean value that represents if the node is in the BDD.
It searches the BDD for the node by converting node identifier to binairy then 
Then it uses bdd.restrict() and then checking if the result is a one.
'''
def find_node(bdd: BinaryDecisionDiagram, node: int, letter: str) -> bool:

    node_bin = format(node, 'b').rjust(5, '0')
    vars_x = set_bddvars(letter, 5)  # Generate list of BDD variables

    node = {}  
    for i in range(5):  #iterates over the binairy rep of the node and assignes each spot as T/F
        node[vars_x[i]] = int(node_bin[i])  # nodes = [0,1,1,1,0] 

    restricted = bdd.restrict(node) # restrict bdd based on the dictionary node derived
    restricted_test = restricted.is_one()  #Checks to see if the result exists

    return restricted_test

'''
This function takes a bdd as input and then returns a boolean value that represents if the edge is in the BDD.
It searches the BDD for the edge by converting node identifiers to binary then creating a dictionairy of the edges
then using bdd.restrict based on the edges and then checking if the result is a one.
'''

def search_bdd(bdd: BinaryDecisionDiagram, node1: int, node2: int) -> bool:

    node1_bin = format(node1, 'b').rjust(5, '0')  # Convert node to binary and fill with 0s right justified
    node2_bin = format(node2, 'b').rjust(5, '0')  

    edges = {}
    for i in range(5): #iterates over the binairy rep of the nodes and assignes each spot as T/F
        edges[vars_x[i]] = int(node1_bin[i])  # ex. edges = [0,1,1,1,0]
        edges[vars_y[i]] = int(node2_bin[i])  # ex. edges = [1,0,0,1,1]

    restricted = bdd.restrict(edges)  # Restricts based on the nodes
    restricted_test = restricted.is_one()  #Checks to see if edge exits
    return restricted_test