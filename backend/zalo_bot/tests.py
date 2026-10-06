import copy
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import Mock, patch
from django.test import RequestFactory, SimpleTestCase
from .core import Engine, normalize
from .gateway import Queue, process_event, message_text
from . import views

PRICES = [
    {'ma_dich_vu':'XR01','ten_dich_vu':'Chụp X-quang ngực thẳng','don_gia':'50000'},
    {'ma_dich_vu':'CT01','ten_dich_vu':'Chụp cắt lớp vi tính ngực','don_gia':'123456'},
    {'ma_dich_vu':'SPINE','ten_dich_vu':'Chụp X-quang cột sống ngực','don_gia':'80000'},
    {'ma_dich_vu':'CTSPINE','ten_dich_vu':'Chụp cắt lớp vi tính cột sống ngực','don_gia':'222222'},
    {'ma_dich_vu':'OTHER','ten_dich_vu':'Xét nghiệm khác','don_gia':None},
    {'ma_dich_vu':'KHAM','ten_dich_vu':'Khám nội khoa','don_gia':'0'},
]
CONFIG = {'enabled':True,'token':'test-token','secret':'test-secret-123','allowed_chats':{'pilot-chat'}}
EVENT = {'ok':True,'result':{'event_name':'message.text.received','message':{
    'from':{'id':'sender','is_bot':False}, 'chat':{'id':'pilot-chat','chat_type':'PRIVATE'},
    'message_id':'msg-1','text':'đặt lịch','date':0}}}


class CoreTests(SimpleTestCase):
    def setUp(self):
        self.engine=Engine(lambda:PRICES)

    def test_normalize_vietnamese(self):
        self.assertEqual(normalize('ĐẶT LỊCH, Bảo hiểm!'),'dat lich bao hiem')

    def test_booking_unaccented_and_no_false_confirmation(self):
        response=self.engine.answer('toi muon dat lich kham')
        self.assertEqual(response['topic'],'booking')
        self.assertIn('chưa có nghĩa',response['reply'])
        self.assertTrue(response['actions'][0]['url'].startswith('https://bvlbpbl.vn/'))

    def test_faq_count_and_review_metadata(self):
        self.assertEqual(len(self.engine.faqs),30)
        for faq in self.engine.faqs:
            self.assertEqual(faq['review_status'],'draft_pilot')
            self.assertIsNone(faq['approved_by'])
            self.assertTrue(faq['sources'])

    def test_unknown_query_does_not_match_general_words(self):
        self.assertEqual(self.engine.answer('toi thich ca phe')['topic'],'unknown')

    def test_urgent_overrides_booking_and_pricing(self):
        response=self.engine.answer('dat lich gia kham, toi khong tho duoc')
        self.assertEqual(response['topic'],'emergency')
        self.assertIn('115',response['reply'])

    def test_no_diagnosis(self):
        self.assertEqual(self.engine.answer('toi co bi lao khong')['topic'],'clinical')

    def test_no_prescription(self):
        self.assertEqual(self.engine.answer('toi nen uong thuoc gi')['topic'],'clinical')

    def test_handoff_does_not_claim_agent_received(self):
        self.assertIn('chưa xác nhận',self.engine.answer('cho gap nguoi that')['reply'])

    def test_context_followup_and_separation(self):
        self.engine.answer('dat lich','a')
        self.assertEqual(self.engine.answer('can giay to','a')['topic'],'bhyt')
        self.engine.answer('bhyt','a')
        self.assertIn('trường hợp',self.engine.answer('trai tuyen thi sao','a')['reply'])
        self.assertNotIn('a',self.engine.sessions.get('b',{}))

    def test_price_matches_service_terms(self):
        response=self.engine.answer('gia X-quang nguc')
        self.assertIn('50.000 đ',response['reply'])
        self.assertNotIn('123.456',response['reply'])
        self.assertNotIn('Xét nghiệm khác',response['reply'])
        self.assertNotIn('cột sống',response['reply'])

    def test_price_ct_word_boundary(self):
        response=self.engine.answer('gia ct nguc')
        self.assertIn('123.456 đ',response['reply'])
        self.assertNotIn('50.000',response['reply'])
        self.assertNotIn('cột sống',response['reply'])

    def test_unknown_service_not_invented(self):
        self.assertIn('Chưa tìm thấy',self.engine.answer('gia dich vu xyzabc')['reply'])

    def test_generic_price_asks_service(self):
        self.assertIn('dịch vụ nào',self.engine.answer('bang gia')['reply'])

    def test_zero_price_not_missing(self):
        self.assertIn('0 đ',self.engine.answer('gia kham benh')['reply'])

    def test_downstream_failure_falls_back(self):
        engine=Engine(Mock(side_effect=OSError()))
        self.assertIn('chưa tải được',engine.answer('gia xquang')['reply'])

    def test_zalo_text_limit_keeps_links(self):
        response={'reply':'✦😀'*3000,'actions':[{'label':'OA','url':'https://zalo.me/bvlaophoibaclieu'}]}
        text=message_text(response)
        self.assertLessEqual(len(text.encode('utf-16-le'))//2,2000)
        self.assertIn('https://zalo.me/',text)


class GatewayTests(SimpleTestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.queue=Queue(Path(self.temp.name)/'queue.sqlite3')
        self.engine=Engine(lambda:PRICES)

    def process(self,event=None,config=None):
        return process_event(copy.deepcopy(EVENT) if event is None else event,copy.deepcopy(CONFIG) if config is None else config,self.engine,self.queue)

    def test_dedup_before_engine_and_once_sent(self):
        with patch.object(self.engine,'answer',wraps=self.engine.answer) as answer:
            self.assertEqual(self.process(),'queued')
            self.assertEqual(self.process(),'duplicate')
            self.assertEqual(answer.call_count,1)
        client=Mock()
        self.assertTrue(self.queue.deliver_one(client))
        self.assertFalse(self.queue.deliver_one(client))
        client.send.assert_called_once()
        self.assertEqual(self.queue.counts(),{'sent':1})
        with self.queue.connection() as db:
            self.assertEqual(db.execute('SELECT chat,text FROM outbox').fetchone(),(None,None))

    def test_disabled_empty_allowlist_no_reply(self):
        config=copy.deepcopy(CONFIG);config['allowed_chats']=set()
        self.assertEqual(self.process(config=config),'disabled')

    def test_foreign_chat_no_reply(self):
        event=copy.deepcopy(EVENT);event['result']['message']['chat']['id']='other'
        self.assertEqual(self.process(event),'ignored')

    def test_bot_sender_no_loop(self):
        event=copy.deepcopy(EVENT);event['result']['message']['from']['is_bot']=True
        self.assertEqual(self.process(event),'ignored')

    def test_group_ignored(self):
        event=copy.deepcopy(EVENT);event['result']['message']['chat']['chat_type']='GROUP'
        self.assertEqual(self.process(event),'ignored')

    def test_unsupported_and_malformed_events(self):
        for value in ({},{'result':[]},{'result':{'event_name':'message.image.received'}},{'result':{'event_name':'message.text.received','message':[]}}):
            self.assertEqual(self.process(value),'ignored')

    def test_message_id_required(self):
        event=copy.deepcopy(EVENT);event['result']['message'].pop('message_id')
        self.assertEqual(self.process(event),'ignored')

    def test_ambiguous_network_failure_never_auto_resends(self):
        self.process();client=Mock();client.send.side_effect=TimeoutError()
        self.queue.deliver_one(client)
        self.assertFalse(self.queue.deliver_one(client))
        self.assertEqual(self.queue.counts(),{'unknown':1})

    def test_removed_allowlist_cancels_pending(self):
        self.process();client=Mock()
        self.queue.deliver_one(client,set())
        client.send.assert_not_called()
        self.assertEqual(self.queue.counts(),{'cancelled':1})


class WebhookTests(SimpleTestCase):
    def setUp(self):
        self.factory=RequestFactory()
        self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup)
        queue=Queue(Path(self.temp.name)/'webhook.sqlite3')
        self.patch_config=patch.object(views,'configuration',return_value=copy.deepcopy(CONFIG))
        self.patch_queue=patch.object(views,'Queue',return_value=queue)
        self.patch_engine=patch.object(views,'engine',Engine(lambda:PRICES))
        for item in (self.patch_config,self.patch_queue,self.patch_engine):
            item.start();self.addCleanup(item.stop)

    def request(self,body=None,secret='test-secret-123'):
        return self.factory.post('/api/v1/zalo-bot/webhook/', data=json.dumps(body if body is not None else EVENT),content_type='application/json',HTTP_X_BOT_API_SECRET_TOKEN=secret)

    def test_wrong_secret_rejected(self):
        self.assertEqual(views.webhook(self.request(secret='wrong')).status_code,403)

    def test_missing_token_fail_closed(self):
        with patch.object(views,'configuration',return_value={**CONFIG,'token':''}):
            self.assertEqual(views.webhook(self.request()).status_code,503)

    def test_valid_event_queues_and_duplicate_acknowledges(self):
        first=json.loads(views.webhook(self.request()).content)
        second=json.loads(views.webhook(self.request()).content)
        self.assertEqual(first['status'],'queued');self.assertEqual(second['status'],'duplicate')

    def test_probe_acknowledges_without_sending(self):
        self.assertEqual(json.loads(views.webhook(self.request({})).content)['status'],'ignored')

    def test_invalid_json(self):
        req=self.factory.post('/api/v1/zalo-bot/webhook/',data='[',content_type='application/json',HTTP_X_BOT_API_SECRET_TOKEN=CONFIG['secret'])
        self.assertEqual(views.webhook(req).status_code,400)

    def test_oversized_payload(self):
        self.assertEqual(views.webhook(self.request({'large':'x'*17000})).status_code,413)
