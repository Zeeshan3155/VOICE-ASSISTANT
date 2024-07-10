from kivy.lang import Builder
from kivymd.app import MDApp
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import MDFabButton
from kivymd.uix.scrollview import ScrollView
from kivy.animation import Animation
from kivy.metrics import dp
from kivymd.uix.card import MDCard
from kivy.clock import Clock
from kivy.uix.label import Label
from kivymd.uix.label import MDIcon
import speech_recognition as sr
from processor import VoiceAssistant
from concurrent.futures import ThreadPoolExecutor
from kivymd.uix.widget import MDWidget


voiceassistant = VoiceAssistant()
executor = ThreadPoolExecutor(max_workers=2)

KV = '''
Screen:
    BoxLayout:
        orientation: 'vertical'

        FloatLayout:
            ScrollView:
                MDList:
                    id: chat_list
                    canvas.before:
                        Color:
                            rgba: 0, 0, 0, 1
                        Rectangle:
                            pos: self.pos
                            size: self.size

            MDFabButton:
                id: mic_button
                icon: "microphone"
                pos_hint: {"center_x": 0.5, "y": 0.05}
                on_release: app.start_listening()
                theme_text_color: "Custom"
                text_color: 213, 235, 49, 9
                opposite_colors: True
                elevation_normal: 8
'''


class ChatBotApp(MDApp):
    def build(self):
        self.theme_cls.theme_style = "Dark"
        self.theme_cls.primary_palette = "Aliceblue"
        self.theme_cls.accent_palette = "Yellow"
        return Builder.load_string(KV)

    def start_listening(self):
        self.animate_button()
        future = executor.submit(self.listen)
        future.add_done_callback(self.on_listen_complete)

    def on_listen_complete(self, future):
        self.stop_animation()
        try:
            user_input, response = future.result()
            if len(user_input) == 0:
                Clock.schedule_once(lambda dt: self.add_message("Bot", response))
            else:
                Clock.schedule_once(lambda dt: self.add_message("User", user_input))
                Clock.schedule_once(lambda dt: self.add_message("Bot", response))

            if response == "Bye! It was nice chatting with you.":
                Clock.schedule_once(lambda dt: self.add_message("Bot", response))
                self.stop_app()
        except Exception as e:
            Clock.schedule_once(lambda dt, error_msg=f"Error: {e}": self.add_message("Bot", error_msg))

    @staticmethod
    def listen():
        recognizer = sr.Recognizer()
        try:
            with sr.Microphone() as source:
                print("Listening...")
                audio = recognizer.listen(source)
                try:
                    user_input = recognizer.recognize_google(audio)
                    response = voiceassistant.command(mic_text=user_input)
                    return user_input, response
                except sr.UnknownValueError:
                    voiceassistant.say("Sorry, I did not understand that.")
                    return "", "Sorry, I did not understand that."
                except sr.RequestError as e:
                    voiceassistant.say(f"Could not request results; {e}")
                    return "", f"Could not request results; {e}"
        except sr.WaitTimeoutError:
            return "", "Listening timed out while waiting for phrase to start."
        except Exception as e:
            return "", f"Error with microphone stream: {e}"

    def add_message(self, sender, message):
        try:
            chat_list = self.root.ids.chat_list
            text_color = (1, 1, 0, 1) if sender == "User" else (1, 1, 1, 1)

            card = MDCard(
                orientation='vertical',
                size_hint=(0.9, None),
                pos_hint={'center_x': 0.5},
                padding="8dp",
                elevation=8,
            )

            # Logo (using an MDIcon for a bot icon)
            icon_name = 'account' if sender == 'User' else 'robot-happy-outline'

            logo = MDIcon(
                icon=icon_name,
                size_hint=(None, None),
                size=(dp(40), dp(40)),  # Adjust size as needed
                theme_text_color="Custom",
                text_color=text_color,
            )

            # Horizontal layout for logo and sender label
            sender_layout = MDBoxLayout(
                orientation='horizontal',
                size_hint_y=None,
                height=logo.height,  # Match height with logo
                padding=(dp(8), dp(4)),  # Adjust padding as needed
            )

            sender_layout.add_widget(logo)

            message_label = Label(
                text=message,
                color=text_color,
                size_hint_y=None,
                text_size=(self.root.width * 0.9 - dp(16), None),
                padding=(dp(8), dp(4)),
                valign='top',
                halign='left',
            )

            spacer = MDWidget(size_hint_y=None, height=dp(8))

            message_label.bind(texture_size=message_label.setter('size'))
            message_label.bind(width=lambda instance, value: setattr(instance, 'text_size', (value, None)))

            card.add_widget(sender_layout)  # Add sender layout instead of sender_label directly
            card.add_widget(spacer)
            card.add_widget(message_label)

            def update_card_height(instance, value):
                card.height = sender_layout.height + message_label.height + dp(16)  # Adjust height calculation

            message_label.bind(size=update_card_height)
            card.height = sender_layout.height + message_label.height + dp(16)

            card.opacity = 0
            chat_list.add_widget(card)

            anim = Animation(opacity=1, duration=0.5)
            anim.start(card)
        except Exception as e:
            print(e)

    def animate_button(self):
        mic_button = self.root.ids.get('mic_button')
        if mic_button:
            self.button_animation = Animation(size=(dp(80), dp(80)), duration=0.5) + Animation(size=(dp(70), dp(70)),
                                                                                               duration=0.5)
            self.button_animation.repeat = True
            self.button_animation.start(mic_button)

    def stop_animation(self):
        mic_button = self.root.ids.get('mic_button')
        if mic_button and hasattr(self, 'button_animation'):
            self.button_animation.stop(mic_button)
            mic_button.size = (dp(70), dp(70))

    def stop_app(self):
        self.root.clear_widgets()
        self.get_running_app().stop()


if __name__ == "__main__":
    ChatBotApp().run()
