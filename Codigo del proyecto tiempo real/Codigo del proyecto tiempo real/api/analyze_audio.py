import os
import sys
import whisper
import openpyxl
from pysentimiento import create_analyzer

# Configurar el analizador de sentimientos
sentiment_analyzer = create_analyzer(task="sentiment", lang="es")

def transcribe_audio(file_path, model):
    try:
        result = model.transcribe(file_path, fp16=False)
        return result['text']
    except Exception as e:
        return f"Error al intentar reconocer el audio; {e}"

def analyze_sentiment(text):
    result = sentiment_analyzer.predict(text)
    # Mapear las emociones a Feliz, Neutral y Enojado
    if result.output == "POS":
        emotion = "Feliz"
    elif result.output == "NEG":
        emotion = "Enojado"
    else:
        emotion = "Neutral"
    return emotion, result.probas

def process_transcriptions(transcriptions):
    processed_results = []
    sentences = transcriptions.split('.')
    for sentence in sentences:
        if sentence.strip():
            emotion, _ = analyze_sentiment(sentence.strip())
            processed_results.append((emotion, sentence.strip()))
    return processed_results

def save_results_to_excel(results, output_path):
    workbook = openpyxl.Workbook()
    sheet = workbook.active
    sheet.title = "Transcripciones"
    sheet.append(["numero de frases", "emocion", "la frase", "en que audio esta"])

    phrase_count = 1

    for phrase_num, (emotion, sentence, audio_index) in enumerate(results, start=1):
        sheet.append([phrase_num, emotion, sentence, audio_index])

    workbook.save(output_path)

def main():
    audio_folder = sys.argv[1]
    output_folder = r"C:\Users\crist\Documents\Proyecto de seminario\OpenVokaturi-4-0\Transcriptions"
    os.makedirs(output_folder, exist_ok=True)
    output_path = os.path.join(output_folder, "transcripciones.xlsx")
    
    model = whisper.load_model("large")
    
    all_results = []
    current_audio_index = 1

    for audio_file in os.listdir(audio_folder):
        if audio_file.lower().endswith((".wav", ".mp3", ".aac", ".ogg")):
            audio_file_path = os.path.join(audio_folder, audio_file)
            transcription = transcribe_audio(audio_file_path, model)
            if transcription:  # Asegurar que la transcripción no esté vacía
                results = process_transcriptions(transcription)
                for result in results:
                    all_results.append((result[0], result[1], current_audio_index))
                current_audio_index += 1
    
    save_results_to_excel(all_results, output_path)
    print(f"Resultados guardados en {output_path}")

if __name__ == "__main__":
    main()
