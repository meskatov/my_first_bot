import json
import re


def format_dossier(results, query):
    dossier = {
        "📛 ФИО": [], "📞 Телефон": [], "📧 Email": [], "🎂 Дата рождения": [],
        "🏠 Адрес": [], "🆔 ИНН": [], "🔢 СНИЛС": [], "🪪 Паспорт": [],
        "🏢 Компания": [], "📡 Оператор": [], "🗺️ Регион": [], "📌 Дополнительно": []
    }

    for item in results:
        if isinstance(item, dict):
            for key in ['fio', 'full_name', 'fullname', 'name']:
                if item.get(key):
                    dossier["📛 ФИО"].append(str(item[key]))
                    break
            for key in ['phone', 'phone_number', 'phones', 'mobile']:
                if item.get(key):
                    dossier["📞 Телефон"].append(str(item[key]))
                    break
            for key in ['email', 'emails', 'mail']:
                if item.get(key):
                    dossier["📧 Email"].append(str(item[key]))
                    break
            for key in ['bdate', 'birth_date', 'birthday']:
                if item.get(key):
                    dossier["🎂 Дата рождения"].append(str(item[key]))
                    break
            for key in ['address', 'addresses', 'location']:
                if item.get(key):
                    dossier["🏠 Адрес"].append(str(item[key]))
                    break
            for key in ['inn', 'INN']:
                if item.get(key):
                    dossier["🆔 ИНН"].append(str(item[key]))
                    break
            for key in ['snils', 'SNILS']:
                if item.get(key):
                    dossier["🔢 СНИЛС"].append(str(item[key]))
                    break
            for key in ['company', 'organization']:
                if item.get(key):
                    dossier["🏢 Компания"].append(str(item[key]))
                    break
            for key in ['operator', 'carrier']:
                if item.get(key):
                    dossier["📡 Оператор"].append(str(item[key]))
                    break
            if item.get('region'):
                dossier["🗺️ Регион"].append(str(item['region']))
            if item.get('passport') or item.get('passport_number'):
                dossier["🪪 Паспорт"].append(str(item.get('passport') or item.get('passport_number')))
            if item.get('rating'):
                dossier["📌 Дополнительно"].append(f"⭐ Рейтинг: {item['rating']}")
            if item.get('views'):
                dossier["📌 Дополнительно"].append(f"👁️ Просмотров: {item['views']}")
            if item.get('phone_types'):
                dossier["📌 Дополнительно"].append(f"📱 Тип: {', '.join(item['phone_types'])}")

    for key in dossier:
        dossier[key] = list(dict.fromkeys(dossier[key]))[:10]
    return dossier


def print_dossier(dossier, query):
    lines = []
    lines.append("=" * 55)
    lines.append(f"📄 ДОСЬЕ: {query}")
    lines.append("=" * 55)

    has_data = False
    for field, values in dossier.items():
        if values:
            lines.append(f"\n{field}:")
            for v in values:
                lines.append(f"  • {v}")
            has_data = True

    if not has_data:
        lines.append("\n❌ Ничего не найдено")
    lines.append("=" * 55)
    return "\n".join(lines)