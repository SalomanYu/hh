"""
Данный код будет приводить все названия резюме и названия этапов к единому виду, соответствующих значению "Вес профессии в уровне"
"""

import json
import xlrd 
import ru_core_news_md



from step_5_join_reset_steps_in_career import load_resumes_json, save_to_json, nested_tuple_to_dict


levels_dict = { # Стоит ли добавлять сюда: Владелец, Секретаря руководителя относит к 3 категории
    1: ('junior', 'помощник', 'ассистент', 'младший', 'стажёр', 'стажер', 'assistant', 'intern', 'интерн', 'начинать', 'волонтер', 'волонтёр'), # начинающий заменен на начинать с учетом лемматизации
    3: ('senior', 'руководитель', 'head of', 'портфель', 'team lead', 'управлять', 'начальник', 'директор', 'head'), # управляющий заменен на управлять с учетом лемматизации
    2: ('middle', 'заместитель', 'старший', 'lead', 'ведущий', 'главный', 'лидер')
}


def get_default_names(category):
    book_reader = xlrd.open_workbook('Excel/product_manager.xlsx')
    work_sheet = book_reader.sheet_by_index(0)
    table_titles = work_sheet.row_values(0)



    for col_num in range(len(table_titles)):
        if table_titles[col_num] == 'Наименование професии и различные написания':
            table_names_col = col_num
        
        elif table_titles[col_num] == 'Вес профессии в уровне':
            table_weight_in_level_col = col_num # 25 Включительно
        elif table_titles[col_num] == 'Уровень должности':
            table_level_col = col_num

        elif table_titles[col_num] == 'Профобласть':
            table_category_col = col_num
        
        elif table_titles[col_num] == 'Вес профессии в соответствии':
            table_weight_in_group = col_num
    
    names = []
    for row in range(work_sheet.nrows): # 
        if work_sheet.cell(row, table_category_col).value.strip() == category.strip():
            names.append(work_sheet.cell(row, table_names_col).value)

    result = {}


    for row_num in range(work_sheet.nrows): # Выбираем только менеджеров 
        if work_sheet.cell(row_num, table_category_col).value.strip() == category:
            if (work_sheet.cell(row_num, table_weight_in_level_col).value == 0) and (work_sheet.cell(row_num, table_weight_in_group).value == 1):
                result[int(work_sheet.cell(row_num, table_level_col).value)] = work_sheet.cell(row_num, table_names_col).value 
            elif work_sheet.cell(row_num, table_weight_in_level_col).value == 1:
                result[int(work_sheet.cell(row_num, table_level_col).value)] = work_sheet.cell(row_num, table_names_col).value 

    return result, names


if __name__ == "__main__":
    nlp = ru_core_news_md.load()

    data = load_resumes_json('JSON/step_3_groups_without_dublicates.json')
    resumes = list(data.items())
    dict_level_default_names, table_names = get_default_names(category='Маркетинг, реклама, PR') # Получаем словарь {уровень: наименование с весом 1 в уровне}

    # # Пишем алгоритм для тех резюме, наименования которых были взяты из таблицы "Соответствия и уровни", поэтому мы полагаемся, что в переменной data уже есть информация об уровнях
    for resume in resumes: # Цикл по всем резюмешкам
        level = resume[1][0]['level'] # Берем уровень каждого резюме
        for level_name, default_name in dict_level_default_names.items(): # Цикл по сформированному словарю со стандартными названиями уровней
            if level == level_name: # Сравниваем уровень резюме с ключами списка
                for item in resume[1]: # Цикл по всем этапам резюме (Здесь мы меняем название резюме в каждом этапе + меняем название этапа, содержащего ключевое слово из       словаря с ключевыми словами для каждого уровня)
                    for table_name in table_names:
                        if table_name.strip().lower() in item['name_of_profession'].strip().lower():
                            item['name_of_profession'] = default_name # Меняем название резюме
                            job_steps = resume[1] # Все этапы в резюме
                            for step in job_steps:
                                for level_keyword in levels_dict: # Цикл по всем ключам словаря ключевых слов
                                    for keyword in levels_dict[level_keyword]: # Цикл по всем ключевым словам определенного уровня
                                        if (keyword in step['experience_post'].lower()):
                                            doc_table_name = nlp(table_name.strip().lower())
                                            lemma_table_name = " ".join([token.lemma_ for token in doc_table_name])
                                            
                                            doc_step_post = nlp(step['experience_post'].strip().lower())
                                            lemma_step_post = " ".join([token.lemma_ for token in doc_step_post])
                                            if lemma_table_name in lemma_step_post or keyword == step['experience_post'].lower():
                                                print(step['experience_post'])
                                                step['experience_post'] = dict_level_default_names[level_keyword] # Меняем название этапа
    
    save_to_json(nested_tuple_to_dict(resumes), 'step_4_groups_with_default_names')

         
