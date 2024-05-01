from requests import get
import pyttsx3
from pyaudio import PyAudio, paInt16
from vosk import Model, KaldiRecognizer
import json


class VoiceAssistant:

    def __init__(self):
        self.commands = [
            {"id": 0, "text": "случайный",
             "answer": "Ваше занятие: ", "handler": self.random},
            {"id": 1, "text": "название",
             "answer": "Тип занятия: ", "handler": self.name},
            {"id": 2, "text": "участники",
             "answer": "Потребуется участников", "handler": self.remembers},
            {"id": 3, "text": "следующая",
             "answer": "Следующее занятие", "handler": self.next},
            {"id": 4, "text": "сохранить",
             "answer": "Сохраняю в файл", "handler": self.save}
        ]
        self.data = get("https://www.boredapi.com/api/activity").json()

        self.tts = pyttsx3.init()
        self.model = Model('vosk-model-small-ru-0.22')
        self.record = KaldiRecognizer(self.model, 16000)
        pa = PyAudio()
        self.stream = pa.open(format=paInt16,
                              channels=1,
                              rate=16000,
                              input=True,
                              frames_per_buffer=8000)
        self.stream.start_stream()
        self.speak("Вас приветствует голосовой ассистент.")
        self.speak("Вот мои команды:")
        for command in self.commands:
            print(f"{command['id'] + 1}. \"{command['text']}\"")

    def random(self):
        self.speak(self.data['activity'])

    def name(self):
        self.speak(self.data['type'])

    def remembers(self):
        self.speak(self.data['participants'])

    def next(self):
        self.data = get("https://www.boredapi.com/api/activity").json()
        self.speak(self.data['activity'])

    def save(self):
        with open("text.txt", "w") as txt_file:
            for i in self.data:
                txt_file.write(f'{i}: {self.data[i]}\n')

    def listen(self):
        while True:
            data = self.stream.read(4000, exception_on_overflow=False)
            if self.record.AcceptWaveform(data) and len(data) > 0:
                answer = json.loads(self.record.Result())
                if answer['text']:
                    print("Вы:", answer['text'])
                    yield answer['text']

    def speak(self, say):
        self.stream.stop_stream()
        print(say)
        self.tts.say(say)
        self.tts.runAndWait()
        self.stream.start_stream()


if __name__ == "__main__":
    assistant = VoiceAssistant()
    assistant.speak('Начинаю работу')

    for text in assistant.listen():
        for command in assistant.commands:
            if text.startswith(command["text"]):
                if (assistant.data and command["id"] in [1, 2, 3]) or \
                        command["id"] in [0, 4]:
                    assistant.speak(command["answer"])
                    command["handler"]()
                else:
                    assistant.speak("Нет текста, используйте для начала команду \"Создать\"")
                break
        else:
            assistant.speak("Я не знаю этой команды!")
