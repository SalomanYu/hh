from multiprocessing import Pool
from datetime import date
import re, os, time
import sqlite3

from bs4 import  BeautifulSoup
import requests 


from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options

from required_variables import hh_variables

SUCCESS_MESSAGE = '\033[2;30;42m [SUCCESS] \033[0;0m' 
WARNING_MESSAGE = '\033[2;30;43m [WARNING] \033[0;0m'
ERROR_MESSAGE = '\033[2;30;41m [ ERROR ] \033[0;0m'


class Resume:
    def __init__(self):
        self.name_database = hh_variables['name_database']
        self.cities = hh_variables['cities']
        self.parcing_urls = hh_variables['parsing_urls']
        self.headers = hh_variables['headers']

    def start(self):

        """
        Основная функция, которая осуществляет переход по всем городам и категориям
        """
        self.name_db_table = 'Resumes'
        self.create_table(self.name_db_table)

        for self.city in self.cities: # Отбираем каждый город из списка по отдельности
            
            for self.address in self.parcing_urls: # Запускаем цикл по отфильтрованным по ссылкам категории
                print("\n",SUCCESS_MESSAGE+f'\t{self.city}-{self.address}\n') # Принт просто для того, чтобы понимать с какой категорией сейчас работаем
                # Этот цикл отвечает за перелистывание страниц
                # time_now = datetime.now().strftime("%H:%M:%S")
                url = f'https://{self.city}.hh.ru' + self.parcing_urls[self.address] 
                for page_num in range(250): # 250
                    self.page_url = f"{url}&page={page_num}"
                    self.parser_resume_list(self.page_url)
                
            

    def parser_resume_list(self, url):
        
        """
        Функция, запускающая многопоточность
        """
        try:
            print('Собираем список резюме...')
            req = requests.get(url, headers=self.headers) # открываем страницу со списком резюме
            soup = BeautifulSoup(req.text, 'lxml')

            resume_urls_list = [f"https://{self.city}.hh.ru{item['href']}" for item in soup.find_all('a', class_='resume-search-item__name')] # Создаем список ссылок всех резюме        
            print('Запускаем многопоточность...')
            with Pool(4) as process:
                process.map_async(self.parse_resume, resume_urls_list, callback=self.data_resume_list, error_callback=lambda x:print(f'Thread error --> {x}'))
                process.close()
                process.join()
            return resume_urls_list
        except requests.exceptions.ConnectionError:
            print(ERROR_MESSAGE+'\tНе удалось подключиться к сети...')
            print(WARNING_MESSAGE+'\tПродолжим работу через минуту...')
            time.sleep(60)
        
        # Эта строчка просто для тестирования, чтобы после выполнения правильность заполнения таблицы
    
    def data_resume_list(self, response):

        """
        Функция, срабатывающая после завершения многопоточного парсинга. Она будет записывать спарсенные данные в таблицы
        """

        # Создаем sql-таблицу для каждой категории
        # self.database = SQL(self.name_database)
        print('Завершение работы многопоточности...')
        for row in response:
            try:
                if type(row[0]) == tuple: # Условие необходимо для резюме, у которых несколько мест работы. Поэтому они возвращают список с кортежами строк для записи в БД 
                    self.add_to_table(self.name_db_table, row, many_rows=True)
                    print('Записали в таблицу инфу о списке резюме')
                else: # Здесь строки записываются по одному
                    self.add_to_table(self.name_db_table, row)
            except BaseException as error:
                print(ERROR_MESSAGE+'\tчет не получилось записать ', error)
                break
        return 
        
    def parse_resume(self, url):

        """
        Функция запускает методы парсинга отдельных блоков резюме и передает результат в виде списка или списка кортежей функции data_resume_list
        """
        print('Парсим резюме...')
        try:
            # self.(self.name_db_table)
            self.req = requests.get(url, headers=self.headers)
            soup = BeautifulSoup(self.req.text, 'lxml')
            
            # print(self.get_experience(soup, url))
            data = self.collect_all_resume_info(soup, url) # Мы передаем soup и затем переопределяем его, чтобы из-за многопоточности не было смешиваний резюме
            return data
            
        except BaseException as error:
            print(error)
            print(ERROR_MESSAGE+'\tНе получилось спарсить резюме: ', url)
            return []

    def get_title(self, soup):

        """
        Метод получения наименования резюме
        """
        try:
            self.soup = soup
            title = self.soup.find(attrs={'data-qa': 'resume-block-title-position', 'class': 'resume-block__title-text'}).text
        
            return title
        except BaseException as error:
            print(WARNING_MESSAGE+'\tОтпало НАИМЕНОВАНИЕ: ', error)
            return ''

    def get_salary(self, soup):

        """
        Метод получения зарплаты резюме
        """
        try:
            self.soup = soup
            salary = self.soup.find('span', class_='resume-block__salary resume-block__title-text_salary')

            if salary:
                return salary.text
            else: 
                return ''
        except BaseException as error:
            print(WARNING_MESSAGE+'\tОтпала ЗАРПЛАТА: ', error)
            return ''

    def get_education_info(self, soup):

        """
        Метод получения информации об образовании
        """
        try:
            self.soup = soup
            # education_direction = self.soup.find(attrs={'data-qa': 'resume-block-education'}).find('div', attrs={'data-qa': 'resume-block-education-organization'})
            specializations =  [item.text for item in self.soup.find_all('li', class_='resume-block__specialization')] # Забираем перечень специализаций
            # переменная нужна, чтобы понять указано ли учебное заведение в описании образования или нет
            education_type = self.soup.find(attrs={'data-qa': 'resume-block-education'}).find(class_='bloko-header-2').text 
            
            # список всех учебных заведений
            educations_list = self.soup.find(attrs={'data-qa': 'resume-block-education'}).find('div', class_='resume-block-item-gap').find_all('div', class_='resume-block-item-gap')
            if len(educations_list) > 0: 
                education_names_list = []
                education_directions_list = []
                education_years_list = []
                for item in educations_list:
                    name = item.find(attrs={'data-qa':'resume-block-education-name'}).text 
                    # Тут прописывается проверка указано ли направление образования или нет. Обычно направления нет у тех, кто оканчивал только школу
                    direction = '' if item.find(attrs={'data-qa':'resume-block-education-organization'}) == None else item.find(attrs={'data-qa':'resume-block-education-organization'}).text
                    year = item.find('div', class_='bloko-column bloko-column_xs-4 bloko-column_s-2 bloko-column_m-2 bloko-column_l-2').text
                    
                    education_names_list.append(name)
                    education_directions_list.append(direction)
                    education_years_list.append(year)
                return ' | '.join(specializations), ' | '.join(education_names_list), ' | '.join(education_directions_list), ' | '.join(education_years_list)
            
            else: # Если в разделе Образование написано просто - среднее образование
                if education_type == 'Образование':
                    education_type = self.soup.find(attrs={'data-qa': 'resume-block-education'}).find_all('div', class_='bloko-column bloko-column_xs-4 bloko-column_s-8 bloko-column_m-9 bloko-column_l-12')[-1].text
                    return ' | '.join(specializations), education_type, '', '' 
        except BaseException as error:
            print(WARNING_MESSAGE+'\tОтпало ОБРАЗОВАНИЕ: ', error)
            return '', '', '', ''

    def get_skills(self, soup):

        """
        Метод получения информации о навыках
        """
        
        try:
            self.soup = soup
            if self.soup.find('div', class_='bloko-tag-list') != None: # Проверяем существует ли блок с навыками соискателя
                skills_html = self.soup.find('div', class_='bloko-tag-list').find_all('span')
                key_skills = []
                for item in skills_html:
                    key_skills.append(item.text)
                return ' | '.join(key_skills) if type(key_skills) == list else key_skills

            else:
                return ''
        except AttributeError:
            print(WARNING_MESSAGE+'\tОТПАЛИ СКИЛЛЫ')
            return ''

    def get_languages(self, soup):
        
        """
        Метод получения информации о доступных языках
        """

        try:
            self.soup = soup
            languages = [item.text for item in self.soup.find(attrs={'data-qa': 'resume-block-languages'}).find_all('p')]
            edited_languages = []
            for language in languages:
                new_lang = language.split('—')[0] + f"({language.split(' — ')[1]})" # Приводим к виду [ Русский ( Родной); Английский ( B2 — Средне-продвинутый) ]
                edited_languages.append(new_lang)

            return " | ".join(edited_languages)
        except BaseException as error:
            print(WARNING_MESSAGE+'\tОтпали ЯЗЫКИ: ', error)
            return ''

    def get_experience(self, soup, url):
        """
        Метод получения информации об опыте работы
        """
        try:
            self.soup = soup
            # Что означают эти переменные странные?
            # work_spaces - ....
            # Надо написать подробное описание метода
            work_soup = self.soup # Потребуется для изменения soup внутри функции во время вызова selenium

            work_spaces = work_soup.find(attrs={'data-qa': 'resume-block-experience', 'class': 'resume-block'})
            self.work_periods = []
            if work_spaces == None:
                self.total_work_experience = ''
                self.work_periods.append({
                    'Должность': '',
                    'Промежуток': '',
                    'Отрасль':'',
                    'Подотрасль': '',
                    'Продолжительность': ''
                })
            else:
                if work_soup.find('span', class_='resume-industries__open'):
                    options = Options()
                    options.add_argument("--headless") # ФОНОВЫЙ РЕЖИМ
                    options.add_argument('--no-sandbox')
                    options.add_argument('--disable-dev-shm-usage')
                    
                    browser = webdriver.Chrome(options=options)
                    browser.get(url)
                    # browser.get(self.url)
                    browser.implicitly_wait(3)

                    see_more_btns = browser.find_elements(By.XPATH, "//span[@class='resume-industries__open']")
                    for btn in see_more_btns: btn.click()     
                    work_soup = BeautifulSoup(browser.page_source, 'lxml') # Переопределение soup`a 
                    work_spaces = work_soup.find(attrs={'data-qa': 'resume-block-experience', 'class': 'resume-block'}) # Переопределение опыта                
                    browser.quit()


                self.total_work_experience = work_soup.find('span', class_='resume-block__title-text resume-block__title-text_sub').text
                if  'опыт работы' in self.total_work_experience.lower():
                    self.total_work_experience = self.total_work_experience.replace(u'\xa0', u' ').replace('Опыт работы', '')
                elif 'work experience' in self.total_work_experience.lower():
                    self.total_work_experience = self.total_work_experience.replace(u'\xa0', u' ').replace('Work experience', '')
                else:
                    self.total_work_experience = work_soup.find_all('span', class_='resume-block__title-text resume-block__title-text_sub')[1].text.replace(u'\xa0', u' ').replace('Опыт работы', '')

                
                for work in work_spaces.find_all('div', class_='resume-block-item-gap')[1:]:
                    pattern_period = '\w+ \d{4} — \w+ \d{4}' # найдет все записи следующего вида: Июнь 2005 — Февраль 2021

                    period = work.find('div', class_='bloko-column bloko-column_xs-4 bloko-column_s-2 bloko-column_m-2 bloko-column_l-2').text.replace(u'\xa0', u' ')
                    period_new = re.findall(pattern_period, period)[0] if re.findall(pattern_period, period) else re.findall('\w+ \d{4} — .*?\d', period)[0][:-1]
                    
                    months_count = re.split(pattern_period, period)
                    if len(months_count) > 1:
                        months_count = months_count[-1]
                    else:
                        months_count = re.findall('\d+', re.findall('\w+ \d{4} — .*?\d+', period)[0].split()[-1])[-1] +  ' '.join(re.split('\w+ \d{4} — .*?\d+', period))

                    work_title = work.find('div', {'data-qa':'resume-block-experience-position',"class":'bloko-text bloko-text_strong'}).text
                    try:
                        branch = [item.text for item in work.find('div', class_='resume-block__experience-industries resume-block_no-print').find_all('p')]
                        subranches = []
                        # Следующий цикл для подотраслей такого типа: https://kazan.hh.ru/resume/8bbd526100027d2f200039ed1f323563626552?hhtmFrom=resume_search_result
                        for item in work.find('div', class_='resume-block__experience-industries resume-block_no-print').find_all('ul'):
                            subranches.append(' ; '.join([li.text for li in item.find_all('li')]))
                    except BaseException:
                        branch = [work.find('div', class_='resume-block__experience-industries resume-block_no-print').text.split('...')[0]]
                        subranches = []

                    self.work_periods.append({
                        'Должность': work_title,
                        'Отрасль': ' | '.join(branch),
                        'Подотрасль': ' | '.join(subranches),
                        'Промежуток': period_new,
                        'Продолжительность': months_count
                    })
            return self.work_periods, self.total_work_experience
        except BaseException as error:
            print(WARNING_MESSAGE+'\tОтпал ОПЫТ РАБОТЫ: ', error)
            return ({
                    'Должность': '',
                    'Промежуток': '',
                    'Отрасль':'',
                    'Подотрасль': '',
                    'Продолжительность': ''
                })

    def get_training(self, soup):
        
        """
        Метод получения информации о повышении квалификации
        """

        try:
            self.soup = soup
            training_html = self.soup.find('div', attrs={'data-qa': 'resume-block-additional-education', 'class':'resume-block'}).find('div', class_='resume-block-item-gap').find_all('div', 'resume-block-item-gap')
            if len(training_html) > 0:
                education_names_list = []
                education_directions_list = []
                education_years_list = []
                for item in training_html:
                    year = item.find('div', class_='bloko-column bloko-column_xs-4 bloko-column_s-2 bloko-column_m-2 bloko-column_l-2').text
                    company = item.find(attrs={'data-qa':'resume-block-education-name'}).text
                    direction = item.find(attrs={'data-qa':'resume-block-education-organization'}).text
                    
                    education_names_list.append(company)
                    education_directions_list.append(direction)
                    education_years_list.append(year)
                return ' | '.join(education_names_list), ' | '.join(education_directions_list), ' | '.join(education_years_list)
            else:
                return '', '', ''
        except BaseException:
            print(WARNING_MESSAGE+'\tОТПАЛИ КУРСЫ')
            return '', '', ''
        
            
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
        title = self.get_title(soup)
        
        print(SUCCESS_MESSAGE + f"\t{title}")    
                
        if work_periods != []:
            res = []
            for item in work_periods: # Пробегаемся по количеству мест работы 
                data = (
                        # self.group_id,
                        title,
                        self.address,
                        self.city,
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
                    title,
                    self.address,
                    self.city, 
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
    
    def connect_to_db(self, db_name):
        self.db_name = db_name
        os.makedirs('SQL', exist_ok=True) # Создаем папку SQL, если она еще не создана

        today = date.today()

        db = sqlite3.connect(f'SQL/{self.db_name}({str(today.year)}_{str(today.month)}).db')
        cursor = db.cursor()
        return cursor, db
        

    def create_table(self, name):
        cursor, db = self.connect_to_db(self.name_database)

        pattern = f"""
            CREATE TABLE IF NOT EXISTS {name}(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
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

        pattern = f"INSERT INTO {name}(name_of_profession, category_resume, city, general_experience, specialization, salary, higher_education_university,"\
            "higher_education_direction, higher_education_year, languages, skills, advanced_training_name, advanced_training_direction," \
            f"advanced_training_year, branch, subbranch, experience_interval, experience_duration, experience_post, url) VALUES({','.join('?' for i in range(20))})"

        if many_rows:
            # Результат выполнения команды в скобках VALUES превратится в VALUES(?,?,?, ?n), n = len(data) 
            cursor.executemany(pattern, data)
        else:
            # pattern = f"INSERT INTO {name} VALUES({','.join('?' for i in range(20))})"
            cursor.execute(pattern, data)
 
        db.commit()
        db.close()

if __name__ == "__main__":  
    bot = Resume()
    # bot.start()
    # bot.parse_resume('https://kazan.hh.ru/resume/6d8b504100083e0dfc0039ed1f663338376652?query=junior+product+manager&source=search&hhtmFrom=resumes_catalog')
