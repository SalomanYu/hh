"""
Нам нужно определить средний профессиональный опыт с которым кандидат может претендовать на должность (Junior, Middle, Senior) уровней.
"""

from step_3_remove_repeat_groupes import load_resumes_json, save_to_json
from step_4_rename_to_default_name import get_default_names
from how_time_is_required_for import experience_to_months


def detect_experience(data:dict) -> dict:
    default_names = get_default_names('Маркетинг, реклама, PR')[0]
    resumes = list(data.items())
    test_resume = data['https://hh.ru/resume/815823320008ebcfc00039ed1f6b6e69646465?query=product+manager&source=search&hhtmFrom=resumes_catalog'][::-1]
    proffecion_name = test_resume[0]['name_of_profession']

    time_required_for_levels = {}
    for def_level_name in list(default_names.values()):
        time_required_for_levels[def_level_name] = []
        for resume in resumes:
            if resume[1][0]['name_of_profession'] == def_level_name:
                time_required_for_levels[def_level_name].append(
                    {
                    'user_id': resume[0],
                    'months': experience_to_months(resume[1][0]['general_experience'])
                    })
            else:
                step_position = -1
                job_steps = resume[1][::-1]    
                for step_index in range(len(job_steps)):
                    if job_steps[step_index]['experience_post'] == def_level_name:
                        step_position = step_index
                if step_position == 0: # Если в самом начале этап этого уровня
                    time_required_for_levels[def_level_name].append(
                        {
                        'user_id': resume[0],
                        'months': 0
                        })
                elif step_position > 0:
                    level_months = 0
                    for item in range(step_position):
                        level_months += experience_to_months(job_steps[item]['experience_duration'])
                    time_required_for_levels[def_level_name].append(
                        {
                        'user_id': resume[0],
                        'months': level_months
                        })
    return time_required_for_levels     



def change_level_for_zero_positions(data:dict) -> tuple:
    # Нужно поменять этот блок, когда будем проверять выборку больше, чем product manager
    zero_position = tuple(data.items())[0]
    level_groups = tuple(data.items())[1:]
    for zero_item in range(len(zero_position[1])):
        # for level in range(len(level_groups), 0, -1):
        for level in range(len(level_groups)):
            level_sum = 0
            for item in level_groups[level][1]:
            # for item in level_groups[level-1][1]:
                level_sum += item['months']
            # average = level_sum // len(level_groups[level-1][1])
            average = level_sum // len(level_groups[level][1])
            if (average >= zero_position[1][zero_item]['months']) or (average <= zero_position[1][zero_item]['months'] and level == len(level_groups)-1):
                zero_position[1][zero_item]['new_level'] = level+1
                zero_position[1][zero_item]['new_name'] = level_groups[level][0]
                break

    # return {zero_position[0]: zero_position[1]}
    print(zero_position)
    return zero_position


def save_update_zero_professions(zero_professions:dict, original_data:dict) -> dict:
    for profession in zero_professions[1]:
        if profession['user_id'] in original_data:
            for job_step in original_data[profession['user_id']]:
                try:
                    job_step['level'] = profession['new_level']
                    job_step['name_of_profession'] = profession['new_name']
                except BaseException:
                    continue

    save_to_json(original_data, 'step_6_update_zero_levels')

def main():
    data = load_resumes_json('JSON/step_5_groups_without_job_steps_dublicate.json')
    dict_with_experience_statistic = detect_experience(data)

    updated_zero_professions = change_level_for_zero_positions(dict_with_experience_statistic)

    save_update_zero_professions(updated_zero_professions, data)
    

if __name__ == "__main__":
    main()
