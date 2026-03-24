import pandas as pd
import numpy as np
from catboost import CatBoostClassifier, Pool
from sklearn.model_selection import train_test_split
from sklearn.metrics import roc_auc_score, log_loss, accuracy_score, classification_report
import gzip
import os

print("Загрузка данных...")
train_file = '../avazu-ctr-prediction/train.gz'

SAMPLE_FRACTION = 0.2

chunk_size = 1000000
chunks = []
total_loaded = 0

with gzip.open(train_file, 'rt') as f:
    for chunk in pd.read_csv(f, chunksize=chunk_size):
        chunks.append(chunk)
        total_loaded += len(chunk)
        print(f"Загружено {total_loaded:,} строк...")

df = pd.concat(chunks, ignore_index=True)
print(f"Итого загружено: {len(df):,} строк")

if SAMPLE_FRACTION < 1.0:
    original_size = len(df)
    df = df.sample(frac=SAMPLE_FRACTION, random_state=42)
    print(f"Применено сэмплирование: {SAMPLE_FRACTION*100:.1f}% данных")
    print(f"Размер после сэмплирования: {len(df):,} строк (было {original_size:,})")

print(f"\nРазмер датасета: {df.shape}")
print(f"Распределение целевой переменной:\n{df['click'].value_counts()}")
print(f"Доля кликов: {df['click'].mean():.4f}")

target = 'click'
id_col = 'id'

feature_cols = [col for col in df.columns if col not in [target, id_col]]

categorical_features = [col for col in feature_cols if not col.startswith('C') or col in ['C1']]

print(f"\nВсего признаков: {len(feature_cols)}")
print(f"Категориальных признаков: {len(categorical_features)}")
print(f"Категориальные признаки: {categorical_features}")

X = df[feature_cols]
y = df[target]

X_train, X_val, y_train, y_val = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

print(f"\nРазмер обучающей выборки: {X_train.shape}")
print(f"Размер валидационной выборки: {X_val.shape}")

train_pool = Pool(
    data=X_train,
    label=y_train,
    cat_features=categorical_features
)

val_pool = Pool(
    data=X_val,
    label=y_val,
    cat_features=categorical_features
)

print("\nОбучение модели CatBoost...")

model = CatBoostClassifier(
    iterations=1000,
    learning_rate=0.1,
    depth=6,
    loss_function='Logloss',
    eval_metric='AUC',
    random_seed=42,
    verbose=100,
    early_stopping_rounds=50,
    task_type='CPU',
    use_best_model=True
)

model.fit(
    train_pool,
    eval_set=val_pool,
    plot=False
)

print("\nОценка модели на валидационной выборке...")

y_pred_proba = model.predict_proba(X_val)[:, 1]
y_pred = model.predict(X_val)

auc = roc_auc_score(y_val, y_pred_proba)
logloss = log_loss(y_val, y_pred_proba)
accuracy = accuracy_score(y_val, y_pred)

print(f"\n{'='*50}")
print(f"РЕЗУЛЬТАТЫ МОДЕЛИ")
print(f"{'='*50}")
print(f"ROC-AUC Score: {auc:.4f}")
print(f"Log Loss: {logloss:.4f}")
print(f"Accuracy: {accuracy:.4f}")
print(f"\nClassification Report:")
print(classification_report(y_val, y_pred))

feature_importance = model.get_feature_importance()
feature_names = X_train.columns

importance_df = pd.DataFrame({
    'feature': feature_names,
    'importance': feature_importance
}).sort_values('importance', ascending=False)

print(f"\nТоп-10 важных признаков:")
print(importance_df.head(10).to_string(index=False))

model_path = 'catboost_model.cbm'
model.save_model(model_path)
print(f"\nМодель сохранена в: {model_path}")

importance_df.to_csv('feature_importance.csv', index=False)
print(f"Важность признаков сохранена в: feature_importance.csv")

metrics_df = pd.DataFrame({
    'metric': ['ROC-AUC', 'Log Loss', 'Accuracy'],
    'value': [auc, logloss, accuracy]
})
metrics_df.to_csv('metrics.csv', index=False)
print(f"Метрики сохранены в: metrics.csv")

print("\nГотово!")
