from flask import Flask, request, jsonify, send_from_directory
import openai
import requests
from moviepy.editor import ImageClip, concatenate_videoclips, AudioFileClip
import os

app = Flask(__name__)

openai.api_key = os.getenv('OPENAI_API_KEY')
TEMP_DIR = 'temp_files'
if not os.path.exists(TEMP_DIR):
    os.makedirs(TEMP_DIR)

def generate_image_from_text(text_description):
    try:
        response = openai.Image.create(
            prompt=text_description,
            n=1,
            size="1024x1024"
        )
        image_url = response['data'][0]['url']
        return image_url
    except Exception as e:
        raise ValueError(f"Error generating image: {str(e)}")

def download_image(image_url, index):
    try:
        response = requests.get(image_url)
        image_path = os.path.join(TEMP_DIR, f'image_{index}.png')
        with open(image_path, 'wb') as file:
            file.write(response.content)
        return image_path
    except Exception as e:
        raise ValueError(f"Error downloading image: {str(e)}")

def create_video_from_images_and_audio(image_paths, audio_file_path):
    try:
        clips = [ImageClip(img_path).set_duration(3) for img_path in image_paths]
        video = concatenate_videoclips(clips, method="compose")
        audio = AudioFileClip(audio_file_path)
        video = video.set_audio(audio)
        video_path = os.path.join(TEMP_DIR, 'output_video.mp4')
        video.write_videofile(video_path, fps=24)
        return video_path
    except Exception as e:
        raise ValueError(f"Error creating video: {str(e)}")

@app.route('/process-audio', methods=['POST'])
def process_audio():
    try:
        audio_file = request.files['audio']
        audio_file_path = os.path.join(TEMP_DIR, 'audio.wav')
        audio_file.save(audio_file_path)

        # Generate images for each scene
        transcript = "Your video scenes will be generated based on this input."  # Placeholder for transcript
        scenes = transcript.split('. ')  # Split transcript into scenes
        image_paths = []

        for idx, scene in enumerate(scenes):
            image_url = generate_image_from_text(scene)
            image_path = download_image(image_url, idx)
            image_paths.append(image_path)

        # Create video from images and audio
        video_path = create_video_from_images_and_audio(image_paths, audio_file_path)

        return jsonify({'transcript': transcript, 'video_url': f'/download/{os.path.basename(video_path)}'})

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/download/<filename>', methods=['GET'])
def download_file(filename):
    return send_from_directory(TEMP_DIR, filename)

if __name__ == '__main__':
    app.run(debug=True)
