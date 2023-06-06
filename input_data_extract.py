##################
#IMPORTING REQUIRED LIBRARIES
##################
import arxiv
import pandas as pd
import string
import nltk
import random
import re
from nltk.corpus import wordnet
#nltk.download('stopwords')
#nltk.download('punkt')
#nltk.download('averaged_perceptron_tagger')
#nltk.download('wordnet')
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from nltk.tokenize import word_tokenize
from collections import Counter


# Initialize the lemmatizer
lemmatizer = WordNetLemmatizer()

'''adding keywords that should be present in the abstract'''
query = 'abs:"machine learning" OR abs:"neural networks" OR abs:"deep learning" OR abs:"artifical intelligence" OR abs:"deep neural network"  '

'''creating pandas dataframe to read the input file'''
df=pd.DataFrame(columns=["Research_title","Research_abstract","Research_category"])

'''Calling arxiv api to pull research title, abstracts and resaerch category  from the website and saving into dataframe '''
random.seed(0)
search=arxiv.Search(query=query,max_results=1400)
for item in search.results() :
        df=pd.concat([df, pd.DataFrame({'Research_title':[item.title],
                                        'Research_abstract':[item.summary.replace('\n',' ')],
                                        'Research_category':[item.primary_category]})],ignore_index=True)

'''Replacing next line with space and changing the extract to lowercase'''
df['Research_abstract']=df['Research_abstract'].str.replace('\n',' ',regex=True).str.replace(r'[^\w\s]+',' ',regex=True).str.lower()

'''removing stop words from abstracts using nltk library'''
stop_words=set(stopwords.words('english'))
df['Research_abstract'] = df['Research_abstract'].apply(lambda x: ' '.join([word for word in x.split() if word not in stop_words]))

'''lemmatizing the words in abstract using wordnetlemmatizer'''
lemmatizer = WordNetLemmatizer()
df['Research_abstract'] = df['Research_abstract'].apply(lambda x: lemmatizer.lemmatize(x))

'''removing numbers from the text data'''
df['Research_abstract'] = df['Research_abstract'].apply(lambda x: re.sub('\d+', '', x))


'''logic to remove arre words'''
#threshold for minimum term frequency
min_tf = 3
for i, abstract in enumerate(df['Research_abstract']):
    '''tokenizing the abstracts'''
    tokens = word_tokenize(abstract)   
    '''frequency count of each term'''
    freq = Counter(tokens)   
    '''creating a list of low frequency terms'''
    low_freq_terms = [term for term, count in freq.items() if count < min_tf]   
    '''removing low frequency terms from the abstract'''
    filtered_tokens = [token for token in tokens if token not in low_freq_terms]   
    filtered_abstract = ' '.join(filtered_tokens)   
    '''replacing the original abstract with the filtered abstract in the df'''
    df.at[i, 'Research_abstract'] = filtered_abstract
    
    
'''dropping research papers with resaerch title and resaerch abstracts are same'''
df=df[df['Research_abstract'].str.len() >=100]

'''Writing final pre-processed data to csv file for further consumption'''
df.to_csv('Input_csv.csv',sep='~',header=False,index=False)
