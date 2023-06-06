# Using_LSH_document_similarity
This project uses Locality sensitive hashing to find similar research papers.
The objective is to identify similar research papers using the LSH technique based on their research abstracts through a distributed processing approach. To reduce the computational effort, the MinHash method is used to map high-dimensional text data into a small signature matrix. Candidates generated from the LSH method can be verified using the Jaccard similarity test for
false positives and false negatives.
\b
Following is the list of scripts and a short decription as used in the project:
\b
1> jaccard_sim.py : The jacaard_similarity.py script calculates Jaccard similarity score for different document pairs. Creation of shingles is handled in the mapper module and calculation of Jaccard score on the generated shingles is carried out in the reducer.
