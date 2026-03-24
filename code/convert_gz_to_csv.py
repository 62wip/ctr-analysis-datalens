import pandas as pd
import gzip
import os

def convert_gz_to_csv(gz_file_path, csv_file_path=None, chunksize=None):
    """
    Конвертирует .gz файл в .csv файл

    Parameters:
    -----------
    gz_file_path : str
        Путь к .gz файлу
    csv_file_path : str, optional
        Путь для сохранения .csv файла. Если не указан, будет создан файл
        с тем же именем, но расширением .csv
    chunksize : int, optional
        Размер чанка для обработки больших файлов. Если None, файл загружается целиком
    """

    # Если путь для csv не указан, создаем его из пути gz файла
    if csv_file_path is None:
        csv_file_path = gz_file_path.replace('.gz', '.csv')

    print(f"Конвертация: {gz_file_path} -> {csv_file_path}")

    # Проверяем существование исходного файла
    if not os.path.exists(gz_file_path):
        print(f"❌ Ошибка: файл {gz_file_path} не найден!")
        return False

    try:
        if chunksize:
            # Обработка большого файла по частям
            print(f"Обработка файла по частям (chunksize={chunksize:,})...")
            first_chunk = True

            for i, chunk in enumerate(pd.read_csv(gz_file_path, compression='gzip', chunksize=chunksize)):
                mode = 'w' if first_chunk else 'a'
                header = first_chunk

                chunk.to_csv(csv_file_path, mode=mode, header=header, index=False)

                if first_chunk:
                    first_chunk = False

                print(f"  Обработано чанков: {i+1}, строк: {(i+1)*chunksize:,}", end='\r')

            print()  # Новая строка после прогресса
        else:
            # Загрузка всего файла сразу
            print("Загрузка файла...")
            df = pd.read_csv(gz_file_path, compression='gzip')

            print(f"Загружено строк: {len(df):,}")
            print(f"Столбцов: {len(df.columns)}")

            print("Сохранение в CSV...")
            df.to_csv(csv_file_path, index=False)

        # Проверяем размер файлов
        gz_size = os.path.getsize(gz_file_path) / (1024 * 1024)  # MB
        csv_size = os.path.getsize(csv_file_path) / (1024 * 1024)  # MB

        print(f"✅ Конвертация завершена!")
        print(f"   Размер .gz файла: {gz_size:.2f} MB")
        print(f"   Размер .csv файла: {csv_size:.2f} MB")
        print(f"   Коэффициент сжатия: {csv_size/gz_size:.2f}x")

        return True

    except Exception as e:
        print(f"❌ Ошибка при конвертации: {e}")
        return False


if __name__ == "__main__":
    # Пути к файлам
    base_path = '../avazu-ctr-prediction/'

    files_to_convert = [
        'train.gz',
        'test.gz',
        'sampleSubmission.gz'
    ]

    print("="*60)
    print("КОНВЕРТАЦИЯ GZ ФАЙЛОВ В CSV")
    print("="*60)
    print()

    # Конвертируем каждый файл
    for filename in files_to_convert:
        gz_path = os.path.join(base_path, filename)
        csv_path = os.path.join(base_path, filename.replace('.gz', '.csv'))

        # Для больших файлов используем chunksize
        # train.gz очень большой, поэтому обрабатываем по частям
        if filename == 'train.gz':
            print(f"\n📊 {filename} (большой файл, обработка по частям)")
            convert_gz_to_csv(gz_path, csv_path, chunksize=1000000)
        else:
            print(f"\n📊 {filename}")
            convert_gz_to_csv(gz_path, csv_path)

        print()

    print("="*60)
    print("✨ Все файлы обработаны!")
    print("="*60)
