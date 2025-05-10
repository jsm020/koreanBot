# Korean Vocabulary Telegram Bot

This bot helps users learn and review Korean vocabulary through personalized and global flashcard tests.

## Features

- Submit Korean words and get translations, example sentences, and audio pronunciations.
- Daily personalized flashcard reviews.
- Global flashcard reviews with random words from all users.
- Tracks user progress and performance.

## Setup

1. Clone the repository.
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Set up the PostgreSQL database using `database_setup.sql`.
4. Configure environment variables in `.env`.
5. Run the bot:
   ```bash
   python main.py
   ```

## Commands

- `/start`: Welcome message with brief instructions.
- `/help`: Detailed guidance on bot commands and features.
- `/test`: Initiate personalized flashcard review.
- `/globaltest`: Initiate flashcard review using random words from all users.

## Technology Stack

- Python (`aiogram`)
- PostgreSQL
- Google Translate API
- Google Text-to-Speech API
- APScheduler

## Future Enhancements

- Enhanced analytics dashboards.
- Premium features (advanced audio, personalized tests, live sessions).
- Gamification features and referral systems.