import subprocess
from pathlib import Path
import os

def accelerate_chunk(input_path, speed=1.5):
    """
    Acelera um arquivo de áudio MP3 usando FFmpeg com filtro 'atempo'.

    Args:
        input_path (str): Caminho do arquivo MP3 de entrada.
        speed (float): Fator de velocidade (>1 acelera, <1 desacelera).

    Returns:
        str: Caminho do novo arquivo acelerado.
    """
    try:
        input_path = Path(input_path)
        output_path = input_path.with_name(f"{input_path.stem}_speed_{speed:.2f}.mp3")

        # FFmpeg só permite atempo entre 0.5 e 2.0 — dividir em filtros se necessário
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
            "-vn",  # remove qualquer vídeo
            str(output_path)
        ]

        subprocess.run(cmd, capture_output=True)

        return str(output_path) if output_path.exists() else None

    except Exception as e:
        print(f"Erro ao acelerar áudio com FFmpeg: {str(e)}")
        return None