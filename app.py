import os
import re
import shutil
import pytube
from moviepy.video.io.ffmpeg_tools import ffmpeg_extract_audio
from pytube import Playlist
from flask import Flask, request, render_template, send_file

app = Flask(__name__)


def download_video_as_mp3(video_url, output_dir):
    yt = pytube.YouTube(video_url)
    video_stream = yt.streams.filter(
        only_audio=True, file_extension='mp4').first()

    # Download video as MP4
    video_stream.download(output_path=output_dir)

    # Define the output MP3 file path
    mp4_file_path = os.path.join(output_dir, video_stream.default_filename)
    mp3_file_path = os.path.splitext(mp4_file_path)[0] + '.mp3'

    # Convert MP4 to MP3
    ffmpeg_extract_audio(mp4_file_path, mp3_file_path)

    # Remove the downloaded MP4 file
    os.remove(mp4_file_path)

    return mp3_file_path


@app.route('/')
def index():
    directory_to_empty = 'downloaded_mp3'
    empty_directory(directory_to_empty)
    return render_template('index.html')


@app.route('/download', methods=['POST'])
def download():
    youtube_link = request.form['youtube_link']
    output_directory = "downloaded_mp3"
    os.makedirs(output_directory, exist_ok=True)

    try:
        mp3_file_path = download_video_as_mp3(youtube_link, output_directory)
        # os.remove(mp3_file_path)
        return send_file(mp3_file_path, as_attachment=True)
    except Exception as e:
        return f"An error occurred: {str(e)}"


def empty_directory(directory_path):
    try:
        items = os.listdir(directory_path)

        for item in items:
            item_path = os.path.join(directory_path, item)
            if os.path.isfile(item_path):
                os.remove(item_path)  # Remove files
            elif os.path.isdir(item_path):
                os.rmdir(item_path)   # Remove directories

        print(f"Directory '{directory_path}' has been emptied.")
    except Exception as e:
        print(f"An error occurred: {str(e)}")


if __name__ == '__main__':
    app.run(debug=True)
