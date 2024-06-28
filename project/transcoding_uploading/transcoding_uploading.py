import json
import boto3
import os
import tempfile
import base64
import subprocess

s3 = boto3.client('s3')
resolution = tuple(map(int, os.environ['RESOLUTION'].split('x')))
bucket = os.environ['BUCKET']

def transcoding_uploading(event, context):
    try:
        s3_key = event["key"]
        s3_bucket = event["bucket"]

        response = s3.get_object(Bucket=s3_bucket, Key=s3_key)
        json_data = response['Body'].read().decode('utf-8')
        data = json.loads(json_data)

        #transcode
        temp_output_file_path = tempfile.mktemp(suffix='.mp4')
        video_content_base64 = data["file_content"]
        ret = transcoding(base64.b64decode(video_content_base64), temp_output_file_path)

        with open(temp_output_file_path, 'rb') as video:
            new_video = video.read()

        #upisati
        key = f"{data['id']}{resolution[0]}_{resolution[1]}.mp4"
        s3.put_object(Bucket=bucket, Key=key, Body=new_video, ContentType='video/mp4')
        os.remove(temp_output_file_path)

        return event
    except Exception as e:
        raise Exception(f"Error in transcoding and uploading process: {str(e)}")


def transcoding(video_content, temp_output_file_path):
    try:
        with tempfile.NamedTemporaryFile(delete=False) as temp_input_file:
            temp_input_file.write(video_content)
            temp_input_file_path = temp_input_file.name

        command = [
            'ffmpeg',
            '-i', temp_input_file_path,
            '-vf', f'scale={resolution[0]}:{resolution[1]}',
            '-c:a', 'copy',
            temp_output_file_path
        ]

        subprocess.run(command, check=True)
    except subprocess.CalledProcessError as e:
        raise Exception(f"FFmpeg error: {str(e)}")
    finally:
        if os.path.exists(temp_input_file_path):
            os.remove(temp_input_file_path)
