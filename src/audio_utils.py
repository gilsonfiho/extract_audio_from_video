import subprocess
from pathlib import Path
import time

def accelerate_chunk(input_path, speed=1.5):
    """
    Acelera um arquivo de áudio MP3 usando FFmpeg com filtro 'atempo'.

    Args:
        input_path (str): Caminho do arquivo MP3 de entrada.
        speed (float): Fator de velocidade (>1 acelera, <1 desacelera).

    Returns:
        str: Caminho do novo arquivo acelerado ou None se falhar.
    """
    # Medir o tempo da execução
    start = time.perf_counter()

    input_path = Path(input_path)
    output_path = input_path.with_name(f"{input_path.stem}_speed_{speed:.2f}.mp3")

    # Gerar filtros atempo válidos para FFmpeg
    tempo_filters = []
    remaining_speed = speed
    while remaining_speed > 2.0:
        tempo_filters.append("atempo=2.0")
        remaining_speed /= 2.0
    while remaining_speed < 0.5:
        tempo_filters.append("atempo=0.5")
        remaining_speed /= 0.5
    tempo_filters.append(f"atempo={remaining_speed:.2f}")
    filter_str = ",".join(tempo_filters)

    cmd = [
        "ffmpeg", "-y", "-i", str(input_path),
        "-filter:a", filter_str,
        "-vn",
        str(output_path)
    ]

    
    result = subprocess.run(cmd, capture_output=True)
    duration = time.perf_counter() - start

    print(f"⏱️ Tempo para acelerar o áudio ({speed:.2f}x): {duration:.2f} segundos")

    return str(output_path) if output_path.exists() else None
