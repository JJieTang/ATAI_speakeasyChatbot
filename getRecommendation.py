from getEntity import getEntity
from queryTemps import movieGenreQueryTemp
from data import graph

needRec = ["recommend", "Recommend", "similar", "like", "resembling", "akin to", "comparable to", "analogous to"]

class getRecommendation:
    def __init__(self):
        pass
    
    def needRecommend(self, query):
        ge = getEntity()
        tagged = ge.getTokens(query)
        for pos_tag in tagged:
            for word in needRec:
                if word in pos_tag[0]:
                    return True

    def getGenre(self, movie):
        movieGenreQuery = movieGenreQueryTemp.format(movie)
        res = set(graph.query(movieGenreQuery))
        genre = [str(s) for s, in res]
        return genre


    #given movie to get similar recommendation
    def getSimilarMovie(self, movie):
        similarMovie = []
        genre1 = self.getGenre(movie)
        ge = getEntity()
        qids,lbls = ge.getNearestEntEmb(movie)
        for lbl in lbls:
            genre2 = self.getGenre(lbl)
            for genre in genre1:
                if genre in genre2:
                    similarMovie.append(lbl)
        return similarMovie


