import tkinter as tk
#from tkinter import messagebox, Text, Entry, Frame, Tk, Button
#print(tk.TkVersion)
import random
import re
from datetime import datetime
from collections import defaultdict
import db_speak2me as db

##### Country dictionary #####

# Basic Python Chatbot with Pattern Matching
class Talk2MeBot:
    def __init__(self):
        #Define username
        self.current_user = "username"
        self.nickname = None

        #Define countries, languieages, currencies
        self.countries = db.data["countries"]

        # Define conversation patterns and responses
        self.patterns = db.data[db.k_patterns]
        
        # Default responses when no pattern matches
        self.default_responses = db.data[db.k_default_responses]
    
    

    def set_nickname(self, re_result, user_input:str):
        ...


    def get_response(self, user_input):
        """
        Find the best response based on user input
        """
        user_input = user_input.lower().strip()
        

        # Check each pattern for matches
        for pattern, responses in self.patterns.items():
            re_result = re.search(pattern, user_input, re.IGNORECASE)
            if re_result:
                return random.choice(responses).format(
                    x = execute_expression(user_input),
                    date = date_and_time("%a %d %b %y"),
                    day = date_and_time("%A"),
                    month = date_and_time("%B"),
                    year = date_and_time("%Y"),
                    time = date_and_time("%H:%M:%S"),
                    user = self.current_user,
                    nick = self.set_nickname(re_result, user_input) #UNDERGOING DEVELOPMENT..
                    
                    )
        
        # Return default response if no pattern matches
        return random.choice(self.default_responses)
    

 


    def chat(self):
        """
        Start an interactive chat session
        """
        print("🤖 Talk2MeBot: Hello! I'm your Python chatbot. Type 'quit' to exit.")
        print("Try saying hello, asking for a joke, or just chatting!")
        print("-" * 50)
        
        while True:
            user_input = input("You: ")
            
            if user_input.lower() in ['quit', 'exit', 'bye']:
                print("🤖 Talk2MeBot: Thanks for chatting! Goodbye!")
                break
            
            response = self.get_response(user_input)
            print(f"🤖 Talk2MeBot: {response}")



#3. FEATURE DEVELOPER
#Add at least 2 extra features, such as:

#Tell the time (datetime)
def date_and_time(format="%a %d %b %Y, %H:%M"):    
    now = datetime.now()
    #print(now.strftime("%a %d %b %Y, %H:%M"))
    #print(now.strftime("%H:%M"))
    return now.strftime(format)


#Do simple math (2+2, 10*5)

def execute_expression(user_input):
    ex_calc = []
    print(":::::::::::::::::::::::::::::::::")
    for ex in extract_expression(user_input):
        ex_calc.append(f"{ex} = {math(ex)}")
    return "\n" + "\n".join(ex_calc)
    


def math(expression): #need to extract expression in user input
    r = None
    try:
        r = eval(expression)
    except:
        r = f"Could not evaluate: {expression}"
    return r
    

def extract_expression(user_input):

    valid_start = {"(", "-", "+", "."}
    valids = {"-", "+", "/", "*", "%", " ", "(", ")"}
    index_start, index_end = None, None
    expressions = []
    
    for i,c in enumerate(user_input):

        #collect start_index
        if index_start == None:
            if (c in valid_start or c.isdigit()):
                index_start = i

        #collect end_index
        if index_start != None and index_end == None:
            if (c not in valids and not c.isdigit()):
                index_end = i-1
            if (i == len(user_input) -1) and (c.isdigit() or c in valids):
                index_end = i+1

        #reset indicies for next expression
        if index_start != None and index_end != None:
            expressions.append(user_input[index_start:index_end])
            index_start, index_end = None, None

    return expressions


    #Remember the user’s name
    


# Create and run the chatbot
if __name__ == "__main__":
    bot = Talk2MeBot()
    bot.chat()



