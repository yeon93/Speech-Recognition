'''
1. 유투브 동영상에서 오디오만 추출
2. assembly ai를 이용해 STT
3. text에 감정 분석 적용하기(positive / negative / neutral)

참고) https://www.assemblyai.com/docs/audio-intelligence#sentiment-analysis
'''


import json
#from youtube_extractor import get_video_info, get_audio_url
#from api import save_transcript
        

def save_video_sentiments(url):
    video_info = get_video_info(url)
    audio_url = get_audio_url(video_info)
    if audio_url:
        import re
        title = video_info['title']
        title = title.strip()                          # 앞뒤 빈칸 제거
        title = re.sub('[^a-zA-Z0-9_ ]', '', title)    # _ 를 제외한 모든 특수문자 제거
        title = re.sub('[ ]', '_', title)              # 띄어쓰기를 _로 대체
        save_dir = 'data/' + title
        save_transcript(audio_url, save_dir, sentiment_analysis=True)
        

url = 'https://www.youtube.com/watch?v=_T3rKNexnhY'  #(3:19)Mous Clarity 2.0 iPhone 14 Review

if __name__ == '__main__':
    with open('data/Mous_Clarity_20_iPhone_14_Review__Theres_Only_One_Thing_I_dont_Like_sentiments.json', 'r') as f:
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
        print(f'Positive sentences : {len(positive)} ({round(len_pos/total*100, 2)}%)')
        print(f'Negative sentences : {len(negative)} ({round(len_neg/total*100, 2)}%)')
        print(f' Neutral sentences : {len(neutral)} ({round(len_neu/total*100, 2)}%)')