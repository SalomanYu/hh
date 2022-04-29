from hh_parser import ERROR_MESSAGE, WARNING_MESSAGE, SUCCESS_MESSAGE, Resume

from multiprocessing import Pool
from time import sleep

import requests
from bs4 import BeautifulSoup

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

import xlrd

class ProffecionParser(Resume):
    def __init__(self, proffecion_name:str, proffecion_level:int, proffecion_weight_in_level:int, proffecion_weight_in_group:int):
        
        super().__init__()
        self.proffection_name = proffecion_name
        self.proffecion_weight_in_group = proffecion_weight_in_group
        self.proffecion_weight_in_level = proffecion_weight_in_level
        self.proffecion_level = proffecion_level

        self.address = '' # категория
        self.name_db_table = 'resumes'
        self.name_database = 'Middle_fresh'
        # if detect(self.proffection_name) == 'ru':
        #     self.nlp = ru_core_news_lg.load()
        # else:
        #     self.nlp = en_core_web_lg.load()

        # self.doc1 = self.nlp(self.proffection_name)
    
    def start(self):

        self.create_table(self.name_db_table)
        # for self.city in self.cities:
            # print(self.proffection_name, self.city)

            # self.domain = f'https://{self.city}.hh.ru/search/resume'
        self.domain = 'https://hh.ru/search/resume'
        self.search(self.domain)
        # self.search('https://voronezh.hh.ru/search/resume')

    def search(self, url):
        options = Options()
        options.add_argument("--headless") # ФОНОВЫЙ РЕЖИМ
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')

        browser = webdriver.Chrome(options=options)
        browser.get(url)
        browser.implicitly_wait(5)


        search_input = browser.find_element(By.XPATH, "//input[@id='a11y-search-input']")
        search_input.click()
        search_input.send_keys(self.proffection_name)
        search_input.send_keys(Keys.ENTER)
        browser.implicitly_wait(2)
        
        search_result_url = browser.current_url
        browser.quit()
        page = 0
        while True:
            print('Страница ', page)
            if self.parser_resume_list(search_result_url + f"&page={page}"):            
                page += 1
            elif self.parser_resume_list(search_result_url + f"?page={page}"):
                page += 1
            else:
                print('yo')
                return False
    
    def find_required_resumes(self, url):
        try:
            req = requests.get(url, headers=self.headers)
            soup = BeautifulSoup(req.text, 'lxml')
            all_resumes = soup.find_all('a', class_='resume-search-item__name')
            resume_urls_list = []
            for item in all_resumes:
                if item.text.lower() == self.proffection_name.lower():
                    resume_urls_list.append(f"https://hh.ru{item['href']}")

                # doc2 = self.nlp(item.text)
                # similarity = self.doc1.similarity(doc2) * 100 
                # if similarity >= 91:
                #     # resume_urls_list.append(f"https://{self.city}.hh.ru{item['href']}")
                #     resume_urls_list.append(f"https://hh.ru{item['href']}")
                #     print(SUCCESS_MESSAGE+ f'{item.text}---{similarity}---{self.proffection_name}')

                # else:
                #     print(ERROR_MESSAGE+ f'{item.text}---{similarity}---{self.proffection_name}')
            
        except requests.exceptions.ConnectionError:
            resume_urls_list = []
            all_resumes = []
            print(ERROR_MESSAGE+'\tНе удалось подключиться к сети...')
            print(WARNING_MESSAGE+'\tПродолжим работу через минуту...')
            sleep(60)

        finally:
            return resume_urls_list, len(all_resumes)


    def parser_resume_list(self, url):
        print(url)
        resume_urls_list, count_resumes_in_page = self.find_required_resumes(url)
        with Pool(4) as process:
                process.map_async(self.parse_resume, resume_urls_list, callback=self.data_resume_list, error_callback=lambda x:print(f'Thread error --> {x}'))
                process.close()
                process.join()
        if len(resume_urls_list) > 0 or count_resumes_in_page > 0:
            return True
        else:
            return False
        # print([item.text for item in all_resumes])


    def get_city(self, soup):
        city = soup.find('span', attrs={"data-qa": 'resume-personal-address'})
        
        return city.text
    
    def collect_all_resume_info(self, soup, url):
        """
        Метод собирает все методы парсера в один массив данных
        """

        work_periods, experience = self.get_experience(soup, url)
        specializations,  education_name, education_direction, education_year = self.get_education_info(soup)
        training_name, training_direction, training_year = self.get_training(soup) 
        languages = self.get_languages(soup)
        self.salary = self.get_salary(soup)
        key_skills = self.get_skills(soup)
        city = self.get_city(soup)
        title = self.get_title(soup)
        print(SUCCESS_MESSAGE + f"\t{title}")    
                
        if work_periods != []:
            res = []
            for item in work_periods: # Пробегаемся по количеству мест работы 
                data = (
                        # self.group_id,
                        self.proffecion_weight_in_group,
                        self.proffecion_level,
                        self.proffecion_weight_in_level,
                        title,
                        self.address,
                        city,
                        experience,
                        specializations,
                        self.salary,
                        education_name, 
                        education_direction,
                        education_year,
                        languages,
                        key_skills,
                        training_name,
                        training_direction,
                        training_year,
                        item['Отрасль'],
                        item['Подотрасль'],
                        item['Промежуток'],
                        item['Продолжительность'],
                        item['Должность'],
                        url
                )
                
                res.append(data)
            return res 
        else: # Вариант, когда нет опыта работы
            data = (
                    # self.group_id,
                    self.proffecion_weight_in_group,
                    self.proffecion_level,
                    self.proffecion_weight_in_level,
                    title,
                    self.address,
                    city, 
                    experience,
                    specializations,
                    self.salary,
                    education_name, 
                    education_direction,
                    education_year,
                    languages,
                    key_skills,
                    training_name,
                    training_direction,
                    training_year,
                    '',
                    '',
                    '',
                    '',
                    '',
                    url
            )
            return data
    
    def create_table(self, name):
        cursor, db = self.connect_to_db(self.name_database)

        pattern = f"""
            CREATE TABLE IF NOT EXISTS {name}(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                weight_in_group INT,
                level INT,
                level_in_group INT,
                name_of_profession VARCHAR(255),
                category_resume VARCHAR (50),
                city VARCHAR(50),
                general_experience VARCHAR(50),
                specialization VARCHAR(255),
                salary VARCHAR(50),
                higher_education_university TEXT,
                higher_education_direction TEXT,
                higher_education_year VARCHAR(100),
                languages VARCHAR(255),
                skills TEXT,
                advanced_training_name TEXT,
                advanced_training_direction TEXT,
                advanced_training_year VARCHAR(100),
                branch VARCHAR(255),
                subbranch VARCHAR(255),
                experience_interval VARCHAR(50),
                experience_duration VARCHAR(50),
                experience_post VARCHAR(255),
                url VARCHAR(255)
                );
            """
        cursor.execute(pattern)
        db.commit()
        db.close()


    def add_to_table(self, name, data,many_rows=False):

        cursor, db = self.connect_to_db(self.name_database)

        pattern = f"INSERT INTO {name}(weight_in_group, level, level_in_group, name_of_profession, category_resume, city, general_experience, specialization, salary, higher_education_university,"\
            "higher_education_direction, higher_education_year, languages, skills, advanced_training_name, advanced_training_direction," \
            f"advanced_training_year, branch, subbranch, experience_interval, experience_duration, experience_post, url) VALUES({','.join('?' for i in range(23))})"

        if many_rows:
            # Результат выполнения команды в скобках VALUES превратится в VALUES(?,?,?, ?n), n = len(data) 
            cursor.executemany(pattern, data)
        else:
            # pattern = f"INSERT INTO {name} VALUES({','.join('?' for i in range(20))})"
            cursor.execute(pattern, data)
 
        db.commit()
        db.close()


def connect_to_excel() -> tuple:
    book_reader = xlrd.open_workbook('Excel/product_manager.xlsx')
    work_sheet = book_reader.sheet_by_index(0)
    table_titles = work_sheet.row_values(0)

    for col_num in range(len(table_titles)):
        
        if table_titles[col_num] == 'Наименование професии и различные написания':
            table_names = work_sheet.col_values(col_num)[1:25]
        
        elif table_titles[col_num] == 'Вес профессии в уровне':
            table_weight_in_level = work_sheet.col_values(col_num)[1:25] # 25 Включительно
        
        elif table_titles[col_num] == 'Уровень должности':
            table_level = work_sheet.col_values(col_num)[1:25]
        
        elif table_titles[col_num] == 'Вес профессии в соответсвии':
            table_weight_in_group = work_sheet.col_values(col_num)[1:25]

    return table_names, table_weight_in_level, table_weight_in_group, table_level

if __name__ == "__main__":
    table_names, table_weight_in_level, table_weight_in_group, table_level = connect_to_excel()
    for item in range(21, len(table_names)):
        print(table_names[item])
        proffecion = ProffecionParser(proffecion_name=table_names[item], proffecion_level=table_level[item],
                    proffecion_weight_in_group=table_weight_in_group[item], proffecion_weight_in_level=table_weight_in_level[item])

        proffecion.start()
