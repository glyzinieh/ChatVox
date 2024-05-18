import configparser

import questionary
import soundcard as sc


class Config:
    def __init__(self, config_file):
        self.config_file = config_file
        self.config = configparser.ConfigParser()

    def read_config(self):
        self.config.read(self.config_file)
        is_setup = str2bool(self.config["General"]["is_setup"])
        if not is_setup:
            self.config["General"] = {
                "is_setup": "True",
                "speaker": sc.default_speaker().name,
            }
            self.config["onecomme"] = {
                "path": "",
                "api_base_url": "http://localhost:11180",
            }
            self.config["genai"] = {"api_key": ""}
            self.config["stylebertvits"] = {
                "path": "",
                "api_base_url": "http://127.0.0.1:5000",
            }
            self.write_config()

        return is_setup

    def write_config(self):
        with open(self.config_file, "w") as f:
            self.config.write(f)

    def setup(self):
        speaker_name = questionary.select(
            "Speaker?",
            choices=get_speakers_list(),
            default=self.config["General"]["speaker"],
        ).ask()
        onecomme_path = questionary.text(
            "Path to OneComme app?",
            default=self.config["onecomme"]["path"],
        ).ask()
        onecomme_api_base_url = questionary.text(
            "OneComme API base URL?",
            default=self.config["onecomme"]["api_base_url"],
        ).ask()
        genai_api_key = questionary.text(
            "GenAI API key?",
            default=self.config["genai"]["api_key"],
        ).ask()
        stylebertvits_path = questionary.text(
            "Path to StyleBertVits directory?",
            default=self.config["stylebertvits"]["path"],
        ).ask()
        stylebertvits_api_base_url = questionary.text(
            "StyleBertVits API base URL?",
            default=self.config["stylebertvits"]["api_base_url"],
        ).ask()
        self.config["General"]["speaker"] = speaker_name
        self.config["onecomme"]["path"] = onecomme_path
        self.config["onecomme"]["api_base_url"] = onecomme_api_base_url
        self.config["genai"]["api_key"] = genai_api_key
        self.config["stylebertvits"]["path"] = stylebertvits_path
        self.config["stylebertvits"]["api_base_url"] = stylebertvits_api_base_url
        self.write_config()


def get_speakers_list():
    return [speaker.name for speaker in sc.all_speakers()]


def str2bool(v):
    return v.lower() in ("yes", "true", "t", "1")


if __name__ == "__main__":
    config = Config("config.ini")
    config.read_config()
    config.setup()
