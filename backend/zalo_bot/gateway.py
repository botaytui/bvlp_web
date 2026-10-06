"""Durable queue of prepared guidance, not incoming patient messages."""
import hashlib
import json
import sqlite3
import time
from contextlib import contextmanager
from pathlib import Path

from .config import BOT_DIR


def message_text(answer):
    suffix = '\n\n' + '\n'.join(f"{a['label']}: {a['url']}" for a in answer['actions']) if answer['actions'] else ''
    text = answer['reply']
    # Stay below the API's 2000-unit limit, including astral characters.
    while len((text + suffix).encode('utf-16-le')) // 2 > 1980:
        text = text[:-20]
    return text + suffix


class Queue:
    def __init__(self, path=None):
        self.path = Path(path or BOT_DIR / 'data' / 'queue.sqlite3')
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.connection() as db:
            db.executescript('''
                CREATE TABLE IF NOT EXISTS receipts (key TEXT PRIMARY KEY, created REAL NOT NULL);
                CREATE TABLE IF NOT EXISTS outbox (
                    key TEXT PRIMARY KEY, chat TEXT, text TEXT, status TEXT NOT NULL,
                    created REAL NOT NULL, attempted REAL);
            ''')

    @contextmanager
    def connection(self):
        db = sqlite3.connect(self.path, timeout=5)
        try:
            with db:
                yield db
        finally:
            db.close()

    def contains(self, key):
        with self.connection() as db:
            return bool(db.execute('SELECT 1 FROM receipts WHERE key=?', (key,)).fetchone())

    def enqueue(self, key, chat, text):
        now = time.time()
        with self.connection() as db:
            db.execute('BEGIN IMMEDIATE')
            # Drop reply destinations/text after 24h; retain hashed receipts for 7 days.
            db.execute('DELETE FROM outbox WHERE created < ?', (now-86400,))
            db.execute('DELETE FROM receipts WHERE created < ?', (now-7*86400,))
            if db.execute('SELECT 1 FROM receipts WHERE key=?', (key,)).fetchone():
                return 'duplicate'
            if db.execute("SELECT COUNT(*) FROM outbox WHERE status='pending'").fetchone()[0] >= 1000:
                return 'full'
            db.execute('INSERT INTO receipts VALUES (?,?)', (key,now))
            db.execute('INSERT INTO outbox VALUES (?,?,?,?,?,NULL)', (key,chat,text,'pending',now))
        return 'queued'

    def deliver_one(self, client, allowed_chats=None):
        with self.connection() as db:
            db.execute('BEGIN IMMEDIATE')
            db.execute('DELETE FROM outbox WHERE created < ?', (time.time()-86400,))
            # An interrupted network call is ambiguous; never automatically resend it.
            db.execute("UPDATE outbox SET status='unknown', chat=NULL, text=NULL WHERE status='sending' AND attempted < ?", (time.time()-60,))
            row = db.execute("SELECT key,chat,text FROM outbox WHERE status='pending' ORDER BY created LIMIT 1").fetchone()
            if not row:
                return False
            key,chat,text=row
            if allowed_chats is not None and chat not in allowed_chats:
                db.execute("UPDATE outbox SET status='cancelled',chat=NULL,text=NULL WHERE key=?", (key,))
                return True
            db.execute("UPDATE outbox SET status='sending',attempted=? WHERE key=?", (time.time(),key))
        status = 'sent'
        try:
            client.send(chat,text)
        except Exception:
            status = 'unknown'
        with self.connection() as db:
            db.execute('UPDATE outbox SET status=?,chat=NULL,text=NULL WHERE key=?', (status,key))
        return True

    def counts(self):
        with self.connection() as db:
            return dict(db.execute('SELECT status,COUNT(*) FROM outbox GROUP BY status').fetchall())


def process_event(payload, config, engine, queue):
    if not config['enabled'] or not config['token'] or not config['allowed_chats']:
        return 'disabled'
    envelope = payload.get('result')
    if not isinstance(envelope, dict):
        return 'ignored'
    if envelope.get('event_name') != 'message.text.received':
        return 'ignored'
    message = envelope.get('message')
    if not isinstance(message, dict):
        return 'ignored'
    chat, sender = message.get('chat'), message.get('from')
    if not isinstance(chat, dict) or not isinstance(sender, dict):
        return 'ignored'
    chat_id = str(chat.get('id', ''))
    if sender.get('is_bot') is not False or chat.get('chat_type') != 'PRIVATE' or chat_id not in config['allowed_chats']:
        return 'ignored'
    text, message_id = message.get('text'), message.get('message_id')
    if not isinstance(text, str) or not text.strip() or len(text) > 2000 or not isinstance(message_id, str) or not message_id:
        return 'ignored'
    key = hashlib.sha256((chat_id+'\0'+message_id).encode()).hexdigest()
    if queue.contains(key):
        return 'duplicate'
    # Topic state uses a hash, and is RAM-only; no user ID / patient mapping is inferred.
    session = hashlib.sha256(chat_id.encode()).hexdigest()
    return queue.enqueue(key, chat_id, message_text(engine.answer(text, session)))
