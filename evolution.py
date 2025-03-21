import json
import random
import math
from colorama import Fore

#pip install keras==3.4.1
import keras

def new_model(layers):
	model = keras.Sequential()

	input_layer = keras.layers.Input((layers[0],))
	model.add(input_layer)

	for i in range(1,len(layers)-1): 
		hidden_layer = keras.layers.Dense((layers[i]), activation="relu", use_bias=True)
		model.add(hidden_layer)

	output_layer = keras.layers.Dense(layers[-1], activation="linear")
	model.add(output_layer)

	return model


def new_model_evolution(prev_models, results):
	#changes that can be made: removal of a datapoint, addition of a layer, or +/- of dense layer size
	new_models = []
	temp_prev = []

	index_a = 0
	index_b = 0

	if len(results) > 1:
		copy_results = list(results[-10:])
		cc = []
		for c in range(len(copy_results)):
			cc.append(copy_results[c][-1])
			copy_results[c] = copy_results[c][-1]

		cc.sort()
		index_a = copy_results.index(cc[0])
		index_b = copy_results.index(cc[1])

	for i in range(0,10):
		ind = index_a
		if i > 4:ind = index_b

		old_p = {}
		old_p["shape"] = list(prev_models[-10:][ind]["shape"])
		old_p["remove_dp"] = list(prev_models[-10:][ind]["remove_dp"])

		if i < 2:#20% to not mutate
			pass
		elif i >= 2 and i < 5:#30% remove a random datapoint
			old_p["shape"][0] -= 1
			
			choc = random.randint(0, prev_models[-10:][ind]["shape"][0]-1)
			while choc in old_p['remove_dp']: choc = random.randint(0, prev_models[-10:][ind]["shape"][0]-1)#prevent duplicate things to remove

			old_p["remove_dp"].append(choc)
			print(old_p)
		elif i >= 5 and i < 8:#30% +/- from hidden layer/s
			#shrink/grow layer size
			to_choose = range(1, len(old_p["shape"])-1)
			if not len(to_choose):to_choose = [1]

			if random.randint(0,1):
				old_p["shape"][random.choice(to_choose)] -= 1
			else:
				old_p["shape"][random.choice(to_choose)] += 1
		else:#20% to add hidden layer
			old_p["shape"][-1] = old_p["shape"][1]
			old_p["shape"].append(1)
		
		print(Fore.GREEN + str(old_p["shape"]))
		print(Fore.RED + str(len(temp_prev)+len(prev_models)))
		temp_prev.append(old_p)
		new_models.append(new_model(old_p["shape"]))

	prev_models += temp_prev
	return new_models
