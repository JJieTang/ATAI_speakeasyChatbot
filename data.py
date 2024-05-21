from rdflib.namespace import Namespace, RDF, RDFS, XSD
from rdflib.term import URIRef, Literal
import csv
import json
import networkx as nx
import pandas as pd
import rdflib
from collections import defaultdict, Counter
import locale
_ = locale.setlocale(locale.LC_ALL, '')
from _plotly_future_ import v4_subplots
from plotly.offline import download_plotlyjs, init_notebook_mode, plot, iplot
import plotly.graph_objs as go
init_notebook_mode(connected=True)
import plotly.io as pio
pio.renderers.default = 'jupyterlab+svg'
import re
import numpy as np
from sklearn.metrics import cohen_kappa_score
#import nltk
#from nltk.corpus import wordnet
#import pandas as pd

#nltk.download('wordnet')

graph = rdflib.Graph()
graph.parse('./data/14_graph.nt', format='turtle')


# prefixes used in the graph
WD = Namespace('http://www.wikidata.org/entity/')
WDT = Namespace('http://www.wikidata.org/prop/direct/')
SCHEMA = Namespace('http://schema.org/')
DDIS = Namespace('http://ddis.ch/atai/')

entities = set(graph.subjects()) | {s for s in graph.objects() if isinstance(s, URIRef)}
predicates = set(graph.predicates())
literals = {s for s in graph.objects() if isinstance(s, Literal)}
with_type = set(graph.subjects(WDT['P31'], None))
with_super = set(graph.subjects(WDT['P279'], None))
types = set(graph.objects(None, WDT['P31']))
supers = set(graph.objects(None, WDT['P279']))
with_label = set(graph.subjects(RDFS.label, None))

top250 = set(open('./data/imdb-top-250.t').read().split('\n')) - {''}

predURIList = list(predicates)
predWDTlist = []
predLblList = []

#generate synonyms of predicate labels
#predAliasDf = pd.DataFrame(columns=['predWDT','predLbl'])

for predURI in predURIList:
    wdtIdPattern = "{}(.*)".format(WDT)
    if re.search(wdtIdPattern, predURI):
        predWDT = re.search(wdtIdPattern, predURI).group(1)
        #print("predWDT:", predWDT)
        predWDTlist.append(predWDT)
        queryTemplate3 = '''
            prefix wdt: <http://www.wikidata.org/prop/direct/>
            prefix wd: <http://www.wikidata.org/entity/>
            
            SELECT ?relLbl WHERE{{
                wdt:{} rdfs:label ?relLbl.
                }}'''.format(predWDT)
        for s, in graph.query(queryTemplate3):
            predLbl = str(s) 
            #print("predLbl:", predLbl)
            predLblList.append(predLbl)
        #predAliasDf.loc[len(predAliasDf)]=[predWDT,predLbl]
#predAliasDf.to_csv("/Users/tangjie/Documents/23fall/AI/speakeasy-python-client-library/data/predAliasFile.csv")

#print(predAliasDf)
#print(predWDTlist)

#for predWDT in predWDTlist:
#   queryTemplate3 = '''
#            prefix wdt: <http://www.wikidata.org/prop/direct/>
#            prefix wd: <http://www.wikidata.org/entity/>
#            
#            SELECT ?relLbl WHERE{{
#                wdt:{} rdfs:label ?relLbl.
#                }}'''.format(predWDT)
#    for s, in graph.query(queryTemplate3):
#        predLbl = str(s) 
#        predLblList.append(predLbl)
#print(predLblList)
#predLblList_df = pd.DataFrame(predLblList,columns=["predicateLabel"])
#predLblList_df["predLabelSynonyms"] = None


#read alias csv file
alias = pd.read_csv("./data/predAliasFile2.csv")
#print(alias)
#print(alias.loc[79,'predWDT'])
for idx,alt in enumerate(alias['predAlias']):
    #alt.replace(", ",",")
    #print(idx)
    if isinstance(alt, str):
            alt = alt.replace(", ",",")
            alias.loc[idx,'predAlias'] = alt
            #listAlt = list(alt.split(','))
    #print('liatAlt:',listAlt)
    #print(alias.loc[idx,:])


#print(alias['predAlias'])


#get corect film name
all_films = {}
for film in graph.subjects(WDT.P345, None):
    film_label = graph.value(film, RDFS.label)
    if film_label and len(list(graph.objects(film, WDT.P57))) != 0:
        film_label_str = str(film_label)
        all_films[film] = film_label_str
all_films_list = list(all_films.values())
#print(all_films_list)

import fuzzywuzzy
from fuzzywuzzy import fuzz, process

def get_correct_film_name(input_name, all_films_list):
    match, score = process.extractOne(input_name, all_films_list)
    similarity_threshold = 100
    if score < similarity_threshold:
        return match
    else:
        return input_name
    
#input_file_name = "Star Wars The Masked Gang Cyprus"
#print(get_correct_film_name(input_file_name, all_films_list))

# load the embeddings
entity_emb = np.load('./data/entity_embeds.npy')
relation_emb = np.load('./data/relation_embeds.npy')

with open('./data/entity_ids.del', 'r') as ifile:
    ent2id = {rdflib.term.URIRef(ent): int(idx) for idx, ent in csv.reader(ifile, delimiter='\t')}
    id2ent = {v: k for k, v in ent2id.items()}
with open('./data/relation_ids.del', 'r') as ifile:
    rel2id = {rdflib.term.URIRef(rel): int(idx) for idx, rel in csv.reader(ifile, delimiter='\t')}
    id2rel = {v: k for k, v in rel2id.items()}
    
ent2lbl = {ent: str(lbl) for ent, lbl in graph.subject_objects(RDFS.label)}
lbl2ent = {lbl: ent for ent, lbl in ent2lbl.items()}


#images file
with open("./data/images.json", "r") as f:
    image_json = json.load(f)

#imbd250 
#file = open("/Users/tangjie/Documents/23fall/AI/speakeasy-python-client-library/data/imdb-top-250.t", "r")
#content = file.read()
#print(content)



##crowdsource
crowdSource = pd.read_csv('/Users/tangjie/Documents/23fall/AI/speakeasy-python-client-library/data/crowd_data_olat_P344FullstopCorrected.tsv', sep='\t')
#print(crowdSource)
#filter malicious worker
mask1 = crowdSource['WorkTimeInSeconds'] >= 20 #worker time
filtered_crowdSource1 = crowdSource[mask1]
filtered_crowdSource1['LifetimeApprovalRate'] = filtered_crowdSource1['LifetimeApprovalRate'].str.rstrip('%').astype('float') / 100.0 #life time approve rate
mask2 = filtered_crowdSource1['LifetimeApprovalRate'] >= 0.50
filtered_crowdSource2 = filtered_crowdSource1[mask2]
#print(filtered_crowdSource2)
crowd = filtered_crowdSource2
csv_file_path = '/Users/tangjie/Documents/23fall/AI/speakeasy-python-client-library/data/crowd.csv'
crowd.to_csv(csv_file_path,index=False)

#calculate the inter-rater agreement (Fleiss’ kappa) per batch
answers = {}
batches = crowd.HITTypeId.unique()
#print(batches)
for batch in batches:
    #print(batch)
    crowdB = crowd[crowd.HITTypeId == batch]
    tasks = crowdB.HITId.unique()
    if batch not in answers:
        answers[batch] = []
    for task in tasks:
        agreeN = 0
        disagreeN = 0
        #print(task)
        answer = []
        crowdT = crowdB[crowdB.HITId == task]
        #print(crowdT)
        for idx,row in crowdT.iterrows():
            #print(row)
            if row.AnswerLabel == "CORRECT":
                #answer.append(1)
                agreeN += 1
            else:
                #answer.append(0)
                disagreeN += 1
        answer.append(agreeN)
        answer.append(disagreeN)
        answers[batch].append(answer)
    #print(answers)


