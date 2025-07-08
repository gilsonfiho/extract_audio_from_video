import os
import time
import whisper
import difflib
from jiwer import wer
from pathlib import Path


# Pasta com os arquivos .mp3 acelerados e seus .txt
PASTA = r"C:\Users\gilso\OneDrive\Área de Trabalho\git\extract_audio_from_video\output"

# Carrega o modelo Whisper (opções: tiny, base, small, medium, large)
model = whisper.load_model("base")

# Coletar arquivos .mp3 com tag de velocidade
arquivos = sorted([f for f in os.listdir(PASTA) if f.endswith(".mp3") and "speed" in f])

# Resultados acumulados
resultados = []

for mp3_file in arquivos:
    caminho_mp3 = os.path.join(PASTA, mp3_file)
    velocidade = mp3_file.split("_speed_")[1].split("_")[0]  # extrai "1.25" de "example_speed_1.25_parte_001.mp3"

    print(f"\n🎧 Transcrevendo {mp3_file} (Velocidade: {velocidade}x)...")

    # Tempo de execução
    inicio = time.time()
    resultado = model.transcribe(caminho_mp3, language="pt")
    fim = time.time()
    tempo_exec = fim - inicio

    # Texto gerado
    texto_obtido = resultado["text"].strip()

    resultados.append({
        "velocidade": velocidade,
        "tempo": tempo_exec,
        "texto": texto_obtido
    })

# Exibir resultado
print("\n====================== BENCHMARK ======================")
print(f"{'Velocidade':<12} {'Tempo (s)':<10} Transcrição")
print("-" * 60)
for r in resultados:
    print(f"{r['velocidade']:<12} {r['tempo']:<10.2f} {r['texto'][:90]}")


# Opcional: salvar CSV ou JSON com resultados
