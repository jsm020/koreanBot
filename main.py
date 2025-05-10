import logging
from aiogram import Bot, Dispatcher, executor, types
from apscheduler.schedulers.asyncio import AsyncIOScheduler
import asyncpg
import requests
from google.cloud import texttospeech

# Initialize logging
logging.basicConfig(level=logging.INFO)

# Initialize bot and dispatcher
API_TOKEN = "YOUR_TELEGRAM_BOT_API_TOKEN"
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

# Database connection pool
db_pool = None

# Scheduler for daily tasks
scheduler = AsyncIOScheduler()

# Initialize Google Text-to-Speech API
tts_client = texttospeech.TextToSpeechClient()

@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
    await message.reply("Welcome to the Korean Vocabulary Bot! Use /help to see available commands.")

@dp.message_handler(commands=['help'])
async def send_help(message: types.Message):
    await message.reply("Available commands:\n/start - Welcome message\n/help - Show this help message\n/test - Start personalized flashcard review\n/globaltest - Start global flashcard review")

async def init_db():
    global db_pool
    db_pool = await asyncpg.create_pool(
        user='your_db_user',
        password='your_db_password',
        database='your_db_name',
        host='localhost'
    )

async def on_startup(dispatcher):
    await init_db()
    scheduler.start()

async def on_shutdown(dispatcher):
    await db_pool.close()
    scheduler.shutdown()

# Replace Google Translate API with LibreTranslate
LIBRETRANSLATE_URL = "http://localhost:5000/translate"

def translate_text(text, target_language="en"):
    """Translate text using LibreTranslate."""
    response = requests.post(
        LIBRETRANSLATE_URL,
        data={"q": text, "source": "ko", "target": target_language}
    )
    if response.status_code == 200:
        return response.json().get("translatedText", "Translation failed")
    else:
        return "Translation failed"

def generate_audio(text, language_code="ko-KR"):
    """Generate audio pronunciation for the given text."""
    synthesis_input = texttospeech.SynthesisInput(text=text)
    voice = texttospeech.VoiceSelectionParams(
        language_code=language_code, ssml_gender=texttospeech.SsmlVoiceGender.NEUTRAL
    )
    audio_config = texttospeech.AudioConfig(audio_encoding=texttospeech.AudioEncoding.MP3)
    response = tts_client.synthesize_speech(
        input=synthesis_input, voice=voice, audio_config=audio_config
    )
    return response.audio_content

@dp.message_handler()
async def handle_korean_word(message: types.Message):
    """Handle user-submitted Korean words."""
    korean_word = message.text

    # Validate if the text is Korean
    if not all('\uac00' <= char <= '\ud7a3' for char in korean_word):
        await message.reply("Please send a valid Korean word.")
        return

    # Fetch translation and example sentence
    translation = translate_text(korean_word, target_language="en")
    example_sentence = f"Example sentence for {korean_word}."  # Placeholder for now

    # Generate audio pronunciation
    audio_content = generate_audio(korean_word)
    audio_file_path = f"audio_{message.from_user.id}_{korean_word}.mp3"
    with open(audio_file_path, "wb") as audio_file:
        audio_file.write(audio_content)

    # Save to database
    async with db_pool.acquire() as connection:
        await connection.execute(
            """
            INSERT INTO Words (korean_word, audio_url, translation, example_sentence, user_id)
            VALUES ($1, $2, $3, $4, $5)
            """,
            korean_word, audio_file_path, translation, example_sentence, message.from_user.id
        )

    await message.reply(f"Word saved!\nTranslation: {translation}\nAudio: {audio_file_path}")

async def send_daily_flashcards():
    """Send daily flashcards to all users."""
    async with db_pool.acquire() as connection:
        users = await connection.fetch("SELECT DISTINCT user_id FROM Words")
        for user in users:
            user_id = user['user_id']
            words = await connection.fetch(
                """
                SELECT korean_word, translation FROM Words
                WHERE user_id = $1
                ORDER BY RANDOM() LIMIT 5
                """,
                user_id
            )
            if words:
                flashcard_message = "Your daily flashcards:\n"
                for word in words:
                    flashcard_message += f"\n{word['korean_word']} - {word['translation']}"
                await bot.send_message(user_id, flashcard_message)

# Schedule the daily flashcard task
scheduler.add_job(send_daily_flashcards, 'cron', hour=17, minute=0)

if __name__ == '__main__':
    from aiogram import executor
    executor.start_polling(dp, on_startup=on_startup, on_shutdown=on_shutdown)
