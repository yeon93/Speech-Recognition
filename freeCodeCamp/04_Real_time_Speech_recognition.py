'''
1. 파이썬에서 실시간 음성 인식
2. OPEN AI 의 api를 이용해 가상 비서(챗봇) 구축
3. WebSockets와 asyncio 사용

참고) https://www.assemblyai.com/docs/walkthroughs#realtime-streaming-transcription
'''

import pyaudio
import websockets
import asyncio
import base64    #보내기 전 데이터를 base64 문자열로 인코딩해야 함
import json
from openai_api_key import API_KEY_OPENAI
from assemblyai_api_key import API_KEY_ASSEMBLYAI
import openai

openai.api_key = API_KEY_OPENAI

def ask_computer(prompt):
    #return "This is my answer"
    #prompt = "What is your favorite color?"
    res = openai.Completion.create(
        engine="text-davinci-002",
        prompt=prompt,
    )
    # print(res)
    return res["choices"][0]["text"]

#Basic의 음성 녹음 코드
FRAMES_PER_BUFFER = 3200
FORMAT = pyaudio.paInt16    
CHANNELS = 1
RATE = 8000

p = pyaudio.PyAudio()
stream = p.open(rate=RATE,
                channels=CHANNELS,
                format=FORMAT,
                input=True,
                frames_per_buffer=FRAMES_PER_BUFFER)


#websocket을 위한 url
URL = 'wss://api.assemblyai.com/v2/realtime/ws?sample_rate=16000'


#데이터를 보내고 받는 함수
async def send_receive():
    print(f'Connecting websocket to url ${URL}')
    async with websockets.connect(
        URL,
        extra_headers=(("Authorization", API_KEY_ASSEMBLYAI),),
        ping_interval=5,
        ping_timeout=20
    ) as _ws:
        await asyncio.sleep(0.1)
        print("Receiving SessionBegins ...")
        session_begins = await _ws.recv()
        print(session_begins)
        print("Sending messages ...")
        async def send():
            while True:
                try:
                    data = stream.read(FRAMES_PER_BUFFER, exception_on_overflow=False)
                    data = base64.b64encode(data).decode("utf-8")
                    json_data = json.dumps({"audio_data":str(data)})
                    await _ws.send(json_data)
                except websockets.exceptions.ConnectionClosedError as e:
                    print(e)
                    assert e.code == 4008
                    break
                except Exception as e:
                    assert False, "Not a websocket 4008 error"
                await asyncio.sleep(0.01)
          
            return True
      
        async def receive():
            while True:
                try:
                    result_str = await _ws.recv()
                    result = json.loads(result_str)
                    prompt = result['text']
                    if prompt and result['message_type'] == 'FinalTranscript':
                        print("Me:", prompt)
                        answer = ask_computer(prompt)
                        print("Bot", answer)
                except websockets.exceptions.ConnectionClosedError as e:
                    print(e)
                    assert e.code == 4008
                    break
                except Exception as e:
                    assert False, "Not a websocket 4008 error"
      
        send_result, receive_result = await asyncio.gather(send(), receive())


asyncio.run(send_receive())