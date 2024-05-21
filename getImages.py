
from queryTemps import humanIdQueryTemp, movieIdQueryTemp, personQueryTemp, movieQueryTemp
from data import image_json, graph
from getEntity import getEntity

behind_the_scenes = ["behind the scene", "behind the scenes"]
frame = ["frame", "still frame"]
publicity = ["publicity", "event"]
poster = ["poster"]
imageQuery = ["image", "images", "picture", "pictures", "look like", "looks like", "behind the scene", "behind the scenes", "frame", "still frame", "publicity", "event", "poster"]

class getImages:
    def __init__(self):
        pass

    def needImage(self, query):
        needImage = False
        ge = getEntity()
        tagged = ge.getTokens(query)
        for img in imageQuery:
            if img in query:
                needImage = True
            for pos_tag in tagged:
                if img in pos_tag[0]:
                    needImage = True
        return needImage
        
                
    
    #get people image by id
    def getPeopleImage(self, person):
        queryPersonId = humanIdQueryTemp.format(person)
        resPersonId = list(str(s) for s, in graph.query(queryPersonId))
        print("resPersonId:", resPersonId)
        return resPersonId
    

    #get image with movie and people
    def getPeopleAndMovieImage(self, persons, movies):
        queryPersonId = humanIdQueryTemp.format(persons[0])
        resPersonId = list(str(s) for s, in graph.query(queryPersonId))
        queryMovieId = movieIdQueryTemp.format(movies[0])
        resMovieId = list(str(s) for s, in graph.query(queryMovieId))
        movieList = []
        for id1 in resMovieId:
            movie = list(filter(lambda movie: id1 in movie['movie'], image_json))
            for id2 in resPersonId:
                if id2 in movie['cast']:
                    movieList.append(movie)
        return movieList


    #get image of movie: poster/ frame/ ...
    def getMovieImage(self, movie):
        queryMovieId = movieIdQueryTemp.format(movie)
        #resMovieId = list(graph.query(queryMovieId))
        resMovieId = list(str(s) for s, in graph.query(queryMovieId))
        print("resMovieId:", resMovieId)
        return resMovieId
    
    def getImage(self, resPersonId, resMovieId, movieList, relation):
        imgs = []
        #url = 'https://files.ifi.uzh.ch/ddis/teaching/2023/ATAI/dataset/movienet/images/'
        url = "image:"
        if relation in behind_the_scenes:
            imgs = self.getImg("behind_the_scenes",resPersonId, resMovieId, movieList)
        elif relation in frame:
            imgs = self.getImg("still_frame",resPersonId, resMovieId, movieList)
        elif relation in publicity:
            imgs1 = self.getImg("publicity",resPersonId, resMovieId, movieList)
            imgs2 = self.getImg("event",resPersonId, resMovieId, movieList)
            imgs = imgs1 + imgs2
        elif relation in poster:
            imgs = self.getImg("poster",resPersonId, resMovieId, movieList)
        else:
            if len(resMovieId)!=0:
                for idx,id in enumerate(resMovieId):
                    #img = 'https://www.imdb.com/title/'+resMovieId[idx]
                    for entry in image_json:
                        if resMovieId[idx] in entry["movie"]:
                            #print("resMovieId[idx]", resMovieId[idx])
                            image_link = entry["img"]
                            img = url + image_link
                            imgs.append(img.strip(".jpg"))
            elif len(resPersonId)!=0:
                for idx,id in enumerate(resPersonId):
                    #img = 'https://www.imdb.com/name/'+resPersonId[idx]
                    for entry in image_json:
                        if resPersonId[idx] in entry["cast"]:
                            #print("resPersonId[idx]", resPersonId[idx])
                            image_link = entry["img"]
                            img = url + image_link
                            imgs.append(img.strip(".jpg"))
        return imgs
    
    def getImg(self, relation, resPersonId, resMovieId, movieList):
        #url = 'https://files.ifi.uzh.ch/ddis/teaching/2023/ATAI/dataset/movienet/images/'
        url = "image:"
        imgs = []
        if len(movieList) != 0:
                for movie in movieList:
                    if movie['type'] == relation:
                        imgM = movie['img']
                        img = url + imgM
                        imgs.append(img.strip(".jpg"))
        elif len(resPersonId) != 0:
            for idx,id in enumerate(resPersonId):
                movies = list(filter(lambda movie: id in movie['cast'], image_json))
                for movie in movies:
                    if movie['type'] == relation:
                        imgM = movie['img']
                        img = url + imgM
                        imgs.append(img.strip(".jpg"))
        elif len(resMovieId) != 0:
            for idx,id in enumerate(resMovieId):
                movies = list(filter(lambda movie: id in movie['movie'], image_json))
                for movie in movies:
                    if movie['type'] == relation:
                        imgM = movie['img']
                        img = url + imgM
                        imgs.append(img.strip(".jpg"))
        return imgs