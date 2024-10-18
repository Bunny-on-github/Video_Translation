from flask import Flask, render_template, request, jsonify, send_from_directory
from moviepy.editor import VideoFileClip
import speech_recognition as sr
from gtts import gTTS
import os
from translate import Translator

app = Flask(__name__)

# Folder paths for saving audio and videos
UPLOAD_FOLDER = 'uploads'
AUDIO_FOLDER = 'audio'
TRANSLATED_AUDIO_FOLDER = 'translated_audio'

# Ensure the directories exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(AUDIO_FOLDER, exist_ok=True)
os.makedirs(TRANSLATED_AUDIO_FOLDER, exist_ok=True)

# Step 1: Extract audio from video
def extract_audio_from_video(video_path):
    video = VideoFileClip(video_path)
    audio_path = os.path.join(AUDIO_FOLDER, "extracted_audio.wav")
    video.audio.write_audiofile(audio_path)
    return audio_path

# Step 2: Speech-to-Text
def recognize_speech(audio_path):
    recognizer = sr.Recognizer()
    with sr.AudioFile(audio_path) as source:
        audio = recognizer.record(source)
    
    try:
        text = recognizer.recognize_google(audio)
        return text
    except sr.UnknownValueError:
        return "Speech Recognition could not understand the audio."
    except sr.RequestError as e:
        return f"Could not request results; {e}"

# Step 3: Translate English text to Hindi
def translate_text_to_hindi(text):
    translator = Translator(to_lang="hi")
    translated_text = translator.translate(text)
    return translated_text

# Step 4: Convert translated text to speech
def convert_text_to_speech(text):
    output_audio_path = os.path.join(TRANSLATED_AUDIO_FOLDER, "translated_audio.mp3")
    tts = gTTS(text=text, lang='hi')
    tts.save(output_audio_path)
    return output_audio_path

# Step 5: Replace audio in video
def replace_audio_in_video(video_path, new_audio_path):
    output_video_path = os.path.join(UPLOAD_FOLDER, "output_video.mp4")
    os.system(f'ffmpeg -i {video_path} -i {new_audio_path} -c:v copy -map 0:v:0 -map 1:a:0 -shortest {output_video_path}')
    return output_video_path

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/process_video', methods=['POST'])
def process_video():
    file = request.files['video']
    video_path = os.path.join(UPLOAD_FOLDER, 'uploaded_video.mp4')
    file.save(video_path)

    # Step 1: Extract audio from video
    audio_path = extract_audio_from_video(video_path)

    # Step 2: Get transcription
    english_text = recognize_speech(audio_path)

    # Step 3: Translate the text to Hindi
    translated_text = translate_text_to_hindi(english_text)

    # Step 4: Convert translated Hindi text to speech
    translated_audio_path = convert_text_to_speech(translated_text)

    # Step 5: Replace audio in the video
    output_video_path = replace_audio_in_video(video_path, translated_audio_path)

    return jsonify({
        "status": "Processing Complete",
        "output_video": output_video_path,
        "transcription": english_text,
        "translation": translated_text,
        "audio_path": audio_path,
        "translated_audio_path": translated_audio_path
    })

# Route to serve saved audio files
@app.route('/audio/<path:filename>')
def get_audio_file(filename):
    return send_from_directory(AUDIO_FOLDER, filename)

@app.route('/translated_audio/<path:filename>')
def get_translated_audio_file(filename):
    return send_from_directory(TRANSLATED_AUDIO_FOLDER, filename)

if __name__ == "__main__":
    app.run(debug=True)
