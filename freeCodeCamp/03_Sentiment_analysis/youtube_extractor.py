import youtube_dl
from youtube_dl.utils import DownloadError


ydl = youtube_dl.YoutubeDL()

def get_video_info(url):
    with ydl:
        try:
            video_info = ydl.extract_info(url, download=False)    #동영상을 다운로드할 필요없이, url을 바로 assembly ai에 전달 가능
        except DownloadError:
            return None

    if 'entries' in video_info:    #playlist 또는 list of videos
        video = video_info['entries'][0]
    else:    #하나의 video
        video = video_info
        
    return video


def get_audio_url(video):
    for f in video['formats']:
        if f['ext'] == 'm4a':    #확장자 m4a : 비디오 파일도 처리할 수있는 MP4와 달리 오디오만 지원하는 파일 형식 중 하나
            return f['url']
