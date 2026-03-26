import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime

sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (16, 8)
plt.rcParams['font.size'] = 12

def parse_hour_field(hour_value):
    hour_str = str(hour_value)
    year = 2000 + int(hour_str[:2])
    month = int(hour_str[2:4])
    day = int(hour_str[4:6])
    hour = int(hour_str[6:8])

    return datetime(year, month, day, hour)

def build_hourly_timeseries(train_file, output_csv=None, output_plot=None):
    print("="*60)
    print("ПОСТРОЕНИЕ ВРЕМЕННОГО РЯДА ПОКАЗОВ")
    print("="*60)

    print("\n📊 Загрузка данных...")
    df = pd.read_csv(train_file, compression='gzip', usecols=['hour', 'click'])

    print(f"✅ Загружено записей: {len(df):,}")

    print("\n🕐 Преобразование временных меток...")
    df['datetime'] = df['hour'].apply(parse_hour_field)

    print("\n📈 Агрегация данных по часам...")
    hourly_stats = df.groupby('datetime').agg({
        'click': ['count', 'sum']
    }).reset_index()

    hourly_stats.columns = ['datetime', 'impressions', 'clicks']
    hourly_stats['ctr'] = (hourly_stats['clicks'] / hourly_stats['impressions'] * 100).round(4)
    hourly_stats = hourly_stats.sort_values('datetime')

    hourly_stats['date'] = hourly_stats['datetime'].dt.date
    hourly_stats['hour'] = hourly_stats['datetime'].dt.hour
    hourly_stats['day_of_week'] = hourly_stats['datetime'].dt.day_name()

    print(f"\n✅ Создан временной ряд:")
    print(f"   Период: {hourly_stats['datetime'].min()} - {hourly_stats['datetime'].max()}")
    print(f"   Количество часов: {len(hourly_stats)}")
    print(f"   Всего показов: {hourly_stats['impressions'].sum():,}")
    print(f"   Всего кликов: {hourly_stats['clicks'].sum():,}")
    print(f"   Средний CTR: {hourly_stats['ctr'].mean():.4f}%")

    print(f"\n📊 Статистика показов по часам:")
    print(f"   Минимум: {hourly_stats['impressions'].min():,}")
    print(f"   Максимум: {hourly_stats['impressions'].max():,}")
    print(f"   Среднее: {hourly_stats['impressions'].mean():,.0f}")
    print(f"   Медиана: {hourly_stats['impressions'].median():,.0f}")

    if output_csv:
        print(f"\n💾 Сохранение в CSV: {output_csv}")
        hourly_stats.to_csv(output_csv, index=False)
        print("✅ CSV сохранен")

    if output_plot:
        print(f"\n📊 Построение графика: {output_plot}")

        fig, axes = plt.subplots(2, 1, figsize=(16, 10))

        axes[0].plot(hourly_stats['datetime'], hourly_stats['impressions'],
                     linewidth=1.5, color='#2E86AB', alpha=0.8)
        axes[0].fill_between(hourly_stats['datetime'], hourly_stats['impressions'],
                             alpha=0.3, color='#2E86AB')
        axes[0].set_title('Временной ряд показов рекламы (почасовая группировка)',
                         fontsize=16, fontweight='bold', pad=20)
        axes[0].set_xlabel('Дата и время', fontsize=12)
        axes[0].set_ylabel('Количество показов', fontsize=12)
        axes[0].grid(True, alpha=0.3)
        axes[0].ticklabel_format(style='plain', axis='y')

        mean_impressions = hourly_stats['impressions'].mean()
        axes[0].axhline(y=mean_impressions, color='#1a5276', linestyle='--',
                       linewidth=2, alpha=0.7, label=f'Среднее: {mean_impressions:,.0f}')
        axes[0].legend(fontsize=11)

        axes[1].plot(hourly_stats['datetime'], hourly_stats['clicks'],
                     linewidth=1.5, color='#A23B72', alpha=0.8)
        axes[1].fill_between(hourly_stats['datetime'], hourly_stats['clicks'],
                             alpha=0.3, color='#A23B72')
        axes[1].set_title('Временной ряд кликов (почасовая группировка)',
                         fontsize=16, fontweight='bold', pad=20)
        axes[1].set_xlabel('Дата и время', fontsize=12)
        axes[1].set_ylabel('Количество кликов', fontsize=12)
        axes[1].grid(True, alpha=0.3)
        axes[1].ticklabel_format(style='plain', axis='y')

        mean_clicks = hourly_stats['clicks'].mean()
        axes[1].axhline(y=mean_clicks, color='#6b1f47', linestyle='--',
                       linewidth=2, alpha=0.7, label=f'Среднее: {mean_clicks:,.0f}')
        axes[1].legend(fontsize=11)

        plt.tight_layout()
        plt.savefig(output_plot, dpi=300, bbox_inches='tight')
        print("✅ График сохранен")
        plt.close()

    return hourly_stats


if __name__ == "__main__":
    train_file = '../avazu-ctr-prediction/train.gz'
    output_csv = 'data/hourly_timeseries.csv'
    output_plot = '../typst/images/hourly_timeseries.png'

    timeseries = build_hourly_timeseries(train_file, output_csv, output_plot)

    print("\n" + "="*60)
    print("✨ Временной ряд построен успешно!")
    print("="*60)
