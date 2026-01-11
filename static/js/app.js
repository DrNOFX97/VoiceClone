// CloneVoz - Aplicação JavaScript

// Variáveis globais
let mediaRecorder;
let audioChunks = [];
let recordedBlob;
let currentVoiceSample;
let generatedFilename;

// Elementos DOM
const recordBtn = document.getElementById('recordBtn');
const stopBtn = document.getElementById('stopBtn');
const uploadBtn = document.getElementById('uploadBtn');
const recordingStatus = document.getElementById('recordingStatus');
const audioPreview = document.getElementById('audioPreview');
const audioPlayback = document.getElementById('audioPlayback');
const textInput = document.getElementById('textInput');
const charCount = document.getElementById('charCount');
const voiceSampleSelect = document.getElementById('voiceSampleSelect');
const languageSelect = document.getElementById('languageSelect');
const generateBtn = document.getElementById('generateBtn');
const generationStatus = document.getElementById('generationStatus');
const generatedAudio = document.getElementById('generatedAudio');
const generatedPlayback = document.getElementById('generatedPlayback');
const downloadBtn = document.getElementById('downloadBtn');
const statusBanner = document.getElementById('statusBanner');
const recordingsContainer = document.getElementById('recordingsContainer');
const outputsList = document.getElementById('outputsList');
const systemInfo = document.getElementById('systemInfo');

// Inicializar aplicação
document.addEventListener('DOMContentLoaded', () => {
    console.log('🎤 CloneVoz inicializado');
    carregarGravacoes();
    carregarSaidas();
    carregarInfoSistema();
    configurarEventListeners();
});

// Configurar event listeners
function configurarEventListeners() {
    recordBtn.addEventListener('click', iniciarGravacao);
    stopBtn.addEventListener('click', pararGravacao);
    uploadBtn.addEventListener('click', enviarGravacao);
    textInput.addEventListener('input', atualizarContadorCaracteres);
    voiceSampleSelect.addEventListener('change', verificarBotaoGerar);
    textInput.addEventListener('input', verificarBotaoGerar);
    generateBtn.addEventListener('click', gerarFala);
    downloadBtn.addEventListener('click', descarregarAudioGerado);
}

// Mostrar banner de estado
function mostrarEstado(mensagem, tipo = 'success') {
    statusBanner.textContent = mensagem;
    statusBanner.className = `status-banner ${tipo}`;
    statusBanner.style.display = 'block';

    setTimeout(() => {
        statusBanner.style.display = 'none';
    }, 5000);
}

// Atualizar contador de caracteres
function atualizarContadorCaracteres() {
    const contagem = textInput.value.length;
    charCount.textContent = contagem;
    verificarBotaoGerar();
}

// Verificar se o botão gerar deve estar ativo
function verificarBotaoGerar() {
    const temTexto = textInput.value.trim().length > 0;
    const temVoz = voiceSampleSelect.value !== '';
    generateBtn.disabled = !(temTexto && temVoz);
}

// Iniciar gravação
async function iniciarGravacao() {
    try {
        const stream = await navigator.mediaDevices.getUserMedia({ audio: true });

        mediaRecorder = new MediaRecorder(stream);
        audioChunks = [];

        mediaRecorder.ondataavailable = (event) => {
            audioChunks.push(event.data);
        };

        mediaRecorder.onstop = () => {
            recordedBlob = new Blob(audioChunks, { type: 'audio/wav' });
            const audioUrl = URL.createObjectURL(recordedBlob);
            audioPlayback.src = audioUrl;
            audioPreview.style.display = 'block';
            uploadBtn.disabled = false;
        };

        mediaRecorder.start();

        recordBtn.disabled = true;
        stopBtn.disabled = false;
        recordingStatus.textContent = '🔴 A gravar... Fala claramente durante pelo menos 10 segundos';
        recordingStatus.className = 'status-text recording';

    } catch (error) {
        console.error('Erro ao aceder ao microfone:', error);
        mostrarEstado('Erro ao aceder ao microfone. Verifica as permissões.', 'error');
    }
}

// Parar gravação
function pararGravacao() {
    if (mediaRecorder && mediaRecorder.state !== 'inactive') {
        mediaRecorder.stop();
        mediaRecorder.stream.getTracks().forEach(track => track.stop());

        recordBtn.disabled = false;
        stopBtn.disabled = true;
        recordingStatus.textContent = '✅ Gravação parada. Revê e guarda.';
        recordingStatus.className = 'status-text';
    }
}

// Enviar gravação
async function enviarGravacao() {
    if (!recordedBlob) {
        mostrarEstado('Não há gravação para enviar', 'error');
        return;
    }

    try {
        uploadBtn.disabled = true;
        recordingStatus.textContent = '⏳ A enviar...';
        recordingStatus.className = 'status-text';

        const formData = new FormData();
        formData.append('audio', recordedBlob, 'gravacao.wav');

        const response = await fetch('/api/upload-voice', {
            method: 'POST',
            body: formData
        });

        const data = await response.json();

        if (data.success) {
            mostrarEstado(`✅ Amostra de voz guardada! Duração: ${data.duration}s`, 'success');
            recordingStatus.textContent = '';
            audioPreview.style.display = 'none';
            uploadBtn.disabled = true;

            // Recarregar gravações
            await carregarGravacoes();

            // Auto-selecionar a nova gravação
            voiceSampleSelect.value = data.filename;
            verificarBotaoGerar();
        } else {
            mostrarEstado(data.error || 'Falha no envio', 'error');
            uploadBtn.disabled = false;
        }

    } catch (error) {
        console.error('Erro no envio:', error);
        mostrarEstado('Falha no envio: ' + error.message, 'error');
        uploadBtn.disabled = false;
    }
}

// Carregar gravações
async function carregarGravacoes() {
    try {
        const response = await fetch('/api/recordings');
        const data = await response.json();

        if (data.success) {
            mostrarGravacoes(data.recordings);
            atualizarSelectAmostraVoz(data.recordings);
        } else {
            recordingsContainer.innerHTML = '<p>Erro ao carregar gravações</p>';
        }
    } catch (error) {
        console.error('Erro ao carregar gravações:', error);
        recordingsContainer.innerHTML = '<p>Erro ao carregar gravações</p>';
    }
}

// Mostrar gravações
function mostrarGravacoes(gravacoes) {
    if (gravacoes.length === 0) {
        recordingsContainer.innerHTML = '<p class="loading">Ainda não há amostras de voz. Grava uma acima!</p>';
        return;
    }

    recordingsContainer.innerHTML = gravacoes.map(rec => `
        <div class="recording-item">
            <div class="recording-info">
                <div class="recording-name">📁 ${rec.filename}</div>
                <div class="recording-meta">
                    Tamanho: ${formatarTamanhoFicheiro(rec.size)} |
                    Criado: ${formatarData(rec.created)}
                </div>
            </div>
            <div class="recording-actions">
                <button class="btn btn-primary" onclick="selecionarAmostraVoz('${rec.filename}')">
                    Usar Esta
                </button>
            </div>
        </div>
    `).join('');
}

// Atualizar select de amostra de voz
function atualizarSelectAmostraVoz(gravacoes) {
    voiceSampleSelect.innerHTML = '<option value="">-- Seleciona uma amostra de voz --</option>';

    gravacoes.forEach(rec => {
        const option = document.createElement('option');
        option.value = rec.filename;
        option.textContent = rec.filename;
        voiceSampleSelect.appendChild(option);
    });
}

// Selecionar amostra de voz
function selecionarAmostraVoz(filename) {
    voiceSampleSelect.value = filename;
    verificarBotaoGerar();
    mostrarEstado(`Amostra de voz "${filename}" selecionada`, 'success');
}

// Gerar fala
async function gerarFala() {
    const texto = textInput.value.trim();
    const amostraVoz = voiceSampleSelect.value;
    const idioma = languageSelect.value;

    if (!texto || !amostraVoz) {
        mostrarEstado('Por favor fornece texto e seleciona uma amostra de voz', 'error');
        return;
    }

    try {
        generateBtn.disabled = true;
        generationStatus.textContent = '🔄 A gerar fala... Isto pode demorar um momento.';
        generationStatus.className = 'status-text generating';

        const response = await fetch('/api/generate', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                text: texto,
                voice_sample: amostraVoz,
                language: idioma
            })
        });

        const data = await response.json();

        if (data.success) {
            generatedFilename = data.output_file;
            generatedPlayback.src = `/api/download/${data.output_file}`;
            generatedAudio.style.display = 'block';
            generationStatus.textContent = '✅ Fala gerada com sucesso!';
            generationStatus.className = 'status-text';
            mostrarEstado('✨ Fala gerada com sucesso!', 'success');

            // Recarregar saídas
            await carregarSaidas();
        } else {
            mostrarEstado(data.error || 'Falha na geração', 'error');
            generationStatus.textContent = '';
        }

    } catch (error) {
        console.error('Erro na geração:', error);
        mostrarEstado('Falha na geração: ' + error.message, 'error');
        generationStatus.textContent = '';
    } finally {
        generateBtn.disabled = false;
    }
}

// Descarregar áudio gerado
function descarregarAudioGerado() {
    if (generatedFilename) {
        window.location.href = `/api/download/${generatedFilename}`;
        mostrarEstado('Download iniciado!', 'success');
    }
}

// Carregar saídas
async function carregarSaidas() {
    try {
        const response = await fetch('/api/outputs');
        const data = await response.json();

        if (data.success) {
            mostrarSaidas(data.outputs);
        } else {
            outputsList.innerHTML = '<p>Erro ao carregar ficheiros de áudio</p>';
        }
    } catch (error) {
        console.error('Erro ao carregar saídas:', error);
        outputsList.innerHTML = '<p>Erro ao carregar ficheiros de áudio</p>';
    }
}

// Mostrar saídas
function mostrarSaidas(saidas) {
    if (saidas.length === 0) {
        outputsList.innerHTML = '<p class="loading">Ainda não há áudio gerado. Cria um acima!</p>';
        return;
    }

    outputsList.innerHTML = saidas.map(output => `
        <div class="recording-item">
            <div class="recording-info">
                <div class="recording-name">🎵 ${output.filename}</div>
                <div class="recording-meta">
                    Tamanho: ${formatarTamanhoFicheiro(output.size)} |
                    Criado: ${formatarData(output.created)}
                </div>
            </div>
            <div class="recording-actions">
                <audio controls style="max-width: 300px; margin-right: 10px;">
                    <source src="/api/download/${output.filename}" type="audio/wav">
                </audio>
                <button class="btn btn-success" onclick="descarregarFicheiro('${output.filename}')">
                    ⬇️ Descarregar
                </button>
            </div>
        </div>
    `).join('');
}

// Descarregar ficheiro
function descarregarFicheiro(filename) {
    window.location.href = `/api/download/${filename}`;
    mostrarEstado('Download iniciado!', 'success');
}

// Carregar informações do sistema
async function carregarInfoSistema() {
    try {
        const response = await fetch('/api/info');
        const data = await response.json();

        if (data.success) {
            const info = data.info;
            systemInfo.innerHTML = `
                <div class="info-item">
                    <span class="info-label">Modelo:</span>
                    <span class="info-value">${info.model}</span>
                </div>
                <div class="info-item">
                    <span class="info-label">Dispositivo:</span>
                    <span class="info-value">${info.device.toUpperCase()}</span>
                </div>
                <div class="info-item">
                    <span class="info-label">Idiomas Suportados:</span>
                    <span class="info-value">${info.supported_languages}</span>
                </div>
            `;
        } else {
            systemInfo.innerHTML = '<p>Erro ao carregar informações do sistema</p>';
        }
    } catch (error) {
        console.error('Erro ao carregar informações do sistema:', error);
        systemInfo.innerHTML = '<p>Erro ao carregar informações do sistema</p>';
    }
}

// Funções utilitárias
function formatarTamanhoFicheiro(bytes) {
    if (bytes < 1024) return bytes + ' B';
    if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB';
    return (bytes / (1024 * 1024)).toFixed(1) + ' MB';
}

function formatarData(isoString) {
    const data = new Date(isoString);
    return data.toLocaleString('pt-PT');
}
