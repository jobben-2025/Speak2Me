from datetime import time, date, datetime
from collections import defaultdict

#3. FEATURE DEVELOPER
#Add at least 2 extra features, such as:

#Tell the time (datetime)
now = datetime.now()
print(now.strftime("%a %d %b %Y, %H:%M"))
print(now.strftime("%H:%M"))



#Do simple math (2+2, 10*5)
intent_kw = {
    "joke": {"tell me a joke", "amuse me", "be funny"},
    "math": {"calc", "calculate", "eval", "evaluate", "math"}
}

def tell_a_joke(user_input):
    print("gay")


def execute_expression(user_input):
    print("math")
    e = extract_expression(user_input)
    print(e)


intent_response = {
    "joke": tell_a_joke,
    "math": execute_expression
}

expression_keys = {"calculate", "calc", "evaluate", "eval", "math"}
def run():
    while True:
        user_input = input("input:")
        r = check_intent(user_input, intent_kw)
        print(r)
        handle_intent(user_input, r, intent_response)


def math(expression): #need to extract expression in user input
    r = None
    try:
        r = eval(expression)
    except:
        r = f"Could not evaluate: {expression}"
    return r
    

def extract_expression(user_input):
    valid_start = {"-", "+", "."}
    valids = {"-", "+", "/", "*", "%"}
    index_start = None
    index_end = -1
    for i,c in enumerate(user_input):
        if index_start == None and (c in valid_start or c.isdigit()):
            index_start = i
        if index_end == -1 and (c not in valids and not c.isdigit()):
            index_end = i
    return user_input[index_start:index_end+1]

def my_sorting(the_item):
    return the_item[1]

def check_intent(user_input:str, intent_key:dict):
    scores = defaultdict(int)
    for k,v in intent_key.items():
        for kw in v:
            if kw in user_input:
                scores[k]+=1
    #return sorted(scores.items(), key=lambda v:v[1],reverse=True) #before ":" define parameter / after ":" using parameter
    return sorted(scores.items(), key=my_sorting,reverse=True) #before ":" define parameter / after ":" using parameter

def handle_intent(user_input:str, check_intent, intent_response:dict):
    for k,v in check_intent:
        if v > 0:
            intent_response[k](user_input)




run()


#Tell a joke


#Remember the user’s name