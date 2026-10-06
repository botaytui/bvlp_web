import json
import urllib.error
import urllib.request


class BotAPIError(Exception):
    """Deliberately excludes request URLs (which contain the Bot Token)."""


class BotClient:
    def __init__(self, token):
        if not token or any(c.isspace() for c in token) or any(c in token for c in '/?#'):
            raise BotAPIError('Bot Token chưa hợp lệ.')
        self.token = token

    def call(self, method, payload=None, timeout=15):
        if method not in ('getMe', 'getUpdates', 'getWebhookInfo', 'setWebhook', 'testWebhook', 'sendMessage'):
            raise BotAPIError('API không được hỗ trợ.')
        req = urllib.request.Request(
            f'https://bot-api.zaloplatforms.com/bot{self.token}/{method}',
            data=json.dumps(payload or {}).encode(), headers={'Content-Type':'application/json'}, method='POST')
        try:
            with urllib.request.urlopen(req, timeout=timeout) as response:
                data = json.load(response)
        except (urllib.error.URLError, TimeoutError, ValueError, OSError):
            raise BotAPIError('Không xác nhận được phản hồi từ Zalo; kiểm tra kết nối hoặc Token.') from None
        if not isinstance(data, dict) or data.get('ok') is not True:
            raise BotAPIError('Zalo từ chối yêu cầu. Kiểm tra Token, cấu hình hoặc hạn mức.')
        return data.get('result', {})

    def send(self, chat_id, text):
        if len(text.encode('utf-16-le')) // 2 > 2000:
            raise BotAPIError('Nội dung vượt giới hạn tin nhắn Zalo.')
        return self.call('sendMessage', {'chat_id':chat_id, 'text':text})
