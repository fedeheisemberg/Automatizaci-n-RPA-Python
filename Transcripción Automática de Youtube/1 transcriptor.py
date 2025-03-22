import os
import pytube
from youtube_transcript_api import YouTubeTranscriptApi
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.probability import FreqDist
import re

# Descargar recursos necesarios de NLTK
nltk.download('punkt')
nltk.download('stopwords')

def get_video_id(youtube_url):
    """Extrae el ID del video de una URL de YouTube."""
    if 'youtu.be' in youtube_url:
        return youtube_url.split('/')[-1].split('?')[0]
    if 'youtube.com' in youtube_url:
        if 'v=' in youtube_url:
            return youtube_url.split('v=')[1].split('&')[0]
        elif 'embed/' in youtube_url:
            return youtube_url.split('embed/')[1].split('?')[0]
    return None

def get_transcript(video_id, language='es'):
    """Obtiene la transcripción del video de YouTube."""
    try:
        transcript_list = YouTubeTranscriptApi.get_transcript(video_id, languages=[language])
        transcript = ' '.join([t['text'] for t in transcript_list])
        return transcript
    except Exception as e:
        print(f"Error al obtener la transcripción: {e}")
        return None

def extract_audio(youtube_url, output_path='audio'):
    """Descarga solo el audio del video de YouTube."""
    if not os.path.exists(output_path):
        os.makedirs(output_path)
    
    try:
        yt = pytube.YouTube(youtube_url)
        audio_stream = yt.streams.filter(only_audio=True).first()
        out_file = audio_stream.download(output_path=output_path)
        base, ext = os.path.splitext(out_file)
        new_file = base + '.mp3'
        os.rename(out_file, new_file)
        print(f"Audio descargado: {new_file}")
        return new_file
    except Exception as e:
        print(f"Error al descargar el audio: {e}")
        return None

def generate_summary_extractive(text, num_sentences=10):
    """Genera un resumen extractivo basado en frecuencia de palabras."""
    sentences = sent_tokenize(text)
    
    # Filtrar stopwords
    stop_words = set(stopwords.words('spanish'))
    words = word_tokenize(text.lower())
    filtered_words = [word for word in words if word.isalnum() and word not in stop_words]
    
    # Frecuencia de palabras
    word_freq = FreqDist(filtered_words)
    
    # Puntuar las oraciones basándose en la frecuencia de palabras
    sentence_scores = {}
    for i, sentence in enumerate(sentences):
        words_in_sentence = word_tokenize(sentence.lower())
        score = sum([word_freq[word] for word in words_in_sentence if word in word_freq])
        sentence_scores[i] = score / max(len(words_in_sentence), 1)  # Normalizar por longitud
    
    # Seleccionar las mejores oraciones
    top_sentences = sorted(sentence_scores.items(), key=lambda x: x[1], reverse=True)[:num_sentences]
    top_sentences = sorted(top_sentences, key=lambda x: x[0])  # Ordenar por posición original
    
    summary = ' '.join([sentences[i] for i, _ in top_sentences])
    return summary

def clean_transcript(text):
    """Limpia la transcripción eliminando caracteres no deseados."""
    # Eliminar caracteres especiales y normalizar espacios
    text = re.sub(r'\s+', ' ', text)
    text = re.sub(r'[^\w\s.,;:!?¿¡()"""\'-]', '', text)
    return text.strip()

def main():
    youtube_url = "https://www.youtube.com/watch?v=dHR5VYgH3fA"
    video_id = get_video_id(youtube_url)
    
    if not video_id:
        print("No se pudo extraer el ID del video.")
        return
    
    print(f"Obteniendo transcripción para el video: {video_id}")
    transcript = get_transcript(video_id)
    
    if not transcript:
        print("No se pudo obtener la transcripción. Intentando descargar el audio...")
        audio_file = extract_audio(youtube_url)
        if not audio_file:
            print("No se pudo procesar el audio. Terminando el programa.")
            return
        # Aquí podrías implementar la transcripción desde el archivo de audio usando whisper o similar
    
    # Limpiar la transcripción
    cleaned_transcript = clean_transcript(transcript)
    
    # Guardar la transcripción completa
    with open("transcripcion_completa.txt", "w", encoding="utf-8") as f:
        f.write(cleaned_transcript)
    
    print("\nGenerando resumen extractivo...")
    extractive_summary = generate_summary_extractive(cleaned_transcript, num_sentences=15)
    
    # Guardar el resumen extractivo
    with open("resumen_extractivo.txt", "w", encoding="utf-8") as f:
        f.write(extractive_summary)
    
    print("\nProceso completado. Archivos generados:")
    print("- transcripcion_completa.txt")
    print("- resumen_extractivo.txt")

if __name__ == "__main__":
    main()