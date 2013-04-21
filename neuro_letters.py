from numpy import *
from itertools import *
from time import *

#calss to read letters from specified file, and parse them
class Letter:
	rows = 8
	coloumns = 6

	def __init__ (self, array, letter = None):
		self.visual = []
		self.char_let = letter
		for x in range (self.rows):
			start_pos = x*self.coloumns
			end_pos = start_pos + self.coloumns
			self.visual.append(array [start_pos:end_pos])
		
		#not sure, maby this is spaces
		if not self.visual[0][0].isdigit():
			print "not letter"
			self.char_let = " "
	#return 0/1 array of each letter representetation
	def flatten(self):
		return list(chain.from_iterable(self.visual))
	
	#return 0/1 array of each letter representetation, randomly noised
	def noised(self, noise):
		to_ret = list(chain.from_iterable(self.visual))
		rand_positions = []
		for x in range (noise):
			rand_positions.append (random.randint(0, self.rows*self.coloumns - 1))
		for x in rand_positions:
			if to_ret[x] == "0":
				to_ret[x] = "1"
			else:
				to_ret[x] = "0"
		return to_ret	

	def __str__ (self):
		return self.char_let

#class that represents perceptron (1-hidden layer neural network)
class NeuroNet:
	
	neurs_in_inp_layer = 48
	neurs_in_hid_layer = 37
	neurs_in_out_layer = 26
	learning_speed = 0.5

	def __init__(self):
		# inner walues of each neuron
		self.hidden_value = [] 
		self.output_value = [] 
		# output walues of each neuron
		self.hid_out = []
		self.output = []
		#weigts of synapses between each neuron
		self.hid_weight_array = []
		self.out_weight_array = []
		
		#initialize weigts of Synapses by random numbers
		for x in range(self.neurs_in_hid_layer):
			self.hid_weight_array.append([random.random()/20 for y in range(self.neurs_in_inp_layer)])

		for x in range (self.neurs_in_out_layer):
			self.out_weight_array.append([random.random()/20  for y in range(self.neurs_in_hid_layer)])

	# output function for each synapse
	def sigma (self, val):
		return 1/(1+exp(-val))

	#perceptron detection algorytm
	def start(self, array):		
		max_out = 0
		class_num = 0
		self.hid_out = []
		self.output = []
		self.hidden_value = [0]*self.neurs_in_hid_layer
		self.output_value = [0]*self.neurs_in_out_layer

		#if input value is 1, then initialize each synapse between input and hidden neurons
		for x in range(self.neurs_in_inp_layer):
			if array[x]=='1':				
				for y in range (self.neurs_in_hid_layer):
					self.hidden_value[y] += self.hid_weight_array[y][x]

		#initialize each synapse between hidden and output neurons, by each hidden-neuron value
		for x in range (self.neurs_in_hid_layer):
			self.hid_out.append(self.sigma(self.hidden_value[x]))
			for y in range (self.neurs_in_out_layer):
				self.output_value[y] += self.out_weight_array[y][x] * self.hid_out[x]
		
		# check all output neurons value. Which neuron value is biggest, that is our letter-class
		for x in range (self.neurs_in_out_layer):
			self.output.append(self.sigma(self.output_value[x]))

			if self.output[x] > max_out:
				max_out = self.output[x]
				class_num = x
		#return letter number (class) and 
		return class_num, max_out

	# error weight-correction (Backpropagation algoritnm) 
	def correct (self, class_num, array):
		sig_err_out = []
		sig_err_hid = []
		sig_err_sum = 0

		# correct synapse weigths, due to their outputs, and real calss value
		# there are a lot of maths, so just beleive, that it works
		for x in range (self.neurs_in_out_layer):
			this_class = 0
			if class_num == x:
				this_class = 1
			sig_err_out.append(self.output[x] * (1 - self.output[x]) * (this_class - self.output[x]))
			for y in range (self.neurs_in_hid_layer):
				self.out_weight_array[x][y] += self.learning_speed * sig_err_out[x] * self.hid_out[y]

		for x in range (self.neurs_in_hid_layer):	
			for y in range (self.neurs_in_out_layer): 
				sig_err_sum += sig_err_out[y] * self.out_weight_array[y][x] 

			sig_err_hid.append(self.hid_out[x] * (1 - self.hid_out[x]) * sig_err_sum) 
			for y in range (self.neurs_in_inp_layer):
				self.hid_weight_array[x][y] += self.learning_speed * sig_err_hid[x] * int (array[y]) 

#function to learn clear/noised letters in iterative/random order
def LearnLetters (letters_dict, noised=0, IsRandom=False):
	errs = 0
	true_class = -1
	ASCII_A = 65
	ASCII_Z = 65+25
	# walk trough alphabet iteratively ()
	for x in range (ASCII_A, ASCII_Z+1):
		if IsRandom:
			rand_ascii = random.randint(ASCII_A, ASCII_Z+1)
			let = chr(rand_ascii)
			true_class = rand_ascii - ASCII_A
		else:
			let = chr(x) #letter from ascii
			true_class += 1

		letter_arr = letters_dict[let].noised(noised)
		# feed to our network each letter
		class_num, max_out = perceptron.start(letter_arr)
		print noised, " !!!!", true_class, let

		#repeat this until it will return true output value, and perceptron will be shure, that it is right letter
		while class_num != true_class or max_out < 0.7:
			errs += 1
			print class_num, max_out
			perceptron.correct(true_class, letter_arr)
		
			letter_arr = letters_dict[let].noised(noised)
			class_num, max_out = perceptron.start(letter_arr)
	return errs
		

#reading part
f = open('./ABC_template.txt')
input_arr = f.readlines()
f.close()
f = open('./Neural_Homework.txt')
detecting_arr = f.readlines()
f.close()

letters_dict = {}
letters_to_detect = []
perceptron = NeuroNet()

for string in input_arr:
	#input string slicing due to its file format
	letters_dict[string[0]] = Letter(string[3::2], string[0])

for string in detecting_arr:
	#input string slicing due to its file format
	letters_to_detect.append(Letter(string[::2]))


##############################
##learning
##############################
errs = 1
while errs:
	errs = 0
	errs += LearnLetters (letters_dict)
	errs += LearnLetters (letters_dict, IsRandom=True)
	

for noise in range (1,15):
	errs = 1
	while errs:
		errs = 0
		errs += LearnLetters (letters_dict, noised = noise, )
		errs += LearnLetters (letters_dict, noised = noise, IsRandom=True)

##############################
##detection
##############################
for x in range (letters_to_detect.__len__()):
	if letters_to_detect[x].char_let != " ":
		class_num, max_out = perceptron.start(letters_to_detect[x].flatten())
		rec_let = chr(class_num + 65)
		letters_to_detect[x].char_let = rec_let
	print letters_to_detect[x]
