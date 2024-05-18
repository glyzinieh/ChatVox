import os
import threading
import time
import urllib.parse
from queue import Queue

import google.generativeai as genai
import requests
import soundcard as sc
import soundfile as sf


class Comment:
    def __init__(self, user_name: str, message: str) -> None:
        self.user_name = user_name
        self.message = message

        self.reply = None
        self.voice_file = None


class GetComments:
    def __init__(self, base_url: str) -> None:
        self.base_url = base_url
        self.api_url = urllib.parse.urljoin(base_url, "/api/comments")
        self.read_comments_length = 0
        self.last_time = 0

    def get_comments(self) -> list[Comment]:
        res = requests.get(self.api_url)
        comments_data = res.json()

        comments = [
            Comment(comment["data"]["name"], comment["data"]["comment"])
            for comment in comments_data
        ]
        return comments

    def get_unread_comments(self) -> list[Comment]:
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
    def __init__(self, api_key: str, system_prompt: str = temp_prompt) -> None:
        genai.configure(api_key=api_key)

        # モデルの設定
        generation_config = {
            "temperature": 0.9,  # 生成するテキストのランダム性を制御
            "top_p": 1,  # 生成に使用するトークンの累積確率を制御
            "top_k": 1,  # 生成に使用するトップkトークンを制御
            "max_output_tokens": 512,  # 最大出力トークン数を指定`
        }

        self.model = genai.GenerativeModel(
            "gemini-pro", generation_config=generation_config
        )

        self.messages = [
            {"role": "user", "parts": [system_prompt]},
            {"role": "model", "parts": ["理解しました"]},
        ]

    def generate_reply(self, message: str) -> str:
        self.messages.append({"role": "user", "parts": [message]})
        try:
            response = self.model.generate_content(self.messages)
            reply = response.text
        except Exception as e:
            print(e)
            reply = "エラーが発生したよ。"
        self.messages.append({"role": "model", "parts": [reply]})
        return reply


temp_params = {}


class StyleBertVITS:
    def __init__(
        self, base_url: str, output_folder: str, params: dict = temp_params
    ) -> None:
        self.base_url = base_url
        self.api_url = urllib.parse.urljoin(base_url, "/voice")

        self.output_folder = output_folder
        os.makedirs(self.output_folder, exist_ok=True)

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

    def generate_voice(self, text: str) -> bytes:
        params = self.params
        params["text"] = text
        res = requests.post(self.api_url, params=params)
        voice = res.content
        return voice

    def save_voice(self, text: str) -> str:
        voice = self.generate_voice(text)

        file_name = f"{int(time.time())}.wav"
        file_path = os.path.join(self.output_folder, file_name)
        with open(file_path, "wb") as f:
            f.write(voice)

        return file_path


class PlayAudio:
    def __init__(self, speaker_name: str) -> None:
        self.speaker = sc.get_speaker(speaker_name)

    def play(self, file_path: str) -> None:
        try:
            data, fs = sf.read(file_path)
            self.speaker.play(data, samplerate=fs)
        except Exception as e:
            print(e)


class ChatVox:
    def __init__(self, onecomme_api_base_url, genai_api_key, stylebertvits_api_base_url, speaker_name) -> None:
        self._get_comments = GetComments(onecomme_api_base_url)
        self._gemini_pro = GeminiPro(genai_api_key)
        self._style_bert_vits = StyleBertVITS(stylebertvits_api_base_url, "output")
        self._play_audio = PlayAudio(speaker_name)

        self.exit_flag = False

        self.thread_get_comments = threading.Thread(
            target=self.get_comments, daemon=True
        )
        self.comments_queue = Queue(6)
        self.thread_generate_reply = threading.Thread(
            target=self.generate_reply, daemon=True
        )
        self.reply_queue = Queue(3)
        self.thread_play_audio = threading.Thread(target=self.play_audio, daemon=True)

    def Run(self) -> None:
        self.thread_get_comments.start()
        self.thread_generate_reply.start()
        self.thread_play_audio.start()
        while not self.exit_flag:
            time.sleep(1)

    def get_comments(self) -> None:
        while not self.exit_flag:
            comments = self._get_comments.get_unread_comments()
            for comment in comments:
                self.comments_queue.put(comment)
            time.sleep(15)

    def generate_reply(self) -> None:
        while not self.exit_flag:
            if not self.comments_queue.empty():
                comment = self.comments_queue.get()
                reply = self._gemini_pro.generate_reply(comment.message)

                voice_file = self._style_bert_vits.save_voice(reply)
                comment.reply = reply
                comment.voice_file = voice_file
                self.reply_queue.put(comment)

                self.comments_queue.task_done()

    def play_audio(self) -> None:
        while not self.exit_flag:
            if not self.reply_queue.empty():
                comment = self.reply_queue.get()
                reply = comment.reply
                voice_file = comment.voice_file

                print(f"{comment.user_name}: {comment.message}")
                print(f"Bot: {reply}")
                self._play_audio.play(voice_file)

                os.remove(voice_file)
                time.sleep(3)

                self.reply_queue.task_done()


if __name__ == "__main__":
    from config import Config

    config = Config("config.ini")
    config.read_config()

    # ChatVoxクラスのインスタンス化
    chat_vox = ChatVox(
        config.config["onecomme"]["api_base_url"],
        config.config["genai"]["api_key"],
        config.config["stylebertvits"]["api_base_url"],
        config.config["General"]["speaker"],
    )
    chat_vox.Run()
