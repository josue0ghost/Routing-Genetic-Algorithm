import classes
import crossover
import mutation
import fitness
import pandas as pd
import numpy as np
import random

from deap import base, creator, tools

# Get data from csv file
def get_data(csv_file):
  data_df = pd.read_csv(csv_file, dtype={
    'pos_name': str,
    'latitude': float,
    'longitude': float,
    'address': str,
    'entree_time': int,
    'unloading_time': int,
    'journey2pos_time': int,
    'delivery_time': int,
    'journey2unloadingpoint_time': int,
    'checkout_time': int,
    'min_travels': int,
    'max_travels': int,
    'extra_times': int
  })
  
  data = data_df.to_records(index=False).tolist()
  
  return data

# shuffle the Point_of_Sale list of an individual
def shuffle_sequence(individual):
  random.shuffle(individual)
  return individual

# Read CSV and create a initial list of Point_of_Sale
readed_points_of_sale = get_data('data.csv')

# Create a list of Point_of_Sale
pos_list = [
  classes.Point_of_Sale(
    point[0], point[1], point[2], point[3],
    point[4], point[5], point[6], point[7],
    point[8], point[9], point[10], point[11], point[12]
  )
  for point in readed_points_of_sale
]

distance_df = mutation.build_distance_dataframe(pos_list)

# Using DEAP library
# weights is a tuple of -1.0s which means we want to Minimize two values: Distance and Time
creator.create("FitnessMin", base.Fitness, weights=(-1.0,-1.0))
creator.create("Individual", list, fitness=creator.FitnessMin)

# initializing DEAP's toolbox
toolbox = base.Toolbox()
# individual's attribute sequence will shuffle a list of POS at creation
toolbox.register("sequence", shuffle_sequence, pos_list)
# individual inherits from Individual and will have the attribute 'sequence'
toolbox.register("individual", tools.initIterate, creator.Individual, toolbox.sequence)
# population will be a list of individuals
toolbox.register("population", tools.initRepeat, list, toolbox.individual)
# mate function from ./crossover.py
toolbox.register("mate", crossover.cxOrdered)
# mutation function that uses DEAP's function mutShuffleIndexes. 
# indpb is the probability of each attribute to be exchanged to another position
toolbox.register("mutate", mutation.smart_mutation_with_df, distance_df=distance_df)
# tournsize = The number of individuals participating in each tournament
toolbox.register("select", tools.selTournament, tournsize=2)
# fitness function from ./crossover.py
toolbox.register("evaluate", fitness.evaluate_osrm)

# Main Genetic Algorithm
def genetic_algorithm(matepb, mutpb, ngen, npop):
  """Executes the main genetic algorithm.
  :param matepb: Probability that two individuals cross.
  :param mutpb: Probability that an individual mutates.
  :param ngen: Number of generations the population will have
  :param npop: How many individuals will make up the population
  :returns: a :term:`list` containing the las generation of a population
  """

  population = toolbox.population(n=npop)
  # Evaluate the entire population
  fitnesses = map(toolbox.evaluate, population)

  for individual, fitness in zip(population, fitnesses):
    individual.fitness.values = fitness

  for generation in range(ngen):
    # Select the next generation individuals
    offspring = toolbox.select(population, len(population))

    # Clone the selected individuals
    offspring = list(map(toolbox.clone, offspring))

    # Apply crossover and mutation on the offspring
    for child1, child2 in zip(offspring[::2], offspring[1::2]):
      if random.random() < matepb:
        toolbox.mate(child1, child2)
        # Invalidates the fitness of the offspring after crossing
        del child1.fitness.values
        del child2.fitness.values

    for mutant in offspring:
      if random.random() < mutpb:
        toolbox.mutate(mutant)
        # Invalidates the fitness of the mutant after mutation
        del mutant.fitness.values

    # Evaluate the individuals with an invalid fitness
    invalid_ind = [ind for ind in offspring if not ind.fitness.valid]
    fitnesses = map(toolbox.evaluate, invalid_ind)
    for ind, fit in zip(invalid_ind, fitnesses):
      ind.fitness.values = fit

    elite = tools.selBest(population, 1)  # Keep the best individual

    # The population is entirely replaced by the offspring
    population[:] = offspring
    population[:1] = elite
  
  return population  

# GA Execution
# (YYYY-MM-DD)T(HH:mm:ss.ms)(UTC-6)
# crossover.departure_time = "2024-09-27T09:00:00.000000-06:00"

# pop = main(matepb=0.5, mutpb=0.5, ngen=100, npop=100)
def ga_request(central, pos, departure_time):
  print(central)
  print(pos)
  print(departure_time)
  fitness.origin = classes.Point_of_Sale("Central", central['lat'], central['lng'])
  fitness.departure_time = departure_time
