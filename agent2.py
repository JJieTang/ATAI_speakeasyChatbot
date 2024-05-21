from speakeasypy import Speakeasy, Chatroom
from typing import List
import time
from processMessage import processMessage

DEFAULT_HOST_URL = 'https://speakeasy.ifi.uzh.ch'
listen_freq = 2

imageQuery = ["image", "images", "picture", "pictures", "look like", "looks like", "behind the scene", "behind the scenes", "frame", "still frame", "publicity", "event", "poster"]
answer_template = "Sorry, there seems no answer to your question. Please try to rephrase or simplify your question."

class Agent:
    def __init__(self, username, password):
        self.username = username
        # Initialize the Speakeasy Python framework and login.
        self.speakeasy = Speakeasy(host=DEFAULT_HOST_URL, username=username, password=password)
        self.speakeasy.login()  # This framework will help you log out automatically when the program terminates.

    def listen(self):
        while True:
            # only check active chatrooms (i.e., remaining_time > 0) if active=True.
            rooms: List[Chatroom] = self.speakeasy.get_rooms(active=True)
            for room in rooms:
                if not room.initiated:
                    # send a welcome message if room is not initiated
                    room.post_messages(f'Hello! This is a welcome message from {room.my_alias}.')
                    room.initiated = True
                # Retrieve messages from this chat room.
                # If only_partner=True, it filters out messages sent by the current bot.
                # If only_new=True, it filters out messages that have already been marked as processed.
                for message in room.get_messages(only_partner=True, only_new=True):
                    print(
                        f"\t- Chatroom {room.room_id} "
                        f"- new message #{message.ordinal}: '{message.message}' "
                        f"- {self.get_time()}")

                    # Implement your agent here #
                    try:
                        pM = processMessage()
                        answers, hasCrowd, interAgreement, agreeAnswer, disagreeAnswer = pM.getFinalAnswers(message.message)
                        if isinstance(answers, list):
                            if answers[-1]=="img_mark":
                                print("img_mark")
                                room.post_messages(f"I think this is the picture you want {answers[0]}")
                                #room.post_messages(f"![Image]({answers[0]})")
                            else:
                                if hasCrowd:
                                    answersCrowd = answers[0] + f" - according to the crowd, who had an inter-rater agreement of {interAgreement} in this batch. The answer distribution for this specific task was {agreeAnswer} support votes and {disagreeAnswer} reject vote."
                                    room.post_messages(f"{answersCrowd}")
                                else:
                                    answers = ' or '.join(answers)
                                    room.post_messages(f"I think it is {answers}")
                        else:
                            if hasCrowd:
                                answersCrowd = answers[0] + f" - according to the crowd, who had an inter-rater agreement of {interAgreement} in this batch. The answer distribution for this specific task was {agreeAnswer} support votes and {disagreeAnswer} reject vote."
                                room.post_messages(f"{answersCrowd}")
                            else:
                                room.post_messages(f"{answers}")
                    except:
                        room.post_messages(f"Sorry, there seems no answer to your question. Please try to rephrase or simplify your question.")
                    
                    
                    # Send a message to the corresponding chat room using the post_messages method of the room object.
                    #room.post_messages(f"Received your message: '{message.message}' ")
                    # Mark the message as processed, so it will be filtered out when retrieving new messages.
                    room.mark_as_processed(message)

                # Retrieve reactions from this chat room.
                # If only_new=True, it filters out reactions that have already been marked as processed.
                for reaction in room.get_reactions(only_new=True):
                    print(
                        f"\t- Chatroom {room.room_id} "
                        f"- new reaction #{reaction.message_ordinal}: '{reaction.type}' "
                        f"- {self.get_time()}")

                    # Implement your agent here #

                    room.post_messages(f"Received your reaction: '{reaction.type}' ")
                    room.mark_as_processed(reaction)

            time.sleep(listen_freq)

    @staticmethod
    def get_time():
        return time.strftime("%H:%M:%S, %d-%m-%Y", time.localtime())


if __name__ == '__main__':
    demo_bot = Agent("toast-grandioso-muffin_bot", "xe24VAObYWcBIQ")
    demo_bot.listen()