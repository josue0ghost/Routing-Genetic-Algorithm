import random
import requests
import json
import classes
from datetime import datetime, timedelta
import pytz

routes_responses_dict = {}
# Origin
origin = classes.Point_of_Sale("Central", 14.588072840778365, -90.51033129922843, "2da Calle 10-59 Zona 14")

'''
inputs:
parent1 = ["0","3","2","1","4"]
parent2 = ["2","4","3","0","1"]

example with cxpoint = 1, cxpoint = 4
child1 = ["0","4","3","0","4"]
child2 = ["2","3","2","1","1"]

relations: 
4 - 3 - 2
0 - 1

results:
child1 = ["1","4","3","0","2"]
child2 = ["4","3","2","1","0"]
'''
def cxPartialyMatched(parent1:list, parent2:list):
	size = min(len(parent1), len(parent2))
	# Choose crossover points
	cxpoint1, cxpoint2 = sorted(random.sample(range(size), 2))

	# Create offspring by exchanging genetic information between parents
	child1 = parent1.copy()
	child2 = parent2.copy()

	mapped_relations = {}
	for i in range(cxpoint1, cxpoint2):
		child1[i], child2[i] = child2[i], child1[i]

		mapped_relations[child1[i]] = child2[i]
		mapped_relations[child2[i]] = child1[i]
	
	def legalize_child(child):
		for i in range(size):
			if i < cxpoint1 or i >= cxpoint2:
				while child.count(child[i]) > 1:
					child[i] = mapped_relations[child[i]]

	legalize_child(child1)
	legalize_child(child2)

	return child1, child2


def evaluate(individual:list):
	# Main variables
	# (YYYY-MM-DD)T(HH:mm:ss.ms)(UTC-6)
	departure_time = "2024-05-28T09:00:00.000000-06:00"
	API_KEY = ''
	http_url = 'https://routes.googleapis.com/directions/v2:computeRoutes'
	headers = {
		'Content-Type': 'application/json',
		'X-Goog-Api-Key': API_KEY,
		'X-Goog-FieldMask': 'routes.distanceMeters,routes.duration'
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

	for i in range(len(points_of_sale) - 1):
		POS_origin = points_of_sale[i]
		POS_destination = points_of_sale[i + 1]

		data["origin"]["location"]["latLng"]["latitude"] = POS_origin.latitude
		data["origin"]["location"]["latLng"]["longitude"] = POS_origin.longitude
		data["destination"]["location"]["latLng"]["latitude"] = POS_destination.latitude
		data["destination"]["location"]["latLng"]["longitude"] = POS_destination.longitude

		# If the request responses has already be done, don't do the request again
		dict_key = f'{POS_origin.name},{POS_destination.name},{data["departureTime"]}'
		existing_response = routes_responses_dict.get(dict_key)

		if existing_response:
			responses_list.append(existing_response)
			new_departure_time = add_time(departure_time, existing_response['duration'])
		else:
			req_result = requests.post(http_url, json=data, headers=headers)
			result = req_result.json()

			new_response = result["routes"][0]

			# Sum destination times to the api response
			# Removing the s at the end of the string because 'duration' comes in format: '{Num}s'
			res_duration = int(new_response["duration"].rstrip('s'))
			new_res_duration = POS_destination.total_time + res_duration
			new_response["duration"] = new_res_duration

			# Convert distance from string to integer type
			new_response["distanceMeters"] = int(new_response["distanceMeters"])

			responses_list.append(new_response)

			# Save the request in a dictionary to save resources and execution time
			routes_responses_dict[dict_key] = new_response
			new_departure_time = add_time(departure_time, new_res_duration)
		
		data["departureTime"] = new_departure_time

	# Sum all distances and duration
	total_distance = sum(response['distanceMeters'] for response in responses_list if response.get('distanceMeters'))
	total_duration = sum(response['duration'] for response in responses_list if response.get('duration'))

	# return a tuple
	# return (total_distance, total_duration)
	return (total_duration, total_distance)


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