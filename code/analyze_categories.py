import pandas as pd
import gzip

# Читаем ВСЕ данные для анализа
print("Загрузка данных (это может занять несколько минут)...")
with gzip.open('../avazu-ctr-prediction/train.gz', 'rt') as f:
    df = pd.read_csv(f)

print(f"Загружено {len(df)} строк")

# Анализ site_category
print("\n=== Анализ site_category ===")
site_cat_counts = df['site_category'].value_counts().head(10)
print("Топ-10 категорий сайтов:")
print(site_cat_counts)
print(f"\nВсего уникальных категорий сайтов: {df['site_category'].nunique()}")

# Анализ app_category
print("\n=== Анализ app_category ===")
app_cat_counts = df['app_category'].value_counts().head(10)
print("Топ-10 категорий приложений:")
print(app_cat_counts)
print(f"\nВсего уникальных категорий приложений: {df['app_category'].nunique()}")

# Сохраняем результаты для использования в Typst
print("\n=== Сохранение результатов ===")
site_cat_counts.to_csv('data/site_category_top10.csv', header=['count'])
app_cat_counts.to_csv('data/app_category_top10.csv', header=['count'])
print("Результаты сохранены в data/")
