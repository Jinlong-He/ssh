import csv, os, sys, io
from flask import Flask, render_template, request, redirect, url_for
from pypinyin import pinyin, Style
import datetime
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')


app = Flask(__name__)

# 模拟数据存储
prescriptions = []
formulas = []
herbs_file = 'herbs.csv'
prescription={  'patient_name': '张三',
                'patient_gender': '男',
                'patient_age': 30,
                'prescription_date': datetime.date.today(),
                'formula_template': '',
                'taking_days': 14,
                'daily_dose': 1,
                'herbs': []
            }
price_sum = 0


def get_chinese_initials(text):
    """
    获取中文文本的首字母缩写
    :param text: 中文文本
    :return: 首字母缩写
    """
    # 使用 pypinyin 库将中文转换为首字母
    initials = ''.join([p[0][0] for p in pinyin(text, style=Style.FIRST_LETTER)])
    return initials

# 读取 CSV 文件中的药材数据
def read_herbs():
    herbs = []
    try:
        with open(herbs_file, 'r', newline='', encoding='utf-8') as file:
            # 指定 delimiter 为制表符
            reader = csv.DictReader(file, delimiter='\t')
            for row in reader:
                herbs.append(row)
    except FileNotFoundError:
        pass
    return herbs

def read_herbs_dict():
    herbs = {}
    try:
        with open(herbs_file, 'r', newline='', encoding='utf-8') as file:
            # 指定 delimiter 为制表符
            reader = csv.DictReader(file, delimiter='\t')
            for row in reader:
                herbs[row['name']] = row['price_per_g']
    except FileNotFoundError:
        pass
    return herbs

# 写入药材数据到 CSV 文件
def write_herbs(herbs):
    fieldnames = ['id', 'name', 'price_per_g', 'key']
    with open(herbs_file, 'w', newline='', encoding='utf-8') as file:
        # 指定 delimiter 为制表符
        writer = csv.DictWriter(file, fieldnames=fieldnames, delimiter='\t')
        writer.writeheader()
        for herb in herbs:
            writer.writerow(herb)

def read_formulas():
    formula_names = []
    formulas = {}
    folder_path = 'formulas'
    name_dict = {}
    with open('formulas.csv', 'r', newline='', encoding='utf-8') as file:
        # 指定 delimiter 为制表符
        reader = csv.DictReader(file, delimiter='\t')
        for row in reader:
            name_dict[row['en']] = row['ch']
    try:
        # all_items = os.listdir(folder_path)
        all_items = os.listdir(folder_path)
        for item in all_items:
            # item = item.encode('latin1').decode('utf-8')
            item_path = os.path.join(folder_path, item)
            if os.path.isfile(item_path) and item.endswith('.csv'):
                formula_name = name_dict[item[:-4]]
                formula_names.append(formula_name)
                formula = read_formula(item_path)
                formulas[formula_name] = formula
    except FileNotFoundError:
        pass
    return (formula_names, formulas)

def read_formula(formula_file):
    formula = []
    try:
        with open(formula_file, 'r', newline='', encoding='utf-8') as file:
            # 指定 delimiter 为制表符
            reader = csv.DictReader(file, delimiter='\t')
            for row in reader:
                formula.append(row)
    except FileNotFoundError:
        pass
    return formula

def read_prescription(prescription_file):
    prescription = []
    try:
        if isinstance(prescription_file,str):
            with open(prescription_file, 'r', newline='', encoding='utf-8') as file:
                # 指定 delimiter 为制表符
                reader = csv.DictReader(file, delimiter='\t')
                for row in reader:
                    prescription.append(row)
        else:
            reader = csv.DictReader(prescription_file, delimiter='\t')
            for row in reader:
                prescription.append(row)
    except FileNotFoundError:
        pass
    return prescription

def write_prescription(prescription):
    patient_name = prescription['patient_name']
    date = prescription['prescription_date']
    file_name = patient_name + '_' + date + '.xxx'
    # print(file_name)

def get_price(herbs):
    price_sum = 0
    for herb in herbs:
        price_sum += herb['price']
    price_sum = round(price_sum, 2)
    return price_sum

# write_prescription([], temp)
@app.route('/', methods=['GET', 'POST'])
def index():
    (formula_names, formulas) = read_formulas()
    herbs_dict = read_herbs_dict()
    herbs = prescription['herbs']
    # print(formula_names)
    # print(formulas)
    for name in formula_names:
        formula = formulas[name]
        for item in formula:
            price_per_g = herbs_dict[item['name']]
            item['price_per_g'] = price_per_g
            item['price'] = round(float(price_per_g) * int(item['weight']), 2)
    price_sum = get_price(herbs)
    if request.method == 'POST':
        # print(request.form)
        if 'select_formula' in request.form:
            formula_name = request.form.get('select_formula')
            herbs = formulas[formula_name]
        elif 'delete_item' in request.form:
            herb_id = request.form.get('delete_item')
            herbs = [herb for herb in herbs if herb['id'] != herb_id]
            for herb in herbs:
                if int(herb['id']) > int(herb_id) :
                    herb['id'] = str(int(herb['id']) - 1)
        elif 'edit_item' in request.form:
            formula_id = request.form.get('edit_item')
            weight = request.form.get('edit_weight')
            for herb in herbs:
                # print(herb)
                if herb['id'] == formula_id:
                    herb['weight'] = weight
                    price_per_g = herb['price_per_g']
                    herb['price'] = round(float(price_per_g) * int(weight), 2)
                    break
        elif 'add_item' in request.form:
            new_id = str(len(herbs) + 1)
            name = request.form.get('name')
            weight = request.form.get('weight')
            abbreviation = get_chinese_initials(name)
            if name in herbs_dict :
                price_per_g = herbs_dict[name]
                price = round(float(price_per_g) * int(weight), 2)
                new_herb = {'id': new_id, 'name': name, 'weight': weight, 'price_per_g': price_per_g, 'price': price}
                herbs.append(new_herb)
        prescription['herbs'] = herbs
        price_sum = get_price(herbs)
        if 'new_prescription' in request.form:
            prescription['patient_name'] = request.form.get('patient_name')
            prescription['patient_gender'] = request.form.get('patient_gender')
            prescription['patient_age'] = request.form.get('patient_age')
            prescription['prescription_date'] = request.form.get('prescription_date')
            prescription['taking_days'] = request.form.get('taking_days')
            prescription['daily_dose'] = request.form.get('daily_dose')
            # print(prescription)
            price_sum = round(get_price(herbs) * int(prescription['taking_days']),0)
            write_prescription(prescription)
    return render_template('index.html', herbs=herbs, formula_names=formula_names, prescription=prescription, price_sum = price_sum)



@app.route('/view_prescription')
def view_prescription():
    return render_template('view_prescription.html', prescriptions=prescriptions)

@app.route('/manage_herbs', methods=['GET', 'POST'])
def manage_herbs():
    herbs = read_herbs()
    if request.method == 'POST':
        # print(request.form)
        if 'add_herb' in request.form:
            new_id = str(len(herbs) + 1)
            name = request.form.get('name')
            price_per_g = request.form.get('price_per_g')
            abbreviation = get_chinese_initials(name)
            new_herb = {'id': new_id, 'name': name, 'price_per_g': price_per_g, 'key': abbreviation}
            herbs.append(new_herb)
            write_herbs(herbs)
        elif 'delete_herb' in request.form:
            herb_id = request.form.get('delete_herb')
            herbs = [herb for herb in herbs if herb['id'] != herb_id]
            write_herbs(herbs)
        elif 'edit_herb' in request.form:
            herb_id = request.form.get('edit_herb')
            name = request.form.get('edit_name')
            price_per_g = request.form.get('edit_price_per_g')
            for herb in herbs:
                if herb['id'] == herb_id:
                    herb['name'] = name
                    herb['price_per_g'] = price_per_g
                    break
            write_herbs(herbs)
    return render_template('manage_herbs.html', herbs=herbs)

@app.route('/manage_formulas')
def manage_formulas():
    return render_template('manage_formulas.html', formulas=formulas)

if __name__ == '__main__':
    # app.run()
    app.run(debug=True)
    # app.run(host='202.144.192.25', port=2223)