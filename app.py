"""
VoiceClone Flask Application
Web interface for voice cloning system
"""

from flask import Flask, render_template, request, jsonify, send_file
from flask_cors import CORS
from werkzeug.utils import secure_filename
import os
from pathlib import Path
import logging
from datetime import datetime
from dotenv import load_dotenv
from voice_cloner_fish import VoiceCloner
from pydub import AudioSegment

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# Configuration
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50MB max file size

# Directories
RECORDINGS_DIR = Path('recordings')
OUTPUTS_DIR = Path('outputs')
RECORDINGS_DIR.mkdir(exist_ok=True)
OUTPUTS_DIR.mkdir(exist_ok=True)

# Allowed audio extensions
ALLOWED_EXTENSIONS = {'wav', 'mp3', 'ogg', 'flac', 'm4a'}

# Initialize Voice Cloner (lazy loading)
voice_cloner = None


def get_voice_cloner():
    """Lazy load voice cloner"""
    global voice_cloner
    if voice_cloner is None:
        logger.info("Loading voice cloner...")
        voice_cloner = VoiceCloner()
        logger.info("Voice cloner loaded successfully")
    return voice_cloner


def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/')
def index():
    """Main page"""
    return render_template('index.html')


@app.route('/api/info', methods=['GET'])
def get_info():
    """Get system information"""
    try:
        cloner = get_voice_cloner()
        info = cloner.info()
        return jsonify({
            'success': True,
            'info': info
        })
    except Exception as e:
        logger.error(f"Error getting info: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/languages', methods=['GET'])
def get_languages():
    """Get supported languages"""
    try:
        cloner = get_voice_cloner()
        languages = cloner.get_supported_languages()
        return jsonify({
            'success': True,
            'languages': languages
        })
    except Exception as e:
        logger.error(f"Error getting languages: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/upload-voice', methods=['POST'])
def upload_voice():
    """Upload voice recording"""
    try:
        if 'audio' not in request.files:
            return jsonify({
                'success': False,
                'error': 'No audio file provided'
            }), 400

        file = request.files['audio']

        if file.filename == '':
            return jsonify({
                'success': False,
                'error': 'No file selected'
            }), 400

        if file and allowed_file(file.filename):
            # Generate unique filename
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = secure_filename(f"voice_sample_{timestamp}.wav")
            filepath = RECORDINGS_DIR / filename
            temp_filepath = RECORDINGS_DIR / f"temp_{filename}"

            # Save file temporarily
            file.save(temp_filepath)
            logger.info(f"Voice sample saved temporarily: {temp_filepath}")

            # Convert to proper WAV format (handle WebM from browser)
            try:
                audio = AudioSegment.from_file(temp_filepath)
                audio.export(filepath, format="wav", parameters=["-ar", "24000", "-ac", "1"])
                logger.info(f"Converted to WAV: {filepath}")
                # Remove temp file
                temp_filepath.unlink()
            except Exception as e:
                logger.error(f"Error converting audio: {e}")
                # If conversion fails, try to use the original
                if temp_filepath.exists():
                    temp_filepath.rename(filepath)

            # Validate duration
            cloner = get_voice_cloner()
            is_valid, duration = cloner.validate_audio_duration(str(filepath))

            if not is_valid:
                return jsonify({
                    'success': False,
                    'error': f'Audio too short. Duration: {duration:.1f}s. Need at least 6 seconds.'
                }), 400

            return jsonify({
                'success': True,
                'filename': filename,
                'duration': round(duration, 2),
                'message': 'Voice sample uploaded successfully'
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Invalid file type. Allowed: ' + ', '.join(ALLOWED_EXTENSIONS)
            }), 400

    except Exception as e:
        logger.error(f"Error uploading voice: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/generate', methods=['POST'])
def generate_speech():
    """Generate speech from text"""
    try:
        data = request.get_json()

        # Validate input
        if not data:
            return jsonify({
                'success': False,
                'error': 'No data provided'
            }), 400

        text = data.get('text', '').strip()
        voice_sample = data.get('voice_sample')
        language = data.get('language', 'en')

        if not text:
            return jsonify({
                'success': False,
                'error': 'Text is required'
            }), 400

        if not voice_sample:
            return jsonify({
                'success': False,
                'error': 'Voice sample is required'
            }), 400

        # Check if voice sample exists
        speaker_wav_path = RECORDINGS_DIR / voice_sample
        if not speaker_wav_path.exists():
            return jsonify({
                'success': False,
                'error': 'Voice sample not found'
            }), 404

        # Generate output filename
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_filename = f"generated_{timestamp}.wav"
        output_path = OUTPUTS_DIR / output_filename

        # Generate speech
        cloner = get_voice_cloner()
        logger.info(f"Generating speech for text: {text[:50]}...")

        result_path = cloner.clone_voice(
            text=text,
            speaker_wav=str(speaker_wav_path),
            language=language,
            output_path=str(output_path)
        )

        return jsonify({
            'success': True,
            'output_file': output_filename,
            'message': 'Speech generated successfully'
        })

    except Exception as e:
        logger.error(f"Error generating speech: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/download/<filename>')
def download_file(filename):
    """Download generated audio file"""
    try:
        file_path = OUTPUTS_DIR / secure_filename(filename)

        if not file_path.exists():
            return jsonify({
                'success': False,
                'error': 'File not found'
            }), 404

        return send_file(
            file_path,
            as_attachment=True,
            download_name=filename
        )

    except Exception as e:
        logger.error(f"Error downloading file: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/recordings', methods=['GET'])
def list_recordings():
    """List all voice recordings"""
    try:
        recordings = []
        for file_path in RECORDINGS_DIR.glob('*.wav'):
            recordings.append({
                'filename': file_path.name,
                'size': file_path.stat().st_size,
                'created': datetime.fromtimestamp(file_path.stat().st_ctime).isoformat()
            })

        recordings.sort(key=lambda x: x['created'], reverse=True)

        return jsonify({
            'success': True,
            'recordings': recordings
        })

    except Exception as e:
        logger.error(f"Error listing recordings: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/outputs', methods=['GET'])
def list_outputs():
    """List all generated audio files"""
    try:
        outputs = []
        for file_path in OUTPUTS_DIR.glob('*.wav'):
            outputs.append({
                'filename': file_path.name,
                'size': file_path.stat().st_size,
                'created': datetime.fromtimestamp(file_path.stat().st_ctime).isoformat()
            })

        outputs.sort(key=lambda x: x['created'], reverse=True)

        return jsonify({
            'success': True,
            'outputs': outputs
        })

    except Exception as e:
        logger.error(f"Error listing outputs: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.errorhandler(404)
def not_found(error):
    """404 error handler"""
    return jsonify({
        'success': False,
        'error': 'Endpoint not found'
    }), 404


@app.errorhandler(500)
def internal_error(error):
    """500 error handler"""
    return jsonify({
        'success': False,
        'error': 'Internal server error'
    }), 500


if __name__ == '__main__':
    # Get configuration from environment
    host = os.getenv('HOST', '0.0.0.0')
    port = int(os.getenv('PORT', 5000))
    debug = os.getenv('FLASK_DEBUG', 'True').lower() == 'true'

    logger.info(f"Starting VoiceClone server on {host}:{port}")
    logger.info(f"Debug mode: {debug}")

    app.run(host=host, port=port, debug=debug)
