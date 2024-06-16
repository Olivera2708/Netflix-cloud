import json
import boto3
import os
import ffmpeg
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
    input_video = ffmpeg.input('pipe:0')
    output_video = ffmpeg.output(input_video, 'pipe:1', vf=f'scale={resolution[0]}:{resolution[1]}', vcodec='libx264', acodec='aac', preset='medium', crf=23)
    
    out, _ = (
        ffmpeg.run(output_video, input=video, capture_stdout=True, capture_stderr=True)
    )
    
    return base64.b64encode(out).decode('utf-8')
