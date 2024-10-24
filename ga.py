import classes
import crossover
import mutation
import fitness
import pandas as pd
import numpy as np
import random

from deap import base, creator, tools

# Using DEAP library
# initializing DEAP's toolbox
toolbox = base.Toolbox()
# weights is a tuple of -1.0s which means we want to Minimize two values: Distance and Time
creator.create("FitnessMin", base.Fitness, weights=(-1.0,-1.0))
creator.create("Individual", list, fitness=creator.FitnessMin, polylines=[])

# shuffle the Point_of_Sale list of an individual
def shuffle_sequence(individual):
  random.shuffle(individual)
  return individual

def get_unique_values(pop):
  # Show results. Get unique values
  def extract_names(individual):
      return [pos.name for pos in individual]

  pop_data = np.array([extract_names(ind) for ind in pop])
  pop_df = pd.DataFrame(pop_data)

  fitnesses_list = []
  for ind in pop:
    fitnesses_list.append(ind.fitness.values)

  fitness_df = pd.DataFrame(fitnesses_list, columns=['Distancia (m)', 'Tiempo (s)'])

  result_df = pd.concat([pop_df, fitness_df], axis=1)
  return result_df

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

def ga_request(central, pos, departure_time):
  """Executes the main genetic algorithm through the flask app.
  :param central: Dict object with name, lat and lng attributes.
  :param pos: list of dicts with the same attributes from Point_of_Sale class except for the `address` attribute.
  :param departure_time: Datetime string with the format `YYYY-MM-DDTHH:mm:00.000000-06:00`
  :returns: a :term:`DataFrame` containing the last generation of a population
  """
  fitness.origin = classes.Point_of_Sale("Central", central['lat'], central['lng'])
  fitness.departure_time = departure_time

  # Conversion to Point_of_Sale
  pos = pd.DataFrame(pos).to_records(index=False).tolist()
  pos_list = [
    classes.Point_of_Sale(
      point[1], point[2], point[3], "",
      point[4], point[5], point[6], point[7],
      point[8], point[9], point[10], point[11], point[12]
    )
    for point in pos
  ]
  distance_df = mutation.build_distance_dataframe(pos_list)

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
  # fitness function from ./fitness.py
  toolbox.register("evaluate", fitness.evaluate_osrm)
  toolbox.register("evaluate_traffic", fitness.evaluate_google)

  # Algorithm execution with OSRM
  pop = genetic_algorithm(matepb=0.5, mutpb=0.5, ngen=100, npop=100)

  # Last evaluation with Routes API
  fitnesses = map(toolbox.evaluate_traffic, pop)
  for individual, fit in zip(pop, fitnesses):
    individual.fitness.values = fit

  print(pop[0].polylines)
  # Get unique values in population
  result_df = get_unique_values(pop)

  return result_df.value_counts().to_frame(name="f")