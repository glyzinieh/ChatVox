import configparser

import questionary
import soundcard as sc

# config.iniファイルの読み込み
config = configparser.ConfigParser()
config.read("config.ini")

def write_config():
    with open("config.ini", "w") as configfile:
        config.write(configfile)


def get_speakers_list():
    return [speaker.name for speaker in sc.all_speakers()]


def choose_speaker() -> None:
    default_speaker = sc.default_speaker()

    choices = get_speakers_list()

    speaker_name = questionary.select(
        "Speaker?",
        choices=choices,
        default=default_speaker.name,
    ).ask()

    config["General"]["speaker"] = speaker_name
    write_config()


if __name__ == "__main__":
    choose_speaker()
