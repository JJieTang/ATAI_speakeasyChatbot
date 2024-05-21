import re
import nltk
from data import alias
import spacy
from queryTemps import RelURIQueryTemp

nlp = spacy.load("en_core_web_sm")

nltk.download('punkt')
nltk.download('averaged_perceptron_tagger')

from rdflib.namespace import Namespace
WDT = Namespace('http://www.wikidata.org/prop/direct/')

class getRelation:
    def __init__(self):
        pass

    def theOfQuery(self, query):
        theOfPattern = r'the ((\w+ )+)of'
        matched = False
        matching = []
        matches = re.search(theOfPattern, query, re.IGNORECASE)
        if matches:
            matching.append(matches.group(1))
        if len(matching) != 0:
            matched = True
        else:
            matched = False
        for m in range(len(matching)):
            if matching[m][-1] == " ":
                matching[m] = matching[m][:-1]
        return matched, matching
    
    def getVerbs(self, query):
        verbs = []
        tokens = nltk.word_tokenize(query)
        tagged = nltk.pos_tag(tokens)
        print("pos_tag:",tagged)
        for pos_tag in tagged:
            if "VB" in pos_tag[1]:
                verbs.append(pos_tag[0])
        print("verbs:", verbs)
        return verbs
    

    def parseQuery(self,query):
        matched, matching = self.theOfQuery(query)
        print("theOfPattern:",matching)
        print(matched)
        if matched == True:
            relations = matching
        else:
            verbs = self.getVerbs(query)
            relations = verbs
        print("original relations:",relations)
        return relations
    
    def getRelURI(self, graph, relation):
        relURIs = []
        RelURIQuery = RelURIQueryTemp.format(relation)
        relURIList = list(graph.query(RelURIQuery))
        print(relURIList)
        for relURI in relURIList:
            if WDT in str(relURI[0]):
                relURIs.append(relURI[0])
        return relURIs
    
    def getRelId(self, relURIs):
        relIDs = []
        for relURI in relURIs:
            wdtIdPattern = "{}(.*)".format(WDT)
            relId = re.search(wdtIdPattern, relURI).group(1)
            relIDs.append(relId)
        return relIDs
    
    def searchAlias(self,relation):
        wdtPredList = []
        for idx, alt in enumerate(alias['predAlias']):
            if isinstance(alt, str):
                listAlt = list(alt.split(','))
            if relation in listAlt:
                wdtPred = alias.loc[idx,'predWDT']
                wdtPredList.append(wdtPred)
        return wdtPredList
    