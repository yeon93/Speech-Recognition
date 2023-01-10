'''
1. 유투브 동영상에서 오디오만 추출
2. assembly ai를 이용해 STT
3. text에 감정 분석 적용하기(positive / negative / neutral)

참고) https://www.assemblyai.com/docs/audio-intelligence#sentiment-analysis
'''


import json
from youtube_extractor import get_video_info, get_audio_url
from api import save_transcript
        

def save_video_sentiments(url):
    video_info = get_video_info(url)
    audio_url = get_audio_url(video_info)
    if audio_url:
        title = video_info['title'].strip().replace(' ','_')
        save_dir = 'data/' + title
        save_transcript(audio_url, save_dir, sentiment_analysis=True)
        

url = 'https://www.youtube.com/watch?v=_T3rKNexnhY'  #(3:19)Mous Clarity 2.0 iPhone 14 Review
json_file = save_video_sentiments(url)
print(json_file)
print('\n\n')

if __name__ == '__main__':
    with open(json_file, 'r') as f:
        data = json.load(f)
        
        positive, negative, neutral = [], [], []
        
        for result in data:
            text = result['text']
            if result['sentiment'] == 'POSITIVE':
                positive.append(text)
            elif result['sentiment'] == 'NEGATIVE':
                negative.append(text)
            else:
                neutral.append(text)
        
        len_pos, len_neg, len_neu = len(positive), len(negative), len(neutral)
        total = len_pos + len_neg + len_neu
        print(f'Positive sentences : {len(positive)} ({round(len_pos/total, 2)}%)')
        print(f'Negative sentences : {len(negative)} ({round(len_neg/total, 2)}%)')
        print(f' Neutral sentences :  {len(neutral)} ({round(len_neu/total, 2)}%)')