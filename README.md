# 🎤 CloneVoz - Sistema de Clonagem de Voz com IA

Clone a tua voz com apenas 10 segundos de áudio e gera fala em português de Portugal!

![Python](https://img.shields.io/badge/Python-3.11-blue.svg)
![Fish Speech](https://img.shields.io/badge/Fish%20Speech-V1.5%20S1--mini-green.svg)
![Flask](https://img.shields.io/badge/Flask-Interface%20Web-lightgrey.svg)
![GPU](https://img.shields.io/badge/GPU-MPS%20%7C%20CUDA%20%7C%20CPU-orange.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)

---

## 🌟 Funcionalidades

- 🎙️ **Clonagem Rápida de Voz**: Clona qualquer voz com apenas 10 segundos de áudio
- 🇵🇹 **Suporte PT-PT**: Preserva perfeitamente o sotaque português de Portugal
- 🌍 **Multi-Idioma**: Funciona com 12+ idiomas incluindo Português, Inglês, Espanhol, Francês e mais
- 🎨 **Interface Web em PT-PT**: Interface bonita e intuitiva totalmente em português
- 🔊 **Alta Qualidade**: Síntese de voz profissional com Fish Speech S1-mini
- 💾 **Biblioteca de Áudio**: Guarda e gere as tuas vozes clonadas e áudio gerado
- 🚀 **Geração Rápida**: Gera fala em segundos
- 📝 **Texto-para-Fala**: Escreve qualquer texto e ouve na tua voz clonada
- 🖥️ **Suporte GPU**: Aceleração com MPS (Mac M1/M2), CUDA (NVIDIA) ou CPU

---

## 🎯 Casos de Uso

- 📚 Criar audiolivros com a tua própria voz
- 🎥 Narrar vídeos sem gravar
- 🤖 Construir assistentes virtuais com a tua voz
- 🎙️ Gerar conteúdo de podcast
- 📞 Criar mensagens de voz personalizadas
- 🌐 Ferramentas de acessibilidade para deficiências vocais

---

## 🛠️ Stack Tecnológica

- **Modelo de IA**: Fish Speech V1.5 S1-mini (OpenAudio)
- **Backend**: Python 3.11, Flask 3.0
- **Frontend**: HTML5, CSS3, JavaScript (100% PT-PT)
- **Processamento de Áudio**: PyTorch, torchaudio, torchcodec
- **GPU Support**: Metal Performance Shaders (MPS), CUDA, CPU
- **Tamanho do Modelo**: ~3.3 GB

---

## 📋 Pré-requisitos

### Software
- **Python 3.11** (obrigatório - não funciona com 3.12 ou 3.13)
- **Microfone** para gravar amostras de voz
- **~10 GB de espaço em disco** (modelo + dependências)
- **Conexão à internet** (para download inicial do modelo)

### Hardware

#### 🍎 Mac (Recomendado)
- **Mac M1/M2/M3** com GPU integrada (MPS)
- **RAM**: 12-16 GB de unified memory
- **Performance**: Boa (~10-30 segundos por geração)

#### 🖥️ PC com GPU NVIDIA (CUDA)
- **VRAM Recomendada**: 12 GB para inferência fluída
- **GPUs Compatíveis**:
  - **Económica**: RTX 3060 (12 GB) - ~€350
  - **Média**: RTX 4070 (12 GB) - ~€650
  - **High-End**: RTX 4090 (24 GB) - ~€1800
- **Performance**: Excelente (RTX 4090: real-time factor 1:7)

#### 💻 CPU (Fallback)
- **Qualquer CPU moderno** (Intel/AMD)
- **RAM**: 16 GB recomendado
- **Performance**: Lenta (~1-5 minutos por geração)

---

## 🚀 Instalação Rápida

### Opção 1: Seguir a Receita Completa

**Recomendado para primeira instalação!**

Vê o ficheiro [`RECEITA_INSTALACAO.md`](RECEITA_INSTALACAO.md) para um guia passo-a-passo detalhado como se fosse uma receita culinária.

### Opção 2: Instalação Rápida

```bash
# 1. Clonar o repositório
git clone https://github.com/DrNOFX97/VoiceClone.git
cd VoiceClone

# 2. Criar ambiente virtual Python 3.11
python3.11 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 3. Instalar dependências da aplicação
pip install --upgrade pip
pip install -r requirements.txt

# 4. Instalar Fish Speech (em paralelo)
cd ~/projetos
git clone https://github.com/fishaudio/fish-speech.git
cd fish-speech
python3.11 -m venv venv_fish
source venv_fish/bin/activate
pip install -e .
pip install torchcodec

# 5. Baixar o modelo (~3.3 GB)
huggingface-cli download fishaudio/fish-speech-1.5 \
  --local-dir checkpoints/openaudio-s1-mini \
  --include "*.pth" "*.json"

# 6. Corrigir bug do torchaudio (ver RECEITA_INSTALACAO.md)
# Editar: fish_speech/inference_engine/reference_loader.py
# Linha ~37: substituir torchaudio.list_audio_backends() por self.backend = "soundfile"
```

---

## 🔥 Como Executar

### Iniciar os Servidores (2 terminais necessários)

**Terminal 1 - Fish Speech API Server:**
```bash
cd ~/projetos/fish-speech
source venv_fish/bin/activate
python tools/api_server.py \
  --llama-checkpoint-path checkpoints/openaudio-s1-mini \
  --decoder-checkpoint-path checkpoints/openaudio-s1-mini/codec.pth \
  --decoder-config-name modded_dac_vq \
  --device mps \
  --listen 127.0.0.1:8080
```

**Terminal 2 - Aplicação Web:**
```bash
cd ~/projetos/VoiceClone
source venv/bin/activate
python app.py
```

### Abrir no Browser

Navega para: **http://127.0.0.1:8000**

---

## 📖 Como Usar

### Passo 1: Gravar Amostra de Voz
1. Clica em **"Iniciar Gravação"**
2. Permite acesso ao microfone
3. Grava pelo menos **10 segundos** de fala clara
4. Diz algo natural como: *"Olá, o meu nome é Fernando e esta é a minha voz"*
5. Clica em **"Parar Gravação"** e depois **"Guardar Gravação"**

### Passo 2: Gerar Fala
1. Seleciona a amostra de voz que gravaste
2. Escreve qualquer texto na caixa de texto
3. Escolhe o idioma (Português PT-PT por padrão)
4. Clica em **"Gerar Fala"**
5. Aguarda 10-30 segundos
6. Ouve o resultado na tua voz clonada!

### Passo 3: Descarregar ou Ouvir
- Ouve diretamente no player integrado
- Descarrega o ficheiro de áudio gerado
- Guarda na tua biblioteca de áudio

---

## 🎨 Preview da Interface

### Dashboard Principal
- **Secção de Gravação**: Captura a tua amostra de voz
- **Secção de Geração**: Insere texto e cria fala
- **Biblioteca de Áudio**: Navega pelos teus ficheiros guardados com player integrado
- **Informações do Sistema**: Vê o modelo e device a ser usado

**Interface 100% em Português de Portugal!** 🇵🇹

---

## 🔧 Configuração

### Idiomas Suportados

- 🇵🇹 **Português (PT-PT e PT-BR)** - Preserva sotaque português!
- 🇬🇧 Inglês (en)
- 🇪🇸 Espanhol (es)
- 🇫🇷 Francês (fr)
- 🇩🇪 Alemão (de)
- 🇮🇹 Italiano (it)
- 🇷🇺 Russo (ru)
- 🇨🇳 Chinês (zh)
- 🇯🇵 Japonês (ja)
- 🇰🇷 Coreano (ko)
- E mais...

### Configurações de Áudio

Podes ajustar (em `.env`):
- Taxa de amostragem (padrão: 24000 Hz)
- Dispositivo: MPS (Mac GPU) | CUDA (NVIDIA GPU) | CPU
- Formato de saída: WAV

---

## 📁 Estrutura do Projeto

```
VoiceClone/
├── app.py                      # Aplicação Flask
├── voice_cloner_fish.py        # Lógica de clonagem (Fish Speech)
├── test_generation.py          # Script de teste
├── requirements.txt            # Dependências Python
├── README.md                   # Esta documentação
├── RECEITA_INSTALACAO.md       # Guia passo-a-passo detalhado
├── .env                        # Variáveis de ambiente
├── .gitignore                  # Ficheiros ignorados pelo Git
├── recordings/                 # Amostras de voz guardadas
├── outputs/                    # Ficheiros de áudio gerados
├── static/                     # CSS, JS, imagens
│   ├── css/
│   │   └── style.css          # Estilos em PT-PT
│   └── js/
│       └── app.js             # JavaScript em PT-PT
└── templates/                  # Templates HTML
    └── index.html             # Interface principal em PT-PT
```

---

## 🔒 Privacidade & Segurança

- ✅ Todo o processamento acontece **localmente** na tua máquina
- ✅ Nenhum dado é enviado para servidores externos
- ✅ As tuas amostras de voz são guardadas apenas no teu computador
- ✅ Tens controlo total sobre os teus dados
- ✅ Código 100% open source para auditoria

---

## 🐛 Resolução de Problemas

### Erro: "torchcodec is required"
```bash
cd ~/projetos/fish-speech
source venv_fish/bin/activate
pip install torchcodec
```

### Erro: "API request failed with status 500"
- Verifica se o Fish Speech API server está a correr no terminal 1
- Reinicia o servidor API
- Verifica os logs no terminal do Fish Speech

### Erro: "list_audio_backends not found"
- Segue o Passo 6 da instalação (corrigir bug do torchaudio)
- Edita `fish_speech/inference_engine/reference_loader.py`
- Substitui `torchaudio.list_audio_backends()` por `self.backend = "soundfile"`

### Download do modelo é lento
Na primeira vez, vai fazer download de ~3.3 GB. Sê paciente (5-15 minutos)!

### Problemas de qualidade de áudio
- Garante que o microfone está a funcionar
- Grava num ambiente silencioso
- Fala de forma clara e natural
- Usa pelo menos 10 segundos de áudio

### Erros de instalação
```bash
# Se tiveres erros do PyTorch:
pip install torch torchaudio --index-url https://download.pytorch.org/whl/cu118
```

---

## 🎖️ Tecnologias & Créditos

### Fish Speech V1.5
- **Modelo**: OpenAudio S1-mini (0.5B parâmetros)
- **Ranking**: #1 no TTS-Arena2 (Janeiro 2025)
- **Repositório**: https://github.com/fishaudio/fish-speech
- **Paper**: https://arxiv.org/abs/2411.01156
- **Licença**: BSD-3-Clause (uso comercial permitido)

### Vantagens do Fish Speech sobre XTTS-v2
✅ Melhor preservação do sotaque PT-PT
✅ Modelo mais recente (2025 vs 2023)
✅ Mais rápido e eficiente
✅ Suporte nativo para MPS (Mac M1/M2)
✅ Melhor qualidade de áudio
✅ Zero-shot: funciona sem fine-tuning

---

## 🛣️ Roadmap

- [x] Interface 100% em PT-PT
- [x] Suporte para Fish Speech V1.5
- [x] Player de áudio integrado
- [x] Preservação de sotaque PT-PT
- [x] Suporte MPS (Mac M1/M2)
- [ ] Controlo de emoções (feliz, triste, excitado)
- [ ] Processamento batch de texto-para-fala
- [ ] Mistura de vozes (blend múltiplas vozes)
- [ ] Endpoints API para integração
- [ ] Versão mobile
- [ ] Conversão de voz em tempo real
- [ ] Suporte multi-speaker

---

## 🤝 Contribuir

Contribuições são bem-vindas! Por favor, sente-te à vontade para submeter um Pull Request.

1. Faz fork do projeto
2. Cria o teu branch de feature (`git checkout -b feature/FeatureIncrivel`)
3. Faz commit das tuas alterações (`git commit -m 'Adicionar FeatureIncrivel'`)
4. Faz push para o branch (`git push origin feature/FeatureIncrivel`)
5. Abre um Pull Request

---

## 📄 Licença

Este projeto está licenciado sob a Licença MIT - vê o ficheiro [LICENSE](LICENSE) para detalhes.

**Nota**: O modelo Fish Speech está licenciado sob BSD-3-Clause (uso comercial permitido).

---

## 🙏 Agradecimentos

- [Fish Speech](https://github.com/fishaudio/fish-speech) - Framework incrível de TTS
- Equipa de desenvolvimento do modelo S1-mini
- Comunidade open-source
- ~~[Coqui TTS](https://github.com/coqui-ai/TTS)~~ - Versão anterior (XTTS-v2)

---

## 📞 Contacto

- **Autor**: Fernando Nuno Vieira
- **GitHub**: [@DrNOFX97](https://github.com/DrNOFX97)
- **LinkedIn**: [fnvieira](https://linkedin.com/in/fnvieira)

---

## 📚 Documentação Adicional

- [`RECEITA_INSTALACAO.md`](RECEITA_INSTALACAO.md) - Guia passo-a-passo detalhado como receita culinária
- [Fish Speech Docs](https://speech.fish.audio/docs/) - Documentação oficial do Fish Speech
- [Fish Speech GitHub](https://github.com/fishaudio/fish-speech) - Repositório oficial

---

## ⭐ Dá uma estrela se achares útil!

**Feito com ❤️ usando Python, IA e Português de Portugal** 🇵🇹

---

## 📊 Especificações Técnicas

| Especificação | Valor |
|---------------|-------|
| **Modelo** | Fish Speech S1-mini (OpenAudio) |
| **Tamanho do Modelo** | ~3.3 GB |
| **Parâmetros** | 0.5B |
| **Taxa de Amostragem** | 44.1 kHz |
| **Formato de Áudio** | WAV |
| **Dispositivos Suportados** | MPS (Mac M1/M2), CUDA (NVIDIA), CPU |
| **Tempo de Geração** | 10-30 segundos |
| **Áudio de Referência Mínimo** | 10 segundos |
| **Python Requerido** | 3.11 |
| **Ranking TTS-Arena2** | #1 (Janeiro 2025) |

---

**Versão**: 2.0 (Fish Speech Edition)
**Data**: Janeiro 2026
**Status**: ✅ Funcional e Testado
