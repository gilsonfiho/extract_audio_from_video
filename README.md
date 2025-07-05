# 🎵 Extrator de Áudio Otimizado

## 📖 Descrição

Uma ferramenta **Python otimizada** para extrair áudio de vídeos e dividir em chunks MP3, especialmente projetada para **ambientes com poucos recursos**. Utiliza OpenCV para obter informações do vídeo e FFmpeg para processamento de áudio eficiente.

## ✨ Características Principais

- 🎯 **Otimizado para poucos recursos** - Processamento single-thread e configurações eficientes
- 🎵 **Saída em MP3** - Formato compacto e amplamente compatível
- 📊 **Barras de progresso** - Feedback visual em tempo real com TQDM
- 🎚️ **Configurações de qualidade** - Low, Medium, High
- 🔧 **Fácil de usar** - Interface simples e intuitiva
- 🧹 **Limpeza automática** - Remove arquivos temporários
- 📱 **Mono channel** - Reduz tamanho dos arquivos

## 🛠️ Instalação

### 1. Instalar Dependências Python
```bash
pip install -r requirements.txt
```

### 2. Instalar FFmpeg

**Ubuntu/Debian:**
```bash
sudo apt update
sudo apt install ffmpeg
```

**Windows:**
- Baixar de [ffmpeg.org](https://ffmpeg.org/download.html)
- Extrair e adicionar ao PATH

**macOS:**
```bash
brew install ffmpeg
```

### 3. Verificar Instalação
```bash
ffmpeg -version
python -c "import cv2, tqdm, numpy; print('✅ Pronto para usar!')"
```

## 🚀 Uso Rápido

### Exemplo Básico
```python
from opencv_audio_extractor import extract_and_split_to_mp3

# Extrair e dividir em 5 partes
resultado = extract_and_split_to_mp3(
    video_path="meu_video.mp4",
    n_parts=5,
    output_dir="audio_chunks",
    quality="medium"
)

if resultado["success"]:
    print(f"✅ {len(resultado['split_files'])} arquivos criados!")
    for arquivo in resultado['split_files']:
        print(f"📄 {arquivo}")
```

### Uso Avançado
```python
from opencv_audio_extractor import OpenCVAudioExtractor

# Criar extrator
extractor = OpenCVAudioExtractor("video.mkv")

# Obter informações do vídeo
info = extractor.get_video_info()
print(f"Duração: {info['duration']:.2f}s")
print(f"FPS: {info['fps']:.2f}")

# Processar com configurações customizadas
resultado = extractor.process_video_to_mp3_chunks(
    n_parts=10,
    output_dir="output",
    quality="high",
    cleanup=True
)
```

## ⚙️ Configurações de Qualidade

| Qualidade | Bitrate | Sample Rate | Uso Recomendado |
|-----------|---------|-------------|-----------------|
| `low`     | 64kbps  | 22050Hz     | Podcasts, economia extrema |
| `medium`  | 128kbps | 44100Hz     | Uso geral, boa qualidade |
| `high`    | 192kbps | 44100Hz     | Música, alta qualidade |

## 📁 Estrutura de Saída

```
output/
├── video_parte_001.mp3
├── video_parte_002.mp3
├── video_parte_003.mp3
└── ...
```

## 🔧 Parâmetros Principais

### `extract_and_split_to_mp3()`
- **video_path** (str): Caminho para o arquivo de vídeo
- **n_parts** (int): Número de partes para dividir
- **output_dir** (str): Diretório de saída (padrão: "output")
- **quality** (str): Qualidade do áudio ("low", "medium", "high")
- **cleanup** (bool): Remover arquivo temporário (padrão: True)

### Retorno
```python
{
    "success": True,
    "original_video": "video.mp4",
    "video_info": {...},
    "n_parts": 5,
    "split_files": ["arquivo1.mp3", "arquivo2.mp3", ...],
    "output_dir": "output",
    "total_size_mb": 45.67,
    "quality": "medium"
}
```

## 📊 Exemplo de Saída

```
🔧 Extrator de Áudio Otimizado - OpenCV + FFmpeg
🎵 Formato de saída: MP3
💾 Otimizado para poucos recursos

==================================================
EXTRAÇÃO E DIVISÃO DE ÁUDIO - OTIMIZADO
==================================================

Extraindo áudio: meu_video
Duração: 300.45s
Qualidade: medium (128k)
Extraindo áudio: 100%|████████████| 300/300 [01:23<00:00, 3.61s/s]

Dividindo áudio em 5 partes...
Duração total: 300.45s
Duração por parte: 60.09s
Dividindo áudio: 100%|████████████| 5/5 [00:15<00:00, 3.12s/parte]

==================================================
PROCESSAMENTO CONCLUÍDO!
Total de arquivos: 5
Tamanho total: 12.34MB
==================================================

✅ Processamento concluído!
📁 Arquivos em: output
🔢 Partes criadas: 5
📊 Tamanho total: 12.34MB
🎵 Qualidade: medium
📄 Arquivos MP3:
   1. meu_video_parte_001.mp3 (2.45MB)
   2. meu_video_parte_002.mp3 (2.48MB)
   3. meu_video_parte_003.mp3 (2.47MB)
   4. meu_video_parte_004.mp3 (2.46MB)
   5. meu_video_parte_005.mp3 (2.48MB)
```

## 🎯 Otimizações para Poucos Recursos

### Configurações Automáticas
- **Single-thread processing** - Usa apenas 1 core
- **Mono channel** - Reduz tamanho em ~50%
- **Batch processing** - Processa em lotes pequenos
- **Memory cleanup** - Remove arquivos temporários
- **Efficient codecs** - Usa libmp3lame otimizado

### Recomendações
- Use qualidade `low` para economia máxima
- Defina `cleanup=True` para economizar espaço
- Processe vídeos menores por vez
- Monitore uso de memória com `htop`

## 📋 Requisitos do Sistema

### Mínimos
- **Python**: 3.6+
- **RAM**: 512MB
- **Espaço**: 2x tamanho do vídeo original
- **CPU**: 1 core

### Recomendados
- **Python**: 3.8+
- **RAM**: 1GB+
- **Espaço**: 5x tamanho do vídeo original
- **CPU**: 2+ cores

## 🐛 Solução de Problemas

### FFmpeg não encontrado
```bash
# Verificar se está instalado
ffmpeg -version

# Ubuntu/Debian
sudo apt install ffmpeg

# Verificar PATH no Windows
where ffmpeg
```

### Erro de memória
```python
# Use qualidade menor
resultado = extract_and_split_to_mp3(
    video_path="video.mp4",
    n_parts=10,  # Mais partes = menor uso de memória
    quality="low"  # Menor qualidade = menos RAM
)
```

### Vídeo muito grande
```python
# Processar em partes menores
for i in range(0, total_duration, 600):  # 10 min cada
    # Extrair segmento específico primeiro
    # Depois processar segmento
```

## 🔄 Formatos Suportados

### Entrada (via FFmpeg)
- **Vídeo**: MP4, AVI, MKV, MOV, FLV, WMV, 3GP
- **Áudio**: MP3, WAV, AAC, OGG, FLAC

### Saída
- **Áudio**: MP3 (mono, otimizado)

## 📝 Transcrição de Áudio com Whisper

Este projeto inclui um script independente para **transcrever arquivos MP3** usando o modelo Whisper da OpenAI.

### 🔧 Requisitos

- `openai-whisper`

### ▶️ Como usar

1. Execute a funcionalidade principal para gerar um .mp3 no diretório `/output`  
2. Execute o script:

```bash
python transcrever_audio.py
```

O script irá:

- Carregar o modelo Whisper (`base`)
- Transcrever o arquivo `audio/video_parte_001.mp3`
- Salvar a transcrição como `transcricoes/video_parte_001.txt`

### 📂 Exemplo de entrada e saída

```
output/
└── video_parte_001.mp3
└── video_parte_001.txt
```

## 🤝 Contribuição

1. Fork o repositório
2. Crie uma branch (`git checkout -b feature/nova-funcionalidade`)
3. Commit suas mudanças (`git commit -am 'Adiciona nova funcionalidade'`)
4. Push para a branch (`git push origin feature/nova-funcionalidade`)
5. Abra um Pull Request

## 📄 Licença

Este projeto está sob a licença MIT. Veja o arquivo `LICENSE` para mais detalhes.

## 🙏 Agradecimentos

- **OpenCV** - Processamento de vídeo
- **FFmpeg** - Manipulação de áudio/vídeo
- **TQDM** - Barras de progresso
- **Comunidade Python** - Ferramentas incríveis

## 📞 Suporte

- 🐛 **Issues**: Reporte bugs no GitHub
- 💬 **Discussões**: Use GitHub Discussions
- 📧 **Email**: Para questões privadas

---

**Desenvolvido com ❤️ para ambientes com poucos recursos**