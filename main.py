import os
import time
import urllib.parse
import wave

import pyaudio
import requests


class Comments:
    def __init__(self, base_url):
        self.base_url = base_url
        self.api_url = urllib.parse.urljoin(base_url, "/api/comments")
        self.read_comments_length = 0
        self.last_time = 0

    def get_comments(self):
        current_time = time.time()
        elapsed_time = current_time - self.last_time
        if elapsed_time < 30:
            time.sleep(30 - elapsed_time)
        self.last_time = current_time

        res = requests.get(self.api_url)
        comments = res.json()
        return comments

    def get_unread_comments(self):
        comments = self.get_comments()
        unread_comments = comments[self.read_comments_length :]
        self.read_comments_length = len(comments)
        return unread_comments


temp_prompt = """以下の内容に従ってください。この内容は、会話履歴が残っている限り有効です。理解したら”理解しました”と応答してください。
あなたは14歳の女の子のVTuberです。以下の条件を守って回答してください。
- あなたはVTuberのキャラクターとして、ファンとチャットを行います
- Chatbotの名前は「桃瀬ひより」
- 常にハイテンションな会話文で、敬語など丁寧な言葉使いはしません
- 回答は常に短く、３文未満で答えます。
- 以前の回答と全く同じ内容は返さない
"""


class GeminiPro:
    def __init__(self, api_key, system_prompt=temp_prompt):
        genai.configure(api_key=api_key)

        self.model = genai.GenerativeModel("gemini-pro")

        self.messages = [
            {"role": "user", "parts": [system_prompt]},
            {"role": "model", "parts": ["理解しました"]},
        ]

    def generate_reply(self, comment):
        self.messages.append({"role": "user", "parts": [comment]})
        response = self.model.generate_content(self.messages)
        reply = response.text
        self.messages.append({"role": "model", "parts": [reply]})
        return reply


temp_params = {}


class StyleBertVITS:
    def __init__(self, base_url, output_folder, params=temp_params):
        self.base_url = base_url
        self.api_url = urllib.parse.urljoin(base_url, "/voice")

        self.output_folder = output_folder

        self.params = {
            "model_id": 0,
            "speaker_id": 0,
            "sdp_ratio": 0.2,
            "noise": 0.6,
            "noisew": 0.8,
            "length": 1,
            "language": "JP",
            "auto_split": True,
            "split_interval": 0.5,
            "assist_text": "",
            "assist_text_weight": 1,
            "style": "Neutral",
            "style_weight": 5,
        }
        self.params.update(params)

    def generate_voice(self, text):
        params = self.params
        params["text"] = text
        res = requests.post(self.api_url, params=params)
        voice = res.content
        return voice

    def save_voice(self, text):
        voice = self.generate_voice(text)

        # file_name = f"{int(time.time())}.wav"
        file_name = "output.wav"
        file_path = os.path.join(self.output_folder, file_name)
        with open(file_path, "wb") as f:
            f.write(voice)

        return file_path


class PlayAudio:
    def __init__(self, speaker_id):
        self.speaker_id = speaker_id
        self.CHUNK = 1024
        self.p = pyaudio.PyAudio()

    def speak(self, voice_file):
        wf = wave.open(voice_file, "rb")

        stream = self.p.open(
            format=self.p.get_format_from_width(wf.getsampwidth()),
            channels=wf.getnchannels(),
            rate=wf.getframerate(),
            output=True,
            output_device_index=self.speaker_id,
        )

        data = wf.readframes(self.CHUNK)

        while data:
            stream.write(data)
            data = wf.readframes(self.CHUNK)

        stream.stop_stream()
        stream.close()

        self.p.terminate()


# メイン関数
# async def main():
def main():
    # unread_comments = await get_unread_comments()
    unread_comments = comments.get_unread_comments()

    for comment in unread_comments:
        user_name = comment["data"]["name"]
        message = comment["data"]["comment"]
        print(f"{user_name}: {message}")

        bot_name = "Bot"
        reply = gemini_pro.generate_reply(message)
        print(f"{bot_name}: {reply}")

        voice_file = style_bert_vits.save_voice(reply)
        play_audio.speak(voice_file)

        # await asyncio.sleep(10)
        time.sleep(5)


if __name__ == "__main__":
    import configparser

    import google.generativeai as genai
    import questionary
    from questionary import Choice

    # config.iniファイルの読み込み
    config = configparser.ConfigParser()
    config.read("config.ini")

    # ユーザーにスピーカーIDを選択させる
    audio = pyaudio.PyAudio()
    speaker_list = [
        Choice(
            title=audio.get_device_info_by_index(i)["name"],
            value=audio.get_device_info_by_index(i)["index"],
        )
        for i in range(audio.get_device_count())
        if audio.get_device_info_by_index(i)["maxOutputChannels"] > 0
    ]

    speaker_id = questionary.select("Choose speaker", choices=speaker_list).ask()

    config["General"]["speaker_id"] = str(speaker_id)
    with open("config.ini", "w") as f:
        config.write(f)

    # Commentsクラスのインスタンス化
    comments = Comments(config["onecomme"]["api_base_url"])

    # GeminiProクラスのインスタンス化
    gemini_pro = GeminiPro(config["genai"]["api_key"])

    # StyleBertVITSクラスのインスタンス化
    style_bert_vits = StyleBertVITS(config["stylebertvits"]["api_base_url"], "output")

    # PlayAudioクラスのインスタンス化
    play_audio = PlayAudio(speaker_id)

    while True:
        main()

    # loop = asyncio.new_event_loop()
    # asyncio.set_event_loop(loop)
    # loop.call_soon(main())
    # loop.run_forever()
