import random
import requests
import json
import classes
from datetime import datetime, timedelta
import pytz

routes_responses_dict = {}

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
	cxpoint1 = random.randint(0, size)
	cxpoint2 = random.randint(0, size - 1)
	if cxpoint2 >= cxpoint1:
		cxpoint2 += 1
	else:  # Swap the two cx points
		cxpoint1, cxpoint2 = cxpoint2, cxpoint1

	# Create offspring by exchanging genetic information between parents
	child1 = parent1.copy()
	child2 = parent2.copy()

	mapped_relations = {}
	for i in range(cxpoint1, cxpoint2):
		child1[i], child2[i] = child2[i], child1[i]
		# Determine mapping relationship to legalize offspring
		temp_list = mapped_relations.get(child1[i])

		temp_list = mapped_relations.get(child1[i]) if mapped_relations.get(child1[i]) else []
		temp_list.extend([child2[i]])
		mapped_relations[child1[i]] = temp_list

		temp_list = mapped_relations.get(child2[i]) if mapped_relations.get(child2[i]) else []
		temp_list.extend([child1[i]])
		mapped_relations[child2[i]] = temp_list

	# Legalize children with the mapping relationship
	for i in range(size):
		if i < cxpoint1 or i >= cxpoint2:
			if child1[i] in mapped_relations.keys():
				# mientras la cantidad de repetidos sea igual a 0
				repeating_items = True
				while repeating_items:
					# Hacer hasta que no hayan repetidos
					for j in mapped_relations.get(child1[i]):
						child1[i] = j
						if child1.count(j) == 1:
							repeating_items = False
							break
						else:
							repeating_items = True

	for i in range(size):
		if i < cxpoint1 or i >= cxpoint2:
			if child2[i] in mapped_relations.keys():
				# mientras la cantidad de repetidos sea igual a 0
				repeating_items = True
				while repeating_items:
					# Hacer hasta que no hayan repetidos
					for j in mapped_relations.get(child2[i]):
						child2[i] = j
						if child2.count(j) == 1:
							repeating_items = False
							break
						else:
							repeating_items = True
											
	return child1, child2

def evaluate(individual:list):
	# Main variables
	# (YYYY-MM-DD)T(HH:mm:ss.ms)(UTC-6)
	departure_time = "2024-05-24T09:00:00.000000-06:00"
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

	# Origin
	origin = classes.Point_of_Sale("Origin", 14.588072840778365, -90.51033129922843, "2da Calle 10-59 Zona 14")

	# Copy the original list to not alterate the individual POS list
	# Adding the Origin latLng at the start and the end of the list
	# For it is the start and the end of the route
	points_of_sale:list = individual.copy()
	points_of_sale.insert(0, origin)
	points_of_sale.append(origin)

	responses = []

	for i in range(len(points_of_sale) - 1):
		POS_origin = points_of_sale[i]
		POS_destination = points_of_sale[i + 1]

		data["origin"]["location"]["latLng"]["latitude"] = POS_origin.latitude
		data["origin"]["location"]["latLng"]["longitude"] = POS_origin.longitude
		data["destination"]["location"]["latLng"]["latitude"] = POS_destination.latitude
		data["destination"]["location"]["latLng"]["longitude"] = POS_destination.longitude

		# If the request responses has already be done, don't do the request again
		dict_key = f'{POS_origin.name},{POS_destination.name},{data["departureTime"]}'
		if routes_responses_dict.get(dict_key):
			response = routes_responses_dict.get(dict_key)
			responses.append(response)
			new_departure_time = add_time(departure_time, POS_destination.total_time, int(response['duration'].rstrip('s')))
			data["departureTime"] = new_departure_time
		else:
			req_result = requests.post(http_url, json=data, headers=headers)
			res_json = req_result.json()
			responses.append(res_json["routes"][0])
			# Save the request in a dictionary to save resources and time of execution
			routes_responses_dict[dict_key] = res_json["routes"][0]
			new_departure_time = add_time(departure_time, POS_destination.total_time, int(res_json["routes"][0]['duration'].rstrip('s')))
			data["departureTime"] = new_departure_time
		

	# Sum all distances and duration
	total_distance = 0
	total_duration = 0
	for item in responses:
		if item.get('distanceMeters'):
			total_distance += int(item['distanceMeters'])
		if item.get('duration'):
			# Removing the s at the end of the string because 'duration' comes in format: '{Num}s'
			total_duration += int(item['duration'].rstrip('s'))
	
	# return a tuple
	return total_distance,total_duration,


def print_responses():
	print(routes_responses_dict)

def add_time(departure_time, origin_total_time, response_duration):
	# Convert string to datetime
	departure_datetime = datetime.strptime(departure_time, "%Y-%m-%dT%H:%M:%S.%f-06:00")
	# Convert to UTC timezone
	departure_datetime = departure_datetime.replace(tzinfo=pytz.UTC)
	# Sum seconds using timedelta
	add_seconds=origin_total_time + response_duration
	new_datetime = departure_datetime + timedelta(seconds=add_seconds)
	# Convert back to string format
	new_departure_time = new_datetime.strftime("%Y-%m-%dT%H:%M:%S.%f") + "-06:00"

	# data["departureTime"] = new_departure_time
	return new_departure_time