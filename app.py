import csv, os, sys, io, _json
from flask import Flask, render_template, request, redirect, url_for, jsonify
from pypinyin import pinyin, Style
import datetime
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')


app = Flask(__name__)

# 模拟数据存储
prescriptions = []
formulas = []
herbs_file = 'herbs.csv'


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
            reader = csv.DictReader(file)
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
            reader = csv.DictReader(file)
            for row in reader:
                herbs[row['name']] = row['price_per_g']
    except FileNotFoundError:
        pass
    return herbs


def read_herbs_abb():
    herbs = {}
    try:
        with open('herbs.csv', 'r', newline='', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                herbs[row['key']] = {
                    'name': row['name'],
                    'price_per_g': float(row['price_per_g'])
                }
    except FileNotFoundError:
        pass
    return herbs


# 写入药材数据到 CSV 文件
def write_herbs(herbs):
    fieldnames = ['id', 'name', 'price_per_g', 'key']
    with open(herbs_file, 'w', newline='', encoding='utf-8') as file:
        # 指定 delimiter 为制表符
        writer = csv.DictWriter(file, fieldnames=fieldnames)
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
        reader = csv.DictReader(file)
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
    return formula_names, formulas


def read_formula(formula_file):
    formula = []
    try:
        with open(formula_file, 'r', newline='', encoding='utf-8') as file:
            # 指定 delimiter 为制表符
            reader = csv.DictReader(file)
            for row in reader:
                formula.append(row)
    except FileNotFoundError:
        pass
    return formula


def read_prescription(prescription_file):
    prescription = []
    try:
        if isinstance(prescription_file, str):
            with open(prescription_file, 'r', newline='', encoding='utf-8') as file:
                # 指定 delimiter 为制表符
                reader = csv.DictReader(file)
                for row in reader:
                    prescription.append(row)
        else:
            reader = csv.DictReader(prescription_file)
            for row in reader:
                prescription.append(row)
    except FileNotFoundError:
        pass
    return prescription


def write_prescription(prescription):
    tableData = prescription['tableData']
    total_price = prescription['total_price']
    patient_info = prescription['patient_info']
    prescription_date = patient_info['prescription_date']
    # 创建日期文件夹
    date_folder = 'prescriptions'
    # date_folder = os.path.join('prescriptions', str(prescription_date))
    # os.makedirs(date_folder, exist_ok=True)
    file_name = os.path.join(date_folder, f"{prescription_date}.csv")
    fieldnames = ['patient_name', 'patient_gender', 'patient_age', 'prescription_date', 
                  'taking_days', 'daily_dose', 'herbs', 'weights', 'price_gs', 'prices', 'total_price']
    herbs = []
    weights = []
    price_gs = []
    prices = []
    for item in tableData:
        if item['herbName'] != '':
            herbs.append(item['herbName'])
            weights.append(item['weight'])
            price_gs.append(item['price'])
            prices.append(item['total'])
    with open(file_name, 'a', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        if file.tell() == 0:
            writer.writeheader()
        writer.writerow({
            'patient_name': patient_info['patient_name'],
            'patient_gender': patient_info['patient_gender'],
            'patient_age': patient_info['patient_age'],
            'prescription_date': patient_info['prescription_date'],
            # 'formula_template': patient_info['formula_template'],
            'taking_days': patient_info['taking_days'],
            'daily_dose': patient_info['daily_dose'],
            'herbs': '/'.join(herbs),
            'weights': '/'.join(weights),
            'price_gs': '/'.join(price_gs),
            'prices': '/'.join(prices),
            'total_price': total_price
        })


def get_price(herbs):
    price_sum = 0
    for herb in herbs:
        price_sum += herb['price']
    price_sum = round(price_sum, 2)
    return price_sum


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
                if int(herb['id']) > int(herb_id):
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
            if name in herbs_dict:
                price_per_g = herbs_dict[name]
                price = round(float(price_per_g) * int(weight), 2)
                new_herb = {'id': new_id, 'name': name, 'weight': weight, 'price_per_g': price_per_g, 'price': price}
                herbs.append(new_herb)
        # prescription['herbs'] = herbs
        price_sum = get_price(herbs)
        if 'new_prescription' in request.form:
            pass
            # prescription['patient_name'] = request.form.get('patient_name')
            # prescription['patient_gender'] = request.form.get('patient_gender')
            # prescription['patient_age'] = request.form.get('patient_age')
            # prescription['prescription_date'] = request.form.get('prescription_date')
            # prescription['taking_days'] = request.form.get('taking_days')
            # prescription['daily_dose'] = request.form.get('daily_dose')
            # # print(prescription)
            # price_sum = round(get_price(herbs) * int(prescription['taking_days']), 0)
            # write_prescription(prescription)
    return render_template('index.html', herbs=herbs, formula_names=formula_names, prescription=prescription,
                           price_sum=price_sum)


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


@app.route('/new_prescription', methods=['GET', 'POST'])
def new_prescription():
    herbs = read_herbs_abb()
    today_date = datetime.date.today()
    (formula_names, formulas) = read_formulas()
    herbs_dict = read_herbs_dict()
    for name in formula_names:
        formula = formulas[name]
        for item in formula:
            price_per_g = herbs_dict[item['name']]
            item['price_per_g'] = price_per_g
            item['price'] = round(float(price_per_g) * int(item['weight']), 2)
    if request.method == 'POST':
        if 'save-prescription' in request.form:
            print(request.form)
            # 获取表单数据
            # patient_name = request.form.get('patient_name')
            # patient_gender = request.form.get('patient_gender')
            # patient_age = request.form.get('patient_age')
            # prescription_date = request.form.get('prescription_date')
            # taking_days = request.form.get('prescription_pay_count')
            # daily_dose = request.form.get('prescription_dose_count')

            # 更新 prescription 字典
            # prescription.update({
            #     'patient_name': patient_name,
            #     'patient_gender': patient_gender,
            #     'patient_age': patient_age,
            #     'prescription_date': prescription_date,
            #     'taking_days': taking_days,
            #     'daily_dose': daily_dose
            #     # 'herbs': herbs
            # })

            # 保存药方信息
            # print(prescription)
        # write_prescription(prescription)

        # 重定向到查看药方页面或其他合适页面
        return redirect(url_for('view_prescription'))

    return render_template('new_prescription.html', herbs=herbs, today_date=today_date, formula_names=formula_names, formulas=formulas)

@app.route('/send_prescription_table', methods=['POST'])
def send_prescription_table():
    prescription = request.get_json()
    # 在这里可以对数据进行处理，例如保存到数据库等
    print('接收到的数据:', prescription)
    write_prescription(prescription)
    return jsonify({'message': '数据已接收'})

if __name__ == '__main__':
    # app.run()
    app.run(debug=True)
    # app.run(host='202.144.192.25', port=2223)
