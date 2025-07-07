"""
Script para transcrever um arquivo de áudio MP3 usando o modelo Whisper.

Este script carrega um modelo Whisper pré-treinado, transcreve o conteúdo
de um arquivo de áudio e salva o texto em um arquivo `.txt` correspondente.

Requisitos:
- whisper

Autor: Gilson Almeida (https://github.com/gilsonfiho)
Data: 2025-07-05
"""

import whisper
import os
import sys

def transcrever():
    """
    Executa o processo de transcrição de um arquivo MP3 usando o Whisper.

    Etapas:
    - Verifica se o arquivo de áudio existe.
    - Carrega o modelo Whisper.
    - Realiza a transcrição do áudio.
    - Salva a transcrição em um arquivo .txt.

    Saída:
    - Arquivo de texto com a transcrição no mesmo diretório do áudio.
    """

    # Caminho do arquivo MP3 (ajuste conforme o local do seu arquivo e SO)
    audio_path = r"C:\Users\gilso\OneDrive\Área de Trabalho\git\extract_audio_from_video\output\example_speed_1.20_parte_001.mp3" 

    # Verifica se o arquivo existe
    if not os.path.exists(audio_path):
        print(f"❌ Arquivo não encontrado: {audio_path}")
        print("Verifique o caminho e o nome do arquivo.")
        sys.exit(1)

    # Define o nome do arquivo de saída com extensão .txt
    output_text = os.path.splitext(audio_path)[0] + ".txt"

    # Carrega o modelo Whisper (opções: tiny, base, small, medium, large)
    print("Carregando modelo Whisper...")
    model = whisper.load_model("base")

    # Realiza a transcrição do áudio
    print("Transcrevendo áudio...")
    result = model.transcribe(audio_path)

    # Extrai o texto da transcrição
    transcription = result["text"]

    # Salva o texto em um arquivo .txt
    with open(output_text, "w", encoding="utf-8") as f:
        f.write(transcription)

    print(f"✅ Transcrição salva em: {output_text}")

if __name__ == "__main__":
    transcrever()
