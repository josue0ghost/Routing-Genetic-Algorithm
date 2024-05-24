class Individual(list):
  def __init__(self, sequence:list):
    # Point_of_Sale list
    self.sequence = sequence


class Point_of_Sale:
  def __init__(self, name, latitude, longitude, address,
      entree_time=0, unloading_time=0, journey2pos_time=0, delivery_time=0, 
      journey2unloadingpoint_time=0, checkout_time=0,
      min_travels=0, max_travels=0, extra_times=0):

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
    # Number of journeys needed to deliver all needed products
    # Varies by pos
    self.min_travels = min_travels
    self.max_travels = max_travels
    # if needed (delays)
    self.extra_times = extra_times

    self.total_time = entree_time + unloading_time + journey2pos_time + delivery_time + journey2unloadingpoint_time + checkout_time + extra_times

  def __str__(self):
    return f'{self.name}'

