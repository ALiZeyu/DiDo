# -*- coding: utf-8 -*-
import urllib2
import json
import os
import Test
import requests


def get_response_batch(out_list, input_list):
    for sentence in input_list:
        new_str = ''
        my_array = sentence.split('\t')
        question = my_array[1]
        new_str += my_array[0] + '\t' + my_array[1] + '\t' + get_response_string(question) + '\t' + my_array[3] + '\t' + my_array[4]
        out_list.append(new_str)


def get_response_string(question):
    prefix = 'http://jnlu-broker.jd.com/get_all_domain_results?device_id=123&text='
    prefix += question
    response = requests.get(prefix)
    json_str = response.content
    print question
    print json_str
    parsed_json = json.loads(json_str, strict=False)
    attri_list = ["song", "instruct", "chat", "weather", "local", "shopping", "info"]
    result = ''
    for attribute in attri_list:
        temp_str = ''
        if not parsed_json.has_key(attribute) or parsed_json[attribute]["responseText"] is None or len(parsed_json[attribute]["responseText"].strip()) == 0:
            temp_str = 'Empty'
        else:
            if attribute == 'song':
                temp_str = song_test(parsed_json[attribute]["responseText"])
            elif attribute == 'instruct':
                instruction = parsed_json[attribute]["responseText"].strip()
                if instruction == 'INTENT_UNKNOWN':
                    temp_str = '没有可以执行的指令'
                else:
                    temp_str = '执行'+instruction+'指令'
            else:
                temp_str = parsed_json[attribute]["responseText"].strip()
        result += temp_str + '\t'
    return result.strip()


def response_file_create(input_path, output_path):
    data = Test.read_file(input_path)
    title = 'Intent\tInput\tsong\tinstruct\tchat\tweather\tlocal\tshopping\tinfo'
    exception_list = []
    out_list = []
    i = 0
    for sentence in data:
        i += 1
        # if i > 30:
        #     break
        new_str = ''
        my_array = sentence.split('\t')
        question = my_array[1]
        # try:
        new_str += my_array[0] + '\t' + my_array[1] + '\t' + get_response_string(question) + '\t' + my_array[3] + '\t' + my_array[4]
        # except Exception:
        #     exception_list.append(question)
        #     continue
        out_list.append(new_str)
    Test.write_file(output_path, out_list)
    Test.write_file('data/json_exception.txt', exception_list)


# def pipe_line(path):
#     result_suffix = 'D://dingdong/jnlu_response'
#     dir_list = os.listdir(path)
#     for dir_name in dir_list:
#         dir_path = path + '/' + dir_name
#         file_list = os.listdir(dir_path)
#         for file_name in file_list:
#             input_path = dir_path + '/' + file_name
#             output_path = result_suffix + '/' + dir_name + '/' + file_name


def get_page(question):
    attribute = 'song'
    prefix = 'http://jnlu-broker.jd.com/get_all_domain_results?device_id=123&text='
    prefix += question
    print prefix
    response = requests.get(prefix)
    json_str = response.content
    print json_str
    parsed_json = json.loads(json_str, strict=False)
    print 'Intent_NULL' if len(parsed_json[attribute]["responseText"].strip()) == 0 else parsed_json[attribute][
         "responseText"].strip()


def song_test(json_str):
    # question = '一个好人我应该去爱她就去你的去别。'
    # prefix = 'http://jnlu-broker.jd.com/get_all_domain_results?device_id=123&text='
    # prefix += question
    # print prefix
    # response = requests.get(prefix)
    # json_str = response.content
    # # parsed = json.loads(json_str, strict=False)
    # parsed = json.loads(json_str, strict=False)
    # song_dict = parsed["song"]["responseText"]
    song_parsed = json.loads(json_str)
    sec_str = ''
    if 'song' in song_parsed and 'singer' in song_parsed:
        sec_str = '播放歌手“' + song_parsed["singer"] + '”的歌曲《' + song_parsed["song"] + '》'
    elif 'singer' in song_parsed > 0:
        sec_str = '播放歌手“' + song_parsed["singer"] + '”的歌曲'
    elif 'song' in song_parsed > 0:
        sec_str = '播放歌曲《' + song_parsed["song"] + '》'
    else:
        sec_str = song_parsed["source"]
    return sec_str


def get_response_by_question(question):
    prefix = 'http://jnlu-broker.jd.com/get_all_domain_results?device_id=123&text='
    prefix += question
    response = requests.get(prefix)
    json_str = response.content
    print json_str


if __name__ == '__main__':
    # input_text = '请问 您的订单由于送货时间未到不能出库 是什么意思。'
    # get_page(input_text)
    # get_response_string(input_text, "song")
    response_file_create('E:/pyworkspace/Test/data/dingdong_small.txt', 'data/url_format.txt')
    # get_response_by_question('请关闭，我要不听这个歌叮咚叮咚。')
    # song_test()
