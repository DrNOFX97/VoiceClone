# 🎤 Receita: Como Fazer Clone de Voz com Fish Speech

> Uma receita passo-a-passo para criar a tua aplicação de clonagem de voz com IA

## 📋 Ingredientes (Requisitos)

- **Hardware**: Mac com chip M1/M2 (ou PC com NVIDIA GPU/CPU)
- **Sistema**: macOS 11+ (ou Linux/Windows)
- **Python**: 3.11
- **Espaço em disco**: ~10 GB livres
- **Conexão à internet**: Para download de modelos

---

## 🥘 Preparação (30-60 minutos)

### Passo 1: Preparar o Fish Speech (Motor de IA)

```bash
# 1.1 - Criar o diretório de trabalho
cd ~/projetos
git clone https://github.com/fishaudio/fish-speech.git
cd fish-speech

# 1.2 - Criar ambiente virtual Python isolado
python3.11 -m venv venv_fish
source venv_fish/bin/activate

# 1.3 - Instalar as dependências base
pip install -e .

# 1.4 - Instalar o pacote mágico (sem ele não funciona!)
pip install torchcodec

# 1.5 - Baixar o modelo de IA (~3.3 GB - vai fazer um café!)
huggingface-cli download fishaudio/fish-speech-1.5 \
  --local-dir checkpoints/openaudio-s1-mini \
  --include "*.pth" "*.json"
```

**Dica do Chef**: O download demora ~5-15 minutos dependendo da tua internet!

---

### Passo 2: Corrigir Temperos (Bugs Conhecidos)

O Fish Speech tem um pequeno bug com versões novas do torchaudio. Vamos corrigir:

```bash
# 2.1 - Editar o ficheiro problemático
nano fish_speech/inference_engine/reference_loader.py
```

**Encontra a linha** (~linha 37):
```python
backends = torchaudio.list_audio_backends()
```

**Substitui por**:
```python
# torchaudio.list_audio_backends() foi removido em v2.1.0+
# Usar soundfile que é mais fiável
self.backend = "soundfile"
```

**Salva e sai** (Ctrl+O, Enter, Ctrl+X)

---

### Passo 3: Criar a Aplicação Web (Interface Bonita)

```bash
# 3.1 - Voltar ao diretório projetos
cd ~/projetos

# 3.2 - Criar estrutura da aplicação
mkdir -p VoiceClone/{templates,static/{css,js},recordings,outputs}
cd VoiceClone

# 3.3 - Criar ambiente virtual para a aplicação
python3.11 -m venv venv
source venv/bin/activate

# 3.4 - Instalar dependências da web
pip install flask==3.0.0 werkzeug==3.0.1 flask-cors==4.0.0
pip install torch torchaudio transformers loguru
pip install soundfile librosa pydub numpy scipy tqdm requests
```

---

### Passo 4: Criar os Ficheiros da Aplicação

#### 4.1 - Backend Python (`voice_cloner_fish.py`)

```python
"""
Voice Cloner com Fish Speech - Backend
"""
import os
import torch
import requests
import base64
from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

FISH_SPEECH_PATH = Path.home() / "projetos" / "fish-speech"
API_URL = "http://127.0.0.1:8080"

class VoiceCloner:
    def __init__(self, device=None):
        # Detectar GPU automaticamente
        if device is None:
            if torch.backends.mps.is_available():
                self.device = "mps"  # Mac M1/M2
            elif torch.cuda.is_available():
                self.device = "cuda"  # NVIDIA
            else:
                self.device = "cpu"

        logger.info(f"Usando dispositivo: {self.device}")

        # Verificar se API está a correr
        self._check_api_server()

    def _check_api_server(self):
        try:
            response = requests.get(f"{API_URL}/v1/health", timeout=2)
            if response.status_code == 200:
                logger.info("✅ Fish Speech API está a correr!")
                return
        except Exception as e:
            logger.error("❌ Fish Speech API não está a correr!")
            logger.error("Inicia o servidor com: cd ~/projetos/fish-speech && source venv_fish/bin/activate && python tools/api_server.py --llama-checkpoint-path checkpoints/openaudio-s1-mini --decoder-checkpoint-path checkpoints/openaudio-s1-mini/codec.pth --decoder-config-name modded_dac_vq --device mps --listen 127.0.0.1:8080")
            raise RuntimeError("API não disponível")

    def clone_voice(self, text, speaker_wav, language='pt', output_path='output.wav'):
        """
        Clonar voz e gerar fala

        Args:
            text: Texto para converter em fala
            speaker_wav: Ficheiro de áudio de referência (tua voz)
            language: Código do idioma ('pt', 'en', 'es', etc.)
            output_path: Onde salvar o áudio gerado
        """
        logger.info(f"🎙️ A gerar fala em {language}...")
        logger.info(f"📝 Texto: {text[:50]}...")

        # Ler áudio de referência
        with open(speaker_wav, 'rb') as f:
            audio_data = f.read()
            audio_b64 = base64.b64encode(audio_data).decode('utf-8')

        # Preparar pedido para API
        request_data = {
            "text": text,
            "references": [{
                "audio": audio_b64,
                "text": ""  # Auto-detectar
            }],
            "chunk_length": 200,
            "format": "wav",
            "max_new_tokens": 1024,
            "top_p": 0.8,
            "repetition_penalty": 1.1,
            "temperature": 0.8,
            "normalize": True,
            "use_memory_cache": "off",
            "streaming": False
        }

        # Enviar para API
        response = requests.post(
            f"{API_URL}/v1/tts",
            json=request_data,
            timeout=180
        )

        if response.status_code != 200:
            raise RuntimeError(f"Erro na API: {response.text}")

        # Salvar áudio
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, 'wb') as f:
            f.write(response.content)

        logger.info(f"✅ Áudio gerado: {output_path}")
        return str(output_path)
```

#### 4.2 - Servidor Web (`app.py`)

Cria o ficheiro `app.py` com Flask para servir a interface web. (Ver ficheiro completo no projeto)

#### 4.3 - Interface HTML (`templates/index.html`)

Cria o HTML com o design PT-PT. (Ver ficheiro completo no projeto)

---

## 🔥 Cozinhar (Executar)

### Passo 5: Iniciar o Servidor Fish Speech API

```bash
# 5.1 - Abrir um terminal novo
cd ~/projetos/fish-speech
source venv_fish/bin/activate

# 5.2 - Iniciar o servidor API
python tools/api_server.py \
  --llama-checkpoint-path checkpoints/openaudio-s1-mini \
  --decoder-checkpoint-path checkpoints/openaudio-s1-mini/codec.pth \
  --decoder-config-name modded_dac_vq \
  --device mps \
  --listen 127.0.0.1:8080
```

**Aguarda até ver**: "Uvicorn running on http://127.0.0.1:8080"

---

### Passo 6: Iniciar a Aplicação Web

```bash
# 6.1 - Abrir OUTRO terminal novo
cd ~/projetos/VoiceClone
source venv/bin/activate

# 6.2 - Iniciar o Flask
python app.py
```

**Aguarda até ver**: "Running on http://127.0.0.1:8000"

---

## 🍽️ Servir (Usar)

1. **Abre o browser**: http://127.0.0.1:8000

2. **Grava a tua voz**:
   - Clica em "Iniciar Gravação"
   - Fala claramente durante 10-30 segundos
   - Diz algo como: "Olá, o meu nome é [teu nome]. Esta é a minha voz."
   - Clica em "Parar Gravação"
   - Clica em "Guardar Gravação"

3. **Gera fala clonada**:
   - Seleciona a amostra de voz que gravaste
   - Escreve o texto que queres converter
   - Clica em "Gerar Fala"
   - Aguarda 10-30 segundos
   - Ouve o resultado!

---

## 🧹 Limpeza (Manutenção)

### Para parar os servidores:
```bash
# Nos terminais onde estão a correr, pressiona:
Ctrl + C
```

### Para reiniciar depois:
```bash
# Terminal 1: Fish Speech API
cd ~/projetos/fish-speech && source venv_fish/bin/activate
python tools/api_server.py --llama-checkpoint-path checkpoints/openaudio-s1-mini --decoder-checkpoint-path checkpoints/openaudio-s1-mini/codec.pth --decoder-config-name modded_dac_vq --device mps --listen 127.0.0.1:8080

# Terminal 2: Aplicação Web
cd ~/projetos/VoiceClone && source venv/bin/activate
python app.py
```

---

## 🔍 Resolução de Problemas

### Erro: "torchcodec is required"
```bash
cd ~/projetos/fish-speech
source venv_fish/bin/activate
pip install torchcodec
```

### Erro: "API request failed with status 500"
- Verifica se o servidor API Fish Speech está a correr
- Verifica os logs no terminal do Fish Speech
- Reinicia o servidor API

### Erro: "Fish Speech API server is already running"
- Isto é normal! Significa que já está a correr
- Não precisa de fazer nada

### Erro: Áudio não gera
1. Verifica que os 2 servidores estão a correr
2. Verifica que gravaste uma amostra de voz (mínimo 10 segundos)
3. Verifica a consola do browser (F12) para erros JavaScript

---

## 📊 Especificações Técnicas

- **Modelo**: Fish Speech S1-mini (OpenAudio)
- **Tamanho**: ~3.3 GB
- **GPU Support**: MPS (Mac), CUDA (NVIDIA), CPU
- **Idiomas**: Português (PT-PT e PT-BR), Inglês, Espanhol, Francês, Alemão, Italiano, Russo, Chinês, Japonês, Coreano
- **Taxa de Amostragem**: 44.1 kHz
- **Formato**: WAV

---

## 🎖️ Créditos

- **Fish Speech**: https://github.com/fishaudio/fish-speech
- **Desenvolvido por**: Fernando Nuno Vieira
- **Data**: Janeiro 2026
- **Modelo**: Fish Speech V1.5 S1-mini

---

## 📝 Notas Finais

Esta receita foi testada e funciona perfeitamente em Mac M1/M2 com GPU MPS.

**Tempo total de preparação**: ~45 minutos
**Tempo de cozinhar**: ~10-30 segundos por geração
**Dificuldade**: Média (requer conhecimentos básicos de terminal)

**Bom apetite... quer dizer, boa clonagem!** 🎤✨
