from django.db import migrations


def seed_specialties(apps, schema_editor):
    Specialty = apps.get_model("appointments", "Specialty")
    rows = [
        ("ho-hap", "Khám hô hấp", 10),
        ("lao", "Khám lao", 20),
        ("phoi-man-tinh", "Bệnh phổi mạn tính", 30),
        ("noi-tong-hop", "Khám Nội tổng hợp", 40),
        ("tu-van-phong-benh", "Tư vấn và phòng bệnh hô hấp", 50),
    ]
    for code, name, sort_order in rows:
        Specialty.objects.update_or_create(
            code=code,
            defaults={"name": name, "sort_order": sort_order, "is_active": True},
        )


class Migration(migrations.Migration):
    dependencies = [("appointments", "0001_initial")]
    operations = [migrations.RunPython(seed_specialties, migrations.RunPython.noop)]
