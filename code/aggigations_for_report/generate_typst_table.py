import pandas as pd

def generate_typst_table(csv_file, output_file, max_rows=10):
    df = pd.read_csv(csv_file)

    if len(df) > max_rows:
        df = df.head(max_rows)

    typst_code = []

    typst_code.append("#set page(flipped: true)")
    typst_code.append("#set text(size: 7pt)")
    typst_code.append("")
    typst_code.append("#figure(")
    typst_code.append("  table(")

    num_cols = len(df.columns)
    typst_code.append(f"    columns: {num_cols},")

    align_list = []
    for col in df.columns:
        if df[col].dtype in ['int64', 'float64']:
            align_list.append('right')
        else:
            align_list.append('left')
    typst_code.append(f"    align: ({', '.join(align_list)}),")

    headers = ', '.join([f'[*{col}*]' for col in df.columns])
    typst_code.append(f"    {headers},")

    for idx, row in df.iterrows():
        values = []
        for col in df.columns:
            val = row[col]
            if pd.isna(val):
                values.append('[-]')
            elif isinstance(val, (int, float)):
                values.append(f'[{val}]')
            else:
                val_str = str(val).replace('\\', '\\\\').replace('[', '\\[').replace(']', '\\]')
                values.append(f'[`{val_str}`]')

        typst_code.append(f"    {', '.join(values)},")

    typst_code.append("  ),")
    typst_code.append("  caption: [Примеры записей из набора данных (первые 10 строк)],")
    typst_code.append(") <tab:dataset_examples>")
    typst_code.append("")
    typst_code.append("#set page(flipped: false)")
    typst_code.append("#set text(size: 14pt)")

    with open(output_file, 'w', encoding='utf-8') as f:
        f.write('\n'.join(typst_code))

    print(f"✓ Typst-код таблицы сохранен в: {output_file}")
    print(f"  Строк: {len(df)}, Колонок: {num_cols}")
    print(f"\nДля вставки в документ используйте:")
    print(f"  #include \"{output_file}\"")

if __name__ == '__main__':
    csv_file = 'data/first_10_rows.csv'
    output_file = '../dataset_table.typ'

    generate_typst_table(csv_file, output_file, max_rows=10)

    print("\n✅ Готово!")
