from data import image_json
from getAnswer import getAnswer
from getEntity import getEntity
from getRecommendation import getRecommendation
from getImages import getImages
import random

imageQuery = ["image", "images", "picture", "pictures", "look like", "looks like", "behind the scene", "behind the scenes", "frame", "still frame", "publicity", "event", "poster"]
answer_template = "Sorry, there seems no answer to your question. Please try to rephrase or simplify your question."



class processMessage:
    def __init__(self):
        pass

    def getFinalAnswers(self, message):
        hasImage = False
        needRecommendation = False
        gImg = getImages()
        if gImg.needImage(message):
            hasImage = True
        print(hasImage)
        gRec = getRecommendation()
        if gRec.needRecommend(message):
            needRecommendation = True
        print(needRecommendation)
        ga = getAnswer()
        relationList,relIds = ga.get_relation(message)
        ge = getEntity()
        entityList = ge.parseQuery(message)
        entList, entIds = ga.get_one_entity(message,relationList)
        res = []
        hasCrowd = False
        interAgreement, agreeAnswer, disagreeAnswer = 0, 0, 0
        if not hasImage:
            if not needRecommendation:
                if (len(relIds)!=0) and (len(entIds)!=0):
                    hasCrowd, interAgreement, agreeAnswer, disagreeAnswer, fixAns, originAnswer = ga.get_crowd(entIds, relIds)
                    print("hasCrowd:",hasCrowd)
                    print("interAgreement:",interAgreement)
                    res = ga.get_direct_res(relIds,entIds)
                    #if len(res)!=0: #embedding
                    if hasCrowd:
                        if disagreeAnswer > agreeAnswer:
                            fixKey = fixAns.keys()
                            if fixKey == "Subject":
                                entIds = fixAns["Subject"]
                                res = ga.get_direct_res(relIds,entIds)
                            elif fixKey == "Predicate":
                                relIds = fixAns["Predicate"]
                                res = ga.get_direct_res(relIds,entIds)
                            else:
                                res = []
                                res.append(fixAns["Object"])
                        else:
                            res = []
                            res.append(originAnswer)
                    if len(res)==0:
                        res = ga.get_embedding(relIds,entList)
                else:
                    answers = answer_template
                if len(res) == 0:
                    answers = answer_template
                else:
                    answers = ga.generate_answer(res)
            else:
                entList, entIds = ga.get_several_entities(message,relationList)
                answers = ga.getRecommendation(entList,entityList)
            print("answers:", answers)
        else:
            answers = ga.get_images(entList,message)
            #print("type",type(answers))
            if len(answers) == 0:
                answers = "Sorry, we can't find request image in our dataset"
                '''random_image = random.choice(image_json)["img"]
                random_image = "image:"+ random_image
                answers = random_image
                print(answers)'''
            else:
                img_url = answers[0]
                print(img_url)
                answers = []
                answers.append(img_url)
                answers.append("img_mark")
                #print(answers)

        return answers, hasCrowd, interAgreement, agreeAnswer, disagreeAnswer
