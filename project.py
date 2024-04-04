
from pyeda.inter import *


## Generate variables for use in project ########################################################

# Define the variables X and Y for XX1-XX5 and YY1-YY5 sets (later used in PRIME and EVEN)
letter_x = 'x'
letter_y = 'y'
'''

This function takes a string variable (Either X or Y for the later PRIME and EVEN sets) 
and an integer length as input (5 for XX1-XX5 or YY1-YY5) then returns a list of BDD variables.
'''
def set_bddvar(variable: str, length: int):  
    list = [] # Initialize an empty list
    for i in range(length):
        list.append(bddvar(f'{variable}{i}')) # Append the BDD variables to the list, produced X1, X2, ...
    return list


# generate lists of vars xx0...xx5 & yy0...yy5 with set_bddvar function
vars_i = set_bddvar(letter_x, 5)
vars_j = set_bddvar(letter_y, 5)

# Generate graph for translation to BDD ########################################################
'''
This function takes a list of BDD variables as input and then returns a BDD graph matrix.
True or False represent an edge between two nodes in the graph.
'''
def create_graph() -> list[list[bool]]:

    graph_matrix = [[False] * 32 for idx in range(32)] #set all index to false initially

    for i in range(5):
        for j in range(5):
            if (i + 3) % 32 == j % 32 or (i + 8) % 32 == j % 32:
                graph_matrix[i][j] = True
    return graph_matrix

graph = create_graph() # Create the graph matrix

# Convert graph to BDD #########################################################################

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

    test_expression = expr("xx0")
    print(test_expression)

    nodenum_bin = format(nodenum, '05b')  # Convert to binary and pad with 0s up to 5 digits justified right
    
    expr_strs = []  # List for strings of names of nodes

    for i in range(5):
        node_name = f"{2 *letter}{i}"  # Generate node name like 'Xx0'
        if nodenum_bin[i] == '1':
            expr_strs.append(node_name)
        else:
            expr_strs.append(f"~{node_name}")

    expression = expr(" & ".join(expr_strs))  # Create the expression using logical AND operator

    return expression


bdd = graph_to_expressions(graph) # Create the BDD graph


                
