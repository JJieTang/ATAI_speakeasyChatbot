from processMessage import processMessage

query = "Recommend movies like Nightmare on Elm Street, Friday the 13th, and Halloween.  "
pM = processMessage()
answers, hasCrowd, interAgreement, agreeAnswer, disagreeAnswer = pM.getFinalAnswers(query)
if isinstance(answers, list):
    if answers[-1]=="img_mark":
        print("img_mark")
        #room.post_messages(f"I think this is the picture you want {answers[0]}")
        #room.post_messages(f"![Image]({answers[0]})")
    else:
        if hasCrowd:
            answersCrowd = answers[0] + f" - according to the crowd, who had an inter-rater agreement of {interAgreement} in this batch. The answer distribution for this specific task was {agreeAnswer} support votes and {disagreeAnswer} reject vote."
            #room.post_messages(f"{answersCrowd}")
            print(answersCrowd)
        else:
            answers = ' or '.join(answers)
            #room.post_messages(f"I think it is {answers}")
            print(answers)
else:
    if hasCrowd:
        answersCrowd = answers[0] + f" - according to the crowd, who had an inter-rater agreement of {interAgreement} in this batch. The answer distribution for this specific task was {agreeAnswer} support votes and {disagreeAnswer} reject vote."
        #room.post_messages(f"{answersCrowd}")
        print(answersCrowd)
    else:
        #room.post_messages(f"{answers}")
        print(answers)
