from speakeasypy import Speakeasy, Chatroom
from typing import List
import time
import data
from data import graph
from getEntity import getEntity
from getRelation import getRelation
import rdflib
from data import all_films_list, get_correct_film_name
from queryTemps import directQueryTemp, embeddingQueryTemp, entIdQueryTemp
from getImages import getImages
from personOrMovie import personOrMovie
from getRecommendation import getRecommendation
from data import crowd
from data import answers
from sklearn.metrics import cohen_kappa_score
import numpy as np


imageQuery = ["image", "images", "picture", "pictures", "look like", "looks like", "behind the scene", "behind the scenes", "frame", "still frame", "publicity", "event", "poster"]

class getAnswer:
    def __init__(self):
        pass
        
    def get_relation(self, query):
        relURIs = []
        relIDs = []
        gr = getRelation()
        relationList = gr.parseQuery(query)
        print("relationList:",relationList)
        for relation in relationList:
            relURIs = gr.getRelURI(graph, relation)
            print("relURIs:",relURIs)
            if len(relURIs) != 0:
                relIDs = gr.getRelId(relURIs)
            else:
                print("relURI does not exist.")
                relIDs = gr.searchAlias(relation)
        print("relIDs:",relIDs)
        return relationList,relIDs
    
    def get_one_entity(self, query, relationList):
        entList = []#parse query and get entity
        entIds = []
        ge = getEntity()
        entURIs = []
        entityList = ge.parseQuery(query)
        for entity in entityList:
            for relation in relationList:
                if entity in relation:
                    entityList.remove(entity)
        print("entityList:",entityList)
        if len(entityList) == 1:
            entURI1 = ge.getEntURI(graph, entityList[0])
            if len(entURI1) != 0: 
                entList.append(entityList[0])
                for URI in entURI1:
                    entURIs.append(URI)
                    entIds.append(ge.getEntID(URI))
            else:
                entity = get_correct_film_name(entityList[0], all_films_list)#typo
                entURI3 = ge.getEntURI(graph, entity)
                if len(entURI3) != 0: 
                    entList.append(entity)
                    for URI in entURI3:
                        entURIs.append(URI)
                        entIds.append(ge.getEntID(URI))
        else:
            full_film_name = " ".join(entityList)
            entURI2 = ge.getEntURI(graph, full_film_name)
            if len(entURI2) == 0:
                ent = get_correct_film_name(full_film_name, all_films_list)#typo
                entURI4 = ge.getEntURI(graph, ent) # correct typo get 1 entity
                if len(entURI4) != 0: 
                    entList.append(ent)
                    for URI in entURI4:
                        entURIs.append(URI)
                        entIds.append(ge.getEntID(URI))
            else:
                entList.append(full_film_name)
                for URI in entURI2:
                    entURIs.append(URI)
                    entIds.append(ge.getEntID(URI))
        print("entList:",entList)
        print("entIds:",entIds)
        return entList, entIds
    
    def get_several_entities(self, query, relationList):
        entList = []#parse query and get entity
        entIds = []
        ge = getEntity()
        entURIs = []
        entityList = ge.parseQuery(query)
        for entity in entityList:
            for relation in relationList:
                if entity in relation:
                    entityList.remove(entity)
        print("entityList:",entityList)
        for entity in entityList:
            print("entity:", entity)
            entURI1 = ge.getEntURI(graph, entity)
            print("entURI1:", entURI1)
            if len(entURI1) != 0: 
                entList.append(entity)
                for URI in entURI1:
                    entURIs.append(URI)
                    entIds.append(ge.getEntID(URI))
            else:
                entityCorrected = get_correct_film_name(entity, all_films_list)#typo
                entURI2 = ge.getEntURI(graph, entityCorrected)
                if len(entURI2) != 0: 
                    entList.append(entityCorrected)
                    for URI in entURI2:
                        entURIs.append(URI)
                        entIds.append(ge.getEntID(URI))
        print("entList:",entList)
        print("entIds:",entIds)
        return entList, entIds
    
    def get_direct_res(self, relIds, entIds):
        res = set()
        directQuery = directQueryTemp.format(entIds[0],relIds[0])
        res = set(graph.query(directQuery))
        return res

    def get_embedding(self,relIds,entList):
        print("Using embedding!!!")
        ge = getEntity()
        qids,lbls = ge.getNearestEntEmb(entList[0])
        ans = set()
        for lbl in lbls:
            print("lbl:", lbl)
            embeddingQuery = embeddingQueryTemp.format(lbl,relIds[0])
            res = set(graph.query(embeddingQuery))
            print("res:,", res)
            for r in res:
                ans.add(r)
            #if len(res) != 0:
                #break
        return ans

    def generate_answer(self, res):
        answers = []
        print("res:",res)
        for row in res:
            if isinstance(row[0], rdflib.term.URIRef):
                #print(3)
                ge2 = getEntity()
                entId = ge2.getEntID(row[0])
                print("entID:", entId)
                entIdQuery = entIdQueryTemp.format(entId)
                entLabels = set(graph.query(entIdQuery))
                for entLabel in entLabels:
                    answers.append(str(entLabel.label))
            elif isinstance(row[0],rdflib.term.Literal):
                answers.append(str(row.objU))
            elif isinstance(row[0], str):
                #print("2")
                #print('wd:' in row[0])
                if ('wd:' in row):
                    #print("1")
                    entId = row.replace('wd:', "")
                    entIdQuery = entIdQueryTemp.format(entId)
                    entLabels = set(graph.query(entIdQuery))
                    for entLabel in entLabels:
                        answers.append(str(entLabel.label))
                else:
                    answers.append(row)
            else:
                #print(2)
                answers.append(str(row.objU))
        return answers
    
    def get_images(self, entList, query):
        images = []
        gi = getImages()
        pom = personOrMovie()
        hasPerson, hasMovie, persons, movies = pom.getPersonOrMovie(entList)
        relation = ""
        for img in imageQuery:
            if img in query:
                relation = img
        if hasPerson and hasMovie:
            movieList=[]
            resPersonId=[]
            resMovieId = []
            movieList = gi.getPeopleAndMovieImage(persons,movies)
            print("movieList:",movieList)
            imgs = gi.getImage(resPersonId, resMovieId, movieList, relation)
            for img in imgs:
                images.append(img)
        elif hasPerson:
            for person in persons:
                movieList=[]
                resPersonId=[]
                resMovieId = []
                resPersonId = gi.getPeopleImage(person)
                print("resPersonId:",resPersonId)
                imgs = gi.getImage(resPersonId, resMovieId, movieList, relation)
                for img in imgs:
                    images.append(img)
        elif hasMovie:
            for movie in movies:
                movieList=[]
                resPersonId=[]
                resMovieId = []
                resMovieId = gi.getMovieImage(movie)
                print("resMovieId:",resMovieId)
                imgs = gi.getImage(resPersonId, resMovieId, movieList, relation)
                for img in imgs:
                    images.append(img)
        return images

    def getRecommendation(self, entList, entityList):
        pom = personOrMovie()
        hasPerson, hasMovie, persons, movies = pom.getPersonOrMovie(entList)
        print("movies:", movies)
        gr = getRecommendation()
        tbr = []
        res = set()
        #recommendation = []
        for movie in movies:
            similarMovie = gr.getSimilarMovie(movie)
            for recommend in similarMovie:
                res.add(recommend)
            print("similarMovie:", similarMovie)
            #recommendation.append(similarMovie)
        recommendation = list(res)
        for entity in entityList:
            if entity in recommendation:
                recommendation.remove(entity)
        for entity in entList:
            if entity in recommendation:
                recommendation.remove(entity)
        return recommendation
    

    def get_crowd(self, entId, relId):
        hasCrowd = False
        interAgreement = 0
        agreeAnswer = 0
        disagreeAnswer = 0
        fixAns = {}
        fixPos = ["Subject", "Object", "Predicate"]
        originAnswer = ""
        for idx,row in crowd.iterrows():
            if (row.Input1ID == "wd:"+entId[0]) and (row.Input2ID == "wdt:"+relId[0]):
                hasCrowd = True
                print(hasCrowd)
                batch = row["HITTypeId"]
                print(batch)
                crowdId = row["HITId"]
                originAnswer = row["Input3ID"]
                print(crowdId)
                break
        if hasCrowd:
            interAgreement = self.get_inter_rater_agreement(batch)
            targetCrowd = crowd[crowd["HITId"] == crowdId]
            for idx,row in targetCrowd.iterrows():
                if row["AnswerLabel"] == "CORRECT":
                    agreeAnswer += 1
                else:
                    disagreeAnswer += 1
                    if (row["FixPosition"] in fixPos) and (row["FixValue"]!=None):
                        fixAns[row["FixPosition"]] = row["FixValue"]
        return hasCrowd, interAgreement, agreeAnswer, disagreeAnswer, fixAns, originAnswer
                
            
    def get_inter_rater_agreement(self, batch):
        ratings = answers[batch]
        #ratings_array = np.array(ratings)
        print("ratings:",ratings)
        kappa = self.fleiss_kappa(ratings)
        return kappa
    
    '''def fleiss_kappa(self, ratings_matrix):
        num_items, num_raters = ratings_matrix.shape
        print("num_items:", num_items)
        print("num_raters:", num_raters)
        categories = np.max(ratings_matrix) + 1  # Assumes ratings are 0-indexed

        # Calculate observed agreement
        observed_agreement = np.sum((np.sum(ratings_matrix, axis=1) - categories) ** 2)
        observed_agreement /= (num_items * (num_raters - 1))
        print("observed_agreement:", observed_agreement)

        # Calculate expected agreement
        p_bar = np.sum(ratings_matrix, axis=0) / (num_items * num_raters)
        expected_agreement = np.sum(p_bar ** 2)
        print("expected_agreement:", expected_agreement)

          # Calculate Fleiss' Kappa
        kappa = (observed_agreement - expected_agreement) / (1 - expected_agreement)

        return round(kappa,3)'''
    
    def fleiss_kappa(self, ratings_matrix):
        Pi_rec = []
        raters = 0
        for idx,rating in enumerate(ratings_matrix):
            print("rating:", rating)
            raters = np.sum(rating)
            sum = 0
            for idx2,rating2 in enumerate(rating):
                tempt = rating2 * (rating2-1)
                sum += tempt
            Pi = sum/(raters*(raters-1))
            Pi_rec.append(Pi)
        print("Pi_rec:", Pi_rec)
        P_bar = np.sum(Pi_rec)/len(ratings_matrix)
        print("P_bar", P_bar)
        Pj_rec = []
        for i in range(2):
            sum = 0
            for idx,rating in enumerate(ratings_matrix):
                sum += rating[i]
            Pj = sum/(raters*len(ratings_matrix))
            Pj_rec.append(Pj)
        Pe_bar = 0
        for i in range(len(Pj_rec)):
            Pe_bar += Pj_rec[i] * Pj_rec[i]
        print("Pe_bar", Pe_bar)
        kappa = (P_bar - Pe_bar)/(1 - Pe_bar)
        return round(kappa,3)



