
from AppOpener import close, open as appopen
from webbrowser import open as webopen
from pywhatkit import search, playonyt
from dotenv import dotenv_values
from bs4 import BeautifulSoup
from rich import print
from groq import Groq
import webbrowser
import subprocess
import requests
import keyboard
import asyncio
import os

env_vars = dotenv_values(".env")
GroqAPIKey = env_vars.get("GroqAPIKey")

useragent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.75 Safari/537.36'

client = Groq(api_key=GroqAPIKey)

messages = []
SystemChatBot = [{"role": "system", "content": f"Hello, I am {os.getenv('Username', 'DefaultName')}, You're a content writer. You have to write content like a letter."}]

sess = requests.Session()  # Global session

def GoogleSearch(Topic):
    search(Topic)
    return True

def Content(Topic):
    def OpenNotepad(File):
        subprocess.Popen(['notepad.exe', os.path.abspath(File)])

    def ContentWriterAI(prompt):
        messages.append({"role": "user", "content": prompt})

        completion = client.chat.completions.create(
            model="mixtral-8x7b-32768",
            messages=SystemChatBot + messages,
            max_tokens=2048,
            temperature=0.7,
            top_p=1,
            stream=True
        )

        Answer = "".join(chunk.choices[0].delta.content for chunk in completion if chunk.choices and chunk.choices[0].delta.content)
        messages.append({"role": "assistant", "content": Answer})
        return Answer

    Topic = Topic.replace("Content ", "").strip()
    ContentByAI = ContentWriterAI(Topic)

    file_path = rf"Data\{Topic.lower().replace(' ', '')}.txt"
    with open(file_path, "w", encoding="utf-8") as file:
        file.write(ContentByAI)

    OpenNotepad(file_path)
    return True

def YouTubeSearch(Topic):
    webbrowser.open(f"https://www.youtube.com/results?search_query={Topic}")
    return True

def PlayYoutube(query):
    playonyt(query)
    return True

def OpenApp(app):
    try:
        appopen(app, match_closest=True, output=True, throw_error=True)
        return True
    except:
        def extract_links(html):
            soup = BeautifulSoup(html, 'html.parser') if html else None
            return [link.get('href') for link in soup.find_all('a', {'jsname': 'UWckNb'})] if soup else []

        def search_google(query):
            response = sess.get(f"https://www.google.com/search?q={query}", headers={"User-Agent": useragent})
            return response.text if response.status_code == 200 else None

        html = search_google(app)
        links = extract_links(html)

        if links:
            webopen(links[0])
        else:
            print("No links found for this app.")

        return True

def CloseApp(app):
    if "chrome" not in app:
        try:
            close(app, match_closest=True, output=True, throw_error=True)
            return True
        except:
            return False

def System(command):
    actions = {
        "mute": lambda: keyboard.press_and_release("volume mute"),
        "unmute": lambda: keyboard.press_and_release("volume mute"),
        "volume up": lambda: keyboard.press_and_release("volume up"),
        "volume down": lambda: keyboard.press_and_release("volume down")
    }
    actions.get(command, lambda: None)()
    return True



async def TranslateAndExecute(commands):
    funcs = []
    for command in commands:
        cmd_lower = command.lower()

        if cmd_lower.startswith("open "):
            funcs.append(asyncio.to_thread(OpenApp, cmd_lower.removeprefix("open ")))
        elif cmd_lower.startswith("close "):
            funcs.append(asyncio.to_thread(CloseApp, cmd_lower.removeprefix("close ")))
        elif cmd_lower.startswith("play "):
            funcs.append(asyncio.to_thread(PlayYoutube, cmd_lower.removeprefix("play ")))
        elif cmd_lower.startswith("content "):
            funcs.append(asyncio.to_thread(Content, cmd_lower.removeprefix("content ")))
        elif cmd_lower.startswith("google search "):
            funcs.append(asyncio.to_thread(GoogleSearch, cmd_lower.removeprefix("google search ")))
        elif cmd_lower.startswith("youtube search "):
            funcs.append(asyncio.to_thread(YouTubeSearch, cmd_lower.removeprefix("youtube search ")))
        elif cmd_lower.startswith("system "):
            funcs.append(asyncio.to_thread(System, cmd_lower.removeprefix("system ")))
        else:
            print(f"No Function Found for {command}")

    results = await asyncio.gather(*funcs)
    return results

async def Automation(commands):
    await TranslateAndExecute(commands)
    return True


