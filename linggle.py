#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sqlite3
from flask import Flask, g, render_template, Response, json
from contextlib import closing
from time import ctime
import pickle
import logging
from examples import get_Examples
from nltk.stem import WordNetLemmatizer
from collections import defaultdict
import HLIParser
from query import checkIfallStar, similar_query_split, getSearchResults_Inside, query_extend

DATABASE = 'linggle.db3'
DEBUG = True
SECRET_KEY = 'hey yo linggle'
USERNAME = 'admin'
PASSWORD = 'default'

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# create our little application :)
app = Flask(__name__)
app.config.from_object(__name__)
# app.config.from_envvar('FLASKR_SETTINGS', silent=True)

##=============cluster data loading===================
vo_clusters_dic = pickle.loads(open('cluster_vo_large.pick','r').read())
#vs_clusters_dic = pickle.loads(open('cluster_vs_large.pick','r').read())
#ov_clusters_dic = pickle.loads(open('cluster_ov_large.pick','r').read())

lemmatizer = WordNetLemmatizer()

def connect_db():
    return sqlite3.connect(app.config['DATABASE'])


def init_db():
    with closing(connect_db()) as db:
        with app.open_resource('schema.sql') as f:
            db.cursor().executescript(f.read())
        db.commit()

def compare(x,y):
    if x[2] > y[2]:
        return -1
    elif x[2] < y[2]:
        return 1
    elif x[1] > y[1]:
        return -1
    elif x[1] < y[1]:
        return 1
    else:
        return 0

def ConvertPercentage(percentage):
    if percentage < 1:
        percentage = " < 1%"
    else:
        percentage = " %2.0f %%" % percentage    
    return percentage

def ConvertFreq(freq):
    if int(freq) >= 100:
        freq_str = "{:,d}".format(int(freq) / 100 * 100)
    else:
        freq_str = str(int(freq)).strip()    
    return freq_str

@app.before_request
def before_request():
    g.db = connect_db()


@app.teardown_request
def teardown_request(exception):
    g.db.close()


@app.route('/')                 # Linggle Homepage
def homepage():
    return render_template('index.html')
    # cur = g.db.execute('select title, text from entries order by id desc')
    # entries = [dict(title=row[0], text=row[1]) for row in cur.fetchall()]
    # return render_template('show_entries.html', entries=entries)

@app.route('/sent/<sent>')
def sentence(sent):
    tokens = sent.strip().replace('?','').lower().split()
    result = HLIParser.parser(tokens) if len(tokens) > 0 else ""
    return Response(result)

@app.route('/examples/<ngram>')
def examples(ngram):
    return Response(get_Examples(ngram), mimetype='application/json')

@app.route('/API/<query>')
def APIquery(query):
    query_in = query.replace("_"," ")
    # query_in = request.GET.get('query')
    logger.debug('=' * 20)
    logger.debug('get the request: ' + str(query_in))

    # print '=' * 20
    # print "get the request", ctime()
    # print "ori = ", query_in

    query_in = " ".join(query_in.replace("%20", " ").split())

    Search_Result = []

    if len(query_in) > 0:

        ##先檢查是否屬於all star狀況
        if checkIfallStar(query_in):  # 是的話特別處理
            print "All Star!!!"
            ##檢查是否有任何一個token是屬於alternative 拆解之(若有多個 拆比較少的那一個)
            new_queries = similar_query_split(query_in)
            print new_queries
            if len(new_queries) > 0:  # 成功轉換
                for query in new_queries:
                    Search_Result_temp = getSearchResults_Inside(query)
                    ##將數次查詢的結果整合到一個資料庫中以便排序
                    Search_Result.extend(Search_Result_temp)

        else:
            print "not all star"
            if query_in.count("?") + query_in.count("...") == 0:  # 直接處理
                Search_Result = getSearchResults_Inside(query_in)
            else:
                new_queries = query_extend(query_in)
                for query in new_queries:
                    Search_Result_temp = getSearchResults_Inside(query)
                    ##將數次查詢的結果整合到一個資料庫中以便排序
                    Search_Result.extend(Search_Result_temp)

    total_no = sum([data[1] for data in Search_Result])
    ##排序 以便取Top N
    #Search_Result.sort(key=lambda x: x[1], reverse=True)
    Search_Result.sort(cmp = compare)

    ##取前Top N就好
    Search_Result = [[data[0], data[1], data[1] * 100 / total_no] for data in Search_Result]

    ## 進行統計跟格式的refinement
    Return_Result = []
    for i in range(len(Search_Result)):

        phrase, freq, percentage = Search_Result[i]

        if int(freq) >= 100:
            freq_str = "{:,d}".format(int(freq) / 100 * 100)
        else:
            freq_str = str(int(freq)).strip()

        if percentage < 1:
            percentage = " < 1%"
        else:
            percentage = " %2.0f %%" % percentage

        Return_Result.append((phrase.replace('<span class="SW">',"").replace("</span>",""),freq,percentage))

    
    resp = Response(json.dumps(Return_Result), status=200, mimetype='application/json')
    return resp

@app.route('/query/<query>')
def query(query):

    CLUSTER_RESULT_LIMIT = 300
    TRADITIONAL_RESULT_LIMIT = 100

    query_in = query
    
    logger.debug('=' * 20)
    logger.debug('get the request: ' + str(query_in))

    query_words = " ".join(query_in.replace("%20", " ").split())
    query_in = query_words.split()

##    ##先看有沒有cache檔
##    try:
##        conn = sqlite3.connect("LinggleII/Data/cache.db3")
##        cursor = conn.cursor()
##        Result = cursor.execute('select result from cache where query =="%s"' %
##                                query_in).fetchone()[0]
##        conn.close()
##        Return_Result = pickle.loads(Result)
##        return Response(json.dumps(Return_Result), mimetype="application/json")
##
##    except:  # 沒有就開始查詢
##        print "not found"
##        pass

    Search_Result = []

    if len(query_in) > 0:

        ##配合新版搭配詞功能，檢查是否符合特定搭配詞狀況
        if len(query_in) == 2 and query_in[1] == "$N" and query_in[0].isalpha(): ##VN
            collocates = [(data[0].replace("<strong>","").replace("</strong>","").split(),data[1]) for data in getSearchResults_Inside(" ".join(query_in))[:CLUSTER_RESULT_LIMIT]]
            ##去除不必要的 strong 標記，並且記錄原型化  做為 cluster　次數的查詢來源           
            collocates_dic = defaultdict(list)
            total_no = 0.0
            for data in collocates:
                collocates_dic[lemmatizer.lemmatize(data[0][1],'n')].append((data[0][1],data[1]))
                total_no += data[1]

            ##取得 cluster 狀況
            clusters = vo_clusters_dic[query_in[0]]            
            Result_Clusters = []
            
            for cluster in clusters:
                Detailed_Cluster = []
                cluster_cnt = 0.0
                words = []
                for sub_cluster in cluster:
                    words.extend(sub_cluster)
                ##取得個別字出現的次數
                for word in words:
                    if len(collocates_dic[word]) > 0:
                        for collocate in collocates_dic[word]:
                            cluster_cnt += collocate[1]
                            Detailed_Cluster.append((collocate[0],collocate[1]))
                ##開始排序　取出 label
                Detailed_Cluster.sort(key = lambda x:x[1], reverse = True)
                print Detailed_Cluster
                if len(Detailed_Cluster) > 0: ##有查到字才留
                    ##進行格式化
                    now_datas = {}
                    now_datas['count'] = cluster_cnt
                    now_datas['percent'] = ConvertPercentage(cluster_cnt*100/total_no)
                    now_datas['tag'] = Detailed_Cluster[0][0].upper()
                    temp_data = [(query_in[0]+" "+data[0],ConvertFreq(data[1]),ConvertPercentage(data[1]*100/total_no)) for data in Detailed_Cluster]
                    now_datas['data'] = temp_data
                    
                    Result_Clusters.append(now_datas)

            Result_Clusters.sort(key = lambda x:x['count'], reverse = True)
            for cluster in Result_Clusters:
                cluster['count'] = ConvertFreq(cluster['count'])

            Return_Result = ("new",Result_Clusters)            

        else:##傳統查詢
            query_in = query_words
            ##先檢查是否屬於all star狀況
            if checkIfallStar(query_in):  # 是的話特別處理
                print "All Star!!!"
                ##檢查是否有任何一個token是屬於alternative 拆解之(若有多個 拆比較少的那一個)
                new_queries = similar_query_split(query_in)
                print new_queries
                if len(new_queries) > 0:  # 成功轉換
                    for query in new_queries:
                        Search_Result_temp = getSearchResults_Inside(query)
                        ##將數次查詢的結果整合到一個資料庫中以便排序
                        Search_Result.extend(Search_Result_temp)

            else:
                new_queries = query_extend(query_in)
                for query in new_queries:
                    Search_Result_temp = getSearchResults_Inside(query)
                    ##將數次查詢的結果整合到一個資料庫中以便排序
                    Search_Result.extend(Search_Result_temp)

            ##避免搜尋到重複的結果
            Search_Result = list(set(Search_Result))
            total_no = sum([data[1] for data in Search_Result])
            ##排序 以便取Top N
            #Search_Result.sort(key=lambda x: x[1], reverse=True)
            Search_Result.sort(cmp = compare)

            ##取前Top N就好
            Search_Result = [[data[0], data[1], data[1] * 100 / total_no]
                             for data in Search_Result[:TRADITIONAL_RESULT_LIMIT]]

            ## 進行統計跟格式的refinement
            Return_Result = []
            for i in range(len(Search_Result)):

                phrase, freq, percentage = Search_Result[i]

                if int(freq) >= 100:
                    freq_str = "{:,d}".format(int(freq) / 100 * 100)
                else:
                    freq_str = str(int(freq)).strip()

                if percentage < 1:
                    percentage = " < 1%"
                else:
                    percentage = " %2.0f %%" % percentage

                # updated
                Return_Result.append({"phrase": phrase, "count": freq,
                                     "percent": percentage, "count_str": freq_str})

            Return_Result = ("old",Return_Result)

    ##        ##存下來 做為cache
    ##        try:
    ##            conn = sqlite3.connect(
    ##                "/home/nlplab/Sites/LinggleII/LinggleII/Data/Cache.db3")
    ##            cursor = conn.cursor()
    ##            cursor.execute("insert into cache values('%s','%s')" %
    ##                           (query_in.replace("'", "''"), pickle.dumps(Return_Result).replace("'", "''")))
    ##            conn.commit()
    ##            conn.close()
    ##        except:
    ##            print "save error"

        resp = Response(json.dumps(Return_Result), status=200, mimetype='application/json')
        return resp        
        
    else:
        Return_Result = ("old",[])
        resp = Response(json.dumps(Return_Result), status=200, mimetype='application/json')
        return resp



if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='Development Server Help')
    parser.add_argument(
        "-d", "--debug", action="store_true", dest="debug_mode",
        help="run in debug mode", default=False)
    parser.add_argument("-p", "--port", dest="port",
                        help="port of server (default:%(default)s)", type=int, default=5000)

    cmd_args = parser.parse_args()
    app_options = {"port": cmd_args.port, 'host':'0.0.0.0'}

    if cmd_args.debug_mode == False:
        app_options["debug"] = True
        app_options["use_debugger"] = False
        app_options["use_reloader"] = False
        app_options["host"] = "0.0.0.0"
        print "yes"

    app.run(**app_options)
 
