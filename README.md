# Using_LSH_document_similarity
This project uses Locality sensitive hashing to find similar research papers.
The objective is to identify similar research papers using the LSH technique based on their research abstracts through a distributed processing approach. To reduce the computational effort, the MinHash method is used to map high-dimensional text data into a small signature matrix. Candidates generated from the LSH method can be verified using the Jaccard similarity test for
false positives and false negatives.
