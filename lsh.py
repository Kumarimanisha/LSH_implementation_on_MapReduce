##################
#IMPORTING REQUIRED LIBRARIES
##################
import random
from mrjob.job import MRJob
from mrjob.step import MRStep
import string
from  itertools import combinations
import json
import gzip
'''creating class for implemeting LSH'''
class LSH(MRJob):
	random.seed(0)
	'''size of vocabulary'''
	size=7580
	'''number of hash functions'''
	n_funcs=500
	'''number of bands'''
	n_bands=20
	'''defining MRStep to assign mapper reducer calling order'''
	def steps(self):
		return [MRStep(mapper=self.mapper_get_shingles, reducer=self.reducer_vocabulary),
			MRStep(mapper=self.mapper_one_hot,combiner=self.combiner_one_hot, reducer=self.reducer_one_hot),
			MRStep(mapper_init=self.mapper_sig_init ,mapper=self.mapper_signature),
			MRStep(mapper_init=self.mapper_bands_init,mapper=self.mapper_bands, reducer=self.reducer_bands),
			MRStep(mapper=self.mapper_candidate_pair, reducer= self.reducer_candidate_pair)] 

	'''calls create_hash_function() initialization'''
	def mapper_sig_init(self):
		self.hash_functions = self.create_hash_functions(self.size, self.n_funcs)

	'''initializes number of bands per row for the mapper mapper_bands'''
	def mapper_bands_init(self):    
		self.n_rows = int(self.n_funcs / self.n_bands)
	'''STEP1: CREATION OF K_SHINGLES'''
	'''mapper to read input file and generate k-size shingles'''
	def mapper_get_shingles(self,_,line,k=5):
		title,abstract,category = line.split("~")
		shingles=[]
		for item in abstract:
			tokens=abstract.split(" ")
			for i in range(len(tokens) - k + 1):
				shingle = " ".join(tokens[i:i + k])
				if shingle not in shingles:
					shingles.append(shingle)
		yield None,(title+"~"+category,shingles)

	'''STEP2: CREATION OF VOCABULARY'''
	'''reducer function to create vocabulary'''
	def reducer_vocabulary(self,key,title_shingles):
		all_shingles=[]
		title_shingle_list=[]
		for topic ,shingles in title_shingles:
			for shingle in shingles:
				if shingle not in all_shingles:
					all_shingles.append(shingle)
			title_shingle_list.append((topic,shingles))
		yield None,(title_shingle_list)
		'''writes vocabulary as compressed gzip file'''
		vocabulary = {shingle: i for i, shingle in enumerate(sorted(all_shingles))}
		with gzip.open('/home/hduser/vocabulary.json.gz', 'wb') as f:
			f.write(json.dumps(vocabulary).encode('utf-8'))
		LSH.size=len(vocabulary)

	'''STEP3: CREATION OF ONE-HOT ENCODING'''
	'''mapper creates one hot encode for all the shingles'''
	def mapper_one_hot(self, key, value):
		'''reads vocabulary in mapper'''
		with gzip.open('/home/hduser/vocabulary.json.gz', 'rb') as f:
			vocabulary = json.loads(f.read().decode('utf-8'))
		for i,(res_paper, shingles) in enumerate(value):
			bit_vector = [0] * LSH.size
			for shingle in shingles:
				i = vocabulary[shingle]
				bit_vector[i] = 1
			yield (res_paper), bit_vector
			
	'''combiner to combine all the one-hot encoding for a resaerch apper before sending to reducer'''        
	def combiner_one_hot(self, key, values):
		bit_vectors = []
		for value in values:
			bit_vectors.append(value)
		combined = [sum(x) for x in zip(*bit_vectors)]
		yield key, combined

	'''reducer collects one-hot bit vector for all the titles'''
	def reducer_one_hot(self,key,value):
		value_list=list(value)
		yield key,value_list

	'''function to create hash_functions'''
	def create_hash_function(self,hash_size):
		hash_func=list(range(1,hash_size+1))
		random.shuffle(hash_func)
		return hash_func

	def create_hash_functions(self,size,n_funcs):
		hashes=[]
		for x in range(n_funcs):
			hash_function=self.create_hash_function(size)
			hashes.append(hash_function)
		return hashes

	'''function to create signature'''
	def create_signature(self,bit_vector,hash_functions):
		hash_signature = []
		for f in hash_functions:
			for i in range(1, len(bit_vector)+1):
				function_index = f.index(i)
				signature_val = bit_vector[function_index]
				if signature_val ==1:
					hash_signature.append(function_index)
					break
		return hash_signature

	'''STEP4: CREATION OF MINHASH SIGNATURES AND BANDS'''
	'''mapper to create signature'''
	def mapper_signature(self, res_paper, bit_vector):
		'''Create hash functions and generate signature'''
		hashes = self.hash_functions
		
		signature = self.create_signature(bit_vector[0], hashes)
		yield res_paper, signature

	'''mapper to divide signature into bands'''
	def mapper_bands(self, key, value):
		bands =[]
		for row in range(0, len(value), self.n_rows):
			band = list(value[row:row+self.n_rows])
			yield key,band

	'''reducer to collect bands for each title'''
	def reducer_bands(self,key,value):
		bands=list(value)
		yield key,bands

	'''STEP5: COMPARING BANDS FOR CANDIDATE PAIRS'''
	'''function to comapre two bands and increemnet matches by 1 if bands are similar'''
	def compare_bands(self, bands1, bands2):
		matches =0
		for s1 , s2 in zip(bands1, bands2):
				if s1 == s2:
					matches+= 1
		return matches

	def mapper_candidate_pair(self, key, value):
		yield None, (key, value)

	'''reducer to call compare_bands() for every research pairs and comapre the bands to find if there is any match and return the apir as candidate pair'''
	def reducer_candidate_pair(self, key, values):
		res_papers = []
		bands = []
		for res_paper, res_paper_bands in values:
			res_papers.append(res_paper)
			bands.append(res_paper_bands)
		
		for res_paper_bands1, res_paper_bands2 in combinations(res_papers, 2):
			matching_bands = self.compare_bands(bands[res_papers.index(res_paper_bands1)], bands[res_papers.index(res_paper_bands2)])
			if matching_bands > 0:
				yield  matching_bands, (res_paper_bands1, res_paper_bands2)


if __name__ == '__main__':
	'''Calling the LSH class'''
	LSH.run()
