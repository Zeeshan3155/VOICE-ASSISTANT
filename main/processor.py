import datetime
import sys

import pyttsx3
import win32com.client as win
import webbrowser
import AppOpener
from datetime import datetime
import json
import os
from groq import Groq
import threading
from queue import Queue

class VoiceAssistant:
    def __init__(self):
        with open("variables.json") as fp:
            file_content = json.load(fp)
            self.websites = file_content['websites']
            self.phrases = file_content['phrases']
            self.response_queue = Queue()
            self.engine = pyttsx3.init()

    def say(self, text):
        threading.Thread(target=self._speak, args=(text,)).start()
    def _speak(self,text):
        self.engine.setProperty('voice',r'HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Speech\Voices\Tokens\TTS_MS_EN-US_ZIRA_11.0')
        self.engine.say(text)
        self.engine.runAndWait()



    def groq_request(self, text):
        client = Groq(
            api_key=os.environ.get("API_KEY"),
        )

        chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "user",
                    "content": text,
                }
            ],
            model="llama3-8b-8192",
        )
        response = chat_completion.choices[0].message.content

        with open(f"logs\\{text}.txt", 'w') as fpp:
            fpp.write(response)

        return response


    def command(self, mic_text):
        print(f"user: {mic_text.lower()}")

        if mic_text.lower() in list(self.websites.keys()):
            print(f"response: Opening website {mic_text}")
            webbrowser.open(self.websites[mic_text.lower()])
            return f"Opening {self.websites[mic_text.lower()]}"

        elif "open app" in mic_text.lower():
            print(f"response: Opening app {mic_text[9:]}")
            AppOpener.open(mic_text.lower()[9:])
            return f"Opening app {mic_text.lower()[9:]}"

        elif "close app" in mic_text.lower():
            print(f"response: Closing app {mic_text[9:]}")
            AppOpener.close(mic_text.lower()[9:])
            return f"Closing app {mic_text.lower()[9:]}"

        elif "time" in mic_text.lower():
            time = datetime.now()
            print(f"The time is {time.strftime("%H")} hours {time.strftime("%M")} minutes")
            self.say(f"The time is {time.strftime("%H")} hours {time.strftime("%M")} minutes")
            return f"The time is {time.strftime("%H")} hours {time.strftime("%M")} minutes"

        elif any(phrase.lower() == mic_text for phrase in self.phrases):
            self.say("Bye! It was nice chatting with you. Feel free to come back anytime with more questions or just to say hi!")
            sys.exit()

        else:
            response = self.groq_request(mic_text)
            print(response)
            self.say(response)
            return response


'''if __name__ == '__main__':
    print('pycharm')
    voiceassistant = VoiceAssistant()
    voiceassistant.listen()'''