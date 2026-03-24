#!/usr/bin/env python3
"""
Скрипт для определения полного периода сбора данных в датасете.
Анализирует весь датасет эффективно.
"""

import sys
import gzip
from datetime import datetime
from collections import Counter


def parse_hour_field(hour_str):
    """
    Парсит поле hour в формате YYMMDDHH.

    Args:
        hour_str: строка в формате YYMMDDHH (например, "14102100")

    Returns:
        datetime объект
    """
    try:
        year = int("20" + hour_str[:2])
        month = int(hour_str[2:4])
        day = int(hour_str[4:6])
        hour = int(hour_str[6:8])
        return datetime(year, month, day, hour)
    except:
        return None


def analyze_full_dataset(file_path):
    """
    Анализирует весь датасет для определения периода.
    """
    print(f"📊 Полный анализ датасета: {file_path}")
    print("="*60)

    try:
        all_hours = set()
        all_dates = set()
        total_lines = 0

        print(f"⏳ Чтение всего датасета...")
        print(f"   (это может занять несколько минут)")

        with gzip.open(file_path, 'rt', encoding='utf-8') as f:
            # Читаем заголовок
            header = f.readline().strip().split(',')

            try:
                hour_index = header.index('hour')
            except ValueError:
                print("❌ Столбец 'hour' не найден!")
                return

            print(f"✅ Найден столбец 'hour' (индекс {hour_index})")

            # Читаем все строки
            for line in f:
                parts = line.strip().split(',')
                if len(parts) > hour_index:
                    hour_str = parts[hour_index]
                    dt = parse_hour_field(hour_str)

                    if dt:
                        all_hours.add(dt)
                        all_dates.add(dt.date())

                total_lines += 1

                # Прогресс каждые 1 млн строк
                if total_lines % 1000000 == 0:
                    print(f"   Обработано: {total_lines:,} строк, найдено {len(all_dates)} уникальных дат")

        if not all_hours:
            print("❌ Не удалось извлечь временные данные")
            return

        # Результаты
        min_time = min(all_hours)
        max_time = max(all_hours)
        unique_dates = sorted(all_dates)

        print(f"\n✅ Анализ завершен!")
        print("="*60)
        print(f"📈 Результаты:")
        print(f"   Всего обработано строк: {total_lines:,}")
        print(f"   Уникальных часов: {len(all_hours)}")
        print(f"   Уникальных дат: {len(unique_dates)}")

        print(f"\n⏰ Временной период:")
        print(f"   Начало: {min_time.strftime('%Y-%m-%d %H:00')}")
        print(f"   Конец:  {max_time.strftime('%Y-%m-%d %H:00')}")

        duration_days = (max_time.date() - min_time.date()).days + 1
        duration_hours = len(all_hours)
        print(f"   Длительность: {duration_days} дней ({duration_hours} часов)")

        print(f"\n📅 Все даты в датасете:")
        for i, date in enumerate(unique_dates, 1):
            weekday = date.strftime('%A')
            print(f"   {i:2d}. {date.strftime('%Y-%m-%d')} ({weekday})")

        # Статистика по часам
        hour_counts = Counter(dt.hour for dt in all_hours)
        print(f"\n🕐 Покрытие по часам суток:")
        hours_covered = len(hour_counts)
        print(f"   Покрыто часов: {hours_covered}/24")

        if hours_covered <= 24:
            for hour in range(24):
                if hour in hour_counts:
                    count = hour_counts[hour]
                    print(f"   {hour:02d}:00 ✓ ({count} дней)")
                else:
                    print(f"   {hour:02d}:00 ✗")

        print("="*60)

    except FileNotFoundError:
        print(f"❌ Файл не найден: {file_path}")
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        import traceback
        traceback.print_exc()


def main():
    """
    Основная функция.
    """
    print("🎯 Полный анализ периода данных Avazu CTR Prediction")
    print("="*60)

    default_path = "avazu-ctr-prediction/train.gz"

    if len(sys.argv) > 1:
        if sys.argv[1] == "--help":
            print("\nИспользование:")
            print(f"  python {sys.argv[0]} [путь_к_файлу.gz]")
            print("\nПримеры:")
            print(f"  python {sys.argv[0]}")
            print(f"  python {sys.argv[0]} avazu-ctr-prediction/train.gz")
            print(f"  python {sys.argv[0]} avazu-ctr-prediction/test.gz")
            return
        else:
            file_path = sys.argv[1]
    else:
        file_path = default_path

    analyze_full_dataset(file_path)


if __name__ == "__main__":
    main()
