import pandas as pd
import os


def merge_files(path):
    folders = os.listdir(path)  
    df = pd.DataFrame()

    for folder in folders:
        for file in os.listdir(os.path.join(path, folder)):
            if file.endswith('.csv'):
                df = df.append(pd.read_csv(f'{path}/{folder}/{file}'), ignore_index=True) 
        print('Прочитали папку ', folder)


    df.head() 
    df.to_csv('Total_excel.csv')
    print('Все excel-файлы были собраны в один Total_Excel.csv')


merge_files('/home/saloman/Excel')