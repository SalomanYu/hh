import json
import sqlite3
import os

class SelectData:
    def __init__(self, db_path, file_output_name):
        self.path = db_path
        self.file_output_name = file_output_name

    def collect(self):
        conn = self.connect_to_db(self.path)
        data = self.select_all_rows(conn)
        groups = self.group_user_ids_to_dict(data)
        self.save_to_json(groups)

        print('Данные были пересены и сгруппированны в json-формате: JSON/' + self.file_output_name)

    def connect_to_db(self, path):
        conn = None
        try:
            conn = sqlite3.connect(path)
        except sqlite3.Error as error:
            print(error)
        
        return conn

    def select_all_rows(self, conn):
        cur = conn.cursor()
        cur.execute('SELECT * FROM resumes')

        rows = cur.fetchall() # принести всё

        data = []
        for row in rows:
            data.append({
                'id': row[0],
                'user_id(url)': row[-1],
                'name_of_profession': row[4],
                'experience_interval': row[20],
                'experience_duration': row[21],
                'experience_post': row[22],
                'branch': row[18],
                'subbranch': row[19],
                'general_experience': row[7],
                'specialization': row[8],
                'weight_in_group': row[1],
                'level': row[2],
                'level_in_group': row[3],
                'category_name': row[5],
                'city': row[6],
                'salary': row[9],
                'higher_education_university': row[10],
                'higher_education_direction': row[11],
                'higher_education_year': row[12],
                'languages': row[13],
                'skills': row[14],
                'advanced_training_name': row[15],
                'advanced_training_direction': row[16],
                'advanced_training_year': row[17],

            })
        
        return data

    def group_user_ids_to_dict(self, data):
        groups_dict = {}
        
        for row in data:
            url = row['user_id(url)']
            if url in groups_dict:
                is_repeat_resume = False
                for elem in groups_dict[url]:
                    if row['experience_interval'] == elem['experience_interval'] and row['experience_post'] == elem['experience_post']:
                        is_repeat_resume = True
                        break
                if not is_repeat_resume:
                    groups_dict[url].append(row)
            
            else:
                groups_dict[url] = [row]

        return groups_dict

    def save_to_json(self, data):
        os.makedirs('JSON', exist_ok=True)

        with open(f'JSON/{self.file_output_name}.json', 'w') as file:
            json.dump(data, file, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    collector = SelectData(db_path='SQL/Middle_fresh(2022_4).db', file_output_name='step_2_groups_result')
    collector.collect()
