from pathlib import Path

import xlrd
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from dvkt.importer import read_dvkt
from dvkt.models import Dvkt


class Command(BaseCommand):
    help = "Nhập danh mục DVKT từ Excel .xls; cập nhật theo mã CSKCB, mã dịch vụ và từ ngày."

    def add_arguments(self, parser):
        parser.add_argument("file", type=Path)
        parser.add_argument("--sheet", help="Tên sheet (mặc định: sheet đầu tiên)")
        parser.add_argument("--dry-run", action="store_true", help="Kiểm tra và thống kê, không lưu thay đổi")

    def handle(self, *args, **options):
        path = options["file"].resolve()
        if not path.is_file():
            raise CommandError(f"Không tìm thấy file: {path}")
        created = updated = unchanged = 0
        try:
            with transaction.atomic():
                for data in read_dvkt(path, options["sheet"]):
                    key = {name: data[name] for name in ("ma_cskcb", "ma_dich_vu", "tu_ngay")}
                    item, is_new = Dvkt.objects.get_or_create(**key, defaults=data)
                    if is_new:
                        created += 1
                    elif any(getattr(item, name) != value for name, value in data.items()):
                        for name, value in data.items():
                            setattr(item, name, value)
                        item.save()
                        updated += 1
                    else:
                        unchanged += 1
                if options["dry_run"]:
                    transaction.set_rollback(True)
        except (OSError, ValueError, xlrd.XLRDError) as error:
            raise CommandError(str(error)) from error
        mode = "KIỂM TRA, KHÔNG LƯU" if options["dry_run"] else "ĐÃ IMPORT"
        self.stdout.write(self.style.SUCCESS(
            f"{mode}: {created + updated + unchanged} dòng; thêm {created}, cập nhật {updated}, giữ nguyên {unchanged}."
        ))
