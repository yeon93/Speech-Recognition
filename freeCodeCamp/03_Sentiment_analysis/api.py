#Speech_recognition.py 를 감정분석 작업에 사용할 수 있도록 수정한 코드임

import requests                                    
from assemblyai_api_key import API_KEY_ASSEMBLYAI 
import time
import json

upload_endpoint = 'https://api.assemblyai.com/v2/upload'
transcript_endpoint = "https://api.assemblyai.com/v2/transcript"
headers = {'authorization': API_KEY_ASSEMBLYAI}

def upload(filename):
    def read_file(filename, chunk_size=5242880): 
        with open(filename, 'rb') as _file:
            while True:
                data = _file.read(chunk_size)
                if not data:
                    break
                yield data
    
    upload_response = requests.post(upload_endpoint, headers=headers, data=read_file(filename))
    audio_url = upload_response.json()['upload_url']
    
    return audio_url


def transcribe(audio_url, sentiment_analysis):
    transcript_request = { "audio_url": audio_url ,    
                            "sentiment_analysis":sentiment_analysis}
    transcript_response = requests.post(transcript_endpoint, json=transcript_request, headers=headers)
    job_id = transcript_response.json()['id']
    
    return job_id


def poll(transcript_id):
    polling_endpoint = transcript_endpoint + '/' + transcript_id
    polling_response = requests.get(polling_endpoint, headers=headers)  
    
    return polling_response.json()


def get_transcription_result_url(audio_url, sentiment_analysis):
    transcript_id = transcribe(audio_url, sentiment_analysis)
    num_sleep = 0
    while True:
        polling_response = poll(transcript_id)
        print('*' * 130)
        
        if polling_response['status'] == 'completed':
            return polling_response, None
        elif polling_response['status'] == 'error':
            return polling_response, polling_response['error']
        
        num_sleep += 1
        print(f'Waiting 30 seconds... ({num_sleep})')
        print('*' * 130)
        time.sleep(30)
        
        
def save_transcript(audio_url, filename, sentiment_analysis=False):
    polling_response, error = get_transcription_result_url(audio_url, sentiment_analysis)
    
    if error == None:
        text_filename = filename + '.txt'
        with open(text_filename, 'w') as f:
            f.write(polling_response['text'])
        
        if sentiment_analysis:
            text_filename = filename + '_sentiments.json'
            with open(text_filename, 'w') as f:
                sentiments = polling_response['sentiment_analysis_results']
                json.dump(sentiments, f, indent=4)
        print('Transcription saved! ')
        return True
    elif error:
        print('Error!!!\n', error)
        return False
        