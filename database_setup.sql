CREATE TABLE Words (
    id SERIAL PRIMARY KEY,
    korean_word TEXT NOT NULL,
    audio_url TEXT,
    translation TEXT NOT NULL,
    example_sentence TEXT,
    submitted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    user_id BIGINT NOT NULL
);

CREATE TABLE UserProgress (
    id SERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL,
    word_id INTEGER REFERENCES Words(id),
    attempts INTEGER DEFAULT 0,
    correct BOOLEAN,
    last_tested TIMESTAMP
);
