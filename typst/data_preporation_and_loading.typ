= Подготовка и загрузка данных для дашборда

Чтобы полноценно реальзовать построенный макет интерактивного дашборда в Yandex DataLens, надо подключить все необходимые для чартов источники данных.
Чарты с первых двух вкладок макета дашборда требуют только полный набор данных: всю аггрегацию и предобратоку данных можно выполнить на самой платформе Yandex DataLens. Третья вкладка требует метрик и сводных данных от обученной модели CatBoost.

Так как напрямую набор данных загрузить в Yandex DataLens нельзя из-за его большого объема, пришлось искать подходящую базу даннных из тех, подключения к которым поддерживает платформа DataLens.

#figure(
  image("images/connction_types_datalens.png", width: 99%),
  caption: [Источники данных в Yandex DataLens],
) <fig:connection_types_datalens>

В итоге в качестве СУБД был выбран ClickHouse, поскольку Яндекс сам рекомендует его для работы с Yandex DataLens. Кроме того, важным фактором стал доступный бесплатный период использования, что позволило развернуть хранилище и протестировать интеграцию без дополнительных затрат. Колончатая структура ClickHouse также обеспечивает высокую скорость выполнения аналитических запросов, что особенно важно при работе с большими объемами данных и построении интерактивных дашбордов.

== Подготовка ClickHouse и загрузка данных

После регистарции на платформе ClickHouse была создан сервис с самой дешевой конфигурацией.

#figure(
  image("images/clickhouse_servieces.png", width: 100%),
  caption: [Сервис "Avazu CTR Prediction Dataset" в ClickHouse],
) <fig:clickhouse_servieces>

#figure(
  image("images/clickhouse_scaling.png", width: 80%),
  caption: [Конфигурация сервиса "Avazu CTR Prediction Dataset"],
) <fig:clickhouse_servieces>

Целиком загрузить за раз весь набор данных не получилось даже в ClickHouse, поэтому он отправлялся по частям с помощью Python-библиотеки `clickhouse_connect`. Она предоставляет удобный интерфейс для подключения к базе данных, выполнения SQL-запросов и пакетной вставки данных, что особенно полезно при работе с большими объемами (как у нас). Благодаря этому данные разбивались на небольшие чанки и последовательно загружались в таблицы, что позволило избежать переполнения памяти и сетевых ограничений.

#figure(
  ```sql
CREATE TABLE avazu_ctr_prediction_data
(
    id String,
    click UInt8,
    hour UInt64,
    C1 Int32,
    banner_pos Int32,
    site_id String,
    site_domain String,
    site_category String,
    app_id String,
    app_domain String,
    app_category String,
    device_id String,
    device_ip String,
    device_model String,
    device_type Int32,
    device_conn_type Int32,
    C14 Int32,
    C15 Int32,
    C16 Int32,
    C17 Int32,
    C18 Int32,
    C19 Int32,
    C20 Int32,
    C21 Int32
)
ENGINE = MergeTree
ORDER BY (hour, id);
  ```,
  caption: [SQL запрос для создания таблицы в ClickHouse],
) <lst:table_creation>

Для начала была создана таблица в ClickHouse с помощью запроса из Листинга @lst:table_creation. Таблица была названа `avazu_ctr_prediction_data`. Далее в нее производилась вставка данных по 1 млн. строк за один запрос.

После этих действий в ClickHouse появилась таблица, содержащая весь набор данных.

== Извлечение необходимых метрик и сводных данных из модели CatBoost

Как было сказано ранее, для третьей вкладки дашборда необходимо получить метрики и сводные таблицы от обученной модели CatBoost. Мы уже обучили модель, как описано в главе "Обучение модели CatBoost". Далее будем использовать ее. Все возможные данные собирались на валидационной выборке.

=== Базовые метрики на валидационной выборке

Базовые метрики качества были получены с помощью библиотеки `sklearn`, в частности модуля `metrics`, как это представленно в Листинге @lst:metrics_calculation. После чего метрики были сохранены в файл `model_metrics.csv`.

#figure(
  ```python
from sklearn.metrics import roc_auc_score, log_loss

roc_auc = roc_auc_score(val_df[target], val_df[predicted_ctr])
logloss = log_loss(val_df[target], val_df[predicted_ctr])
  ```,
  caption: [Подсчет метрик качества на валидационной выборке],
) <lst:metrics_calculation> \

=== Данные для чартов из Lift блока

CatBoost представляет широкий функционал для определения того, почему модель сделала тот или иной выбор. Основым инструментом для этого является метод `get_feature_importance()`, который есть у класса модели CatBoostClassifier. У него есть параметр `type`, который позволяет получить различную информацию о важности признаков, полученную в ходе обучения модели.

Для сбора Lift показателей по категориям был использован метод с параметром `type='ShapValues'`. В этом режиме метод возвращает значения SHAP (SHapley Additive exPlanations) для каждого объекта и каждого признака -- то есть вклад каждого признака в итоговое предсказание модели. Результат представляет собой матрицу, где для каждой строки (объекта) указаны значения влияния всех признаков, а также дополнительный столбец с базовым значением (средним предсказанием модели).

Положительные значения SHAP показывают, что признак увеличивает вероятность целевого класса, отрицательные -- уменьшают. Это позволяет не только оценить глобальную важность признаков, но агрегировать вклады по категориям для расчета Lift метрик.

#figure(
  ```python
all_shap_values = model.get_feature_importance(val_pool, type='ShapValues')

shap_values_only = all_shap_values[:, :-1]
shap_df = pd.DataFrame(shap_values_only, columns=categorical_features)[categorical_features]


total_traffic = len(val_df)
shap_lift_data = []

for category_name in categorical_features:
    temp_df = pd.DataFrame({
        'category_value': val_df[category_name].values,
        'shap_value': shap_df[category_name].values
    })

    grouped = temp_df.groupby('category_value').agg(
        traffic=('shap_value', 'count'),
        avg_shap=('shap_value', 'mean')
    ).reset_index()

    grouped['category_name'] = category_name
    grouped['traffic_share'] = (grouped['traffic'] / total_traffic)

    shap_lift_data.append(grouped[['category_name', 'category_value', 'avg_shap', 'traffic_share']])

shap_lift_df = pd.concat(shap_lift_data, ignore_index=True)
  ```,
  caption: [Подсчет Lift метрики для категорий],
) <lst:lift_calculation>

Листинг @lst:lift_calculation содержит код для подсчета Lift метрики для категорий. Стоит отметить, что одновремменно с подсчетом пользы конкретного значения категории также собиралась доля трафика, которая относится к этой категории.

Итоговые агрегации были сохранены в файл `shap_lift.csv`.

=== Полезность признаков

Это базовая метрика CatBoost модели, которая отражает вклад каждого признака в целевую переменную. Это базовый тип метрики, который возвращает метод `get_feature_importance()`. Таблица `Feature Importance` была сохранена в файл `feature_importance.csv`.

#figure(
  ```python
feature_importance = model.get_feature_importance()
importance_df = pd.DataFrame({
    'feature': model.feature_names_,
    'importance': feature_importance
})
  ```,
  caption: [Подсчет Feature Importance CatBoost модели],
) <lst:feature_importance_calculation> \

=== Качество влияния на целевую связок признаков

Для получения этой метрики был использован метод `get_feature_importance()` вызывается с параметром `type='Interaction'`. В этом режиме метод возвращает список попарных взаимодействий признаков в табличном виде, где в третьей колонке содержится качество влияния пары на целевую переменную. Результат преобразования этого списка был сохранен в файл `feature_interactions.csv`.

#figure(
  ```python
interaction_importance = model.get_feature_importance(type="Interaction")

interactions_df = pd.DataFrame(
    interaction_importance,
    columns=['feature_1_idx', 'feature_2_idx', 'interaction_score']
)

feature_names = model.feature_names_
interactions_df['feature_1'] = interactions_df['feature_1_idx'].apply(lambda x: feature_names[int(x)])
interactions_df['feature_2'] = interactions_df['feature_2_idx'].apply(lambda x: feature_names[int(x)])
interactions_df = interactions_df[['feature_1', 'feature_2', 'interaction_score']]
  ```,
  caption: [Подсчет Feature Importance CatBoost модели],
) <lst:feature_importance_calculation> \

=== Предсказанный CTR в сравнении с реальным в срезах разных признаков
В этом блоке был рассчитан средний реальный CTR и средний предсказанный CTR в групперовке по следующим признакам: `site_category`, `app_category`, `device_model`, `device_type`. Результат сохранен в файл `diff_ctr.csv`.

#figure(
  ```python
needable_categorical_features = ['site_category', 'app_category', 'device_model', 'device_type']

for category_name in needable_categorical_features:
    grouped = val_df.groupby(category_name).agg({target: 'mean', predicted_ctr: 'mean'}).reset_index()
    grouped.columns = ['category_value', 'real_ctr', 'predicted_ctr']
    grouped['category_name'] = category_name

    diff_ctr_data.append(grouped)

diff_ctr_df = pd.concat(diff_ctr_data, ignore_index=True)
  ```,
  caption: [Вычисления среднего реального и предсказанного CTR в групперовке по разным признакам],
) <lst:diff_ctr_calculation> \

=== Данные для диаграммы надежности модели

В этом блоке была рассчитана калибровка модели -- соответствие предсказанных вероятностей реальным значениям целевой переменной. Для этого использовалась функция `calibration_curve` из библиотеки `sklearn.calibration`, которая разбивает предсказания на интервалы (бины) и для каждого из них вычисляет средний предсказанный CTR и фактическую долю положительных исходов. Результат сохранен в файл `calibration_curve.csv`

#figure(
  ```python
from sklearn.calibration import calibration_curve

prob_true, prob_pred = calibration_curve(val_df[target], val_df[predicted_ctr], n_bins=10, strategy='uniform')

calibration_df = pd.DataFrame({
    'predicted_ctr': prob_pred,
    'real_ctr': prob_true
})
calibration_df['perfect_calibration'] = calibration_df['real_ctr']
  ```,
  caption: [Вычисления среднего реального и предсказанного CTR в групперовке по разным признакам],
) <lst:diff_ctr_calculation>

== Подключение источников данных в Yandex DataLens <data_connection>

=== Подключение ClickHouse

Для подключения ClickHouse к Yandex DataLens потребовалось указать путь базы данных и порт интерфейса, как это показано на Рисунке @fig:clickhouse_connection.

#figure(
  image("images/clickhouse_connection.png", width: 90%),
  caption: [Источники данных в Yandex DataLens],
) <fig:clickhouse_connection>

После чего у меня появилось подключение к базе данных в ClickHouse и доступ к таблице `avazu_ctr_prediction_data`.

=== Подключение метрик и сводных таблиц из модели CatBoost

Yandex DataLens позволяет удобным образом загружать CSV файлы прямо на платформу (можно увидеть на Рисунке @fig:connection_types_datalens). Поэтому все необходимые CSV файлы были просто загружены в Yandex DataLens.

По итогам были получены 2 источника данных. Они представлены на Рисунке @fig:datelens_connections.

#figure(
  image("images/datelens_connections.png", width: 100%),
  caption: [Все созданные подключения в Yandex DataLens],
) <fig:datelens_connections>

== Создание датасетов в Yandex DataLens

Из подключений были созданы все необходые для чартов датасеты. Они представлены на Рисунке @fig:datelens_datasets.

#figure(
  image("images/datelens_datasets.png", width: 100%),
  caption: [Все созданные датасеты в Yandex DataLens],
) <fig:datelens_datasets>

В каждом датасете были проведены преобразования колонок типов данных, а также все названия колонок были переведены на русский с понятным значение для удобства дальнейшего использования.