from langchain.schema import BaseMessage
from .ai_client import AiClient

from utils import get_app_logger

logger = get_app_logger(__name__)

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

AUDI_EXAMPLE_1 = """
{"question":
 [{"lang":"en","text":"What is the meaning of"},{"lang":"es","text":"aqua"},{"lang":"en","text":"?"}],
"answer":
 [{"lang":"en","text":"The meaning of"},{"lang":"es","text":"agua"},{"lang":"en","text":"is water."}]
}
"""

QNA_EXAMPLE_1 = """
<es-MX>“Al”</es-MX> is a contraction in Spanish that combines the preposition <es-MX>“a”</es-MX> (meaning “to” or “at”) and the definite article <es-MX>“el”</es-MX> (meaning “the” for masculine singular nouns). It is used before masculine singular nouns to mean “to the” or “at the.”

Here’s how you use <es-MX>“al”</es-MX>:

1. When <es-MX>“a”</es-MX> (to/at) + <es-MX>“el”</es-MX> (the) appear together before a masculine singular noun, contract them into <es-MX>“al”</es-MX>.
   
   For example:
   - <es-MX>Voy a el parque.</es-MX> → <es-MX>Voy al parque.</es-MX> (I am going to the park.)
   - <es-MX>Llegué a el aeropuerto.</es-MX> → <es-MX>Llegué al aeropuerto.</es-MX> (I arrived at the airport.)

2. Note that you do NOT contract <es-MX>“a”</es-MX> + <es-MX>“la”</es-MX>, <es-MX>“a”</es-MX> + <es-MX>“las”</es-MX>, or <es-MX>“a”</es-MX> + <es-MX>“los”</es-MX>. For example:
   - <es-MX>Voy a la escuela.</es-MX> (I am going to the school.)
   - <es-MX>Voy a las tiendas.</es-MX> (I am going to the stores.)
   - <es-MX>Voy a los mercados.</es-MX> (I am going to the markets.)

In summary, use <es-MX>“al”</es-MX> any time you have <es-MX>“a”</es-MX> + <es-MX>“el”</es-MX> before a masculine singular noun.
"""

QNA_EXAMPLE_2 = """
What is <es-MX>negitio</es-MX>?\t<es-MX>Negotio</es-MX> means business.
"""

SPEAKING_EXAMPLE = """
¡Claro! Here are 10 speaking exercises on the topic of Describing the Weather, perfect for practicing short social interactions. Each exercise has two paragraphs: one in Spanish with IPA pronunciation and one in English for translation.

1.
El\tɛl\tclima\tˈklima\tes\tes\tagradable\taɣɾaˈðaβle\thoy\toj.
The weather is pleasant today.

2.
Hace\tˈaθe\tfrío\tˈfɾio\ten\ten\tla\tla\tciudad\tθjuˈðað\testa\tˈesta\tmañana\tmaˈɲana. 
It's cold  in the city this morning.

3.
¿Te\tte\tgusta\tˈɡusta\tel\tel\tclima\tˈklima\tcaliente\tkaˈljente\ten\ten\tverano\tβeˈɾano?
Do you like hot weather in  summer?

4.
Hoy\toj\thay\taj\tuna\tˈuna\ttormenta\ttoɾˈmenta\tcon\tkɔn\tmucha\tˈmutʃa\tlluvia\tˈʝuβja.
Today there's a storm with a lot of rain.

5.
El\tɛl\tsol\tsoʊl\tbrilla\tˈbɾiʝa\ten\ten\tel\tɛl\tcielo\tˈsjelo\tazul\taˈθul.
The sun shines in the blue sky.

6.
¿Prefieres\tpɾeˈfjɛɾes\tel\tel\tclima\tˈklima\tfrío\tˈfɾio\to\to\tcalor\tkaˈloɾ?
Do\tdu\tyou\tju\tprefer\tprɪˈfɝ\tcold\tkoʊld\tor\tɔr\thot\thɑt\tweather\tˈwɛðər?
Do you prefer cold orr hot weather?


7.
En\ten\tel\tɛl\tinvierno\timˈβjeɾno\thace\tˈaθe\tmucho\tˈmutʃo\tfrío\tˈfɾio.    
In the winter it's very cold.

8.
La\tla\ttemperatura\ttempeɾaˈtuɾa\tes\tes\tsuave\tˈswaβe\ten\ten\tla\tla\ttarde\tˈtaɾðe.
The temperaturee is mild in the afternoon.

9.
¿Cómo\tˈkomo\testá\tesˈta\tel\tel\tclima\tˈklima\tahora\taˈoɾa? 
How is the weather now?

10.
Por\tpoɾ\tla\tla\tnoche\tˈnotʃe\thace\tˈaθe\tfrío\tˈfɾio\ty\ti\tpuede\tˈpweðe\tnevar\tneˈβaɾ.   
At night it's cold and it can can snow.

¡Practiquemos! Repeat each sentence aloud and try making your own weather descriptions!
133 substitutions on 11 lines                                                                                                                    

"""

class StubClient(AiClient):
    def ask_ai(self, messages: list[BaseMessage]) -> str:
        content = messages[0].content
        if content.find("Spanish") > 0:
            if content.find("from the same audio input") > 0:
                return AUDI_EXAMPLE_1
            return EXAMPLE_1
        elif content.find("Japanese") > 0:
            return EXAMPLE_2
        
        return "Buy Bobby a puppy. <zh>练习中文发音</zh> My mom may know."
        # return "Buy Bobby a puppy."
        
    def ask_ai_stream(self, messages: list[BaseMessage]):
        content = messages[0].content
        lines = ""
        if content.find("speaking exercises") > 0:
            lines = SPEAKING_EXAMPLE.split("\n")
        elif content.find("tab character") > 0:
            lines = QNA_EXAMPLE_2.split("\n")
        else:
            lines = QNA_EXAMPLE_1.split("\n")

        for line in lines:
            if line.strip():
                yield line.strip()
                yield "\n"
        yield "\n"
