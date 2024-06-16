import json
import boto3
import os
import base64
import subprocess

s3 = boto3.client('s3')
resolution = tuple(map(int, os.environ['RESOLUTION'].split('x')))
bucket = os.environ['BUCKET']
FFMPEG_CMD = '/opt/bin/ffmpeg'

def transcoding_uploading(event, context):
    s3_key = event["key"]
    s3_bucket = event["bucket"]

    response = s3.get_object(Bucket=s3_bucket, Key=s3_key)
    json_data = response['Body'].read().decode('utf-8')
    data = json.loads(json_data)

    #transcode
    video_content_base64 = data["file_content"]
    new_video_content = transcoding(base64.b64decode(video_content_base64))

    #upisati
    key = f"{data['id']}{resolution[0]}_{resolution[1]}.mp4"

    s3.put_object(Bucket=bucket, Key=key, Body=new_video_content)

    return event

def transcoding(video_content):
    # Transcode using ffmpeg
    cmd = [
        FFMPEG_CMD,
        '-i', 'pipe:0',  # Read input from stdin
        '-vf', f'scale={resolution[0]}:{resolution[1]}',
        '-codec:v', 'h264',
        '-b:v', '1500k',
        '-f', 'mp4',
        'pipe:1'  # Output to stdout
    ]

    # Execute ffmpeg command
    ffmpeg_process = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE)
    transcoded_video_content, _ = ffmpeg_process.communicate(input=video_content)

    return transcoded_video_content
