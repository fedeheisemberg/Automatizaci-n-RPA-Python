import os
import yt_dlp

# Nombre del archivo que contiene las URLs de los videos
INPUT_FILE = "videos.txt"

# Carpeta donde se guardarán los MP3
OUTPUT_FOLDER = "descargas_mp3"
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

# Leer las URLs desde el archivo
with open(INPUT_FILE, "r", encoding="utf-8") as file:
    video_urls = [line.strip() for line in file if line.strip()]

# Opciones de descarga para yt-dlp
ydl_opts = {
    "format": "bestaudio/best",
    "outtmpl": f"{OUTPUT_FOLDER}/%(title)s.%(ext)s",
    "postprocessors": [
        {
            "key": "FFmpegExtractAudio",
            "preferredcodec": "mp3",
            "preferredquality": "192",
        }
    ],
}

# Descargar cada video en formato MP3
with yt_dlp.YoutubeDL(ydl_opts) as ydl:
    ydl.download(video_urls)

print("✅ Descarga completada. Archivos guardados en la carpeta:", OUTPUT_FOLDER)
