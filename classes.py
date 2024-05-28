import random

class Point_of_Sale:
  def __init__(self, name, latitude, longitude, address,
              entree_time=0, unloading_time=0, journey2pos_time=0, delivery_time=0, 
              journey2unloadingpoint_time=0, checkout_time=0, min_travels=1, max_travels=1, extra_times=0):

    self.name = name
    self.latitude = latitude
    self.longitude = longitude
    self.address = address
    # times in seconds
    self.entree_time = entree_time
    self.unloading_time = unloading_time
    self.journey2pos_time = journey2pos_time
    self.delivery_time = delivery_time
    self.journey2unloadingpoint_time = journey2unloadingpoint_time
    self.checkout_time = checkout_time
    # if needed (delays)
    # Number of journeys needed to deliver all needed products
    # Varies by pos
    self.min_travels = min_travels
    self.max_travels = max_travels
    self.extra_times = extra_times

    # list containing numbers from self.min_travels to self.max_travels
    base_list = [i for i in range(self.min_travels, self.max_travels + 1)]
    # generate weights. Output example: [1, 2, 2, 1]
    weights = [0] * len(base_list)
    for i, num in enumerate(base_list):
      weights[i] = num
      weights[-(i+1)] = num
    # choice a random number of travels from base_list
    self.num_travels = random.choices(base_list, weights=weights)[0]

    # Set POS total time
    self.total_time = entree_time + unloading_time + checkout_time + extra_times + (journey2pos_time + delivery_time + journey2unloadingpoint_time)*self.num_travels 

  def __str__(self):
    return f'{self.name}'

