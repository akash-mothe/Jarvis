import pyttsx3
import speech_recognition as sr
import datetime
import time
import wikipedia
from pymongo import MongoClient
from pymongo import errors as mongoerror
import re
import sys
import os
import random
import webbrowser
import pywhatkit as kit
import math
import subprocess
import requests
import json

engine = pyttsx3.init('sapi5')
voices = engine.getProperty('voices')
engine.setProperty('voice', voices[0].id)
engine.setProperty('rate', 146)

def speak(audio):
    engine.say(audio)
    engine.runAndWait()

def take_command():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        print("Listening....")
        r.pause_threshold = 1
        r.energy_threshold = 350
        audio = r.listen(source)
        print(audio)

    try:
        print("Recognizing...")
        query = r.recognize_google(audio, language='en')
        print(f'Command: {query}\n')
    except Exception as e:
        print(e)
        return "None"
    return query

# ========================LOGIC FUNCTIONS==================

def wish_me():
    hour = int(datetime.datetime.now().hour)
    if hour >= 3 and hour < 12:
        t = "good morning"
    elif hour >= 12 and hour<17:
        t = "good afternoon"
    elif hour >= 17 and hour<21:
        t = "good evening"
    else:
        t = "good night"
    return t

def current_time():
    date_and_time = datetime.datetime.now()
    hour = date_and_time.strftime("%#I %#M %p")
    return f"It's {hour}"

def today_date():
    d = datetime.datetime.now().date()
    date = d.strftime("%d")
    month = d.strftime("%B")
    year = d.strftime("%Y")
    day = d.strftime("%A")
    lst = [date,month,year,day]
    return lst

def wiki_data(qu):
    client = MongoClient("localhost",27017)
    my_db = client['jarvis']
    collection = my_db['jarvis_data']
    try:
        summ = wikipedia.summary(qu, sentences = 2)
        p = re.sub(r"\([^()]*\)", "", summ)
        o_que = qu.replace("according to wikipedia", "")
        o_que = o_que.strip()
        print(p)
        speak(p)
        speak("Boss this is new for me, can I save it to my memory?")
        ask = take_command().lower()
        if 'save it' in ask:
            record = {"Question" : o_que, "Answer" : p}
            collection.insert_one(record)
            speak("OK boss, saved it.")
        else:
            speak("OK boss ask me anything.")
    except wikipedia.exceptions.PageError:
        speak("Sorry boss, I didn't found any results.")
    except wikipedia.exceptions.DisambiguationError:
        speak("Sorry boss, I didn't found any results.")     

def teach_jarvis():
    speak("OK boss, tell me the question first.")
    que = take_command().lower()
    speak("OK, then what is the answer.")
    ans = take_command().lower()
    client = MongoClient("localhost",27017)
    my_db = client['jarvis']
    collection = my_db['jarvis_data']
    record = {"Question" : que, "Answer" : ans}
    collection.insert_one(record)
    speak("Thank you boss, I will remember it.")

def memory_data(que):
    # if "" not in que:
    try:
        client = MongoClient("localhost",27017)
        my_db = client['jarvis']
        collection = my_db['jarvis_data']
        result = collection.find_one({"Question":que})
        if result:
            ans = result["Answer"]
            speak(ans)
        else:
            speak("")
    except TypeError:
        speak("Boss, Something went wrong to my memory.")

def calculator(query):
    try:
        query = query.replace("%"," percent")
        lst = query.split()
        numbers = []
        for i in lst:
            if i.isdigit():
                numbers.append(i)
        a = int(numbers[0])
        b = int(numbers[-1])
        if ("plus" in query) or ("add" in query) or ("+" in query):
            result = '%.2f'%(a+b)
            print(result)
            speak(f"It's {result}")
        elif ("minus" in query) or ("-" in query):
            result = '%.2f'%(a-b)
            print(result)
            speak(f"It's {result}")
        elif ("multiply" in query) or ("x" in query) or ("*" in query) or ("into" in query):
            result = '%.2f'%(a*b)
            print(result)
            speak(f"It's {result}")
        elif ("divided" in query) or ("divide" in query):
            result = '%.2f'%(a/b)
            print(result)
            speak(f"It's {result}")
        elif ("square root" in query):
            result = math.sqrt(b)
            print(result)
            speak(f"It's {result}")
        elif ("square of" in query):
            result = b*b
            print(result)
            speak(f"It's {result}")
        elif ("percent of" in query) or ("%" in query) or ("percentage of" in query):
            result = (a*b)/100
            print(result)
            speak(f"It's {result}")
    except:
        speak("Boss i am getting wrong input, Please try again.")

def launch_apps(query):
    try:
        if ('notepad' in query):
            speak("sure boss, opening notepad.")
            subprocess.Popen('notepad.exe')
        elif ('chrome' in query):
            speak("sure boss, opening chrome.")
            subprocess.Popen('C:\\Program Files (x86)\\Google\\Chrome\\Application\\chrome.exe')
        elif ('vs code' in query):
            speak("sure boss, opening vs code.")
            subprocess.Popen('C:\\Users\\LENOVO\\AppData\\Local\\Programs\\Microsoft VS Code\\Code.exe')
        elif ('cmd' in query):
            speak("sure boss, opening cmd.")
            subprocess.Popen('C:\\WINDOWS\\system32\\cmd.exe')
        elif ('whatsapp' in query):
            speak("sure boss, opening whatsapp.")
            subprocess.Popen('C:\\Users\\LENOVO\AppData\\Local\WhatsApp\\WhatsApp.exe')
        elif ('microsoft edge' in query):
            speak("sure boss, opening microsoft edge.")
            subprocess.Popen('C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe')
        elif ('paint' in query):
            speak("sure boss, opening paint.")
            subprocess.Popen('mspaint.exe')
    except:
        speak("Boss i got wrong application name.")

def get_weather():
    api_add = "http://api.openweathermap.org/data/2.5/weather?appid=b23304f177068b867afd1929e4e12952&q=Mehkar"

    data = requests.get(api_add).json()
    desc = data['weather'][0]['description']
    mtemp = data['main']['temp_min']-273.15
    min_temp = "{:.2f}".format(mtemp)
    mxtemp = data['main']['temp_max']-273.15
    max_temp = "{:.2f}".format(mxtemp)
    speak(f"There are {desc} outside. Minimum temperature is {min_temp} degree celcius, and Maximum temperature is {max_temp} degree celcius.")

def get_news():
    try:
        api_url = requests.get("http://newsapi.org/v2/top-headlines?country=in&category=technology&apiKey=5b8541c9b0154f8fae017663f6dcb314")
        data = json.loads(api_url.content)
        news_count = data['totalResults']
        speak(f"Boss, i got total {news_count} letest news.")
        speak('how many you want.')
        news_no = take_command().lower()
        news_no = int(news_no[0])
        all_news = {}
        speak("Sure boss, Here is the Headlines.")
        for i in range(news_no):
            titles = data['articles'][i]['title']
            titles = titles.split("-")
            desc = data['articles'][i]['description']
            speak(f"News {i+1}: {titles[0]}")
            all_news[titles[0]] = desc
        speak('Boss, do you want description of any news')
        ask_desc = take_command().lower()
        if ("yes" in ask_desc):
            speak("Ok, tell me which news you want.")
            keyword = take_command().lower()
            for key,value in all_news.items():
                if keyword in key.lower():
                    speak("Sure boss, here is the description.")
                    speak(value)
                else:
                    speak("Sorry boss, there is no news like that.")
    except ValueError:
        speak("Boss i got wrong input please try again.")



# ==========================LOOPING=====================
def execute_task():
    while True:
        query = take_command().lower()
        if 'hello jarvis' == query:
            speak("Hello bosss, How may I help you?")
        elif 'hi jarvis' == query:
            speak("Yes bosss, how may I help you?")
        elif ('jarvis' == query):
            speak("Yessss bossss.")
        elif (wish_me() in query):
            speak(f"{wish_me()} bosss.")
        elif 'time' in query:
            speak(current_time())
        elif 'who are you' in query:
            speak("I am your jarvis sir.")
        elif ("how are you" in query):
            speak("I am fine boss, I hope you are also fine.")
        elif ("i am also fine" in query) or ("i am fine" in query):
            speak("nice to hear it, from you boss.")
        elif ('who am i' in query):
            speak("You are my boss.")
        elif "what are you doing" in query:
            speak("Making your work simple, sir.")
        elif ("who made you" in query) or ("who is your owner" in query):
            speak("My boss ak. And he still teaching me a new things.")
        elif ('nice' in query) or ('very good' in query):
            speak("Thank you bosssss.")
        elif ('thank you jarvis' in query) or ('thank you' in query):
            speak("I am always here for you bossss.")
        elif ("today's date" in query) or ("today date" in query) or ("date of today" in query):
            speak(f"It's {today_date()[0]} {today_date()[1]} {today_date()[2]}")
        elif ("day of today" in query):
            speak(f"It's {today_date()[3]} sir.")
        elif ("my birthday" in query) or ("my birth date" in query):
            speak("I will wish you on 8 may")
        elif ("wikipedia" in query):
            wiki_data(query)
        elif ("want to teach you" in query) or ("learn something new" in query):
            teach_jarvis()
        elif ("take a note" in query) or ("write a note" in query) or ("make a note" in query):
            speak("Please tell me the note boss.")
            note = take_command()
            f = open("note.txt", "a")
            f.write(f"=> {note}.\n")
            f.close()
            speak("Done boss.")
        elif ("last note" in query):
            fr = open("note.txt","r")
            note_list = fr.readlines()
            last_line = note_list[-1]
            speak("boss your last note is,")
            speak(last_line)
            fr.close()
        elif ("play music" in query):
            folder_path = "A:\\musics\\Medium_Hindi"
            songs = os.listdir(folder_path)
            song = random.choice(songs)
            os.startfile(os.path.join(folder_path,song))
            speak("OK boss playing music.")
        elif ("search on google" in query):
            speak("Sure sir, what should I search on google.")
            ser = take_command()
            speak("OK boss, opening google.")
            webbrowser.open('https://google.com/?#q=' + ser)
        elif ("search on youtube" in query) or ("open youtube" in query) or ("play on youtube" in query):
            speak("Sure sir, what should I play on youtube.")
            ser = take_command()
            if "" not in ser:
                speak("OK boss, opening youtube.")
                kit.playonyt(ser)
                webbrowser.open('https://www.youtube.com/results?search_query=' + ser)
            else:
                speak("Boss you didn't tell me what should i play on youtube.")
        elif ("calculate" in query):
            calculator(query)
        elif ("launch" in query) or ("open" in query):
            launch_apps(query)
        elif ("weather" in query):
            get_weather()
        elif ('latest news' in query) or ("today's news" in query) or ("todays news" in query) or ("today news" in query) or ("current news" in query):
            get_news()


        elif("close the window" in query) or ("close window" in query):
            speak("OK boss, which window should I close.")
            win_name = take_command().lower()
            os.system(f"taskkill/im {win_name}.exe")
            speak(f"{win_name} has been closed")
        elif ("sleep now" in query) or ("keep quiet" in query) or ("keep silence" in query) or ("go to sleep" in query) or ("go to the sleep" in query):
            speak("OK boss, you can call me anytime.")
            break
        else:
            memory_data(query)

if __name__ == "__main__":
    while True:
        wake = take_command().lower()
        if "wake up" in wake:
            speak(f"{wish_me()} bosss, I am ready, how may i help you?")
            execute_task()
        elif "goodbye" in wake:
            speak("Thanks for using me boss, have a good day.")
            sys.exit()

        