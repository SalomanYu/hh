from step_3_remove_repeat_groupes import load_resumes_json
import re

def get_min_and_max_join_steps(resumes):
    max_min_dict = {
        'junior': {
            'max': {
                'count': -1,
                'user_id': '' 
            },
            'min': {
                'count': 100,
                'user_id': ''
            }
        },
        'middle': {
            'max': {
                'count': -1,
                'user_id': '' 
            },
            'min': {
                'count': 100,
                'user_id': ''
            }
        },
        'senior': {
            'max': {
                'count': -1,
                'user_id': '' 
            },
            'min': {
                'count': 100,
                'user_id': ''
            }
        },

    }
    
    for resume in resumes:
        for level in max_min_dict:
            if level in resume[1][0]['name_of_profession'].lower():
                if len(resume[1]) > max_min_dict[level]['max']['count']:
                    # max_steps = len(resume[1]), resume[0]
                    max_min_dict[level]['max']['count'] = len(resume[1])
                    max_min_dict[level]['max']['user_id'] = resume[0]

                elif len(resume[1]) < max_min_dict[level]['min']['count']:
                    # min_steps = len(resume[1]), resume[0]
                    max_min_dict[level]['min']['count'] = len(resume[1])
                    max_min_dict[level]['min']['user_id'] = resume[0]
    return max_min_dict

def experience_to_months(experience) -> int:
    month_pattern = '\d{2} м|\d{2} m|\d м|\d m'
    year_pattern = '\d{2} г|\d{2} y|\d г|\d y|\d{2} л|\d л'

    try:
        months = int(re.findall(month_pattern, experience)[0].split(' ')[0])
    except IndexError:
        months = 0
    try:
        years = int(re.findall(year_pattern, experience)[0].split(' ')[0])
    except IndexError:
        years = 0

    if years != 0:
        return years * 12 + months
    else:
        return months

def get_average_duration(resumes):
    juniors_statistic = []
    middles_statistic = []
    seniors_statistic = []

    for resume in resumes:
        if 'junior' in resume[1][0]['name_of_profession'].lower():
            juniors_statistic.append(experience_to_months(resume[1][0]['general_experience']))
            for job_step in resume[1]:
                if 'junior' in job_step['experience_post'].lower():
                    juniors_statistic.append(experience_to_months(job_step['experience_duration']))

        elif 'middle' in resume[1][0]['name_of_profession'].lower():
            middles_statistic.append(experience_to_months(resume[1][0]['general_experience']))
    
            for job_step in resume[1]:
                if 'middle' in job_step['experience_post'].lower():
                    middles_statistic.append(experience_to_months(job_step['experience_duration']))

        elif 'senior' in resume[1][0]['name_of_profession'].lower():
            seniors_statistic.append(experience_to_months(resume[1][0]['general_experience']))
    
            for job_step in resume[1]:
                if 'senior' in job_step['experience_post'].lower():
                    seniors_statistic.append(experience_to_months(job_step['experience_duration']))
    
    average_junior = round(sum(juniors_statistic) / len(juniors_statistic))
    average_middle = round(sum(middles_statistic) / len(middles_statistic))
    average_senior = round(sum(seniors_statistic) / len(seniors_statistic))

    return average_junior, average_middle, average_senior

if __name__ == "__main__":
    data = load_resumes_json(path='JSON/step_5_groups_without_job_steps_dublicate.json')
    resumes = list(data.items())

    average_junior, average_middle, average_senior = get_average_duration(resumes)
    max_min_dict = get_min_and_max_join_steps(resumes)
    
    print('Среднее количество времени на то, чтобы получить уровень:')
    print(f'\tJunior: {average_junior} мес.')
    print(f'\tMiddle: {average_middle} мес.')
    print(f'\tSenior: {average_senior} мес.')
    print('Максимальные и минимальные этапы в карьере для разных уровней:')

    print(f'\tJunior:')
    print(f'\t\tМаксимум:{max_min_dict["junior"]["max"]["count"]}\n\t\tСсылка:{max_min_dict["junior"]["max"]["user_id"]}')
    print(f'\t\tМинимум:{max_min_dict["junior"]["min"]["count"]}\n\t\tСсылка:{max_min_dict["junior"]["min"]["user_id"]}')
    
    print(f'\tMiddle:')
    print(f'\t\tМаксимум:{max_min_dict["middle"]["max"]["count"]}\n\t\tСсылка:{max_min_dict["junior"]["max"]["user_id"]}')
    print(f'\t\tМинимум:{max_min_dict["middle"]["min"]["count"]}\n\t\tСсылка:{max_min_dict["junior"]["min"]["user_id"]}')
    
    print(f'\tSenior:')
    print(f'\t\tМаксимум:{max_min_dict["senior"]["max"]["count"]}\n\t\tСсылка:{max_min_dict["junior"]["max"]["user_id"]}')
    print(f'\t\tМинимум:{max_min_dict["senior"]["min"]["count"]}\n\t\tСсылка:{max_min_dict["junior"]["min"]["user_id"]}')


    