class Individual(list):
  def __init__(self, sequence:list):
    # Point_of_Sale list
    self.sequence = sequence


class Point_of_Sale:
  def __init__(self, name, latitude, longitude, address):
    self.name = name
    self.latitude = latitude
    self.longitude = longitude
    self.address = address

  def __str__(self):
    return f'{self.name}'

