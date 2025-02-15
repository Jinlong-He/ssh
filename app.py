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
symptom_file = 'symptom.csv'


def get_chinese_initials(text):
    """
    获取中文文本的首字母缩写
    :param text: 中文文本
    :return: 首字母缩写
    """
    # 使用 pypinyin 库将中文转换为首字母
    initials = ''.join([p[0][0] for p in pinyin(text, style=Style.FIRST_LETTER)])
    return initials

def read_symptom():
    syms = []
    try:
        with open(symptom_file, 'r', newline='', encoding='utf-8') as file:
            # 指定 delimiter 为制表符
            reader = csv.DictReader(file)
            for row in reader:
                syms.append(row['sym'])
    except FileNotFoundError:
        pass
    return syms

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

def write_patient(info):
    try:
        fieldnames = ['patient_name', 'patient_phone', 'patient_gender', 'patient_year']
        with open('patient.csv', 'a', newline='', encoding='utf-8') as file:
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            if file.tell() == 0:
                writer.writeheader()
            writer.writerow(info)
    except FileNotFoundError:
        pass

def read_patients():
    infos = {}
    try:
        with open('patient.csv', 'r', newline='', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                infos[row['patient_phone']] = {
                    'patient_name': row['patient_name'],
                    'patient_year': row['patient_year'],
                    'patient_gender': row['patient_gender'],
                    'patient_phone': row['patient_phone'],
                }
    except FileNotFoundError:
        pass
    return infos


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

def read_prescriptions_by_date(selected_date):
    prescriptions = []
    file_path = os.path.join('prescriptions', f"{selected_date}.csv")
    try:
        with open(file_path, 'r', newline='', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                prescription = {
                    'patient_name': row['patient_name'],
                    'patient_gender': row['patient_gender'],
                    'patient_age': row['patient_age'],
                    'patient_phone': row['patient_phone'],
                    'prescription_date': row['prescription_date'],
                    'taking_days': row['taking_days'],
                    'daily_dose': row['daily_dose'],
                    'herbs': row['herbs'].split('/'),
                    'weights': row['weights'].split('/'),
                    'price_gs': row['price_gs'].split('/'),
                    'prices': row['prices'].split('/'),
                    'total_price': row['total_price'],
                    'syms': row['syms'].split('/'),
                    'other': row['other']
                }
                prescriptions.append(prescription)
    except FileNotFoundError:
        pass
    return prescriptions

def read_prescriptions_by_phone(phone):
    prescriptions = []
    file_path = os.path.join('patients', f"{phone}.csv")
    try:
        with open(file_path, 'r', newline='', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                prescription = {
                    'patient_name': row['patient_name'],
                    'patient_gender': row['patient_gender'],
                    'patient_age': row['patient_age'],
                    'patient_phone': row['patient_phone'],
                    'prescription_date': row['prescription_date'],
                    'taking_days': row['taking_days'],
                    'daily_dose': row['daily_dose'],
                    'herbs': row['herbs'].split('/'),
                    'weights': row['weights'].split('/'),
                    'price_gs': row['price_gs'].split('/'),
                    'prices': row['prices'].split('/'),
                    'total_price': row['total_price'],
                    'syms': row['syms'].split('/'),
                    'other': row['other']
                }
                prescriptions.append(prescription)
    except FileNotFoundError:
        pass
    return prescriptions

def write_prescriptions_date(prescriptions, date, mode = 'w'):
    if mode == 'w' :
        date_folder = 'prescriptions'
        file_name = os.path.join(date_folder, f"{date}.csv")
        with open(file_name, 'w', newline='', encoding='utf-8') as file:
            pass
        for prescription in prescriptions:
            write_prescription_date(prescription)

def write_prescriptions_phone(prescriptions, phone, mode = 'w'):
    if mode == 'w' :
        date_folder = 'patients'
        file_name = os.path.join(date_folder, f"{phone}.csv")
        with open(file_name, 'w', newline='', encoding='utf-8') as file:
            pass
        for prescription in prescriptions:
            write_prescription_phone(prescription)

def write_prescription_date(prescription):
    prescription_date = prescription['prescription_date']
    # 创建日期文件夹
    date_folder = 'prescriptions'
    file_name = os.path.join(date_folder, f"{prescription_date}.csv")
    fieldnames = ['patient_name', 'patient_gender', 'patient_age', 'patient_phone', 'prescription_date', 'taking_days', 'daily_dose', 'herbs', 'weights', 'price_gs', 'prices', 'total_price', 'syms', 'other']
    with open(file_name, 'a', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        if file.tell() == 0:
            writer.writeheader()
        writer.writerow({
            'patient_name': prescription['patient_name'],
            'patient_gender': prescription['patient_gender'],
            'patient_age': prescription['patient_age'],
            'patient_phone': prescription['patient_phone'],
            'prescription_date': prescription['prescription_date'],
            'taking_days': prescription['taking_days'],
            'daily_dose': prescription['daily_dose'],
            'herbs': '/'.join(prescription['herbs']),
            'weights': '/'.join(prescription['weights']),
            'price_gs': '/'.join(prescription['price_gs']),
            'prices': '/'.join(prescription['prices']),
            'total_price': prescription['total_price'],
            'syms': '/'.join(prescription['syms']),
            'other': prescription['other']
        })

def write_prescription_phone(prescription):
    fieldnames = ['patient_name', 'patient_gender', 'patient_age', 'patient_phone', 'prescription_date', 
                  'taking_days', 'daily_dose', 'herbs', 'weights', 'price_gs', 'prices', 'total_price', 'syms', 'other']
    phone = prescription['patient_phone']
    date_folder = 'patients'
    file_name = os.path.join(date_folder, f"{phone}.csv")
    with open(file_name, 'a', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        if file.tell() == 0:
            writer.writeheader()
        writer.writerow({
            'patient_name': prescription['patient_name'],
            'patient_gender': prescription['patient_gender'],
            'patient_age': prescription['patient_age'],
            'patient_phone': prescription['patient_phone'],
            'prescription_date': prescription['prescription_date'],
            'taking_days': prescription['taking_days'],
            'daily_dose': prescription['daily_dose'],
            'herbs': '/'.join(prescription['herbs']),
            'weights': '/'.join(prescription['weights']),
            'price_gs': '/'.join(prescription['price_gs']),
            'prices': '/'.join(prescription['prices']),
            'total_price': prescription['total_price'],
            'syms': '/'.join(prescription['syms']),
            'other': prescription['other']
        })

def write_prescription(prescription):
    prescription_date = prescription['prescription_date']
    # 创建日期文件夹
    date_folder = 'prescriptions'
    file_name = os.path.join(date_folder, f"{prescription_date}.csv")
    fieldnames = ['patient_name', 'patient_gender', 'patient_age', 'patient_phone', 'prescription_date', 
                  'taking_days', 'daily_dose', 'herbs', 'weights', 'price_gs', 'prices', 'total_price', 'syms', 'other']
    with open(file_name, 'a', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        if file.tell() == 0:
            writer.writeheader()
        writer.writerow({
            'patient_name': prescription['patient_name'],
            'patient_gender': prescription['patient_gender'],
            'patient_age': prescription['patient_age'],
            'patient_phone': prescription['patient_phone'],
            'prescription_date': prescription['prescription_date'],
            'taking_days': prescription['taking_days'],
            'daily_dose': prescription['daily_dose'],
            'herbs': '/'.join(prescription['herbs']),
            'weights': '/'.join(prescription['weights']),
            'price_gs': '/'.join(prescription['price_gs']),
            'prices': '/'.join(prescription['prices']),
            'total_price': prescription['total_price'],
            'syms': '/'.join(prescription['syms']),
            'other': prescription['other']
        })
    phone = prescription['patient_phone']
    date_folder = 'patients'
    file_name = os.path.join(date_folder, f"{phone}.csv")
    with open(file_name, 'a', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        if file.tell() == 0:
            writer.writeheader()
        writer.writerow({
            'patient_name': prescription['patient_name'],
            'patient_gender': prescription['patient_gender'],
            'patient_age': prescription['patient_age'],
            'patient_phone': prescription['patient_phone'],
            'prescription_date': prescription['prescription_date'],
            'taking_days': prescription['taking_days'],
            'daily_dose': prescription['daily_dose'],
            'herbs': '/'.join(prescription['herbs']),
            'weights': '/'.join(prescription['weights']),
            'price_gs': '/'.join(prescription['price_gs']),
            'prices': '/'.join(prescription['prices']),
            'total_price': prescription['total_price'],
            'syms': '/'.join(prescription['syms']),
            'other': prescription['other']
        })


def get_price(herbs):
    price_sum = 0
    for herb in herbs:
        price_sum += herb['price']
    price_sum = round(price_sum, 2)
    return price_sum


@app.route('/', methods=['GET', 'POST'])
def index():
    infos = read_patients()
    return render_template('index.html', infos=infos)

@app.route('/start', methods=['POST'])
def start():
    infos = read_patients()
    patient_info = request.get_json()
    patient_phone = patient_info['patient_phone']
    print(patient_info)
    if patient_phone not in infos:
        write_patient(patient_info)
    # 在这里可以对数据进行处理，例如保存到数据库等
    return jsonify({'message': '数据已接收'})


@app.route('/view_prescription', methods=['GET', 'POST'])
def view_prescription():
    selected_date = datetime.date.today()
    prescriptions = read_prescriptions_by_date(selected_date)
    if request.method == 'POST':
        if 'change_date' in request.form:
            selected_date = request.form.get('change_date')
            # print(date)
            prescriptions = read_prescriptions_by_date(selected_date)
        elif 'delete_pres' in request.form:
            pres_id = request.form.get('delete_pres')
            selected_date = request.form.get('date')
            prescriptions = read_prescriptions_by_date(selected_date)
            prescription = prescriptions[int(pres_id)]
            new_prescriptions = read_prescriptions_by_phone(prescription['patient_phone'])
            new_prescriptions.remove(prescription)
            prescriptions.pop(int(pres_id))
            write_prescriptions_date(prescriptions, selected_date,'w')
            write_prescriptions_phone(new_prescriptions,prescription['patient_phone'],'w')
            prescriptions = read_prescriptions_by_date(selected_date)
        elif 'edit_pres' in request.form:
            pres_id = int(request.form.get('edit_pres'))
            selected_date = request.form.get('date')
            prescriptions = read_prescriptions_by_date(selected_date)
            herbs = read_herbs_abb()
            prescription = prescriptions[pres_id]
            items = []
            syms = read_symptom()
            selected_syms = prescription['syms']
            for i in range(len(prescription['herbs'])):
                items.append({'herb': prescription['herbs'][i],
                              'weight': prescription['weights'][i],
                              'price_per_g': prescription['price_gs'][i],
                              'price': prescription['prices'][i]})
            return render_template('edit_prescription.html', prescription=prescription, herbs=herbs, items = items, syms=syms, selected_syms=selected_syms)
    return render_template('view_prescription.html', prescriptions=prescriptions, selected_date=selected_date)


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
    patient_phone = request.args.get('phone')
    infos = read_patients()
    info = infos[patient_phone]
    info['patient_age'] = int(str(datetime.date.today()).split('-')[0]) - int(info['patient_year'])
    herbs = read_herbs_abb()
    syms = read_symptom()
    today_date = datetime.date.today()
    (formula_names, formulas) = read_formulas()
    herbs_dict = read_herbs_dict()
    prescriptions = read_prescriptions_by_phone(patient_phone)
    for name in formula_names:
        formula = formulas[name]
        for item in formula:
            price_per_g = herbs_dict[item['name']]
            item['price_per_g'] = price_per_g
            item['price'] = round(float(price_per_g) * int(item['weight']), 2)
    return render_template('new_prescription.html', herbs=herbs, today_date=today_date, formula_names=formula_names, formulas=formulas, info=info, syms = syms, prescriptions = prescriptions)

@app.route('/send_prescription_table', methods=['POST'])
def send_prescription_table():
    prescription = request.get_json()
    # 在这里可以对数据进行处理，例如保存到数据库等
    tableData = prescription['tableData']
    total_price = prescription['total_price']
    patient_info = prescription['patient_info']
    syms = prescription['syms']
    other = prescription['other']
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
    prescription = {
        'patient_name': patient_info['patient_name'],
        'patient_gender': patient_info['patient_gender'],
        'patient_age': patient_info['patient_age'],
        'patient_phone': patient_info['patient_phone'],
        'prescription_date': patient_info['prescription_date'],
        'taking_days': patient_info['taking_days'],
        'daily_dose': patient_info['daily_dose'],
        'herbs': herbs,
        'weights': weights,
        'price_gs': price_gs,
        'prices': prices,
        'total_price': total_price,
        'syms': syms,
        'other': other
    }
    write_prescription(prescription)
    return jsonify({'message': '数据已接收'})

@app.route('/edit_prescription_table', methods=['POST'])
def edit_prescription_table():
    prescription = request.get_json()
    # 在这里可以对数据进行处理，例如保存到数据库等
    tableData = prescription['tableData']
    total_price = prescription['total_price']
    patient_info = prescription['patient_info']
    syms = prescription['syms']
    other = prescription['other']
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
    prescription = {
        'patient_name': patient_info['patient_name'],
        'patient_gender': patient_info['patient_gender'],
        'patient_age': patient_info['patient_age'],
        'patient_phone': patient_info['patient_phone'],
        'prescription_date': patient_info['prescription_date'],
        'taking_days': patient_info['taking_days'],
        'daily_dose': patient_info['daily_dose'],
        'herbs': herbs,
        'weights': weights,
        'price_gs': price_gs,
        'prices': prices,
        'total_price': total_price,
        'syms': syms,
        'other': other 
    }
    date = prescription['prescription_date']
    phone = prescription['patient_phone']
    prescriptions_date = read_prescriptions_by_date(date)
    prescriptions_phone = read_prescriptions_by_phone(phone)
    write_prescriptions_date(prescriptions_date, date,'w')
    write_prescriptions_phone(prescriptions_phone, phone, 'w')
    return jsonify({'message': '数据已接收'})
if __name__ == '__main__':
    # app.run()
    app.run(debug=True)
    # app.run(host='202.144.192.25', port=2223)
