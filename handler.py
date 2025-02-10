import loader
import os, pandas, sys, random
import matplotlib.pyplot as plt
import matplotlib
import numpy as np
matplotlib.use('agg')
plt.rcParams["font.sans-serif"]=["Songti SC"] #设置字体
plt.rcParams["axes.unicode_minus"]=False


(units, units_b, quotas, quotas_b, quotas_n) = loader.load_config()
seasons = ['1-3', '4-6', '7-9', '10-12']
year_quotas = [9, 10, 12, 27, 32, 33, 34]
anti_quotas = [7, 8, 11, 22, 23, 24, 25, 26]
data_path = os.path.join(os.getcwd(), 'datas')
fig_path = os.path.join(os.getcwd(), 'figure')
def init() :
    for unit_name in units :
        file_name = unit_name + '.xlsx'
        file_path = os.path.join(data_path, file_name)
        if not os.path.exists(file_path) :
            ids = []
            id = 0
            for q in quotas :
                ids.append(str(id))
                id += 1
            data = { 'id' : ids, 'quota' : quotas }
            df = pandas.DataFrame(data)
            for year in [2023, 2024, 2025, 2026, 2027] :
                for season in seasons :
                    df[str(year) + '@' + season] = ['NA']*35
            df.to_excel(file_path, index=False)

def import_data(dir, year, season, force = False) :
    for file_name in os.listdir(dir) :
        if 'xlsx' not in file_name :
            continue
        file_path = os.path.join(dir, file_name)
        (unit_name, y, s, datas) = loader.load_excel(file_path)
        excel_path = os.path.join(data_path, unit_name + '.xlsx')
        df = pandas.read_excel(excel_path)
        quotas = []
        for (quota_name, quota) in datas :
            quotas.append(quota)
        if year + '@' + season not in df or force:
            df[year + '@' + season] = quotas
            pandas.DataFrame(df).to_excel(excel_path, sheet_name='Sheet1', index=False, header=True)
        else :
            return False
    return True

def generate_test_datas() :
    year = '2023'
    for season in ['1-3','4-6','7-9','10-12'] :
        dir = year + '_' + season
        if not os.path.exists(os.path.join('test', dir)) :
            os.system('cd test && mkdir ' + dir)
        for unit in units :
            excel_path = os.path.join('test', dir, unit+'.xlsx')
            os.system('cp temp.xlsx ' + excel_path)
            df = pandas.read_excel(excel_path)
            df.iloc[1,1] = unit
            # df.iloc[6,'b'] = 77777
            for row in range(4, 39) :
                df.iloc[row, 1] = random.random()*100
            pandas.DataFrame(df).to_excel(excel_path, sheet_name='Sheet1', index=False, header=True)

def export_figure(year) :
    datas = {}
    all_datas = {}
    latex_datas = {}
    for i in range(len(quotas)) :
        datas[i] = {}
        all_datas[i] = []
        latex_datas[i] = []
    for unit in units :
    # for file_name in os.listdir(data_path) :
        file_name = unit + '.xlsx'
        # print(file_name)
        file_path = os.path.join(data_path, file_name)
        # unit_name = file_name.split('.')[0]
        df = pandas.read_excel(file_path)
        # print(df)
        # df.plot()
        for i in range(len(df)) :
            row = df.loc[i][1:]
            data = 0
            latex_data = []
            # new_datas = []
            for season in seasons :
                ys = str(year) + '@' + season
                ys_str = (str(year) + '年' + season + '月')
                if str(row[ys]) != 'nan' :
                    if i not in year_quotas or season == '1-3':
                        data += row[ys]
                        latex_data.append(round(row[ys], 2))
                        # new_datas.append(row[ys])
                        if ys_str not in datas[i] :
                            datas[i][ys_str] = [row[ys]]
                        else :
                            datas[i][ys_str].append(row[ys])
            # all_datas[i].append((data, unit, new_datas))
            latex_datas[i].append((unit, latex_data))
            all_datas[i].append((data, unit))
    n = len(datas[0])
    latex = '\\documentclass[aspectratio=169]{beamer}\n'
    latex += '\\usepackage{amsfonts,amsmath,oldgerm}\n'
    latex += '\\usepackage{ctex}\n'
    latex += '\\usepackage{tabularx}\n'
    latex += '\\title{报告标题}\n'
    latex += '\\author{作者1、作者2}\n'
    latex += '\\begin{document}\n'
    latex += '\\maketitle\n'
    for i in range(len(quotas)) :
        quota = quotas[i]
        if i not in year_quotas :
            x = np.arange(0, len(units)*n, n)
            width=0.5
            j = 0
            # plt.figure(figsize=(7,10))
            plt.figure(figsize=(10,8))
            plt.title(quota)
            plt.subplots_adjust(bottom=0.3)
            plt.grid(axis='y', zorder=0)
            for (ys, data) in datas[i].items() :
                # plt.bar(units, data, label=ys)
                plt.bar(x+j*width, data, width=width, label=ys, zorder=10)
                j += 1
            plt.xticks(x,units,fontsize=10, rotation=270)
            plt.tick_params(axis='x',length=0)
            plt.legend()
            pdf_path = os.path.join(fig_path, '%s.pdf'%quota)
            plt.savefig(pdf_path)
            plt.clf()
            latex += generate_latex(latex_datas[i], quota, 'season', pdf_path)
            # plt.show()
            # break
        continue
        break
        new_units = []
        new_datas = []
        if i in anti_quotas :
            data = sorted(all_datas[i], key = lambda x : x[0], reverse=False)
        else :
            data = sorted(all_datas[i], key = lambda x : x[0], reverse=True)
        for d, u in data :
            new_datas.append(d)
            new_units.append(u)
        plt.title(quota)
        plt.grid(axis='y', zorder=0)
        plt.bar(new_units, new_datas, zorder=10)
        plt.xticks(fontsize=10, rotation=270)
        plt.savefig(os.path.join(fig_path, '%s_年度.pdf'%quota))
        plt.clf()
            # plt.show()
    latex += '\\end{document}\n'
    f = open('temp.tex', 'w')
    f.write(latex)
    f.close()
        

def generate_latex(datas, quota, type, pdf_name) :
    note = quotas_n[quota]
    size = len(datas[0][1])
    latex = '\\begin{frame}\n'
    latex += '\\begin{columns}\n'
    latex += '\\begin{column}{.4\\linewidth}\n'
    latex += '\\begin{table}[htb]\\tiny\n'
    latex += '\\centering\n'
    # latex += '\\begin{tabular} {' + (size + 2) * '| c ' + ' |}\n'
    latex += '\\begin{tabular} { | m{0.2cm}<{\centering} | m{2.8cm}<{\centering} ' + (size) * '| m{0.65cm}<{\centering} ' + ' |}\n'
    # | m{0.15cm}<{\centering} | m{2.35cm}<{\centering} | m{0.65cm}<{\centering} | m{0.65cm}<{\centering}  |
    latex += '\\hline \\multicolumn{%s}{| p{%scm}<{\centering} |}{\\textbf{%s$\\blacktriangle$}}\\\\\n'%(size+2, str(4.2+size*0.65), quota[:-1])
    # latex += '\\multicolumn{%s}{| p{%scm}<{\centering} |}{\\textbf{%s}}\\\\\n'%(size + 2, str(4.2+size*0.65), note)
    if type == 'year' :
        latex += '\\hline   \\textbf{序号} & \\textbf{机构} & \\textbf{医院值} \\\\ \n'
    else :
        if size == 1 :
            latex += '\\hline   \\textbf{序号} & \\textbf{机构} & \\textbf{1季度} \\\\ \n'
        if size == 2 :
            latex += '\\hline   \\textbf{序号} & \\textbf{机构} & \\textbf{1季度} & \\textbf{2季度} \\\\ \n'
        if size == 3 :
            latex += '\\hline   \\textbf{序号} & \\textbf{机构} & \\textbf{1季度} & \\textbf{2季度} & \\textbf{3季度} \\\\ \n'
        if size == 4 :
            latex += '\\hline   \\textbf{序号} & \\textbf{机构} & \\textbf{1季度} & \\textbf{2季度} & \\textbf{3季度} & \\textbf{4季度} \\\\ \n'
    id = 1
    for unit, data in datas :
        latex += '\\hline %s & %s'%(str(id), unit)
        for d in data :
            latex += '& %s'%(str(d))
        latex += '\\\\\n'
        id += 1
    latex += '\\hline\n'
    latex += '\\end{tabular}\n'
    latex += '\\end{table}\n'
    latex += '\\end{column}\n'
    latex += '\\begin{column}{.6\\linewidth}\n'
    latex += '\\begin{figure}[H]\n'
    latex += '\\includegraphics[width=1.1\\textwidth]{%s}\n'%(pdf_name)
    latex += '\\end{figure}\n'
    latex += '\\end{column}\n'
    latex += '\\end{columns}\n'
    latex += '\\end{frame}\n'
    return(latex)

# generate_latex([('阜新蒙古族自治县蒙医医',[11,11]),('沈阳市中西医结合医院(沈阳市第七人民医院）',[22,11])], '1.门诊中药处方比例▲', 'season', '1')

export_figure(2023)
# generate_test_datas()
# print(import_data('/Users/hejl/Projects/ssy/NTPTCMH/test/2023_1-3', '2023', '1-3', 1))
# init()