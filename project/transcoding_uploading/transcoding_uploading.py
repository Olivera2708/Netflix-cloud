import json
import boto3
import os
from moviepy.editor import VideoFileClip
from io import BytesIO
import base64

s3 = boto3.client('s3')
resolution = tuple(map(int, os.environ['RESOLUTION'].split('x')))
bucket = os.environ['BUCKET']

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
    key = f"{data['id']}_{resolution[0]}_{resolution[1]}.mp4"
    file_content = base64.b64decode(new_video_content)

    s3.put_object(Bucket=bucket, Key=key, Body=file_content)

    return event

def transcoding(video):
    clip = VideoFileClip(video)
    resized_clip = clip.resize(newsize=resolution)
    video_bytes = BytesIO()
    resized_clip.write_videofile(
        video_bytes, 
        codec='libx264', 
        audio_codec='aac',
        preset='medium',
        ffmpeg_params=['-crf', '23']
    )
    video_bytes.seek(0)
    clip.close()
    resized_clip.close()

    return video_bytes.getvalue()
