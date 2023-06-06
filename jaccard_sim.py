##################
#IMPORTING REQUIRED LIBRARIES
##################
from mrjob.job import MRJob
from mrjob.step import MRStep
from itertools import combinations

'''creating class for calcualting the jaccard similarity score for the documents'''
class Jaccard_similarity(MRJob):
    '''defining MRStep to assign mapper reducer calling order'''
    def steps(self):
        return [
            MRStep(mapper=self.mapper_get_shingles,
                   reducer=self.reducer_jaccard),
        ]

    '''function to calcualte Jaccard score'''
    def jaccard(self, a, b):
        return len(set(a).intersection(set(b))) / len(set(a).union(set(b)))

    '''Mapper function defined to break the research abstracts into k-sized shingles'''
    def mapper_get_shingles(self, _, line, k=2):
        title, abstract,category = line.split("~")
        shingles = []
        for item in abstract:
            tokens = abstract.split(" ")
            for i in range(len(tokens) - k + 1):
                shingle = " ".join(tokens[i:i + k])
                if shingle not in shingles:
                    shingles.append(shingle)
        yield None, (title+"~"+category,shingles)
        
        
    '''Reducer function to collect all shingles for each topic and create different combinations of rearch papers to calculate Jaccard similarity between the abstracts'''
    def reducer_jaccard(self, _, values):
        shingles_list = list(values)
        for pair in combinations(shingles_list, 2):
            title1, shingles1 = pair[0]
            title2, shingles2 = pair[1]         
            jaccard_score = self.jaccard(shingles1, shingles2)
            '''yielding research paper with jaccard score greater or equal to 0.5'''
            if jaccard_score >=0.5:
            	yield (title1, title2), round(jaccard_score,2)
           
if __name__ == '__main__':
    '''Calling the class'''
    Jaccard_similarity.run()
