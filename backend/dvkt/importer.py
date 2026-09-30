from datetime import datetime
from decimal import Decimal, InvalidOperation

import xlrd
from django.core.exceptions import ValidationError
from django.db import models

from .models import Dvkt


IMPORT_FIELDS = [field for field in Dvkt._meta.fields if field.name not in {"id", "created_at", "updated_at"}]


def cell_text(cell):
    if cell.ctype in (xlrd.XL_CELL_EMPTY, xlrd.XL_CELL_BLANK):
        return ""
    if cell.ctype == xlrd.XL_CELL_NUMBER:
        return format(Decimal(str(cell.value)).normalize(), "f")
    if cell.ctype != xlrd.XL_CELL_TEXT:
        raise ValueError("Ô dữ liệu không phải chuỗi hoặc số hợp lệ.")
    return cell.value


def parse_cell(cell, field, datemode):
    if isinstance(field, models.DateField) and cell.ctype == xlrd.XL_CELL_DATE:
        return xlrd.xldate_as_datetime(cell.value, datemode).date()
    value = cell_text(cell)
    if not value.strip():
        return None if field.null else ""
    if isinstance(field, models.DateField):
        return datetime.strptime(value.strip(), "%Y%m%d").date()
    if isinstance(field, models.DecimalField):
        number = Decimal(value.strip())
        if not number.is_finite():
            raise ValueError("Số không hữu hạn.")
        return number
    if isinstance(field, models.IntegerField):
        number = Decimal(value.strip())
        if not number.is_finite() or number != number.to_integral_value():
            raise ValueError("Cần số nguyên.")
        return int(number)
    # Giữ nguyên nội dung văn bản và số 0 đầu trong mã dạng chuỗi.
    return value


def read_dvkt(path, sheet_name=None):
    with xlrd.open_workbook(str(path), on_demand=True) as book:
        sheet = book.sheet_by_name(sheet_name) if sheet_name else book.sheet_by_index(0)
        if not sheet.nrows:
            raise ValueError("Sheet không có dữ liệu.")
        headers = [cell_text(cell).strip().upper() for cell in sheet.row(0)]
        expected = {field.name.upper() for field in IMPORT_FIELDS}
        if len(headers) != len(set(headers)) or set(headers) != expected:
            raise ValueError("Tiêu đề phải gồm đúng 27 cột của danh mục DVKT; không được thiếu, trùng hoặc thừa cột.")
        positions = {header: index for index, header in enumerate(headers)}
        seen = set()
        for row in range(1, sheet.nrows):
            if all(cell.ctype in (xlrd.XL_CELL_EMPTY, xlrd.XL_CELL_BLANK) or cell.value == "" for cell in sheet.row(row)):
                continue
            data = {}
            for field in IMPORT_FIELDS:
                try:
                    data[field.name] = parse_cell(sheet.cell(row, positions[field.name.upper()]), field, book.datemode)
                except (ValueError, InvalidOperation, OverflowError) as error:
                    raise ValueError(f"Dòng {row + 1}, cột {field.name.upper()}: {error}") from error
            item = Dvkt(**data)
            try:
                item.full_clean(validate_unique=False, validate_constraints=False)
            except ValidationError as error:
                raise ValueError(f"Dòng {row + 1}: {error}") from error
            if item.den_ngay and item.den_ngay < item.tu_ngay:
                raise ValueError(f"Dòng {row + 1}: Đến ngày phải từ Từ ngày trở đi.")
            key = (item.ma_cskcb, item.ma_dich_vu, item.tu_ngay)
            if key in seen:
                raise ValueError(f"Dòng {row + 1}: Trùng mã CSKCB, mã dịch vụ và từ ngày trong file.")
            seen.add(key)
            yield data
