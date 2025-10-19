import threading
import requests
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.label import Label


BACKEND_URL = 'http://127.0.0.1:5000'


class AssistantUI(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(orientation='vertical', spacing=8, padding=8, **kwargs)

        self.history = Label(text='Welcome to MobAI', size_hint_y=None, height=200)
        self.add_widget(self.history)

        self.input = TextInput(hint_text='Type a message...', size_hint_y=None, height=40)
        self.add_widget(self.input)

        send = Button(text='Send', size_hint_y=None, height=40)
        send.bind(on_press=self.on_send)
        self.add_widget(send)

    def on_send(self, instance):
        text = self.input.text.strip()
        if not text:
            return
        self.append_history(f'You: {text}')
        self.input.text = ''

        threading.Thread(target=self.call_backend, args=(text,), daemon=True).start()

    def append_history(self, text):
        self.history.text += '\n' + text

    def call_backend(self, message):
        try:
            resp = requests.post(BACKEND_URL + '/assist', json={'message': message}, timeout=5)
            if resp.status_code == 200:
                data = resp.json()
                reply = data.get('reply', '<no reply>')
            else:
                reply = f'Error from server: {resp.status_code}'
        except Exception as e:
            reply = f'Network error: {e}'

        # schedule on main thread
        from kivy.clock import Clock
        Clock.schedule_once(lambda dt: self.append_history('MobAI: ' + reply))


class AssistantApp(App):
    def build(self):
        return AssistantUI()


if __name__ == '__main__':
    AssistantApp().run()
