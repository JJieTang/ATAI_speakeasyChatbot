from queryTemps import personQueryTemp, movieQueryTemp
from data import graph

class personOrMovie:
    def __init__(self):
        pass

    def getPersonOrMovie(self, entList):
        hasPerson = False
        hasMovie = False
        persons = []
        movies = []
        for entity in entList:
            queryPerson = personQueryTemp.format(entity)
            resPerson = list(graph.query(queryPerson))
            queryMovie = movieQueryTemp.format(entity)
            resMovie = list(graph.query(queryMovie))
            if len(resPerson)>0:
                print("1")
                hasPerson = True
                persons.append(entity)
            if len(resMovie)>0:
                print("2")
                hasMovie = True
                movies.append(entity)
        return hasPerson, hasMovie, persons, movies