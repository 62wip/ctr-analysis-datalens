import pandas as pd
import numpy as np
from catboost import CatBoostClassifier
import gzip
import os

print("Загрузка обученной модели...")
model = CatBoostClassifier()
model.load_model('catboost_model.cbm')

print("Модель загружена успешно!")
print(f"Количество признаков в модели: {model.feature_names_}")

print("\nЗагрузка тестовых данных...")
test_file = '../avazu-ctr-prediction/test.gz'

chunk_size = 1000000
predictions_list = []
ids_list = []

chunk_num = 0
with gzip.open(test_file, 'rt') as f:
    for chunk in pd.read_csv(f, chunksize=chunk_size, dtype={'id': str}):
        chunk_num += 1
        print(f"\nОбработка чанка {chunk_num}: {len(chunk)} строк")

        # ID уже читаются как строки благодаря dtype={'id': str}
        ids = chunk['id'].tolist()
        ids_list.extend(ids)
        X_test = chunk.drop('id', axis=1)

        print(f"Признаки в тестовых данных: {X_test.columns.tolist()}")

        y_pred_proba = model.predict_proba(X_test)[:, 1]
        predictions_list.append(y_pred_proba)

        print(f"Средняя вероятность клика: {y_pred_proba.mean():.4f}")
        print(f"Мин: {y_pred_proba.min():.4f}, Макс: {y_pred_proba.max():.4f}")

all_predictions = np.concatenate(predictions_list)

print(f"\nВсего предсказаний: {len(all_predictions)}")
print(f"Всего ID: {len(ids_list)}")

submission_file = 'submission.csv'
with open(submission_file, 'w') as f:
    f.write('id,click\n')
    for id_val, click_val in zip(ids_list, all_predictions):
        f.write(f'{id_val},{click_val}\n')
print(f"\nРезультаты сохранены в: {submission_file}")

print(f"\nСтатистика предсказаний:")
print(f"Средняя вероятность клика: {all_predictions.mean():.4f}")
print(f"Медианная вероятность: {np.median(all_predictions):.4f}")
print(f"Стандартное отклонение: {all_predictions.std():.4f}")
print(f"Минимум: {all_predictions.min():.4f}")
print(f"Максимум: {all_predictions.max():.4f}")

print(f"\nКвантили:")
for q in [0.1, 0.25, 0.5, 0.75, 0.9]:
    print(f"  {int(q*100)}%: {np.quantile(all_predictions, q):.4f}")

print("\nГотово!")
