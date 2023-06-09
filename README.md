# Using_LSH_document_similarity
This project uses Locality sensitive hashing to find similar research papers.
The objective is to identify similar research papers using the LSH technique based on their research abstracts through a distributed processing approach. To reduce the computational effort, the MinHash method is used to map high-dimensional text data into a small signature matrix. Candidates generated from the LSH method can be verified using the Jaccard similarity test for
false positives and false negatives.
<br>
Following is the list of scripts and a short decription as used in the project:
<br>
<1> input_data_extract.py : This script uses Arxiv public api and extracts resaerch paper abstracts of random research papers available on Arxiv website. The scrpit also includes various pre-processing stpes and write the final cleaned dataframe as output csv file.
<br>
<2> jaccard_sim.py : The jacaard_similarity.py script calculates Jaccard similarity score for different document pairs. Creation of shingles is handled in the mapper module and calculation of Jaccard score on the generated shingles is carried out in the reducer.
<br>
<3>  Below is the summarized view of how mapper and reducer implementation was done for LSH in the code lsh.py:
* Splitting in shingles : The first mapper get shingles reads the input file line by line and breaks down each line into k -sized shingles. It generates the key as ’None’ and value as concat(Research title +‘ ‘+ category, shingles), the key is kept as ’None’ so that all shingles for all research papers go in the same reducer. reducer vocabulary takes list titles and abstracts from the first mapper and generates vocabulary for all the shingles and writes the output as a JSON.gzip file. The file is compressed to save space and send the vocabulary to each mapper in the next step.
* Creation of vocabulary : Each mapper one hot gets the compressed vocabulary from reducer vocabulary, decompresses it and uses it to generate one-hot encoding for shingles for each research paper. Since the generation of one-hot encoding is computation intensive the logic for one-hot encoding was applied in the mapper. Key value pair generated by mapper get shingles is (research title, bit-vector).combiner one hot collects key value pairs from previous mapper and then passes it to reducer one hot.reducer one hot collects bit-vector for every research title and generates key value pair as (research title, bit-vector).
* Creation of MinHash signature : In mapper signature MinHash signature is created for every research title, the create signature function uses a bit vector for each research paper. The mapper signature creates a key-value pair as (research title, signature).
* Creation of signature bands : mapper bands divided each signature into equal-sized bands. The mapper generates key values as (research
titles, and bands). reducer bands collects a list of bands for every research title and generates key-value pairs as (research title,bands). The mapper candidate pair takes key value pair from reducer bands and creates key value pair as (None,(research title,list of bands)).
* Comparison of bands and finding candidate pairs : In reducer candidate pair different combinations of research papers are created and their bands are compared for similarity. If even one band matches between two research papers, they are considered candidate pairs. The reducer5 generates the sum of all matched bands and returns the key-value pair as (research title, sum(matchedbands)).


Steps to follow for running the code:

1> To run the data extarction and data pre-processing script run below command:
python3 input_data_extract.py

2> Next, to run the mapreduce sccript on hadoop change the value of k,n_funcs and bands in the script and run the code as follows:
python3 lsh.py -r hadoop Input_csv.csv --output hdfs://localhost:54310/output/

Point to note : 
The vocabulary  when changing value of k size gets updated when executed in local mode.

For hadoop mode, code will fail at mapper 3 while creating one_hot_encode. 
Steps to update the code:

>>Uncompress the vocabulary -> gunzip vocabulary.json.gz

>>Get the last index of dictionary -> tail vocabulary.json
			
>>Update size with index+1
			
>>Rerun the code

3> To calculate the jaccard score for the input file run below command. value of k can be changes if required.
python3 jaccard_sim.py Input_csv.csv --output hdfs://localhost:54310/jaccard_score/

4> Download the output files for lsh.py and jaccard_sim from hdfs to local fo rfurther comparison.
/usr/local/hadoop/bin/hdfs dfs -copyToLocal hdfs://localhost:54310/output/
/usr/local/hadoop/bin/hdfs dfs -copyToLocal hdfs://localhost:54310/jaccard_score/
