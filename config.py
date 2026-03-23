DB_PATH = "outreach.db"
DASHBOARD_HOST = "127.0.0.1"
DASHBOARD_PORT = 5000

# Rate limits for scraping (seconds)
TGSTAT_DELAY_MIN = 3
TGSTAT_DELAY_MAX = 6
TELEGRAM_WEB_DELAY_MIN = 2
TELEGRAM_WEB_DELAY_MAX = 4
TELEMETR_DELAY_MIN = 3
TELEMETR_DELAY_MAX = 6

# Instagram
INSTAGRAM_DELAY_MIN = 5
INSTAGRAM_DELAY_MAX = 10

# YouTube
YOUTUBE_DELAY_MIN = 2
YOUTUBE_DELAY_MAX = 5

# X/Twitter
X_DELAY_MIN = 3
X_DELAY_MAX = 6

# Thresholds
MIN_SUBSCRIBERS = 500
MAX_MESSAGES_PER_DAY = 15

# User agent rotation
USER_AGENTS = [
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.3 Safari/605.1.15",
]
