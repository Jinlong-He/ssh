# process_herbs_csv.py
import csv
from pypinyin import pinyin, Style

def get_chinese_initials(text):
    """
    获取中文文本的首字母缩写
    :param text: 中文文本
    :return: 首字母缩写
    """
    # 使用 pypinyin 库将中文转换为首字母
    initials = ''.join([p[0][0] for p in pinyin(text, style=Style.FIRST_LETTER)])
    return initials

def process_csv_file(input_file, output_file):
    """
    处理 CSV 文件，增加一列“缩写”
    :param input_file: 输入的 CSV 文件路径
    :param output_file: 输出的 CSV 文件路径
    """
    try:
        # 打开输入文件进行读取
        with open(input_file, 'r', newline='', encoding='utf-8') as infile:
            reader = csv.DictReader(infile)
            # 获取原有的列名
            fieldnames = reader.fieldnames
            # 增加新的列名“缩写”
            fieldnames.append('key')

            # 打开输出文件进行写入
            with open(output_file, 'w', newline='', encoding='utf-8') as outfile:
                writer = csv.DictWriter(outfile, fieldnames=fieldnames)
                # 写入表头
                writer.writeheader()

                # 逐行处理数据
                for row in reader:
                    name = row.get('name', '')
                    if name:
                        # 获取中文首字母缩写
                        print(name)
                        abbreviation = get_chinese_initials(name)
                        print(abbreviation)
                        # 将缩写添加到当前行
                        row['key'] = abbreviation
                    # 写入处理后的行
                    writer.writerow(row)

        print(f"处理完成，结果已保存到 {output_file}")
    except FileNotFoundError:
        print(f"错误：未找到文件 {input_file}")
    except Exception as e:
        print(f"发生错误：{e}")

if __name__ == "__main__":
    input_file = 'herbs.csv'
    output_file = 'herbs_processed.csv'
    process_csv_file(input_file, output_file)