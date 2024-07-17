from flask import Flask, render_template, jsonify
import threading
import time
import platform
import struct
import numpy as np
import pyaudio
import vosk
import os
import json
import Vokaturi

# Ruta a la ubicación de la DLL
dll_path = r"C:\Users\crist\Documents\Proyecto de seminario\OpenVokaturi-4-0\lib\open\win\OpenVokaturi-4-0-win64.dll"

app = Flask(__name__)

transcription_data = {
    "emotion": "Desconocida",
    "emotion_color": "black",
    "text": "",
    "partial_text": ""
}

# Cargar la biblioteca Vokaturi según el sistema operativo
def load_vokaturi_library():
    if platform.system() == "Darwin":
        assert struct.calcsize("P") == 8
        Vokaturi.load("../lib/open/macos/OpenVokaturi-4-0-mac.dylib")
    elif platform.system() == "Windows" or platform.system() == "CYGWIN_NT-10.0-19044":
        if struct.calcsize("P") == 4:
            Vokaturi.load("../lib/open/win/OpenVokaturi-4-0-win32.dll")
        else:
            assert struct.calcsize("P") == 8
            Vokaturi.load(dll_path)
    elif platform.system() == "Linux":
        assert struct.calcsize("P") == 8
        Vokaturi.load("../lib/open/linux/OpenVokaturi-4-0-linux.so")

load_vokaturi_library()

p = pyaudio.PyAudio()
c_buffer = Vokaturi.float32array(1024)  # Tamaño del buffer ajustado para procesamiento más rápido

def callback(in_data, frame_count, time_info, flag):
    audio_data = np.frombuffer(in_data, dtype=np.float32)
    c_buffer[0:frame_count] = audio_data
    voice.fill_float32array(frame_count, c_buffer)
    return in_data, pyaudio.paContinue

# Crear una instancia de la clase Voice de Vokaturi
sample_rate = 44100
buffer_duration = 0.5  # Duración del buffer reducida para actualizaciones más rápidas
buffer_length = int(sample_rate * buffer_duration)
voice = Vokaturi.Voice(sample_rate, buffer_length, True)

# Configurar el flujo de audio de PyAudio para Vokaturi
stream_vokaturi = p.open(
    rate=sample_rate,
    channels=1,
    format=pyaudio.paFloat32,
    input=True,
    output=False,
    start=True,
    stream_callback=callback
)

# Configurar Vosk
vosk.SetLogLevel(-1)  # Deshabilitar logs innecesarios
model_path = r"C:\Users\crist\Documents\Proyecto de seminario\vosk-model-es-0.42"  # Actualiza esta ruta con la ruta del modelo descargado
if not os.path.exists(model_path):
    print("Modelo no encontrado. Descarga el modelo desde https://alphacephei.com/vosk/models y descomprime en el directorio actual.")
    sys.exit(1)

model = vosk.Model(model_path)
recognizer = vosk.KaldiRecognizer(model, sample_rate)

# Configurar el flujo de audio de PyAudio para Vosk
stream_vosk = p.open(
    rate=sample_rate,
    channels=1,
    format=pyaudio.paInt16,
    input=True,
    frames_per_buffer=2000  # Tamaño del buffer reducido para actualizaciones más rápidas
)

def update_transcription_data():
    global transcription_data
    spoken_text = ""
    last_emotion_time = 0
    last_valid_emotion = "Neutral"
    emotion_colors = {
        "Neutral": "green",
        "Feliz": "blue",
        "Enojado": "red",
        "Desconocida": "gray"
    }

    while stream_vokaturi.is_active() and stream_vosk.is_active():
        current_time = time.time()

        # Procesamiento de emociones
        if current_time - last_emotion_time >= 0.5:  # Actualizar emoción cada 0.5 segundos
            quality = Vokaturi.Quality()
            emotionProbabilities = Vokaturi.EmotionProbabilities()
            voice.extract(quality, emotionProbabilities)

            if quality.valid:
                neutrality = emotionProbabilities.neutrality
                happiness = emotionProbabilities.happiness
                anger = emotionProbabilities.anger

                if neutrality >= 0.1:
                    emotion = "Neutral"
                elif happiness >= 0.1:
                    emotion = "Feliz"
                elif anger >= 0.1:
                    emotion = "Enojado"
                else:
                    emotion = last_valid_emotion  # Mantener la última emoción válida

                transcription_data["emotion"] = emotion
                transcription_data["emotion_color"] = emotion_colors[emotion]
                last_valid_emotion = emotion  # Actualizar la última emoción válida
                last_emotion_time = current_time

        # Transcripción de voz con Vosk
        data = stream_vosk.read(2000, exception_on_overflow=False)
        if recognizer.AcceptWaveform(data):
            result = recognizer.Result()
            result_json = json.loads(result)
            texto = result_json.get('text', '')
            if texto:
                spoken_text += texto + " "
                transcription_data["text"] = spoken_text
                transcription_data["partial_text"] = ""
        else:
            partial_result = recognizer.PartialResult()
            partial_json = json.loads(partial_result)
            new_partial_text = partial_json.get('partial', '')
            if new_partial_text:
                transcription_data["partial_text"] = spoken_text + new_partial_text

threading.Thread(target=update_transcription_data).start()


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/transcription')
def get_transcription():
    return jsonify(transcription_data)

if __name__ == '__main__':
    app.run(debug=True)
