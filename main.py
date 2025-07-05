import cv2
import numpy as np
import os
import math
from pathlib import Path
import subprocess
import tempfile
import shutil
from tqdm import tqdm
import threading
import time


class OpenCVAudioExtractor:
    def __init__(self, video_path):
        """
        Extrator de áudio otimizado usando apenas OpenCV e FFmpeg

        Args:
            video_path (str): Caminho para o arquivo de vídeo
        """
        self.video_path = video_path
        self.video_info = None

    def get_video_info(self):
        """
        Obtém informações do vídeo usando OpenCV

        Returns:
            dict: Informações do vídeo
        """
        try:
            cap = cv2.VideoCapture(self.video_path)

            if not cap.isOpened():
                raise ValueError("Não foi possível abrir o arquivo de vídeo")

            fps = cap.get(cv2.CAP_PROP_FPS)
            frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            duration = frame_count / fps if fps > 0 else 0

            # Obter dimensões
            width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

            cap.release()

            self.video_info = {
                'fps': fps,
                'frame_count': frame_count,
                'duration': duration,
                'width': width,
                'height': height
            }

            return self.video_info

        except Exception as e:
            print(f"Erro ao obter informações do vídeo: {str(e)}")
            return None

    def extract_audio_to_mp3(self, output_dir="output", quality="medium"):
        """
        Extrai áudio do vídeo e salva como MP3

        Args:
            output_dir (str): Diretório de saída
            quality (str): Qualidade do áudio ('low', 'medium', 'high')

        Returns:
            str: Caminho do arquivo MP3 extraído
        """
        try:
            # Criar diretório de saída
            os.makedirs(output_dir, exist_ok=True)

            # Obter informações do vídeo
            if not self.video_info:
                self.get_video_info()

            if not self.video_info:
                return None

            # Nome do arquivo de saída
            video_name = Path(self.video_path).stem
            audio_path = os.path.join(output_dir, f"{video_name}.mp3")

            # Configurações de qualidade
            quality_settings = {
                'low': {'bitrate': '64k', 'sample_rate': '22050'},
                'medium': {'bitrate': '128k', 'sample_rate': '44100'},
                'high': {'bitrate': '192k', 'sample_rate': '44100'}
            }

            settings = quality_settings.get(quality, quality_settings['medium'])

            # Comando FFmpeg otimizado para poucos recursos
            cmd = [
                'ffmpeg',
                '-i', self.video_path,
                '-vn',  # Sem vídeo
                '-acodec', 'libmp3lame',  # Codec MP3
                '-b:a', settings['bitrate'],  # Bitrate
                '-ar', settings['sample_rate'],  # Sample rate
                '-ac', '1',  # Mono para economizar espaço
                '-threads', '1',  # Usar apenas 1 thread
                '-loglevel', 'error',  # Reduzir output
                '-y',  # Sobrescrever
                audio_path
            ]

            print(f"Extraindo áudio: {video_name}")
            print(f"Duração: {self.video_info['duration']:.2f}s")
            print(f"Qualidade: {quality} ({settings['bitrate']})")

            # Executar comando com barra de progresso
            result = self._run_ffmpeg_with_progress(cmd, self.video_info['duration'],
                                                    "Extraindo áudio")

            if result.returncode != 0:
                print(f"Erro FFmpeg: {result.stderr}")
                return None

            # Verificar se o arquivo foi criado
            if os.path.exists(audio_path):
                size_mb = os.path.getsize(audio_path) / (1024 * 1024)
                print(f"Áudio extraído: {os.path.basename(audio_path)} ({size_mb:.2f}MB)")
                return audio_path
            else:
                print("Erro: Arquivo de áudio não foi criado")
                return None

        except Exception as e:
            print(f"Erro na extração: {str(e)}")
            return None

    def split_audio_chunks(self, audio_path, n_parts, output_dir="output"):
        """
        Divide áudio MP3 em chunks usando FFmpeg

        Args:
            audio_path (str): Caminho do arquivo de áudio
            n_parts (int): Número de partes
            output_dir (str): Diretório de saída

        Returns:
            list: Lista de arquivos gerados
        """
        try:
            if not os.path.exists(audio_path):
                print("Arquivo de áudio não encontrado!")
                return []

            # Obter duração do áudio
            duration = self._get_audio_duration(audio_path)
            if duration <= 0:
                print("Não foi possível obter a duração do áudio")
                return []

            # Calcular duração de cada parte
            chunk_duration = duration / n_parts

            split_files = []
            base_name = Path(audio_path).stem

            print(f"Dividindo áudio em {n_parts} partes...")
            print(f"Duração total: {duration:.2f}s")
            print(f"Duração por parte: {chunk_duration:.2f}s")

            # Barra de progresso para divisão
            with tqdm(total=n_parts, desc="Dividindo áudio", unit="parte") as pbar:
                for i in range(n_parts):
                    start_time = i * chunk_duration

                    # Última parte pega o resto
                    if i == n_parts - 1:
                        chunk_duration_actual = duration - start_time
                    else:
                        chunk_duration_actual = chunk_duration

                    # Nome do arquivo da parte
                    part_filename = f"{base_name}_parte_{i + 1:03d}.mp3"
                    part_path = os.path.join(output_dir, part_filename)

                    # Comando FFmpeg para dividir
                    cmd = [
                        'ffmpeg',
                        '-i', audio_path,
                        '-ss', str(start_time),
                        '-t', str(chunk_duration_actual),
                        '-acodec', 'copy',  # Copiar sem recodificar
                        '-avoid_negative_ts', 'make_zero',
                        '-loglevel', 'error',
                        '-y',
                        part_path
                    ]

                    # Executar comando
                    result = subprocess.run(cmd, capture_output=True, text=True)

                    if result.returncode == 0 and os.path.exists(part_path):
                        size_mb = os.path.getsize(part_path) / (1024 * 1024)
                        split_files.append(part_path)
                        pbar.set_postfix(arquivo=part_filename, tamanho=f"{size_mb:.2f}MB")
                    else:
                        pbar.set_postfix(erro=f"Falha na parte {i + 1}")
                        print(f"Erro ao criar parte {i + 1}: {result.stderr}")

                    pbar.update(1)

            return split_files

        except Exception as e:
            print(f"Erro ao dividir áudio: {str(e)}")
            return []

    def _get_audio_duration(self, audio_path):
        """
        Obtém a duração do áudio usando FFprobe

        Args:
            audio_path (str): Caminho do arquivo de áudio

        Returns:
            float: Duração em segundos
        """
        try:
            cmd = [
                'ffprobe',
                '-v', 'error',
                '-show_entries', 'format=duration',
                '-of', 'default=noprint_wrappers=1:nokey=1',
                audio_path
            ]

            result = subprocess.run(cmd, capture_output=True, text=True)

            if result.returncode == 0:
                return float(result.stdout.strip())
            else:
                return 0.0

        except Exception:
            return 0.0

    def _check_ffmpeg(self):
        """
        Verifica se FFmpeg está disponível

        Returns:
            bool: True se disponível
        """
        try:
            result = subprocess.run(['ffmpeg', '-version'],
                                    capture_output=True, text=True)
            return result.returncode == 0
        except:
            return False

    def process_video_to_mp3_chunks(self, n_parts, output_dir="output",
                                    quality="medium", cleanup=True):
        """
        Processa vídeo completo: extrai áudio e divide em chunks MP3

        Args:
            n_parts (int): Número de partes
            output_dir (str): Diretório de saída
            quality (str): Qualidade do áudio
            cleanup (bool): Remover arquivo de áudio temporário

        Returns:
            dict: Resultado do processamento
        """
        print("=" * 50)
        print("EXTRAÇÃO E DIVISÃO DE ÁUDIO - OTIMIZADO")
        print("=" * 50)

        # Verificar se FFmpeg está disponível
        if not self._check_ffmpeg():
            return {"success": False, "error": "FFmpeg não encontrado"}

        # Extrair áudio
        audio_path = self.extract_audio_to_mp3(output_dir, quality)
        if audio_path is None:
            return {"success": False, "error": "Falha na extração de áudio"}

        # Dividir áudio
        split_files = self.split_audio_chunks(audio_path, n_parts, output_dir)
        if not split_files:
            return {"success": False, "error": "Falha na divisão do áudio"}

        # Limpar arquivo temporário se solicitado
        if cleanup:
            try:
                os.remove(audio_path)
                print(f"Arquivo temporário removido: {os.path.basename(audio_path)}")
            except:
                pass

        # Calcular tamanho total
        total_size = sum(os.path.getsize(f) for f in split_files) / (1024 * 1024)

        result = {
            "success": True,
            "original_video": self.video_path,
            "video_info": self.video_info,
            "n_parts": n_parts,
            "split_files": split_files,
            "output_dir": output_dir,
            "total_size_mb": total_size,
            "quality": quality
        }

        print("=" * 50)
        print("PROCESSAMENTO CONCLUÍDO!")
        print(f"Total de arquivos: {len(split_files)}")
        print(f"Tamanho total: {total_size:.2f}MB")
        print("=" * 50)

        return result

    def _run_ffmpeg_with_progress(self, cmd, duration, description):
        """
        Executa comando FFmpeg com barra de progresso

        Args:
            cmd (list): Comando FFmpeg
            duration (float): Duração total em segundos
            description (str): Descrição para a barra de progresso

        Returns:
            subprocess.CompletedProcess: Resultado da execução
        """
        try:
            # Modificar comando para mostrar progresso
            cmd_with_progress = cmd.copy()
            # Remover -loglevel error para capturar progresso
            if '-loglevel' in cmd_with_progress:
                idx = cmd_with_progress.index('-loglevel')
                cmd_with_progress[idx + 1] = 'info'

            # Executar processo
            process = subprocess.Popen(
                cmd_with_progress,
                stderr=subprocess.PIPE,
                stdout=subprocess.PIPE,
                text=True,
                universal_newlines=True
            )

            # Barra de progresso
            with tqdm(total=int(duration), desc=description, unit="s") as pbar:
                current_time = 0

                while True:
                    output = process.stderr.readline()
                    if output == '' and process.poll() is not None:
                        break

                    if output:
                        # Procurar por tempo atual no output do FFmpeg
                        if 'time=' in output:
                            try:
                                time_str = output.split('time=')[1].split()[0]
                                if ':' in time_str:
                                    # Converter HH:MM:SS.ms para segundos
                                    time_parts = time_str.split(':')
                                    if len(time_parts) >= 3:
                                        hours = float(time_parts[0])
                                        minutes = float(time_parts[1])
                                        seconds = float(time_parts[2])
                                        new_time = hours * 3600 + minutes * 60 + seconds

                                        if new_time > current_time:
                                            pbar.update(int(new_time - current_time))
                                            current_time = new_time
                            except:
                                pass

                # Completar barra se necessário
                if current_time < duration:
                    pbar.update(int(duration - current_time))

            # Aguardar conclusão
            stdout, stderr = process.communicate()

            # Criar objeto de resultado compatível
            class Result:
                def __init__(self, returncode, stdout, stderr):
                    self.returncode = returncode
                    self.stdout = stdout
                    self.stderr = stderr

            return Result(process.returncode, stdout, stderr)

        except Exception as e:
            print(f"Erro ao executar FFmpeg: {str(e)}")
            # Fallback para execução sem progresso
            return subprocess.run(cmd, capture_output=True, text=True)


# Função simples para uso direto
def extract_and_split_to_mp3(video_path, n_parts, output_dir="output",
                             quality="medium", cleanup=True):
    """
    Função otimizada para extrair áudio e dividir em chunks MP3

    Args:
        video_path (str): Caminho do vídeo
        n_parts (int): Número de partes
        output_dir (str): Diretório de saída
        quality (str): Qualidade ('low', 'medium', 'high')
        cleanup (bool): Remover arquivo temporário

    Returns:
        dict: Resultado do processamento
    """
    extractor = OpenCVAudioExtractor(video_path)
    return extractor.process_video_to_mp3_chunks(n_parts, output_dir, quality, cleanup)


# Exemplo de uso
if __name__ == "__main__":
    # Configurações
    VIDEO_PATH = "video.mp4"  # Seu vídeo
    N_PARTS = 5  # Número de partes
    OUTPUT_DIR = "output"  # Diretório de saída
    QUALITY = "medium"  # low, medium, high

    # Verificar arquivo
    if not os.path.exists(VIDEO_PATH):
        print(f"❌ Arquivo {VIDEO_PATH} não encontrado!")
        print("Ajuste a variável VIDEO_PATH com o caminho correto.")
    else:
        print("🔧 Extrator de Áudio Otimizado - OpenCV + FFmpeg")
        print("🎵 Formato de saída: MP3")
        print("💾 Otimizado para poucos recursos")

        # Processar
        resultado = extract_and_split_to_mp3(
            video_path=VIDEO_PATH,
            n_parts=N_PARTS,
            output_dir=OUTPUT_DIR,
            quality=QUALITY,
            cleanup=True
        )

        # Mostrar resultados
        if resultado["success"]:
            print(f"\n✅ Processamento concluído!")
            print(f"📁 Arquivos em: {resultado['output_dir']}")
            print(f"🔢 Partes criadas: {resultado['n_parts']}")
            print(f"📊 Tamanho total: {resultado['total_size_mb']:.2f}MB")
            print(f"🎵 Qualidade: {resultado['quality']}")
            print(f"📄 Arquivos MP3:")
            for i, file in enumerate(resultado['split_files'], 1):
                size_mb = os.path.getsize(file) / (1024 * 1024)
                print(f"   {i}. {os.path.basename(file)} ({size_mb:.2f}MB)")
        else:
            print(f"\n❌ Erro: {resultado['error']}")

        # Informações sobre o vídeo original
        if resultado.get("video_info"):
            info = resultado["video_info"]
            print(f"\n📹 Informações do vídeo:")
            print(f"   Duração: {info['duration']:.2f}s")
            print(f"   FPS: {info['fps']:.2f}")
            print(f"   Resolução: {info['width']}x{info['height']}")
            print(f"   Frames: {info['frame_count']}")