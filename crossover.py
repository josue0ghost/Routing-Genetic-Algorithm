import random

def cxOrdered(parent1:list, parent2:list):
	"""Executes a Ordered crossover on the input individuals.
	The two individuals are modified in place. This crossover expects
	:term:`sequence` individuals of any type.
	:param parent1: The first individual participating in the crossover.
	:param parent2: The second individual participating in the crossover.
	:returns: A tuple of two individuals.
	"""
	size = min(len(parent1), len(parent2))
	cxpoint1, cxpoint2 = sorted(random.sample(range(size), 2))

	child1, child2  = [None] * size, [None] * size

	child1[cxpoint1:cxpoint2] = parent1[cxpoint1:cxpoint2]
	child2[cxpoint1:cxpoint2] = parent2[cxpoint1:cxpoint2]

	# We must keep the original values somewhere before scrambling everything
	def fill_child(child, parent):
		current_pos = cxpoint2
		for gene in parent:
			if gene not in child:
				if current_pos >= size:
					current_pos = 0
				child[current_pos] = gene
				current_pos += 1

	fill_child(child1, parent2)
	fill_child(child2, parent1)

	return child1, child2


def cxPartialyMatched(parent1:list, parent2:list):
	"""Executes a partially matched crossover on the input individuals.
	The two individuals are modified in place. This crossover expects
	:term:`sequence` individuals of any type.
	:param parent1: The first individual participating in the crossover.
	:param parent2: The second individual participating in the crossover.
	:returns: A tuple of two individuals.

	This crossover generates two children by matching and swapping 
	pairs of values in a certain range of the two parents. \\
	
	Example with cxpoint1 = 1 and cxpoint2 = 4:

	inputs:\\
	parent1 = ["0","3","2","1","4"] \\
	parent2 = ["2","4","3","0","1"]

	Then: \\
	child1 = ["0","4","3","0","4"] \\
	child2 = ["2","3","2","1","1"]

	Mapped relationships are: \\
	4 - 3 - 2 \\
	0 - 1

	Returns: \\
	child1 = ["1","4","3","0","2"] \\
	child2 = ["4","3","2","1","0"] \\
	"""

	# Choose crossover points
	size = min(len(parent1), len(parent2))
	cxpoint1, cxpoint2 = sorted(random.sample(range(size), 2))

	# Create offspring by exchanging genetic information between parents
	child1 = parent1.copy()
	child2 = parent2.copy()

	# Determine mapping relationships to legalize offspring
	mapped_relations = {}
	for i in range(cxpoint1, cxpoint2):
		child1[i], child2[i] = child2[i], child1[i]

		mapped_relations[child1[i]] = child2[i]
		mapped_relations[child2[i]] = child1[i]
	
	# Legalize children with the mapped relationships
	def legalize_child(child):
		for i in range(size):
			if i < cxpoint1 or i >= cxpoint2:
				while child.count(child[i]) > 1:
					child[i] = mapped_relations[child[i]]

	legalize_child(child1)
	legalize_child(child2)

	return child1, child2

