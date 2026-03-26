import gzip
import pandas as pd
import json

def extract_first_rows(input_file, n_rows=10, output_prefix='first_rows'):
    print(f"Чтение первых {n_rows} строк из {input_file}...")

    with gzip.open(input_file, 'rt') as f:
        df = pd.read_csv(f, nrows=n_rows)

    print(f"Прочитано {len(df)} строк, {len(df.columns)} колонок")
    print(f"Колонки: {', '.join(df.columns)}")

    csv_file = f'{output_prefix}.csv'
    df.to_csv(csv_file, index=False)
    print(f"✓ Сохранено в CSV: {csv_file}")

    print(f"\nСтатистика по первым {n_rows} строкам:")
    print(f"- Кликов (click=1): {df['click'].sum()} ({df['click'].sum()/len(df)*100:.1f}%)")
    print(f"- Без кликов (click=0): {(df['click']==0).sum()} ({(df['click']==0).sum()/len(df)*100:.1f}%)")
    print(f"- Уникальных часов: {df['hour'].nunique()}")

    return df

if __name__ == '__main__':
    train_file = '../avazu-ctr-prediction/train.gz'
    df = extract_first_rows(train_file, n_rows=10, output_prefix='data/first_10_rows')

    print("\n✅ Готово! Файлы сохранены в папке code/")
