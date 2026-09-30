from datetime import date
from decimal import Decimal
from io import StringIO
from unittest.mock import patch

import xlrd
from django.conf import settings
from django.core.management import call_command, CommandError
from django.test import TestCase

from .importer import parse_cell, read_dvkt
from .models import Dvkt


SOURCE = settings.BASE_DIR.parent / "assets" / "411_dvkt.xls"


class DvktImportTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.rows = list(read_dvkt(SOURCE))

    def run_import(self, **options):
        call_command("import_dvkt", str(SOURCE), stdout=StringIO(), **options)

    def test_source_and_value_types(self):
        self.assertEqual(len(self.rows), 431)
        self.assertEqual(len(self.rows[0]), 27)
        self.assertEqual(self.rows[1]["ma_dich_vu"], "02.0002.0071")
        self.assertEqual(self.rows[0]["don_gia"], Decimal("77200"))
        self.assertEqual(self.rows[0]["tu_ngay"], date(2026, 9, 4))
        self.assertIsNone(self.rows[0]["den_ngay"])
        self.assertEqual(self.rows[0]["ma_cskcb"], "95093")
        self.assertEqual(self.rows[-1]["cskcb_cls"], "95002")

    def test_import_and_repeat_do_not_duplicate(self):
        self.run_import()
        self.assertEqual(Dvkt.objects.count(), 431)
        first = Dvkt.objects.get(ma_dich_vu=self.rows[0]["ma_dich_vu"])
        updated_at = first.updated_at
        self.run_import()
        self.assertEqual(Dvkt.objects.count(), 431)
        first.refresh_from_db()
        self.assertEqual(first.updated_at, updated_at)

    def test_existing_row_is_updated(self):
        item = Dvkt.objects.create(**{**self.rows[0], "don_gia": Decimal("1")})
        self.run_import()
        item.refresh_from_db()
        self.assertEqual(item.don_gia, Decimal("77200"))
        self.assertEqual(Dvkt.objects.count(), 431)

    def test_dry_run_does_not_write(self):
        item = Dvkt.objects.create(**{**self.rows[0], "don_gia": Decimal("1")})
        self.run_import(dry_run=True)
        self.assertEqual(Dvkt.objects.count(), 1)
        item.refresh_from_db()
        self.assertEqual(item.don_gia, Decimal("1"))

    def test_late_error_rolls_back_all_rows(self):
        def broken_rows(*args):
            yield self.rows[0]
            raise ValueError("Invalid later row")
        with patch("dvkt.management.commands.import_dvkt.read_dvkt", broken_rows):
            with self.assertRaises(CommandError):
                self.run_import()
        self.assertEqual(Dvkt.objects.count(), 0)

    def test_text_code_preserves_leading_zero(self):
        field = Dvkt._meta.get_field("ma_cskcb")
        self.assertEqual(parse_cell(xlrd.sheet.Cell(xlrd.XL_CELL_TEXT, "01234"), field, 0), "01234")

    def test_invalid_date_and_fractional_integer_rejected(self):
        with self.assertRaises(ValueError):
            parse_cell(xlrd.sheet.Cell(xlrd.XL_CELL_NUMBER, 20260230.0), Dvkt._meta.get_field("tu_ngay"), 0)
        with self.assertRaises(ValueError):
            parse_cell(xlrd.sheet.Cell(xlrd.XL_CELL_NUMBER, 1.5), Dvkt._meta.get_field("stt"), 0)


class DvktPricesApiTests(TestCase):
    def create_service(self, **overrides):
        values = dict(stt=1, ma_dich_vu="22.0152.1609.K.95002", ten_dich_vu="Tên dịch vụ", ten_dvkt_gia="Xét nghiệm tế bào", don_gia=Decimal("60600.1250"), gia_thanh_toan=Decimal("50000"), ma_cskcb="95093", tu_ngay=date(2026, 9, 4))
        values.update(overrides)
        return Dvkt.objects.create(**values)

    def test_public_prices_use_unit_price_and_only_display_fields(self):
        item = self.create_service()
        response = self.client.get("/api/v1/dvkt/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"success": True, "count": 1, "items": [{"stt": 1, "ma_dich_vu": "22.0152.1609", "ten_dich_vu": "Xét nghiệm tế bào", "don_gia": "60600.1250"}]})
        item.refresh_from_db()
        self.assertEqual(item.ma_dich_vu, "22.0152.1609.K.95002")

    def test_same_display_code_retains_distinct_rows_in_stt_order(self):
        self.create_service(stt=2)
        self.create_service(stt=1, ma_dich_vu="22.0152.1609", don_gia=None)
        data = self.client.get("/api/v1/dvkt/").json()
        self.assertEqual(data["count"], 2)
        self.assertEqual([item["stt"] for item in data["items"]], [1, 2])
        self.assertIsNone(data["items"][0]["don_gia"])

    def test_empty_table_returns_empty_list(self):
        self.assertEqual(self.client.get("/api/v1/dvkt/").json(), {"success": True, "count": 0, "items": []})

    def test_endpoint_is_read_only(self):
        self.assertEqual(self.client.post("/api/v1/dvkt/", {}).status_code, 405)
        self.assertEqual(Dvkt.objects.count(), 0)
