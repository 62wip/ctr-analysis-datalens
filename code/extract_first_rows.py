#!/usr/bin/env python3
"""
Скрипт для извлечения первых N строк из датасета Avazu CTR Prediction
и сохранения их в различных форматах для документации
"""

import gzip
import pandas as pd
import json

def extract_first_rows(input_file, n_rows=10, output_prefix='first_rows'):
    """
    Извлекает первые N строк из gzip-сжатого CSV файла

    Args:
        input_file: путь к .gz файлу
        n_rows: количество строк для извлечения
        output_prefix: префикс для выходных файлов
    """
    print(f"Чтение первых {n_rows} строк из {input_file}...")

    # Читаем первые N строк
    with gzip.open(input_file, 'rt') as f:
        df = pd.read_csv(f, nrows=n_rows)

    print(f"Прочитано {len(df)} строк, {len(df.columns)} колонок")
    print(f"Колонки: {', '.join(df.columns)}")

    # Сохраняем в разных форматах

    # 1. CSV (обычный)
    csv_file = f'{output_prefix}.csv'
    df.to_csv(csv_file, index=False)
    print(f"✓ Сохранено в CSV: {csv_file}")

    # 2. JSON (для удобного просмотра)
    json_file = f'{output_prefix}.json'
    df.to_json(json_file, orient='records', indent=2)
    print(f"✓ Сохранено в JSON: {json_file}")

    # 5. Группировка по категориям полей
    groups = {
        'Основные': ['id', 'click', 'hour', 'C1', 'banner_pos'],
        'Сайт': ['site_id', 'site_domain', 'site_category'],
        'Приложение': ['app_id', 'app_domain', 'app_category'],
        'Устройство': ['device_id', 'device_ip', 'device_model', 'device_type', 'device_conn_type'],
        'Дополнительные': ['C14', 'C15', 'C16', 'C17', 'C18', 'C19', 'C20', 'C21']
    }

    grouped_file = f'{output_prefix}_grouped.txt'
    with open(grouped_file, 'w', encoding='utf-8') as f:
        for group_name, columns in groups.items():
            f.write(f"\n{'='*60}\n")
            f.write(f"{group_name}\n")
            f.write(f"{'='*60}\n\n")
            group_df = df[columns]
            f.write(group_df.to_string(index=False))
            f.write("\n")
    print(f"✓ Сохранено сгруппированное представление: {grouped_file}")

    # Статистика
    print(f"\nСтатистика по первым {n_rows} строкам:")
    print(f"- Кликов (click=1): {df['click'].sum()} ({df['click'].sum()/len(df)*100:.1f}%)")
    print(f"- Без кликов (click=0): {(df['click']==0).sum()} ({(df['click']==0).sum()/len(df)*100:.1f}%)")
    print(f"- Уникальных часов: {df['hour'].nunique()}")

    return df

if __name__ == '__main__':
    # Путь к файлу с данными
    train_file = '../avazu-ctr-prediction/train.gz'

    # Извлекаем первые 10 строк
    df = extract_first_rows(train_file, n_rows=10, output_prefix='data/first_10_rows')

    print("\n✅ Готово! Файлы сохранены в папке code/")
