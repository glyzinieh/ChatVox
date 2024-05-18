# ChatVox

AI Vtuberのためのサポートツールです。[GUI版はこちら](https://github.com/glyzinieh/ChatVoxGUI)からダウンロードできます。

わんコメ5からコメントを取得し、Google AI Studioで返答内容を生成し、Style Bert VITS2で返答内容を読み上げます。VB-Audio Virtual Cable・VTube Studio・OBSなどを利用して、YouTube等の配信に利用することを想定しています。

## How to use

### Install

#### 依存ソフトウェア

ChatVoxを利用するためには、これ以外に以下のソフトウェアを別途インストールする必要があります。

- Python
- わんコメ5
- Style Bert VITS2

#### ChatVoxのインストール


```
pip install chat_vox@git+https://github.com/glyzinieh/ChatVox
```

### Configure

カレントディレクトリに以下の内容の`config.ini`を作成してください。作成されていない場合は、初回起動時に生成されます。

```ini
[General]
is_setup = True
speaker = CABLE Input (VB-Audio Virtual Cable)

[onecomme]
path = OneComme.exeのパス
api_base_url = http://localhost:11180

[genai]
api_key = Google AI StudioのAPIキー

[stylebertvits]
path = sbv2ディレクトリのパス
api_base_url = http://127.0.0.1:5000
```

### Example

```Python
from config import Config
from chat_vox import ChatVox

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
```

## Contact

[wisteriatp@gmail.com](mailto:wisteiratp@gmail.com)
