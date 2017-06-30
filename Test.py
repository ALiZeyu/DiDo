# -*- coding: utf-8 -*-
import codecs
import json
import re
import sys
import os
reload(sys)
sys.setdefaultencoding('utf-8')


def read_file(path):
    f = codecs.open(path, 'r', encoding='utf-8')
    content = f.readlines()
    content = [sen.strip() for sen in content]
    f.close()
    return content


def write_file(path, content):
    f = codecs.open(path, 'w', encoding='utf-8')
    for sentence in content:
        f.write(sentence+'\n')
    f.close()


# 统计其中的PK结果类型及其出现次数，用、n隔开数组下标是6
def count_pk(data):
    pk_map = dict()
    for sentence in data:
        type_str = sentence.split('\t')[6]
        if pk_map.has_key(type_str):
            pk_map[type_str] = pk_map[type_str] + 1
        else:
            pk_map[type_str] = 1
    return pk_map


# 输入rwadata，提取前面几个字段并解析json，提取出的信息是：pk格式+输入+输出+flag+rec
def first_filter(in_path, out_path, exception_path):
    data = read_file(in_path)
    del data[0]
    nomal_list = []
    exception_list = []
    all_num = 0
    for sentence in data:
        if not sentence.startswith('智能音箱'):
            continue
        all_num += 1
        myarray = sentence.split('\t', 10)
        if len(myarray) < 10:
            continue
        my_str = myarray[6]+'\t|\t'
        # 同时含有输入和输出
        if len(myarray[8].strip())>0 and myarray[9].strip() != '--':
            my_str += myarray[8]+'\t|\t'+myarray[9]+'\t|\t1'
            nomal_list.append(my_str)
            continue
        json_str = myarray[10].strip()
        # if json_str.find('"rec"') == -1:
        #     # 异常句子待观察
        #     exception_list.append(sentence)
        #     continue
        # erviceType:vbox_4.0	"{"text":"叫一个音量。","serviceType":"LL_RADIO","rc":"0","
        # if not json_str.startswith('"{"'):
        #     p = json_str.find('"{"')
        #     json_str = json_str[p:]
        # json_str = json_str[1:-1]
        # 含有\字符无法处理
        json_str = json_str.replace('\\','')
        json_str = json_str.replace('""', '"')
        # print in_path+json_str
        # try:
        # parsed_json = json.loads(json_str, strict=False)
        # except ValueError:
        #     continue
        # 没输出但是有rec
        # if parsed_json.has_key('rec'):
        #     my_str += myarray[8] + '\t|\t' + parsed_json['rec'] + '\t|\t0'
        #     nomal_list.append(my_str)
        # else:
        #     # 异常句子待观察
        #     exception_list.append(sentence)
        if json_str.find('"rec":') != -1:
            position = json_str.find('"rec":') + 7
            rec_str = ''
            while json_str[position] != '"':
                rec_str += json_str[position]
                position += 1
            my_str += myarray[8] + '\t|\t' + rec_str.strip() + '\t|\t0'
            nomal_list.append(my_str)
        else:
            # 异常句子待观察
            exception_list.append(sentence)
    write_file(out_path, nomal_list)
    print all_num
    print len(nomal_list)
    write_file(exception_path, exception_list)


def sec_filter(in_path, out_path, exception_path):
    '''
    处理方式：songsearch：播放singer的song；instruction：执行type后面的指令；其他：
    '''
    data = read_file(in_path)
    str_map = dict()
    exception_list = []
    out_list = []
    for sentence in data:
        # print sentence
        # out_list.append(sentence)
        myarray = sentence.split('\t|\t')
        temp_str = ''
        if myarray[3] == '1':
            temp_str = myarray[0]+ '\t' +myarray[1]+ '\t' +myarray[2]
        else:
            if myarray[0] == 'SongSearch':
                if myarray[2].find('predicate:sing') != -1:
                    song = ''
                    singer = ''
                    sec_array = myarray[2].strip().split()
                    if len(sec_array) > 1:
                        i = 0
                        for slot_str in sec_array:
                            if slot_str == 'param:singer':
                                singer = sec_array[i+1]
                            elif slot_str == 'param:song':
                                song = sec_array[i+1]
                            i += 1
                    else:
                        dummy_str = myarray[2]
                        if dummy_str.find('param:singer') != -1:
                            b = dummy_str.find('param:singer') + len('param:singer')
                            while b < len(dummy_str) and not dummy_str[b:].startswith('param:'):
                                singer += dummy_str[b]
                                b += 1
                        if dummy_str.find('param:song') != -1:
                            b = dummy_str.find('param:song') + len('param:song')
                            while b < len(dummy_str) and not dummy_str[b:].startswith('param:'):
                                song += dummy_str[b]
                                b += 1
                    if len(singer) > 0 and len(song) > 0:
                        sec_str = '播放歌手“' + singer + '”的歌曲《' + song + '》'
                        temp_str = myarray[0]+ '\t' +myarray[1]+ '\t' + sec_str
                    elif len(singer) > 0:
                        sec_str = '播放歌手“' + singer + '”的歌曲'
                        temp_str = myarray[0] + '\t' + myarray[1] + '\t' + sec_str
                    elif len(song) > 0:
                        sec_str = '播放歌曲《' + song + '》'
                        temp_str = myarray[0] + '\t' + myarray[1] + '\t' + sec_str
                elif myarray[2].find('predicate:belongTags') != -1:
                    tag = ''
                    tag_list = ['欧美歌曲', '佛乐', '治愈的歌', '爵士歌曲', '胎教歌曲', '吉他', '翻唱歌曲',
                                '轻音乐', '春节歌曲', '相声', '欢快的歌', '清新的歌', '聚会歌曲', '红歌',
                                '黄昏的歌', 'ktv热歌榜', '儿歌', '男歌手的歌', '古典音乐', '驾车歌曲', 'rnb歌曲',
                                '夜晚的歌', '母亲节歌曲', '苏格兰风笛', '中秋节歌曲', '瑜伽歌曲', '幸福的歌',
                                '甜蜜的歌', '手风琴', '昆曲', '华语金曲榜', '情人节歌曲', '动漫歌曲', '神曲',
                                '雨天的歌', '越剧', '校园歌曲', '钢琴曲', '度假歌曲', '一个人的歌', '笛子',
                                '摇滚歌曲', '催眠歌曲', '生日歌曲', '学习的歌', '工作的歌', '旅途歌曲', '开心的歌',
                                '中国风歌曲', '起床歌曲', '热歌榜', '原创音乐榜', '80后的歌', '国庆节歌曲',
                                '酒吧歌曲', '安静的歌', '民谣', '散步歌曲', '圣诞节歌曲', '性感的歌',
                                '纯音乐', '发泄的歌', '广场舞歌曲', '经典老歌', '乡村歌曲', '情歌对唱榜',
                                '孤独的歌', '70后的歌', '英伦歌曲', '粤语歌曲', '民族歌曲', 'hito中文榜',
                                '箫', '葫芦丝', '寂寞的歌', '思念的歌', '欧美金曲榜', '影视金曲榜', '下午茶歌曲',
                                '小提琴', '女歌手的歌', '端午节歌曲', '60后的歌', '雷鬼歌曲', '说唱歌曲', '大提琴',
                                '怀旧的歌', '韩语歌曲', '综艺热歌', '伤感的歌', '京剧', '军旅歌曲', '做家务听的歌',
                                '对唱歌曲', '情歌', '浪漫的歌', '新世纪歌曲', '华语歌曲', '90后的歌', '温暖的歌',
                                '网络歌曲榜', '新歌榜', '电子音乐', '放松的歌', 'ktv歌曲', '黄梅戏', '感动的歌',
                                '清晨的歌', '戏曲', '00后的歌', '日语歌曲', '缠绵歌曲', '小品', '午休歌曲',
                                '运动歌曲', '民歌', '儿童节歌曲', '叛逆的歌', '励志的歌', '独立歌曲', '新年歌曲',
                                '金属歌曲', '经典老歌榜', '豫剧', '蓝调歌曲', '激情的歌', '拉丁歌曲', '古筝',
                                '网络歌曲', '闽南语歌曲', '婚礼歌曲', '俄语歌曲', '七夕歌曲']
                    sec_array = myarray[2].strip().split()
                    if len(sec_array) > 1:
                        for slot_str in sec_array:
                            if slot_str.startswith('tag:'):
                                tag = slot_str[4:]
                    else:
                        dummy_str = myarray[2].strip()
                        if dummy_str.find('tag:') != -1:
                            str_next = dummy_str[dummy_str.find('tag:') + len('tag:'):]
                            for candidate in tag_list:
                                if str_next.startswith(candidate):
                                    tag = candidate
                                    break
                    if len(tag) > 0:
                        sec_str = '播放标签为“' + tag + '”下的歌曲'
                        temp_str = myarray[0] + '\t' + myarray[1] + '\t' + sec_str
                elif myarray[2].find('predicate:songlist') != -1 or myarray[2].find('predicate:userSonglist') != -1:
                    song_list = ''
                    sec_array = myarray[2].strip().split()
                    if len(sec_array) > 1:
                        i = 0
                        for slot_str in sec_array:
                            if slot_str == 'param:songlist':
                                song_list = sec_array[i+1]
                            i += 1
                    else:
                        dummy_str = myarray[2].strip()
                        if dummy_str.find('param:songlist') != -1:
                            b = dummy_str.find('param:songlist') + len('param:songlist')
                            while b < len(dummy_str) and not dummy_str[b:].startswith('param:'):
                                song_list += dummy_str[b]
                                b += 1
                    if len(song_list) > 0:
                        sec_str = '播放“' + song_list + '”列表下的歌曲'
                        temp_str = myarray[0] + '\t' + myarray[1] + '\t' + sec_str
                elif myarray[2].find('predicate:hasThemeSong') != -1:
                    theme = ''
                    sec_array = myarray[2].strip().split()
                    if len(sec_array) > 1:
                        i = 0
                        for slot_str in sec_array:
                            if slot_str == 'param:film':
                                theme = sec_array[i+1]
                            i += 1
                    else:
                        dummy_str = myarray[2].strip()
                        if dummy_str.find('param:film') != -1:
                            b = dummy_str.find('param:film') + len('param:film')
                            while b < len(dummy_str) and not dummy_str[b:].startswith('param:'):
                                theme += dummy_str[b]
                                b += 1
                    if len(theme) > 0:
                        sec_str = '播放主题曲《' + theme + '》'
                        temp_str = myarray[0] + '\t' + myarray[1] + '\t' + sec_str
                else:
                    album = ''
                    sec_array = myarray[2].strip().split()
                    if len(sec_array) > 1:
                        i = 0
                        for slot_str in sec_array:
                            if slot_str == 'param:album':
                                album = sec_array[i + 1]
                            i += 1
                    else:
                        dummy_str = myarray[2].strip()
                        if dummy_str.find('param:album') != -1:
                            b = dummy_str.find('param:album') + len('param:album')
                            while b < len(dummy_str) and not dummy_str[b:].startswith('param:'):
                                album += dummy_str[b]
                                b += 1
                    if len(album) > 0:
                        sec_str = '播放专辑“' + album + '”下的歌曲'
                        temp_str = myarray[0] + '\t' + myarray[1] + '\t' + sec_str
            elif myarray[0] == 'Instruction':
                if myarray[2].find('predicate:instruction') != -1:
                    instruction_type = ''
                    sec_array = myarray[2].strip().split()
                    if len(sec_array) > 1:
                        for slot_str in sec_array:
                            if slot_str.startswith('type:'):
                                instruction_type = slot_str[5:]
                    else:
                        dummy_str = myarray[2].strip()
                        if dummy_str.find('type:') != -1:
                            b = dummy_str.find('type:') + len('type:')
                            # 指令是子母和下划线的组合
                            while b < len(dummy_str) and (dummy_str[b].isupper() or dummy_str[b].islower() or dummy_str[b] == '_'):
                                instruction_type += dummy_str[b]
                                b += 1
                    if len(instruction_type) > 0:
                        sec_str = '执行“' + instruction_type + '”指令'
                        temp_str = myarray[0] + '\t' + myarray[1] + '\t' + sec_str
                    else:
                        # 其他类型集中起来看看
                        exception_list.append(sentence)
                else:
                    # 其他类型集中起来看看
                    exception_list.append(sentence)
            elif myarray[0] == 'JPRadio':
                artist = ''
                song = ''
                sec_array = myarray[2].strip().split()
                pattern = re.compile('(param:typeMain|param:name|param:typeSub)')
                if len(sec_array) > 1:
                    i = 0
                    for slot_str in sec_array:
                        if pattern.match(slot_str):
                            song = sec_array[i + 1]
                        elif slot_str == 'param:artist':
                            artist = sec_array[i + 1]
                        i += 1
                else:
                    dummy_str = myarray[2].strip()
                    x = re.findall('(param:typeMain|param:name|param:typeSub)', dummy_str)
                    if len(x) > 0:
                        find_str = x[0]
                        b = dummy_str.find(find_str) + len(find_str)
                        while b < len(dummy_str) and not dummy_str[b:].startswith('param:'):
                            song += dummy_str[b]
                            b += 1
                    if dummy_str.find('param:artist') != -1:
                        b = dummy_str.find('param:artist') + len('param:artist')
                        while b < len(dummy_str) and not dummy_str[b:].startswith('param:'):
                            artist += dummy_str[b]
                            b += 1
                if len(artist) > 0 and len(song) > 0:
                    sec_str = '播放“' + artist + '”的《' + song + '》'
                    temp_str = myarray[0] + '\t' + myarray[1] + '\t' + sec_str
                elif len(artist) > 0:
                    sec_str = '播放“' + artist + '”的节目'
                    temp_str = myarray[0] + '\t' + myarray[1] + '\t' + sec_str
                elif len(song) > 0:
                    sec_str = '播放节目《' + song + '》'
                    temp_str = myarray[0] + '\t' + myarray[1] + '\t' + sec_str
        if len(temp_str) > 0:
            str_map[temp_str] = str_map[temp_str] + 1 if str_map.has_key(temp_str) else 1
    # 写入文件
    num = 0
    for k, v in zip(str_map.iterkeys(), str_map.itervalues()):
        num += v
        out_list.append(k+ '\t' +str(v))
    write_file(out_path, out_list)
    print num
    #write_file(exception_path, exception_list)

# old version of sec
def sec_sec_filter(in_path, out_path, exception_path):
    data = read_file(in_path)
    str_map = dict()
    exception_list = []
    out_list = []
    for sentence in data:
        # print sentence
        myarray = sentence.split('\t|\t')
        temp_str = ''
        if myarray[3] == '1':
            temp_str = myarray[0] + '\t' + myarray[1] + '\t' + myarray[2]
        else:
            if myarray[0] == 'SongSearch':
                if myarray[2].find('predicate:sing') != -1:
                    song = ''
                    singer = ''
                    sec_array = myarray[2].strip().split()
                    i = 0
                    for slot_str in sec_array:
                        if slot_str == 'param:singer':
                            singer = sec_array[i + 1]
                        elif slot_str == 'param:song':
                            song = sec_array[i + 1]
                        i += 1
                    if len(singer) > 0 and len(song) > 0:
                        sec_str = '播放歌手“' + singer + '”的歌曲《' + song + '》'
                        temp_str = myarray[0] + '\t' + myarray[1] + '\t' + sec_str
                    elif len(singer) > 0:
                        sec_str = '播放歌手“' + singer + '”的歌曲'
                        temp_str = myarray[0] + '\t' + myarray[1] + '\t' + sec_str
                elif myarray[2].find('predicate:belongTags') != -1:
                    tag = ''
                    sec_array = myarray[2].strip().split()
                    for slot_str in sec_array:
                        if slot_str.startswith('tag:'):
                            tag = slot_str[4:]
                    if len(tag) > 0:
                        sec_str = '播放标签为' + tag + '下的歌曲'
                        temp_str = myarray[0] + '\t' + myarray[1] + '\t' + sec_str
                elif myarray[2].find('predicate:songlist') != -1 or myarray[2].find('predicate:userSonglist') != -1:
                    song_list = ''
                    sec_array = myarray[2].strip().split()
                    i = 0
                    for slot_str in sec_array:
                        if slot_str == 'param:songlist':
                            song_list = sec_array[i + 1]
                        i += 1
                    if len(song_list) > 0:
                        sec_str = '播放' + song_list + '列表下的歌曲'
                        temp_str = myarray[0] + '\t' + myarray[1] + '\t' + sec_str
                elif myarray[2].find('predicate:hasThemeSong') != -1:
                    theme = ''
                    sec_array = myarray[2].strip().split()
                    i = 0
                    for slot_str in sec_array:
                        if slot_str == 'param:film':
                            theme = sec_array[i + 1]
                        i += 1
                    if len(theme) > 0:
                        sec_str = '播放主题曲' + theme
                        temp_str = myarray[0] + '\t' + myarray[1] + '\t' + sec_str
                else:
                    album = ''
                    sec_array = myarray[2].strip().split()
                    i = 0
                    for slot_str in sec_array:
                        if slot_str == 'param:album':
                            album = sec_array[i + 1]
                        i += 1
                    if len(album) > 0:
                        sec_str = '播放专辑' + album + '下的歌曲'
                        temp_str = myarray[0] + '\t' + myarray[1] + '\t' + sec_str
            elif myarray[0] == 'Instruction':
                if myarray[2].find('predicate:instruction') != -1:
                    instruction_type = ''
                    sec_array = myarray[2].strip().split()
                    for slot_str in sec_array:
                        if slot_str.startswith('type:'):
                            instruction_type = slot_str[5:]
                    if len(instruction_type) > 0:
                        sec_str = '执行“' + instruction_type + '”指令'
                        temp_str = myarray[0] + '\t' + myarray[1] + '\t' + sec_str
                    else:
                        # 其他类型集中起来看看
                        exception_list.append(sentence)
                else:
                    # 其他类型集中起来看看
                    exception_list.append(sentence)
            elif myarray[0] == 'JPRadio':
                artist = ''
                song = ''
                sec_array = myarray[2].strip().split()
                pattern = re.compile('(param:typeMain|param:name|param:typeSub)')
                i = 0
                for slot_str in sec_array:
                    if pattern.match(slot_str):
                        song = sec_array[i + 1]
                    elif slot_str == 'param:artist':
                        artist = sec_array[i + 1]
                    i += 1
                if len(artist) > 0 and len(song) > 0:
                    sec_str = '播放' + artist + '的' + song
                    temp_str = myarray[0] + '\t' + myarray[1] + '\t' + sec_str
                elif len(artist) > 0:
                    sec_str = '播放' + artist + '的节目'
                    temp_str = myarray[0] + '\t' + myarray[1] + '\t' + sec_str
        if len(temp_str) > 0:
            str_map[temp_str] = str_map[temp_str] + 1 if str_map.has_key(temp_str) else 1
    # 写入文件
    num = 0
    for k, v in zip(str_map.iterkeys(), str_map.itervalues()):
        num += v
        out_list.append(k + '\t' + str(v))
    write_file(out_path, out_list)
    print num
    # write_file(exception_path, exception_list)


def count_response(path):
    data = read_file(path)
    count = dict()
    for sentence in data:
        myarray = sentence.split('\t|\t')
        if myarray[3] == '1':
            continue
        if count.has_key(myarray[0]):
            count[myarray[0]] = count[myarray[0]]+1
        else:
            count[myarray[0]] = 1
    print count


def pipeline(path):
    # path : all_data
    dir_list = os.listdir(path)
    for dir_name in dir_list:
        # dir_name : data_20160723
        file_list = os.listdir(path+'/'+dir_name)
        local_path = path + 'Response_' +dir_name
        os.mkdir(local_path)
        for file_name in file_list:
            prefix = file_name[: -4]
            print prefix
            first_filter(path+'/'+dir_name+'/'+file_name, 'data/first/'+prefix+'_first.txt', 'data/first/'+prefix+'_exception.txt')
            sec_filter('data/first/'+prefix+'_first.txt', local_path+'/response_'+prefix+'.txt', 'data/second/exception_'+ prefix +'.txt')


def get_list_tag(path):
    file_list = os.listdir(path)
    list_list = set()
    instruction_list = set()
    for file_name in file_list:
        file_name = path + '/' + file_name
        data = read_file(file_name)
        for sentence in data:
            # print sentence
            myarray = sentence.split('\t|\t')
            temp_str = ''
            if myarray[3] == '1':
                continue
            else:
                if myarray[0] == 'SongSearch':
                    if myarray[2].find('predicate:belongTags') != -1:
                        tag = ''
                        sec_array = myarray[2].strip().split()
                        for slot_str in sec_array:
                            if slot_str.startswith('tag:'):
                                tag = slot_str[4:]
                        if len(tag) > 0:
                            list_list.add(tag)
                elif myarray[0] == 'Instruction':
                    if myarray[2].find('predicate:instruction') != -1:
                        instruction_type = ''
                        sec_array = myarray[2].strip().split()
                        for slot_str in sec_array:
                            if slot_str.startswith('type:'):
                                instruction_type = slot_str[5:]
                        if len(instruction_type) > 0:
                            instruction_list.add(instruction_type)
    # print instruction_list
    for tag in list_list:
        print tag
    # print list_list


if __name__ == '__main__':
    # # data = read_file('C:/Users/lizeyu/Downloads/2016-09-23_2016-09-15_2016-09-15.txt')
    # # pk_map = count_pk(data)
    # # print pk_map
    # sentence = '智能音箱X2	SS02411154500022	iata410f6ff@gz01ec0b360eb3462c00	广东	深圳市	unknown	SongSearch	2016-09-15 23:48:06	在水一方。	--		"{""text"":""在水一方。"",""serviceType"":""LL_MQA"",""rc"":""0"",""score"":""99.679840"",""rec"":""MusicQA	TextSearch	MatchSentence	在水一方	Score	99.679840	predicate:sing	在水一方	param:song	在水一方	"",""semantic"":{""eType"":1001,""predicate"":""sing"",""slotsMatch"":""true"",""slots"":{""song"":""在水一方""}},""data"":{""totalCount"":""113"",""begin"":""0"",""end"":""15"",""from"":""qa"",""result"":[{""hotlevel"":""A"",""singerinfo"":[{""singer"":""邓丽君"",""singerid"":""2354556""}],""song"":""在水一方"",""songid"":""46367679""},{""hotlevel"":""A"",""singerinfo"":[{""singer"":""李健"",""singerid"":""3574""}],""song"":""在水一方"",""songid"":""4293878""},{""hotlevel"":""B"",""singerinfo"":[{""singer"":""汪东城"",""singerid"":""449573""}],""song"":""在水一方"",""songid"":""5828623""},{""hotlevel"":""B"",""singerinfo"":[{""singer"":""陈瑞"",""singerid"":""1910254""}],""song"":""在水一方"",""songid"":""45232057""},{""hotlevel"":""B"",""singerinfo"":[{""singer"":""费玉清"",""singerid"":""278025""}],""song"":""在水一方"",""songid"":""11085585""},{""hotlevel"":""B"",""singerinfo"":[{""singer"":""韦唯"",""singerid"":""157977""}],""song"":""在水一方"",""songid"":""6108460""},{""hotlevel"":""A"",""singerinfo"":[{""singer"":""马吟吟"",""singerid"":""225111""}],""song"":""在水一方"",""songid"":""47916491""},{""hotlevel"":""B"",""singerinfo"":[{""singer"":""许茹芸"",""singerid"":""391621""}],""song"":""在水一方"",""songid"":""7177304""},{""hotlevel"":""B"",""singerinfo"":[{""singer"":""高胜美"",""singerid"":""30956""}],""song"":""在水一方"",""songid"":""45095581""},{""hotlevel"":""B"",""singerinfo"":[{""singer"":""许飞"",""singerid"":""2347355""}],""song"":""在水一方"",""songid"":""5397059""},{""hotlevel"":""A"",""singerinfo"":[{""singer"":""刘乐"",""singerid"":""39237""}],""song"":""在水一方"",""songid"":""38440889""},{""hotlevel"":""B"",""singerinfo"":[{""singer"":""赵鹏"",""singerid"":""433121""}],""song"":""在水一方"",""songid"":""5376048""},{""hotlevel"":""B"",""singerinfo"":[{""singer"":""纯音乐"",""singerid"":""2554975""}],""song"":""在水一方"",""songid"":""58286792""},{""hotlevel"":""B"",""singerinfo"":[{""singer"":""黑鸭子"",""singerid"":""172502""}],""song"":""在水一方"",""songid"":""46149869""},{""hotlevel"":""B"",""singerinfo"":[{""singer"":""高凌风"",""singerid"":""34620""}],""song"":""在水一方"",""songid"":""8599632""}]},""debug"":{""currentinfo"":{},""mqa"":{""predicate"":""sing"",""score"":""99.679840"",""pop"":""1.124040"",""match"":""1.000000"",""symbol"":""----"",""preferment"":""0.902500"",""tolerant"":""1.000000""},""cqa"":{""score"":""0.000000"",""service"":""restaurantX"",""matchScore"":""100.000000""},""radio"":{""score"":""0.000000""},""businessType"":""vbox_4.0"",""expect"":""null""}}"'
    # myarray = sentence.split('\t',10)
    # # for string in myarray:
    # #     print string
    # print myarray[10].strip()
    # json_str = myarray[10].strip()[1:-1]
    # json_str = json_str.replace('""' , '"')
    # print json_str
    # sentence = '{"text":"在水一方。","serviceType":"LL_MQA","rc":"0","score":"99.679840","rec":"MusicQA	TextSearch	MatchSentence	在水一方	Score	99.679840	predicate:sing	在水一方	param:song	在水一方	","semantic":{"eType":1001,"predicate":"sing","slotsMatch":"true","slots":{"song":"在水一方"}},"data":{"totalCount":"113","begin":"0","end":"15","from":"qa","result":[{"hotlevel":"A","singerinfo":[{"singer":"邓丽君","singerid":"2354556"}],"song":"在水一方","songid":"46367679"},{"hotlevel":"A","singerinfo":[{"singer":"李健","singerid":"3574"}],"song":"在水一方","songid":"4293878"},{"hotlevel":"B","singerinfo":[{"singer":"汪东城","singerid":"449573"}],"song":"在水一方","songid":"5828623"},{"hotlevel":"B","singerinfo":[{"singer":"陈瑞","singerid":"1910254"}],"song":"在水一方","songid":"45232057"},{"hotlevel":"B","singerinfo":[{"singer":"费玉清","singerid":"278025"}],"song":"在水一方","songid":"11085585"},{"hotlevel":"B","singerinfo":[{"singer":"韦唯","singerid":"157977"}],"song":"在水一方","songid":"6108460"},{"hotlevel":"A","singerinfo":[{"singer":"马吟吟","singerid":"225111"}],"song":"在水一方","songid":"47916491"},{"hotlevel":"B","singerinfo":[{"singer":"许茹芸","singerid":"391621"}],"song":"在水一方","songid":"7177304"},{"hotlevel":"B","singerinfo":[{"singer":"高胜美","singerid":"30956"}],"song":"在水一方","songid":"45095581"},{"hotlevel":"B","singerinfo":[{"singer":"许飞","singerid":"2347355"}],"song":"在水一方","songid":"5397059"},{"hotlevel":"A","singerinfo":[{"singer":"刘乐","singerid":"39237"}],"song":"在水一方","songid":"38440889"},{"hotlevel":"B","singerinfo":[{"singer":"赵鹏","singerid":"433121"}],"song":"在水一方","songid":"5376048"},{"hotlevel":"B","singerinfo":[{"singer":"纯音乐","singerid":"2554975"}],"song":"在水一方","songid":"58286792"},{"hotlevel":"B","singerinfo":[{"singer":"黑鸭子","singerid":"172502"}],"song":"在水一方","songid":"46149869"},{"hotlevel":"B","singerinfo":[{"singer":"高凌风","singerid":"34620"}],"song":"在水一方","songid":"8599632"}]},"debug":{"currentinfo":{},"mqa":{"predicate":"sing","score":"99.679840","pop":"1.124040","match":"1.000000","symbol":"----","preferment":"0.902500","tolerant":"1.000000"},"cqa":{"score":"0.000000","service":"restaurantX","matchScore":"100.000000"},"radio":{"score":"0.000000"},"businessType":"vbox_4.0","expect":"null"}}'
    # parsed_json = json.loads(json_str, strict=False)
    # if parsed_json.has_key('rec'):
    #     print parsed_json['rec']
    # first_filter('D:/dingdong/data_20161022/2016-10-22_2016-10-21_2016-10-21.txt', 'data/normal.txt', 'data/exception.txt')
    # count_response('data/normal.txt')
    # sec_filter('data/normal.txt', 'data/output.txt', 'data/sec_exception.txt')
    pipeline('D:/dingdong/all_data')
    # get_list_tag('data/right_format')
    # sec_filter('E:/pyworkspace/Test/data/first/2016-10-02_2016-09-03_2016-09-03_first.txt', 'data/watch.txt', '')

