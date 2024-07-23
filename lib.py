from jamo import h2j, j2hcj
import os
import json
from random import *
from copy import deepcopy

PATH_RES = './res/'
# def get_txt_names():
#     file_list = os.listdir(PATH_RES)
#     return [file.replace('.txt', '') for file in file_list if file.endswith('.txt')]

def get_txt_file_list(path):
    file_list = os.listdir(PATH_RES)
    txt_file_list = [
        {
            'name': file.replace('.txt', ''),
            'path': PATH_RES + file
        } for file in file_list if file.endswith('.txt')
    ]
    return txt_file_list

def read_txt_file(file_path):
    file = open(file_path, 'r', encoding='utf-8')
    data = file.readlines()
    file.close()
    return data

def make_quiz_data(txt_file_list):
    quiz_data = []

    for txt_file in txt_file_list:
        data = []
        file_data = read_txt_file(txt_file['path'])

        for line in file_data:
            # 초성 뽑기 전 가공
            line = line.strip()

            data.append({
                'ans': line,
                'chs': han2jaum(line),
                'subject': txt_file['name']
            })
        
        quiz_data.append({
            'subject': txt_file['name'],
            'data': data
        })
    
    return quiz_data

def get_quiz(active_quiz_data):
    active_quiz = deepcopy(choice(active_quiz_data['data']))
    hint_pos_list = [i for i in range(len(active_quiz['ans']))]
    shuffle(hint_pos_list)
    hint_pos_list.pop()
    active_quiz['hint'] = hint_pos_list
    return active_quiz

def get_hint(active_quiz):
    hint_pos = active_quiz['hint'].pop()
    temp = list(active_quiz['chs'])
    temp[hint_pos] = active_quiz['ans'][hint_pos]
    active_quiz['chs'] = ''.join(temp)
    return active_quiz

def get_data(file_name):
    file = open(PATH_RES + file_name, 'r', encoding='utf-8')
    data = file.readlines()
    file.close()
    return data

def get_jaum_set(data):
    jaum_set = []
    for i in data:
        han = i.strip()  # 앞뒤 공백 제거
        jaum_set.append([''.join(han), han2jaum(han)])
    return jaum_set

def han2jaum(han):
    jaum = []
    for i in han:
        temp = h2j(i)  # 완성형 -> 조합형
        imf = j2hcj(temp)  # 자모 분리
        jaum.append(imf[0])  # 초성만 사용
    return ''.join(jaum)

def constraint(num, min_num, max_num):
    if min_num > max_num:
        min_num, max_num = max_num, min_num
    num = max(num, min_num)
    num = min(num, max_num)
    return num

def end_with_vowel(word):
    last_char = word[-1]
    code = ord(last_char)
    # 한글로 끝나면
    if 44032 <= code <= 55203:
        return (code - 44032) % 28 == 0
    elif 12593 <= code <= 12622:
        return False
    # 숫자나 영어로 끝나면
    elif last_char.isalnum():
        return last_char not in '136780lmnrLMNR'
    
    return True

# txt_file_list = get_txt_file_list(PATH_RES)
# # print(txt_file_list)
# # print(read_txt_file(txt_file_list[0]['path']))
# quiz_data = make_quiz_data(txt_file_list)
# # print([file['name'] for file in txt_file_list])
# # print(quiz_data[int(input())])
# active_quiz_data = {
#     'subject': '모두',
#     'data': sum([quiz['data'] for quiz in quiz_data], [])
# }
# print(active_quiz_data)

def make_json(data):
    file_path = 'output.json'
    with open(file_path, 'w', encoding='utf-8') as file:
        json.dump(data, file, ensure_ascii=False)