from typing import Optional
from datetime import datetime, timezone
from sqlmodel import Field, SQLModel, Relationship


class LanguageLevel(SQLModel, table=True):
    """
    Language level entity representing a user's proficiency in a specific language.
    ACTFL levels are used: 
    Novice          
        Low	    Communicates minimally with isolated words and memorized phrases. Often relies on gestures and repetition.
        Mid	    Can produce simple phrases and respond to direct questions on familiar topics. Still limited to memorized language.
        High	Can handle short social interactions using learned phrases. May attempt to create language but with frequent errors.
    Intermediate
        Low	    Can express basic needs and preferences. Speech is halting and relies on memorized chunks.
        Mid	    Can ask and answer questions, handle simple transactions, and describe in present tense. Speech is more fluid but limited to familiar contexts.
        High	Can participate in conversations on everyday topics. Begins to narrate and describe in past and future tenses with some control.
    Advanced
        Low	    Can narrate and describe across major time frames. Handles routine social and work situations with confidence.
        Mid	    Can elaborate on topics, support opinions, and manage complications in conversations. Shows good control of grammar and vocabulary.
        High	Can handle complex tasks and unexpected situations. Language is accurate and nuanced, though not always native-like.
    Superior
            	Can discuss abstract topics, hypothesize, and tailor language to different audiences. Demonstrates fluency, accuracy, and cultural appropriateness.
    Distinguished
            	Can reflect on complex ideas, persuade, and negotiate in highly sophisticated ways. Language is precise, nuanced, and appropriate for any context.
    """
    __tablename__ = "language_level"
    id: int | None = Field(default=None, primary_key=True)
    name: str
    description: str

 