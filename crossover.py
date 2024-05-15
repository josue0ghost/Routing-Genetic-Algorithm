import random
import requests
import json
import classes

#AIzaSyDmJwkXdl2ZzLXaDMtUyak1zQCcV-bgR20

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
	# Seleccionar dos puntos de corte aleatorios
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
	API_KEY = ''
	http_url = 'https://routes.googleapis.com/directions/v2:computeRoutes'
	headers = {
		'Content-Type': 'application/json',
		'X-Goog-Api-Key': API_KEY,
		'X-Goog-FieldMask': 'routes.duration,routes.distanceMeters'
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
		#"departureTime": "2024-10-15T15:01:23.045123456Z",
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
	points_of_sale.insert(-1, origin)
	points_of_sale.append(origin)

	for i in range(len(points_of_sale) - 1):
		POS_origin = points_of_sale[i]
		POS_destination = points_of_sale[i + 1]

		data["origin"]["location"]["latLng"]["latitude"] = POS_origin.latitude
		data["origin"]["location"]["latLng"]["longitude"] = POS_origin.longitude
		data["destination"]["location"]["latLng"]["latitude"] = POS_destination.latitude
		data["destination"]["location"]["latLng"]["longitude"] = POS_destination.longitude

		# If the request respones has already be done, don't do the request again
		responses = []
		if routes_responses_dict.get(f'{POS_origin.name},{POS_destination.name}'):
			responses.append(routes_responses_dict.get(f'{POS_origin.name},{POS_destination.name}'))
		else:
			req_result = requests.post(http_url, json=data, headers=headers)
			res_json = req_result.json()
			responses.append(res_json["routes"][0])
			# Save the request in a dictionary to save resources and time of execution
			routes_responses_dict[f'{POS_origin.name},{POS_destination.name}'] = res_json["routes"][0]
	
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