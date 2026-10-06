import os
from pathlib import Path

BOT_DIR = Path(__file__).resolve().parents[3] / 'zalo' / 'bot'
ENV_FILE = BOT_DIR / '.env'


def configuration():
    values = {}
    if ENV_FILE.exists():
        for line in ENV_FILE.read_text(encoding='utf-8').splitlines():
            key, sep, value = line.partition('=')
            if sep and key.startswith('ZALO_BOT_'):
                values[key] = value.strip()
    for key in ('ZALO_BOT_TOKEN', 'ZALO_BOT_SECRET', 'ZALO_BOT_ALLOWED_CHATS', 'ZALO_BOT_ENABLED'):
        if key in os.environ:
            values[key] = os.environ[key]
    return {
        'token': values.get('ZALO_BOT_TOKEN', ''),
        'secret': values.get('ZALO_BOT_SECRET', ''),
        'allowed_chats': set(filter(None, (x.strip() for x in values.get('ZALO_BOT_ALLOWED_CHATS', '').split(',')))),
        'enabled': values.get('ZALO_BOT_ENABLED') == '1',
    }
