"""
В данном модуле мы занимаемся объединением дубликатов.
"""

import json
from sys import platform

if platform == 'win32':
    import ctypes
    kernel32 = ctypes.windll.kernel32
    kernel32.SetConsoleMode(kernel32.GetStdHandle(-11), 7)



SUCCESS_MESSAGE = '\033[2;30;42m [SUCCESS] \033[0;0m' 
INFO_MESSAGE = '\033[2;30;46m [ INFO  ] \033[0;0m'
WARNING_MESSAGE = '\033[2;30;43m [WARNING] \033[0;0m'
ERROR_MESSAGE = '\033[2;30;41m [ ERROR ] \033[0;0m'


def load_resumes_json(path):
    file = open(path)
    data = json.load(file)
    file.close()

    print(SUCCESS_MESSAGE + f'\tПрочитали данные с файла.')
    return data


def filtering_groups(data) -> tuple:
    """
        This method будет искать индентичные группы. Путем сравнения двух резюме, мы будем узнавать уровень схожести двух резюме
    В основе лежит цикл - один ко многим, в котором мы пытаемся набрать необходимое количество очков для того,
    чтобы понять насколько резюме похожи.
    Если мы наберем максимальное количество очков(4), то мы можем сделать вывод, что резюме одинаковые. Следовательно, одно из них
    мы добавим в список дубликатов.
    
        В качестве аутпута выдаем кортеж - измененный массив данных в формате кортеж с кортежами  и так же выдаем список дубликатов
    для последуюшего удаления
    """

    groups = tuple(data.items()) # переводим словарь в кортеж с кортежами для удобной работы
    dublicate_list = [] # Инициализация переменной, которая будет хранить дубликаты

    print(INFO_MESSAGE + f'\tЗапускаем цикл поиска дубликатов.')
    for current_index in range(len(groups)):
        # В основе сравнения лежит метод - один ко многим. То есть берем по порядку группу и сраниваем ее со всеми остальными
        # Инициализация переменных, с которыми мы будем сравнивать такие же переменные из другой группы
        current_resume_name = groups[current_index][1][0]['name_of_profession']
        current_group_experience = groups[current_index][1][0]['general_experience']
        current_job_steps_count = len(groups[current_index][1])
        current_salary = groups[current_index][1][0]['salary']
        current_languages = groups[current_index][1][0]['languages']
        current_skills = groups[current_index][1][0]['skills']

        # education_block 
        current_univer_name = groups[current_index][1][0]['higher_education_university']
        current_univer_direction = groups[current_index][1][0]['higher_education_direction']
        current_univer_year = groups[current_index][1][0]['higher_education_year']

        for comporable_index in range(current_index+1, len(groups)):
            # Переменная отвечающая за степень схожести групп
            similar_count = 0

            # Инициализация как раз тех переменных, с которыми проводится сравнение
            comporable_resume_name = groups[comporable_index][1][0]['name_of_profession']    
            comporable_group_experience = groups[comporable_index][1][0]['general_experience']
            comporable_job_steps_count = len(groups[comporable_index][1])

            if current_resume_name == comporable_resume_name:
                similar_count += 1
            if current_group_experience == comporable_group_experience:
                similar_count += 1
            if current_job_steps_count == comporable_job_steps_count:
                similar_count += 1
                steps_similart_count = 0 # Считает количество совпадений в этапах

                current_steps = groups[current_index][1]
                comporable_steps = groups[comporable_index][1]

                for step in range(current_job_steps_count):                    
                    if current_steps[step]['experience_post'] == comporable_steps[step]['experience_post']:
                        if current_steps[step]['experience_duration'] == comporable_steps[step]['experience_duration']:
                            if current_steps[step]['experience_interval'] == comporable_steps[step]['experience_interval']:
                                steps_similart_count += 1
                if steps_similart_count == current_job_steps_count:
                    similar_count += 1

            # Что мы делаем, когда находим дубликаты
            if similar_count == 4 or (similar_count == 3 and current_resume_name != comporable_resume_name):
                print(WARNING_MESSAGE + f'\tНашли дубликат.')
                print(INFO_MESSAGE + f'\tСсылки на резюме:')
                print(INFO_MESSAGE + f'\t1. {groups[current_index][0]}:')
                print(INFO_MESSAGE + f'\t2. {groups[comporable_index][0]}:')

                for elem in groups[comporable_index][1]:
                    comporable_salary = elem['salary']
                    comporable_languages = elem['languages']
                    comporable_skills = elem['skills']

                    comporable_univer_name = elem['higher_education_university']
                    comporable_univer_direction = elem['higher_education_direction']
                    comporable_univer_year = elem['higher_education_year']
                    
                    # Если инфа у сравняемых резюме разная и во втором есть какие то пропуски, которых нет в первом. То заполняем второе
                    # резюме и оставляем его в качестве основного. Первое же просто удаляем, как дубликат
                    if (current_salary != comporable_salary) and (comporable_salary == ''):
                        elem['salary'] = current_salary
                    if (current_languages != comporable_languages) and (comporable_languages == ''):
                        elem['languages'] = current_languages
                    if (current_skills != comporable_skills) and (comporable_skills == ''):
                        elem['skills'] = current_skills
                    if (current_univer_name != comporable_univer_name) and (comporable_univer_name == ''):
                        elem['higher_education_university'] = current_univer_name
                    if (current_univer_direction != comporable_univer_direction) and (comporable_univer_direction == ''):
                        elem['higher_education_direction'] = current_univer_direction
                    if (current_univer_year != comporable_univer_year) and (comporable_univer_year == ''):
                        elem['higher_education_year'] = current_univer_year
                
                dublicate_list.append(groups[current_index][0]) # Раз у нас есть 4 совпадения, значит вакансии индентичны и первую мы удаляем
    return groups, dublicate_list

def nested_tuple_to_dict(nested_tuple:tuple) -> dict: # Вложенный кортеж в словарь
    """Метод нужен, чтобы вернуть наши данные к исходному виду"""
    result = {}
    for resume in nested_tuple:
        # Добавляем в словарь значение, в котором ключом будет являться user_id(url) резюме, а value ключа будет список всех этапов работы
        result[resume[0]] = resume[1] 
    
    return result

def remove_dublicates(data, list_to_delete) -> dict:
    if list_to_delete == []:
        print(WARNING_MESSAGE + '\tДубликаты не найдены.')
    else:
        print(WARNING_MESSAGE + f'\tНайдено {len(list_to_delete)} дубликата')
    
    for item in list_to_delete:
        if item in data:
            del data[item]
    
    return data
    
def save_to_json(data:dict, filename:str) -> None:
    # Write filename without .json

    with open(f'JSON/{filename}.json', 'w') as file:
        json.dump(data, file, ensure_ascii=False, indent=2)
    
    print(SUCCESS_MESSAGE + f'\tСохранили отредактированный файл: {filename}')



if __name__ == "__main__":

    data = load_resumes_json('JSON/step_2_groups_result.json')
    groups, dublicate_list = filtering_groups(data)
    retransled_dict = nested_tuple_to_dict(nested_tuple=groups)

    data_without_dublicates = remove_dublicates(data=retransled_dict, list_to_delete=dublicate_list)
    save_to_json(data_without_dublicates, 'step_3_groups_without_dublicates')
