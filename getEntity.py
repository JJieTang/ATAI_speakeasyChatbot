from transformers import pipeline
import re
from rdflib.namespace import Namespace
from transformers import AutoTokenizer
from transformers import AutoModelForTokenClassification
from data import ent2id,ent2lbl,lbl2ent,id2ent,entity_emb
import sklearn
from sklearn.metrics import pairwise_distances
import spacy
import nltk
from queryTemps import EntURIQueryTemp

model = AutoModelForTokenClassification.from_pretrained("dbmdz/bert-large-cased-finetuned-conll03-english")
tokenizer = AutoTokenizer.from_pretrained("bert-base-cased")
ner = pipeline('ner', model=model, tokenizer=tokenizer)


WD = Namespace('http://www.wikidata.org/entity/')

class getEntity:
    def __init__(self):
        pass

    def getTokens(self, query):
        tokens = nltk.word_tokenize(query)
        tagged = nltk.pos_tag(tokens)
        print("tagged:", tagged)
        return tagged
    
    def parseQuery(self, query):
        entities = ner(query, aggregation_strategy="simple")
        entList = [ent["word"] for ent in entities]
        for idx,ent in enumerate(entList):
            if "##" in ent:
                entList[idx-1] = entList[idx-1] + entList[idx][2:]
                entList.remove(ent)
        print(entList)
        return entList
    
    def getEntURI(self, graph, entity):
        EntURIQuery = EntURIQueryTemp.format(entity)
        entURIList = list(graph.query(EntURIQuery))
        entURIs = [str(entURI[0]) for entURI in entURIList]
        return entURIs
    
    def getEntID(self, entURI):
        entId = []
        if WD in entURI:
            wdIdPattern = "{}(.*)".format(WD)
            entId = re.search(wdIdPattern, entURI).group(1)
        return entId

    def getNearestEntEmb(self,word):
        ent = ent2id[lbl2ent[word]]
        emb = entity_emb[ent]
        dist = pairwise_distances(emb.reshape(1, -1), entity_emb).reshape(-1)
        most_likely = dist.argsort()
        qids = []
        lbls = []
        for rank, idx in enumerate(most_likely[:10]):
            qids.append(id2ent[idx][len(WD):])
            lbls.append(ent2lbl[id2ent[idx]])
        return qids,lbls
    
    def getFarestEntEmb(self, word):
        ent = ent2id[lbl2ent[word]]
        emb = entity_emb[ent]
        dist = pairwise_distances(emb.reshape(1, -1), entity_emb).reshape(-1)
        most_likely = dist.argsort()
        qids = []
        lbls = []
        for rank, idx in enumerate(most_likely[-10:]):
            qids.append(id2ent[idx][len(WD):])
            lbls.append(ent2lbl[id2ent[idx]])
        return qids,lbls