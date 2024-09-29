import random
import pandas as pd
from math import radians, cos, sin, sqrt, atan2

def haversine_distance(lat1, lon1, lat2, lon2):
  """
  Calculate the distance between two geographic points using the Haversine formula
  """
  R = 6371.0  # Radio de la Tierra en km
  lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
  
  dlat = lat2 - lat1
  dlon = lon1 - lon2  # Se usa inverso para simplificar después
  
  a = sin(dlat / 2)**2 + cos(lat1) * cos(lat2) * sin(dlon / 2)**2
  c = 2 * atan2(sqrt(a), sqrt(1 - a))
  return R * c

def build_distance_dataframe(pos_list):
  """
  Create a dataframe with distances between `Point_of_Sale`
  """
  data = {}
  
  for pos in pos_list:
    distances = []
    for other_pos in pos_list:
      if pos == other_pos:
        distances.append(0)
      else:
        distance = haversine_distance(pos.latitude, pos.longitude, other_pos.latitude, other_pos.longitude)
        distances.append(distance)
    data[pos.name] = distances
  
  df = pd.DataFrame(data, index=[pos.name for pos in pos_list])
  return df


def smart_mutation_with_df(individual, distance_df):
  """
  Implements a smart mutation using the distance DataFrame
  Select the `Point_of_Sale` closest to the chosen `Point_of_Sale` to exchange positions with each other
  """
  
  # Elegimos un punto de venta al azar
  pos1 = random.choice(individual)
  
  # Obtenemos las distancias del punto seleccionado con todos los demás
  distances = distance_df[pos1.name]
  
  # Seleccionamos el punto más cercano
  nearest_pos_name = distances[distances > 0].idxmin()
  nearest_pos = next(pos for pos in individual if pos.name == nearest_pos_name)
  
  # Intercambiamos los dos puntos de venta cercanos
  idx1, idx2 = individual.index(pos1), individual.index(nearest_pos)
  individual[idx1], individual[idx2] = individual[idx2], individual[idx1]
  
  return individual


