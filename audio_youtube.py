#!/usr/bin/env python3
"""
Descargador de audio de YouTube desde el portapapeles.

Toma la URL del portapapeles, valida que sea un enlace de YouTube
correcto y descarga solo el audio, convertido a MP3.

Requisitos:
    pip install yt-dlp pyperclip

Además, yt-dlp necesita ffmpeg instalado en el sistema para poder
extraer y convertir el audio a MP3. En macOS:
    brew install ffmpeg
"""

import re
import sys
from pathlib import Path

import pyperclip
import yt_dlp

# Carpeta de destino de las descargas
CARPETA_DESTINO = "/Users/jcarlos/Music"

# Calidad del MP3 en kbps (192 es un buen equilibrio calidad/tamaño)
CALIDAD_MP3 = "256"

# Expresión regular para validar URLs de YouTube (video normal, corto o youtu.be)
PATRON_YOUTUBE = re.compile(
    r"^(https?://)?(www\.)?"
    r"(youtube\.com/(watch\?v=|shorts/)|youtu\.be/)"
    r"[\w-]{6,}"
)


def obtener_url_portapapeles() -> str:
    """Lee y devuelve el contenido del portapapeles, sin espacios extra."""
    try:
        return pyperclip.paste().strip()
    except Exception as error:
        print(f"No se pudo leer el portapapeles: {error}")
        sys.exit(1)


def es_url_valida(url: str) -> bool:
    """Verifica que la cadena sea una URL de YouTube con formato correcto."""
    return bool(url) and bool(PATRON_YOUTUBE.match(url))


def mostrar_progreso(estado: dict) -> None:
    """Hook de progreso que yt-dlp llama durante la descarga."""
    if estado["status"] == "downloading":
        porcentaje = estado.get("_percent_str", "").strip()
        velocidad = estado.get("_speed_str", "").strip()
        eta = estado.get("_eta_str", "").strip()
        print(f"\rDescargando... {porcentaje}  {velocidad}  ETA: {eta}   ", end="")
    elif estado["status"] == "finished":
        print("\nDescarga completa. Convirtiendo a MP3...")


def descargar_audio(url: str, carpeta_destino: str) -> None:
    """Descarga solo el audio del video y lo convierte a MP3."""
    Path(carpeta_destino).mkdir(parents=True, exist_ok=True)

    opciones = {
        "format": "bestaudio/best",
        "outtmpl": str(Path(carpeta_destino) / "%(title)s.%(ext)s"),
        "noplaylist": True,
        "progress_hooks": [mostrar_progreso],
        "postprocessors": [
            {
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",
                "preferredquality": CALIDAD_MP3,
            }
        ],
        "quiet": True,
        "no_warnings": True,
    }

    with yt_dlp.YoutubeDL(opciones) as ydl:
        info = ydl.extract_info(url, download=False)
        titulo = info.get("title", "audio")
        print(f"Título: {titulo}")
        print(f"Descargando audio en: {carpeta_destino}\n")
        ydl.download([url])


def main() -> None:
    print("Buscando una URL de YouTube en el portapapeles...")
    url = obtener_url_portapapeles()

    if not url:
        print("El portapapeles está vacío. Copia una URL de YouTube e inténtalo de nuevo.")
        sys.exit(1)

    if not es_url_valida(url):
        print("La URL del portapapeles no es un enlace de YouTube válido:")
        print(f"  {url}")
        sys.exit(1)

    print(f"URL válida detectada:\n  {url}\n")

    try:
        descargar_audio(url, CARPETA_DESTINO)
    except yt_dlp.utils.DownloadError as error:
        print(f"Error al descargar el audio: {error}")
        sys.exit(1)

    print("\n¡Listo! El audio se guardó correctamente en MP3.")


if __name__ == "__main__":
    main()