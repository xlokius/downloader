#!/usr/bin/env python3
"""
Descargador de videos de YouTube desde el portapapeles.

Toma la URL del portapapeles, valida que sea un enlace de YouTube
correcto y descarga el video en MP4 con la máxima calidad disponible.

Requisitos:
    pip install yt-dlp pyperclip

Además, yt-dlp necesita ffmpeg instalado en el sistema para poder
unir la mejor pista de video con la mejor pista de audio en un
único archivo MP4. En macOS:
    brew install ffmpeg
"""

import re
import sys
from pathlib import Path

import pyperclip
import yt_dlp

# Carpeta de destino de las descargas
CARPETA_DESTINO = "/Users/jcarlos/Movies"

# Expresión regular para validar URLs de YouTube (video normal, corto o youtu.be)
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
        print("\nDescarga completa. Procesando archivo final (unión audio/video)...")


def descargar_video(url: str, carpeta_destino: str) -> None:
    """Descarga el video de la URL dada en MP4 y máxima calidad disponible."""
    Path(carpeta_destino).mkdir(parents=True, exist_ok=True)

    opciones = {
        # Mejor video + mejor audio en mp4; si no existe esa combinación,
        # cae al mejor mp4 disponible, y como último recurso al mejor formato
        "format": "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best",
        "merge_output_format": "mp4",
        "outtmpl": str(Path(carpeta_destino) / "%(title)s.%(ext)s"),
        "noplaylist": True,
        "progress_hooks": [mostrar_progreso],
        "quiet": True,
        "no_warnings": True,
    }

    with yt_dlp.YoutubeDL(opciones) as ydl:
        info = ydl.extract_info(url, download=False)
        titulo = info.get("title", "video")
        print(f"Título: {titulo}")
        print(f"Descargando en: {carpeta_destino}\n")
        ydl.download([url])


def main() -> None:
    print("Buscando una URL de YouTube en el portapapeles...")
    url = obtener_url_portapapeles()

    if not url:
        print("El portapapeles está vacío. Copia una URL de YouTube e inténtalo de nuevo.")
        sys.exit(1)

    if not es_url_valida(url):
        print("La URL del portapapeles no es un enlace de YouTube válido:")
        print(f"  {url}")
        sys.exit(1)

    print(f"URL válida detectada:\n  {url}\n")

    try:
        descargar_video(url, CARPETA_DESTINO)
    except yt_dlp.utils.DownloadError as error:
        print(f"Error al descargar el video: {error}")
        sys.exit(1)

    print("\n¡Listo! El video se guardó correctamente.")


if __name__ == "__main__":
    main()
