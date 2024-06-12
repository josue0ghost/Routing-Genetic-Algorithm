import classes
from datetime import datetime, timedelta
import pytz
import random
import requests

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


routes_responses_dict = {}
departure_time = ""
origin = classes.Point_of_Sale("Central", 14.588072840778365, -90.51033129922843)

def evaluate(individual:list):
	"""Executes the calculation of the fitness value on the input individual.
	This fitness function expects :term:`sequence` individual of type 
	`Point_of_Sale`.
	:param individual: The individual to be evaluated.
	:returns: A tuple of integers (distanceMeters, duration)

	This function uses two global variables: \\
	`routes_responses_dict` where API Routes responses are stored and \\
	`origin` which is a `Point_of_Sale` object describing the route's start \\
	point and last destination.
	"""

	# Main variables
	API_KEY = 'AIzaSyCOpv37p0AcdUj32K2UADdSmfwY_5YFH-Y'
	http_url = 'https://routes.googleapis.com/directions/v2:computeRoutes'
	headers = {
		'Content-Type': 'application/json',
		'X-Goog-Api-Key': API_KEY,
		'X-Goog-FieldMask': 'routes.distanceMeters,routes.duration,routes.polyline.encodedPolyline'
	}
	data = {
		"origin": {
			"location": {
				"latLng": {
					"latitude": 0,
					"longitude": 0
				}
			},
			"sideOfRoad": True
		},
		"destination": {
			"location": {
				"latLng": {
					"latitude": 0,
					"longitude": 0
				}
			},
			"sideOfRoad": True
		},
		"travelMode": "DRIVE",
		"routingPreference": "TRAFFIC_AWARE",
		"departureTime": departure_time,
		"computeAlternativeRoutes": False,
		"routeModifiers": {
			"avoidTolls": False,
			"avoidHighways": False,
			"avoidFerries": False
		},
		"languageCode": "en-US",
		"units": "IMPERIAL"
	}

	# Adding the Origin latLng at the start and the end of the list
	# For it is the start and the end of the route
	points_of_sale = [origin] + individual + [origin]

	responses_list = []

	# Making an API request per POS to POS route
	for i in range(len(points_of_sale) - 1):
		POS_origin = points_of_sale[i]
		POS_destination = points_of_sale[i + 1]

		data["origin"]["location"]["latLng"]["latitude"] = POS_origin.latitude
		data["origin"]["location"]["latLng"]["longitude"] = POS_origin.longitude
		data["destination"]["location"]["latLng"]["latitude"] = POS_destination.latitude
		data["destination"]["location"]["latLng"]["longitude"] = POS_destination.longitude

		# If there is already a response for the combination of
		# origin, destination and departure time, don't make the request again
		dict_key = f'{POS_origin.name},{POS_destination.name},{data["departureTime"]}'
		existing_response = routes_responses_dict.get(dict_key)

		if existing_response:
			# Adding response to a list for further calculations
			responses_list.append(existing_response)
			# Sum destination times
			new_departure_time = add_time(data["departureTime"], existing_response['duration'])
		else:
			req_result = requests.post(http_url, json=data, headers=headers)
			result = req_result.json()

			new_response = result["routes"][0]

			# Sum destination times to the api response
			# Removing the s at the end of the string because 'duration' comes in format: '{Num}s'
			res_duration = int(new_response["duration"].rstrip('s'))
			new_res_duration = POS_destination.total_time + res_duration
			new_response["duration"] = new_res_duration

			# Convert distanceMeters from string to integer type
			new_response["distanceMeters"] = int(new_response["distanceMeters"])

			# Polyline
			new_response["polyline"] = new_response["polyline"]["encodedPolyline"]

			# Adding response to a list for further calculations
			responses_list.append(new_response)

			# Save the request in a dictionary to save resources and execution time
			routes_responses_dict[dict_key] = new_response
			new_departure_time = add_time(data["departureTime"], new_res_duration)
		
		data["departureTime"] = new_departure_time

	# Sum all distances and duration
	total_distance = sum(response['distanceMeters'] for response in responses_list if response.get('distanceMeters'))
	total_duration = sum(response['duration'] for response in responses_list if response.get('duration'))

	# return a tuple
	return (total_distance, total_duration)


def add_time(departure_time,  response_duration):
	# Convert string to datetime
	departure_datetime = datetime.strptime(departure_time, "%Y-%m-%dT%H:%M:%S.%f-06:00")
	# Convert to UTC timezone
	departure_datetime = departure_datetime.replace(tzinfo=pytz.UTC)
	# Sum seconds using timedelta
	new_datetime = departure_datetime + timedelta(seconds=response_duration)
	# Convert back to string format
	new_departure_time = new_datetime.strftime("%Y-%m-%dT%H:%M:%S.%f") + "-06:00"

	# data["departureTime"] = new_departure_time
	return new_departure_time