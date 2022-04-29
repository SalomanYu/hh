from random import choice
import matplotlib.pyplot as plt
import numpy as np

import json

plt.clf()

# using some dummy data for this example
xs = np.arange(0,10,1)
ys = np.random.normal(loc=3, scale=0.4, size=10)

# 'bo-' means blue color, round points, solid lines
# plt.plot(xs,ys,'bo-')

# # zip joins x and y coordinates in pairs
# for x,y in zip(xs,ys):

#     label = "{:.2f}".format(y)

#     plt.annotate(label, # this is the text
#                  (x,y), # these are the coordinates to position the label
#                  textcoords="offset points", # how to position the text
#                  xytext=(0,10), # distance from text to points (x,y)
#                  ha='center',
#                  ) # horizontal alignment can be left, right or center

# plt.show()

data = json.load(open('../JSON/step_5_groups_without_job_steps_dublicate.json'))
items = data['https://hh.ru/resume/00ded5960007ed73ce0039ed1f506d59383971?query=product+manager&source=search&hhtmFrom=resumes_catalog']


colors = ('b', 'g', 'r', 'c', 'm', 'y', 'k')

# plt.plot([2,3], [1,1], f'>{choice(colors)}-')
# plt.plot([2,3], [2,2], f'>{choice(colors)}-')

# y = [1] * len(items)
# x = [i+2 for i in range(len(items))]

# for i, j in zip(x,y):
#         print(i, j)
#         label = items[0]['id']
#         plt.annotate(label, (i,j),textcoords="offset points", xytext=(0,10), ha='center')
# plt.show()


resumes = list(data.items())
# print(resumes[0])
# print(len(resumes[0][1]))
plt.rcParams.update({'font.size': 8})

for resume_num in range(5):
        xs = [i+1 for i in range(len(resumes[resume_num][1])+1)] # Составляем список, 
        ys = [resume_num+1] * (len(resumes[resume_num][1])+1)
        plt.plot(xs, ys, f'<{choice(colors)}-')
        final_profession_name = resumes[resume_num][1][0]['name_of_profession'] + ' - ID:' + str(resumes[resume_num][1][0]['id'])
        plt.annotate(final_profession_name, (xs[0], ys[0]), textcoords='offset points', xytext=(0,10), ha='left')
        for item in range(len(resumes[resume_num][1])):
                label = resumes[resume_num][1][item]['experience_post'] #+ '\n' + resumes[resume_num][1][item]['experience_interval'] 
                plt.annotate(label, (xs[item+1], ys[item+1]), textcoords='offset points', xytext=(0,10), ha='left')
plt.show()