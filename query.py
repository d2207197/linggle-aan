# -*- coding: utf-8 -*-
from time import ctime
import socket

def checkIfallStar(query_in):
    # check whether the query would be transformed into all star
    # Search_Result = []
    # transform the query into Joanne's server
    words = query_in.split()
    words2 = []

    for i in range(len(words)):
        word = words[i]
        if word == "*":  # 有特殊語法
            words2.append("*")
        elif word[0] == "+":
            words2.append("*")
        elif word[0] == "$":
            words2.append("*")
        else:
            words2.append(word)

    if len([data for data in words2 if data == "*"]) - len(words2) == 0:  # all star
        return True
    else:
        return False


def getParaphrase(word, pos=""):
    # get paraphrase candidate from Patric Pantel database
    Score_T = 0.05
    conn = sqlite3.connect("LinggleII/Data/PatricPantel.db3")
    cursor = conn.cursor()
    if len(pos) == 0:
        SQL = "select SimWord from PatricPantel where head =='%s' and score > %f order by score desc" % (word, Score_T)
        candidates = [word] + [data[0].lower(
        ) for data in cursor.execute(SQL).fetchall()]
        conn.close()
        return candidates


def getRotateNgramResults(query):
    query = query.replace("%20", " ")
    clisock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    clisock.connect(('nlp0.cs.nthu.edu.tw', 23000))  # nlp0 must run the Sever:
    clisock.send(query)
    Datas = ""
    recdata = clisock.recv(10000)
    while recdata:
        Datas += recdata
        recdata = clisock.recv(10000)

    clisock.close()

    # print Datas
    Search_Results = [data2 for data2 in [data.split(
        "\t") for data in Datas.split("\n")] if len(data2) == 2]
    if len(Search_Results) == 0:
        # maybe not TAB
        Search_Results = [(" ".join(data2[:-1]), data2[-1]) for data2 in [
                          data.split(" ") for data in Datas.split("\n")]]

    return Search_Results


def getSearchResults_Inside(query_in):
    print "prepare to submit query"
    Search_Result = []
    # transform the query into Joanne's server
    words = query_in.split()
    words2 = []
    word_filter = {}
    mark_list = []

    for i in range(len(words)):

        word = words[i]

        if word == "*":  # 有特殊語法
            words2.append("*")
            mark_list.append(i)
        elif word[0] == "+":
            paraphrase = getParaphrase(word[1:])
            if len(paraphrase) == 0:  # 找不到就查自己就好
                words2.append(word[0][1:])
                word_filter[i] = {word[0][1:]: True}
            else:
                words2.append("*")
                word_filter[i] = dict([(data, True) for data in paraphrase])
            mark_list.append(i)

        elif word.count("|") > 0:
            # words2.append("*")
            words2.append(word)
            word_filter[i] = dict([(data, True) for data in word.split("|")])
            mark_list.append(i)
        else:
            words2.append(word)
            if word[0] == "$":
                mark_list.append(i)

    query_out = " ".join(words2)

    print "submit query", ctime()
    temp_Result = [[data[0].split(), data[1]] for data in getRotateNgramResults(query_out) if len(data) == 2 and len(data[0].split()) > 0]
    print "get result", ctime()
    # start filtering
    for posi in word_filter:
        temp_Result = [data for data in temp_Result if data[0][
            posi] in word_filter[posi]]

    ## 標記查詢的特殊詞
    for posi in mark_list:
        for i in range(len(temp_Result)):
            temp_Result[i][0][posi] = '<span class="SW">' + \
                temp_Result[i][0][posi] + "</span>"

    Search_Result = [(" ".join(data[0]), float(data[1]))
                     for data in temp_Result]

    return Search_Result


def query_extend(query_in):
    starlist = ["*", "* *", "* * *", "* * * *"]
    queries = [[]]

    ## 將query轉換成多組以便整合資料
    words = query_in.split()

    for i in range(len(words)):

        word = words[i]

        if word == "...":
            queries.extend(
                [data + [star] for data in queries for star in starlist])
        elif word[0] == "?":
            if len(word) == 1:  # 只有問號
                queries.extend([data + ["*"] for data in queries])
            else:
                queries.extend([data + [word[1:]]
                               for data in queries for star in starlist])
        else:  # 基本型變化
            queries = [data + [word] for data in queries]

    queries = [data for data in list(
        set([" ".join(query) for query in queries])) if data.count(" ") < 5]
    return queries


def similar_query_split(query_in):
    queries = [[]]

    ##將query轉換成多組以便整合資料
    words = query_in.split()
    ##先看有幾組 similar
    similars = [(i, getParaphrase(
        words[i][1:])) for i in range(len(words)) if words[i][0] == "+"]
    print similars
    if len(similars) == 0:  # 沒有則離開
        return []
    else:
        similars.sort(key=lambda x: len(x[1]))  # 少的排前面

    target_posi = similars[0][0]

    for i in range(len(words)):
        word_now = words[i]
        if i == target_posi:
            queries = [data + [data2] for data in queries for data2 in similars[0][1][:10]]  # 先做前十名就好
        else:  # 照原字
            queries = [data + [word_now] for data in queries]

    queries = [" ".join(query) for query in queries]
    return queries
