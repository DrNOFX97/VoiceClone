#!/usr/bin/env python3
"""
Script de teste para geração de fala com Fish Speech
"""

import sys
from voice_cloner_fish import VoiceCloner

def main():
    print("🎤 Teste de Geração de Fala - Fish Speech\n")

    # Inicializar o voice cloner
    print("Inicializando Voice Cloner...")
    cloner = VoiceCloner(device='mps')

    # Texto de teste em PT-PT
    texto = "Olá, o meu nome é Fernando. Este é um teste de clonagem de voz usando o Fish Speech com português de Portugal."

    # Usar a gravação mais longa
    audio_referencia = "recordings/voice_sample_20260110_175446.wav"

    # Ficheiro de saída
    output = "outputs/test_fish_speech_final.wav"

    print(f"\n📝 Texto: {texto}")
    print(f"🎙️  Referência: {audio_referencia}")
    print(f"📁 Saída: {output}")
    print("\n⏳ A gerar fala... (isto pode demorar 10-30 segundos)\n")

    try:
        resultado = cloner.clone_voice(
            text=texto,
            speaker_wav=audio_referencia,
            language='pt',
            output_path=output
        )

        print(f"\n✅ SUCESSO! Áudio gerado: {resultado}")
        print("\nPodes ouvir o áudio gerado em:")
        print(f"  {resultado}")
        print("\nOu pela interface web em:")
        print("  http://127.0.0.1:8000")

        return 0

    except Exception as e:
        print(f"\n❌ ERRO: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())
