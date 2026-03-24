import pandas as pd
import gzip

# Путь к датасету
train_file = '../avazu-ctr-prediction/train.gz'

print("Загрузка данных...")
# Читаем только нужные колонки для экономии памяти
df = pd.read_csv(train_file, compression='gzip', usecols=['site_category', 'app_category'])

print(f"Всего записей: {len(df):,}")
print("\n" + "="*60)

# Анализ категорий сайтов
print("\n📊 КАТЕГОРИИ САЙТОВ (site_category)")
print("="*60)

site_counts = df['site_category'].value_counts()
total_sites = len(df)

print(f"\nВсего уникальных категорий: {len(site_counts)}")
print(f"\nТоп-3 категории сайтов:")

top3_site_sum = 0
for i, (category, count) in enumerate(site_counts.head(3).items(), 1):
    percentage = (count / total_sites) * 100
    top3_site_sum += percentage
    print(f"{i}. {category}: {count:,} ({percentage:.2f}%)")

others_site = 100 - top3_site_sum
print(f"\nОстальные категории: {others_site:.2f}%")
print(f"Сумма топ-3: {top3_site_sum:.2f}%")

# Анализ категорий приложений
print("\n" + "="*60)
print("\n📱 КАТЕГОРИИ ПРИЛОЖЕНИЙ (app_category)")
print("="*60)

app_counts = df['app_category'].value_counts()
total_apps = len(df)

print(f"\nВсего уникальных категорий: {len(app_counts)}")
print(f"\nТоп-3 категории приложений:")

top3_app_sum = 0
for i, (category, count) in enumerate(app_counts.head(3).items(), 1):
    percentage = (count / total_apps) * 100
    top3_app_sum += percentage
    print(f"{i}. {category}: {count:,} ({percentage:.2f}%)")

others_app = 100 - top3_app_sum
print(f"\nОстальные категории: {others_app:.2f}%")
print(f"Сумма топ-3: {top3_app_sum:.2f}%")

# Сохраняем результаты в CSV для дальнейшего использования
print("\n" + "="*60)
print("\n💾 Сохранение результатов...")

# Данные для круговых диаграмм
site_pie_data = pd.DataFrame({
    'category': list(site_counts.head(3).index) + ['Остальные'],
    'count': list(site_counts.head(3).values) + [df['site_category'].isin(site_counts.head(3).index).sum() - total_sites],
    'percentage': [
        (site_counts.iloc[0] / total_sites) * 100,
        (site_counts.iloc[1] / total_sites) * 100,
        (site_counts.iloc[2] / total_sites) * 100,
        others_site
    ]
})

app_pie_data = pd.DataFrame({
    'category': list(app_counts.head(3).index) + ['Остальные'],
    'count': list(app_counts.head(3).values) + [df['app_category'].isin(app_counts.head(3).index).sum() - total_apps],
    'percentage': [
        (app_counts.iloc[0] / total_apps) * 100,
        (app_counts.iloc[1] / total_apps) * 100,
        (app_counts.iloc[2] / total_apps) * 100,
        others_app
    ]
})

site_pie_data.to_csv('data/site_category_pie.csv', index=False)
app_pie_data.to_csv('data/app_category_pie.csv', index=False)

print("✅ Результаты сохранены:")
print("   - data/site_category_pie.csv")
print("   - data/app_category_pie.csv")

print("\n" + "="*60)
print("\n📋 ИТОГОВЫЕ ДАННЫЕ ДЛЯ КРУГОВЫХ ДИАГРАММ")
print("="*60)

print("\n🌐 Сайты:")
print(site_pie_data.to_string(index=False))

print("\n\n📱 Приложения:")
print(app_pie_data.to_string(index=False))

print("\n✨ Готово!")
