#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sqlite3

from flask import Flask, g, render_template, Response, json, request, session, escape, redirect, url_for

from contextlib import closing
from time import ctime
import pickle
import logging
from examples import get_Examples

import HLIParser
from query import checkIfallStar, similar_query_split, getSearchResults_Inside, query_extend

import user, json, urllib

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


def connect_db():
    return sqlite3.connect(app.config['DATABASE'])


def init_db():
    with closing(connect_db()) as db:
        with app.open_resource('schema.sql') as f:
            db.cursor().executescript(f.read())
        db.commit()


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

@app.route('/query/<query>')
def query(query):

    # Maxis # 架構
    # Maxis # 要把 router / controller 分開, 不然這個 linggle.py 太大!!!
    # Maxis #

    query_in = query
    user.querylog(urllib.unquote(query), session['uid'])

    # query_in = request.GET.get('query')
    logger.debug('=' * 20)
    logger.debug('get the request: ' + str(query_in))

    # Maxis # 應該改成 urllib.unquote() 就好 ?!

    query_in = " ".join(query_in.replace("%20", " ").split())

    ##先看有沒有cache檔
    try:
        conn = sqlite3.connect("LinggleII/Data/cache.db3")
        cursor = conn.cursor()
        Result = cursor.execute('select result from cache where query =="%s"' %
                                query_in).fetchone()[0]
        conn.close()
        Return_Result = pickle.loads(Result)
        return Response(json.dumps(Return_Result), mimetype="application/json")

    except:  # 沒有就開始查詢
        print "not found"
        pass

    # print query_in

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
            if query_in.count("?") + query_in.count("...") == 0:  # 直接處理
                Search_Result = getSearchResults_Inside(query_in)
            else:
                new_queries = query_extend(query_in)
                for query in new_queries:
                    Search_Result_temp = getSearchResults_Inside(query)
                    ##將數次查詢的結果整合到一個資料庫中以便排序
                    Search_Result.extend(Search_Result_temp)

    total_no = sum([data[1] for data in Search_Result])
    ##排序 以便取Top N
    Search_Result.sort(key=lambda x: x[1], reverse=True)

    ##取前Top N就好
    Search_Result = [[data[0], data[1], data[1] * 100 / total_no]
                     for data in Search_Result[:100]]

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
        # Search_Result[i] = (phrase,freq,freq_str,percentage)

    ##存下來 做為cache
    try:
        conn = sqlite3.connect(
            "/home/nlplab/Sites/LinggleII/LinggleII/Data/Cache.db3")
        cursor = conn.cursor()
        cursor.execute("insert into cache values('%s','%s')" %
                       (query_in.replace("'", "''"), pickle.dumps(Return_Result).replace("'", "''")))
        conn.commit()
        conn.close()
    except:
        print "save error"

    print "return the result", ctime()

    resp = Response(
        json.dumps(Return_Result), status=200, mimetype='application/json')
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
    app_options = {"port": cmd_args.port}

    if cmd_args.debug_mode:
        app_options["debug"] = True
        app_options["use_debugger"] = False
        app_options["use_reloader"] = False

    app.run(**app_options)
 
