from langchain.schema import BaseMessage
from .ai_client import AiClient

EXAMPLE_1 = """[
  {
    "words": [
      {"w": "Hola", "p": "ˈola"},
      {"w": "me", "p": "me"},
      {"w": "llamo", "p": "ˈʝamo"}
    ],
    "translation": "Hello, my name is..."
  },
  {
    "words": [
      {"w": "¿Cómo", "p": "ˈkomo"},
      {"w": "te", "p": "te"},
      {"w": "llamas?", "p": "ˈʝamas"}
    ],
    "translation": "What is your name?"
  },
  {
    "words": [
      {"w": "Soy", "p": "soj"},
      {"w": "de", "p": "de"},
      {"w": "Estados", "p": "esˈtados"},
      {"w": "Unidos", "p": "uˈnidos"}
    ],
    "translation": "I am from the United States."
  },
  {
    "words": [
      {"w": "Tengo", "p": "ˈteŋɡo"},
      {"w": "veinticinco", "p": "beintiˈθiŋko"},
      {"w": "años", "p": "ˈaɲos"}
    ],
    "translation": "I am twenty-five years old."
  },
  {
    "words": [
      {"w": "¿De", "p": "de"},
      {"w": "dónde", "p": "ˈdonde"},
      {"w": "eres?", "p": "ˈeres"}
    ],
    "translation": "Where are you from?"
  },
  {
    "words": [
      {"w": "Mucho", "p": "ˈmutʃo"},
      {"w": "gusto", "p": "ˈɡusto"}
    ],
    "translation": "Nice to meet you."
  },
  {
    "words": [
      {"w": "¿Hablas", "p": "ˈaβlas"},
      {"w": "español?", "p": "espaˈɲol"}
    ],
    "translation": "Do you speak Spanish?"
  },
  {
    "words": [
      {"w": "Sí,", "p": "si"},
      {"w": "un", "p": "un"},
      {"w": "poco", "p": "ˈpoko"}
    ],
    "translation": "Yes, a little."
  },
  {
    "words": [
      {"w": "¿Cuál", "p": "kwal"},
      {"w": "es", "p": "es"},
      {"w": "tu", "p": "tu"},
      {"w": "número", "p": "ˈnumeɾo"},
      {"w": "de", "p": "de"},
      {"w": "teléfono?", "p": "teˈlefono"}
    ],
    "translation": "What is your phone number?"
  },
  {
    "words": [
      {"w": "Mi", "p": "mi"},
      {"w": "número", "p": "ˈnumeɾo"},
      {"w": "es", "p": "es"},
      {"w": "tres", "p": "tɾes"},
      {"w": "cero", "p": "ˈseɾo"},
      {"w": "cinco", "p": "ˈθiŋko"},
      {"w": "cuatro", "p": "ˈkwatɾo"}
    ],
    "translation": "My number is 305-4..."
  }
]"""

EXAMPLE_2 = """[
  {
    "words": [
      {"w": "はじめまして","p": "Hajimemashite"},
      {"w": "、","p": ","},
      {"w": "私","p": "watashi"},
      {"w": "の","p": "no"},
      {"w": "名前","p": "namae"},
      {"w": "は","p": "wa"},
      {"w": "たかし","p": "Takashi"},
      {"w": "です","p": "desu"},
      {"w": "。","p": "."}
    ],
    "translation": "Nice to meet you, my name is Takashi."
  },
  {
    "words": [
      {"w": "出身","p": "shusshin"},
      {"w": "は","p": "wa"},
      {"w": "ニューヨーク","p": "Nyūyōku"},
      {"w": "です","p": "desu"},
      {"w": "。","p": "."}
    ],
    "translation": "I am from New York."
  },
  {
    "words": [
      {"w": "趣味","p": "shumi"},
      {"w": "は","p": "wa"},
      {"w": "料理","p": "ryōri"},
      {"w": "を","p": "o"},
      {"w": "すること","p": "suru koto"},
      {"w": "です","p": "desu"},
      {"w": "。","p": "."}
    ],
    "translation": "My hobby is cooking."
  },
  {
    "words": [
      {"w": "仕事","p": "shigoto"},
      {"w": "は","p": "wa"},
      {"w": "教師","p": "kyōshi"},
      {"w": "です","p": "desu"},
      {"w": "。","p": "."}
    ],
    "translation": "My job is a teacher."
  },
  {
    "words": [
      {"w": "家族","p": "kazoku"},
      {"w": "は","p": "wa"},
      {"w": "四人","p": "yonin"},
      {"w": "です","p": "desu"},
      {"w": "。","p": "."}
    ],
    "translation": "I have four family members."
  },
  {
    "words": [
      {"w": "日本語","p": "Nihongo"},
      {"w": "を","p": "o"},
      {"w": "勉強","p": "benkyō"},
      {"w": "しています","p": "shiteimasu"},
      {"w": "。","p": "."}
    ],
    "translation": "I am studying Japanese."
  },
  {
    "words": [
      {"w": "週末","p": "shūmatsu"},
      {"w": "は","p": "wa"},
      {"w": "映画","p": "eiga"},
      {"w": "を","p": "o"},
      {"w": "見ること","p": "miru koto"},
      {"w": "が","p": "ga"},
      {"w": "好き","p": "suki"},
      {"w": "です","p": "desu"},
      {"w": "。","p": "."}
    ],
    "translation": "I like watching movies on weekends."
  },
  {
    "words": [
      {"w": "よろしくお願いします","p": "Yoroshiku onegaishimasu"},
      {"w": "。","p": "."}
    ],
    "translation": "Please treat me well."
  },
  {
    "words": [
      {"w": "大学","p": "daigaku"},
      {"w": "で","p": "de"},
      {"w": "経済学","p": "keizaigaku"},
      {"w": "を","p": "o"},
      {"w": "専攻","p": "senkō"},
      {"w": "しています","p": "shiteimasu"},
      {"w": "。","p": "."}
    ],
    "translation": "I am majoring in economics at university."
  },
  {
    "words": [
      {"w": "趣味","p": "shumi"},
      {"w": "は","p": "wa"},
      {"w": "旅行","p": "ryokō"},
      {"w": "です","p": "desu"},
      {"w": "。","p": "."}
    ],
    "translation": "My hobby is traveling."
  }
]"""
class StubClient(AiClient):
    def ask_ai(self, messages: list[BaseMessage]) -> str:
        content = messages[0].content
        if content.find("Spanish") > 0:
            return EXAMPLE_1
        elif content.find("Japanese") > 0:
            return EXAMPLE_2
        
        return "Buy Bobby a puppy. <zh>练习中文发音</zh> My mom may know."
        # return "Buy Bobby a puppy."