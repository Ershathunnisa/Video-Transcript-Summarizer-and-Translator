from flask import Flask, render_template, request, send_from_directory
from pytube import YouTube
from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled
import os
import requests
import sys
import time
import moviepy.editor as mp
import whisper
from moviepy.editor import *
from moviepy.editor import VideoFileClip
from flask import jsonify
from transformers import T5Tokenizer, T5ForConditionalGeneration
from googletrans import Translator
from flask import request, jsonify

app = Flask(__name__)

@app.route('/static/<path:filename>')
def serve_static(filename):
    return send_from_directory('static', filename)

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/extract', methods=['GET', 'POST'])
def extract():
    if request.method == 'POST':
        # Handle file upload
        file = request.files['file']
        if file:
            # Save the file to a specific path
            file_path = os.path.join('uploads', file.filename)
            file.save(file_path)

            # Perform summarization using your existing code
            transcribed_text = transcribe_video(file_path)
            return transcribed_text

    elif request.method == 'GET':
        # Handle video link
        video_url = request.args.get('videoUrl')
        if video_url:
            # Perform summarization using your existing code
            transcribed_text = get_transcription_from_link(video_url)
            return transcribed_text
@app.route('/generate_summary', methods=['POST'])
def generate_summary():
    try:
        data = request.get_json()
        text = data['text']

        # Call your abstractive summarization function here
        summary = generate_abstractive_summary(text)

        # Return the summary as JSON
        return jsonify({'summary': summary})
    except Exception as e:
        return jsonify({'error': str(e)})
@app.route('/translate_text', methods=['POST'])
def translate_text():
    try:
        data = request.get_json()
        text = data['text']

        # Print the received text for debugging
        #print(f"Received text for translation: {text}")

        # Call the translation function
        translation = translate_to_telugu(text)
        #print(f"Translation successful: {translation}")

        return jsonify({'translation': translation})
    except Exception as e:
        print(f"Error in translation route: {str(e)}")
        return jsonify({'error': str(e)})

@app.route('/download')
def download():
    video_url = request.args.get('videoUrl')

    if video_url:
        DOWNLOAD_LOCATION = r"C:\Users\ersha\OneDrive\Desktop"  # Update with your desired download location
        youtube_video = YouTube(video_url)
        video_stream = youtube_video.streams.get_highest_resolution()
        downloaded_file_path = os.path.join(DOWNLOAD_LOCATION, video_stream.default_filename)

        try:
            # Download the video
            video_stream.download(output_path=DOWNLOAD_LOCATION)
            return jsonify({'success': True, 'filePath': downloaded_file_path})
        except Exception as e:
            print(f"Error downloading video: {e}")
            return jsonify({'success': False, 'error': str(e)})

    return jsonify({'success': False, 'error': 'No video URL provided.'})
def get_transcription_from_link(video_url):
    # Implement video transcription logic using your existing code
    # ...
    VIDEO_URL=video_url
    # Get the video ID from the URL
    video_id = VIDEO_URL.split('v=')[1]

    try:
        # Get the transcript
        transcript = YouTubeTranscriptApi.get_transcript(video_id)

        # Check if transcript is present
        if transcript:
            # Concatenate all text entries into a single paragraph
            full_transcript = ' '.join(entry['text'] for entry in transcript)

            # Print the full transcript as a paragraph
            return full_transcript
            '''
            with open('transcript.txt', 'w', encoding='utf-8') as file:
                file.write(full_transcript)'''

            #print('Transcript written to transcript.txt')
        else:
            return '-----no transcript available,download the video-----'
    except TranscriptsDisabled:
        return  '-----no transcript available,Please download the video-----'
        #return "Summarization result from link"
        

def transcribe_video(video_path):
    # Implement video transcription logic using your existing code
    # ...
    clip = VideoFileClip(video_path)
    # Extract the audio from the MP4 file
    audio = clip.audio
    # Save the audio as a WAV file
    audio.write_audiofile("audio.wav")



    model = whisper.load_model('base')

    out = model.transcribe('audio.wav')
    transcribed_text = out['text']


    # Write the transcribed text to a file
    '''
    with open('transcription.txt', 'w', encoding='utf-8') as file:
        file.write(transcribed_text)
    '''
    #print('Transcription written to transcription.txt')
    return transcribed_text
    #video_path=r"C:\Users\ersha\OneDrive\Desktop\74 Insertion Sort Algorithm Explanation with C Program Data Structure Tutorials.mp4"
    #transcribe_video(video_path)
    #return "Summarization result from file"
def generate_abstractive_summary(text):
    model_name = "t5-small"
    model = T5ForConditionalGeneration.from_pretrained(model_name)
    tokenizer = T5Tokenizer.from_pretrained(model_name)

    # Check if the input text already contains the prefix
    if not text.startswith("In this video, you are going to see about:"):
        text = text
    # Tokenize and truncate the input text
    inputs = tokenizer.encode(text, return_tensors="pt", max_length=512, truncation=True)

    # Generate the summary
    summary_ids = model.generate(inputs, max_length=250, length_penalty=2.0, num_beams=4, early_stopping=True)
    
    # Decode the summary
    summary = tokenizer.decode(summary_ids[0], skip_special_tokens=True)

    return summary

def translate_to_telugu(text):
    
    translator = Translator()
    # Split the text into chunks of 5000 characters
    chunks = [text[i:i+5000] for i in range(0, len(text), 5000)]
    translations = [translator.translate(chunk, dest='te').text for chunk in chunks]
    trans_text=''.join(translations)
    return trans_text



if __name__ == '__main__':
    app.run(debug=True)