import configparser

import questionary
import soundcard as sc

# config.iniファイルの読み込み
config = configparser.ConfigParser()
config.read("config.ini")

# ユーザーにスピーカーIDを選択させる
speaker_list = sc.all_speakers()
default_speaker = sc.default_speaker()

speaker_name = questionary.select(
    "Speaker?",
    choices=[speaker.name for speaker in speaker_list],
    default=default_speaker.name,
).ask()

config["General"]["speaker"] = speaker_name

with open("config.ini", "w") as configfile:
    config.write(configfile)
