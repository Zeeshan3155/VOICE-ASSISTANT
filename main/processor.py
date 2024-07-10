import datetime
import pyttsx3
import webbrowser
import AppOpener
from datetime import datetime
import json
import os
from groq import Groq
import threading
from queue import Queue


def groq_request(text):
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

    return response


class VoiceAssistant:
    def __init__(self):
        with open("variables.json") as fp:
            file_content = json.load(fp)
            self.websites = file_content['websites']
            self.phrases = file_content['phrases']
        self.response_queue = Queue()
        self.engine = pyttsx3.init()
        self.lock = threading.Lock()

    def __del__(self):
        self.engine.stop()

    def say(self, text):
        threading.Thread(target=self._speak, args=(text,)).start()

    def _speak(self, text):
        with self.lock:
            try:
                self.engine.say(text)
                self.engine.runAndWait()
            except Exception as e:
                print(e)

    def command(self, mic_text):
        try:
            if mic_text.lower() in list(self.websites.keys()):
                webbrowser.open(self.websites[mic_text.lower()])
                self.say(f"Opening {self.websites[mic_text.lower()]}")
                return f"Opening {self.websites[mic_text.lower()]}"

            elif "open app" in mic_text.lower():
                AppOpener.open(mic_text.lower()[9:])
                self.say(f"Opening app {mic_text.lower()[9:]}")
                return f"Opening app {mic_text.lower()[9:]}"

            elif "close app" in mic_text.lower():
                AppOpener.close(mic_text.lower()[10:])
                self.say(f"Closing app {mic_text.lower()[10:]}")
                return f"Closing app {mic_text.lower()[10:]}"

            elif "time" in mic_text.lower():
                time = datetime.now().strftime("The time is %H hours %M minutes")
                self.say(time)
                return time

            elif any(phrase.lower() == mic_text for phrase in self.phrases):
                bye_text = "Bye! It was nice chatting with you."
                self.say(bye_text)
                return bye_text

            else:
                response = groq_request(mic_text)
                self.say(response)
                return response

        except Exception as e:
            error_msg = f"Error processing command: {e}"
            self.say(error_msg)
            return error_msg
