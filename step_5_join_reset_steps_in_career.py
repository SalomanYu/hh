import re

from step_3_remove_repeat_groupes import nested_tuple_to_dict, save_to_json, load_resumes_json


class JoinDublicateSteps:
    def __init__(self):
        pass

    def start(self) -> None:
        data = load_resumes_json('JSON/step_4_groups_with_default_names.json')

        groups, dublicate_list = self.join_steps(data)
        retransled_dict = nested_tuple_to_dict(groups)

        data_without_dublicate_job_steps = self.remove_repeat_steps(
            retransled_dict, dublicate_list)
        save_to_json(data_without_dublicate_job_steps,
                     'step_5_groups_without_job_steps_dublicate')

    def join_steps(self, data) -> tuple:
        groups = list(data.items())
        dublicate_list = []
        for resume_num in range(len(groups)):
            career_steps = groups[resume_num][1]

            for step_one in range(1, len(career_steps)):
                step_two = step_one - 1
                post_first = career_steps[step_one]['experience_post']
                post_second = career_steps[step_two]['experience_post']

                if post_first.lower().strip() == post_second.lower().strip():
                    branch_first = career_steps[step_one]['branch']
                    branch_second = career_steps[step_two]['branch']

                    if branch_first.lower().strip() == branch_second.lower().strip() or (branch_first.strip() == '' or branch_second.strip() == ''):
                        # subbranch_first = career_steps[step_one]['subbranch']
                        # subbranch_second = career_steps[step_two]['subbranch']
                        # if subbranch_first.lower().strip() == subbranch_second.lower().strip():
                        # Объединяем этапы
                        merged_interval = ' — '.join((career_steps[step_one]['experience_interval'].split(
                            '—')[0], career_steps[step_two]['experience_interval'].split('—')[-1]))
                        merged_duration = self.merge_durations(
                            career_steps, step_one, step_two)

                        dublicate_list.append(career_steps[step_one]['id'])
                        career_steps[step_two]['experience_interval'] = merged_interval
                        career_steps[step_two]['experience_duration'] = merged_duration

        print(len(dublicate_list))
        return groups, dublicate_list

    def merge_durations(self, career_steps, step_one, step_two) -> str:
        # Обрезаем лишние пробелы у строк (Метод strip() не помог)
        duration_first = ' '.join(
            career_steps[step_one]['experience_duration'].split())
        # Обрезаем лишние пробелы у строк (Метод strip() не помог)
        duration_second = ' '.join(
            career_steps[step_two]['experience_duration'].split())

        month_pattern = '\d{2} м|\d{2} m|\d м|\d m'
        year_pattern = '\d{2} г|\d{2} y|\d г|\d y|\d{2} л'

        try:
            months_first = int(re.findall(
                month_pattern, duration_first)[0].split(' ')[0])
        except IndexError:
            months_first = 0
        try:
            months_second = int(re.findall(
                month_pattern, duration_second)[0].split(' ')[0])
        except IndexError:
            months_second = 0
        try:
            years_first = int(re.findall(
                year_pattern, duration_first)[0].split(' ')[0])
        except IndexError:
            years_first = 0
        try:
            years_second = int(re.findall(
                year_pattern, duration_second)[0].split(' ')[0])
        except IndexError:
            years_second = 0

        # Делим на 12, потому что у нас 12 система счисления
        total_months = (months_first + months_second) % 12
        # Делим на 12, потому что у нас 12 система счисления
        total_years = years_first + years_second + \
            ((months_first + months_second) // 12)

        final_date = self.get_current_date(
            years=str(total_years), months=str(total_months))

        return final_date

    def get_current_date(self, years: str, months: str) -> str:
        if months == '1':
            month_type = 'месяц'
        elif months in ('2', '3', '4'):
            month_type = 'месяца'
        else:
            month_type = 'месяцев'

        if years != '11' and str(years)[-1] == '1':
            year_type = 'год'
        elif years not in ('12', '13', '14') and str(years)[-1] in ('2', '3', '4'):
            year_type = 'года'
        else:
            year_type = 'лет'

        if years == '0':
            return ' '.join((months, month_type))
        elif months == '0':
            return ' '.join((years, year_type))

        return ' '.join((years, year_type, months, month_type))

    def remove_repeat_steps(self, data, list_to_remove):
        # print(list_to_remove)
        for key in data:
            try:
                for step_num in range(len(data[key])):
                    id = data[key][step_num]['id']
                    if id in list_to_remove:
                        data[key].remove(data[key][step_num])
                        if id+1 in list_to_remove:
                            data[key].remove(data[key][step_num])
                            print('удалены', id, id+1)
                            continue
                        print('удален', id)
            except IndexError:
                pass

        return data


if __name__ == "__main__":
    step5 = JoinDublicateSteps()
    step5.start()
