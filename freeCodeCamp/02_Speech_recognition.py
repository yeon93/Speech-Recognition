#STEP 1: UPLOAD YOUR AUDIO FILE
import requests                                    #assembly API와 통신할 수 있도록
from assemblyai_api_key import API_KEY_ASSEMBLYAI  #저장해둔 API key 불러오기
import sys
import time


filename = "american.wav"
upload_endpoint = 'https://api.assemblyai.com/v2/upload'
transcript_endpoint = "https://api.assemblyai.com/v2/transcript"
#filename = sys.argv[1]    #'--ip=127.0.0.1'
headers = {'authorization': API_KEY_ASSEMBLYAI}

#로컬 오디오 파일을 assembly ai에 업로드하고, 업로드된 url을 반환하는 함수
def upload(filename):
    
    #음성 데이터를 청크 단위로 읽는 함수(일부 ai는 파일이 청크단위여야 하기 때문)
    def read_file(filename, chunk_size=5242880): 
        with open(filename, 'rb') as _file:
            while True:
                data = _file.read(chunk_size)
                if not data:
                    break
                yield data
    
    #assembly ai에 파일 업로드
    upload_response = requests.post(upload_endpoint,
                            headers=headers,
                            data=read_file(filename))
    #print(response.json())

    audio_url = upload_response.json()['upload_url']
    return audio_url


#url에 텍스트 변환을 요청하고, 해당 작업의 id를 반환하는 함수
def transcribe(audio_url):
    transcript_request = { "audio_url": audio_url }    #변환을 위해 assembly로 전송한 오디오 데이터

    transcript_response = requests.post(transcript_endpoint, json=transcript_request, headers=headers)
    #print(transcript_response.json())
    job_id = transcript_response.json()['id']
    return job_id


#변환 작업에 대한 정보를 반환하는 함수
''' ex)
{'id': 'r86553iyq7-1213-4e28-a631-8e083c6fcfd0', 
'language_model': 'assemblyai_default', 'acoustic_model': 'assemblyai_default', 
'language_code': 'en_us', 'status': 'processing', 
'audio_url': 'https://cdn.assemblyai.com/upload/41211eeb-5b6e-4b4e-9f52-d5426e9bc597', 
'text': None, 'words': None, 'utterances': None, 'confidence': None, 
'audio_duration': None, 'punctuate': True, 'format_text': True, 'dual_channel': None, 
'webhook_url': None, 'webhook_status_code': None, 'webhook_auth': False, 
'webhook_auth_header_name': None, 'speed_boost': False, 'auto_highlights_result': None, 
'auto_highlights': False, 'audio_start_from': None, 'audio_end_at': None, 
'word_boost': [], 'boost_param': None, 'filter_profanity': False, 'redact_pii': False, 
'redact_pii_audio': False, 'redact_pii_audio_quality': None, 'redact_pii_policies': None, 
'redact_pii_sub': None, 'speaker_labels': False, 'content_safety': False, 
'iab_categories': False, 'content_safety_labels': {}, 'iab_categories_result': {}, 
'language_detection': False, 'custom_spelling': None, 'cluster_id': None, 'throttled': None, 
'auto_chapters': False, 'summarization': False, 'summary_type': None, 'summary_model': None, 
'disfluencies': False, 'sentiment_analysis': False, 'chapters': None, 
'sentiment_analysis_results': None, 'entity_detection': False, 'entities': None, 'summary': None}
'''
def poll(transcript_id):
    polling_endpoint = transcript_endpoint + '/' + transcript_id

    #변환 작업에 대한 정보를 assembly ai에 요청
    polling_response = requests.get(polling_endpoint, headers=headers)

    print(polling_response)
    print(polling_response.json())    
    
    return polling_response.json()


#해당 작업이 완료될 때까지 작업 정보를 계속해서 요청하는 함수
def get_transcription_result_url(audio_url):
    transcript_id = transcribe(audio_url)
    while True:
        polling_response = poll(transcript_id)
        print('*' * 130)
        
        if polling_response['status'] == 'completed':
            return polling_response, None
        elif polling_response['status'] == 'error':
            return polling_response, polling_response['error']
        
        print('Waiting 10 seconds...')
        print('*' * 130)
        time.sleep(10)
        
        
#변환 결과인 text를 저장하는 함수
def save_transcript(audio_url):
    start = time.time()
    polling_response, error = get_transcription_result_url(audio_url)
    
    if error == None:
        text_filename = filename[:-3] + '.txt'
        with open(text_filename, 'w') as f:
            f.write(polling_response['text'])
        end = time.time()
        
        print('Transcription saved! (It took {} sec)'.format(round(end-start, 2)))
        
    elif error:
        print('Error!!!\n', error)
        

audio_url = upload(filename)  
save_transcript(audio_url)