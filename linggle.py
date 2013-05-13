#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sqlite3, os, pickle, logging
from flask import Flask, g, render_template, Response, json
from nltk.stem import WordNetLemmatizer
from collections import defaultdict
from urllib import unquote
from contextlib import closing

# our own
import getSampleSent, HLIParser
from query import checkIfallStar, similar_query_split, getSearchResults_Inside, query_extend

DATABASE = 'linggle.db3'
DEBUG = True
SECRET_KEY = 'hey yo linggle'
USERNAME = 'admin'
PASSWORD = 'default'

CLUSTER_ROOT = ['/corpus/Linggle/', '']

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# create our little application :)
app = Flask(__name__)
app.config.from_object(__name__)
# app.config.from_envvar('FLASKR_SETTINGS', silent=True)

##=============cluster data loading===================
for path in CLUSTER_ROOT:
    # print path
    if os.path.exists(path):
        CLUSTER_ROOT_PATH = path
        break
    else:
        CLUSTER_ROOT_PATH = ''

## POS dictionary
logger.debug('Load bncwordlemma.pick')
BNC_POS_Dic = pickle.loads(open( CLUSTER_ROOT_PATH + 'bncwordlemma.pick','r').read())

## clusters of objects for given VERB
logger.debug('Load cluster_vo_large.pick')
vo_clusters_dic = pickle.loads(open( CLUSTER_ROOT_PATH + 'cluster_vo_large.pick','r').read())

## clusters of VERBs for given NOUN
logger.debug('Load cluster_ov_large.pick')
ov_clusters_dic = pickle.loads(open( CLUSTER_ROOT_PATH + 'cluster_ov_large.pick','r').read())

## clusters of NOUN for given Adjective
logger.debug('Load cluster_an_nouns.pick')
an_clusters_dic = pickle.loads(open( CLUSTER_ROOT_PATH + 'cluster_an_nouns.pick','r').read())

## clusters of Adjective for given Noun
logger.debug('Load cluster_an_adj.pick')
na_clusters_dic = pickle.loads(open( CLUSTER_ROOT_PATH + 'cluster_an_adj.pick','r').read())

## clusters of Subject for given Verb
logger.debug('Load cluster_vs_large.pick')
vs_clusters_dic = pickle.loads(open( CLUSTER_ROOT_PATH + 'cluster_vs_large.pick','r').read())

## clusters of Verbs for given Subject
logger.debug('Load cluster_sv_large.pick')
sv_clusters_dic = pickle.loads(open( CLUSTER_ROOT_PATH + 'cluster_sv_large.pick','r').read())

## clusters of Similar Adjecive
logger.debug('Load new_syno_adj_scores.pick')
adj_clusters_dic = pickle.loads(open( CLUSTER_ROOT_PATH + 'new_syno_adj_scores.pick','r').read())

## clusters of Similar Noun
logger.debug('Load new_syno_noun_scores.pick')
noun_clusters_dic = pickle.loads(open( CLUSTER_ROOT_PATH + 'new_syno_noun_scores.pick','r').read())

## clusters of Similar Verb 
logger.debug('Load new_syno_verb_scores.pick')
verb_clusters_dic = pickle.loads(open( CLUSTER_ROOT_PATH + 'new_syno_verb_scores.pick','r').read())

logger.debug('Init WordNetLemmatizer')
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

    LinggleSamplesConn = sqlite3.connect("/corpus/Linggle/LinggleSamples.db3")
    cur = LinggleSamplesConn.cursor()
    examples = getSampleSent.getSamples(str(unquote(ngram)), cur)
    print 'examples',examples
    status = examples['status']
    source = examples['source']
    sent = examples['sent']
    # except:
    # logger.error('example fetch error')

    return_data = {'status':status, 'sent':sent, 'source':source }

    cur.close()
    LinggleSamplesConn.close()

    return Response(json.dumps(return_data), mimetype='application/json')

@app.route('/API/<query>')
def APIquery(query):
    query_in = query.replace("_"," ")
    # query_in = request.GET.get('query')
    # logger.debug('=' * 20)
    logger.debug('# GET THE QUERY: "' + str(query_in)+ '"')

    query_in = " ".join(query_in.replace("%20", " ").split())

    Search_Result = []

    if len(query_in) > 0:

        ##先檢查是否屬於all star狀況
        if checkIfallStar(query_in):  # 是的話特別處理
            # print "All Star!!!"
            ##檢查是否有任何一個token是屬於alternative 拆解之(若有多個 拆比較少的那一個)
            new_queries = similar_query_split(query_in)
            # print new_queries
            if len(new_queries) > 0:  # 成功轉換
                for query in new_queries:
                    Search_Result_temp = getSearchResults_Inside(query)
                    ##將數次查詢的結果整合到一個資料庫中以便排序
                    Search_Result.extend(Search_Result_temp)

        else:
            # print "not all star"
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

    logger.debug('# GET THE QUERY: "' + str(query_in)+ '"')

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
    Final_Result = []

    if len(query_in) > 0:
		if len(query_in) > 1:
			##傳統查詢
			query_in = query_words
			##先檢查是否屬於all star狀況
			if checkIfallStar(query_in):  # 是的話特別處理
				# print "All Star!!!"
				##檢查是否有任何一個token是屬於alternative 拆解之(若有多個 拆比較少的那一個)
				new_queries = similar_query_split(query_in)
				# print new_queries
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

			Final_Result.append(("old",Return_Result))
			query_in = query_in.split()

			##配合新版搭配詞功能，檢查是否符合特定搭配詞狀況
			if len(query_in) == 2 and query_in[0].isalpha() and query_in[1] in ["$N","$V"]: ##VERB $N or ADJ $N or Subj $V

				if query_in[1] == "$N": ##VERB $N or ADJ $N
					collocates = [(data[0].replace("<strong>","").replace("</strong>","").split(),data[1]) for data in getSearchResults_Inside(" ".join(query_in))[:CLUSTER_RESULT_LIMIT]]
					##去除不必要的 strong 標記，並且記錄原型化  做為 cluster　次數的查詢來源
					collocates_dic = defaultdict(list)
					total_no = 0.0
					for data in collocates:
						collocates_dic[lemmatizer.lemmatize(data[0][1],'n')].append((data[0][1],data[1]))
						total_no += data[1]

					##取得 cluster 狀況
					##跟據首字最有可能的詞性進行搜尋

					POS_Candi = [data[1] for data in BNC_POS_Dic[query_in[0].lower()] if data[1] in "av"][0]

					if POS_Candi == "a":
						clusters = an_clusters_dic[query_in[0]]
					else:
						clusters = vo_clusters_dic[query_in[0]]

					##開始分析 cluster的內容
					Result_Clusters = []

					for cluster in clusters:
						Sub_Clusters = [] ##記錄所有 sub-cluster 的內容
						cluster_cnt = 0.0
						cluster_wno = 0 ##記錄此 cluster 的總字數
						max_cnt = 0.0
						label_candi = "" ##記錄此cluster的代表字

						for sub_cluster in cluster:
							Sub_Cluster_Details = [] ##記錄目前處理的 sub-cluster (level 2)的內容
							sub_cluster_cnt = 0.0
							##取得該cluster(level 2)個別字出現的次數 以便之後sub cluster排序
							for word in sub_cluster:
								if len(collocates_dic[word]) > 0:
									for collocate in collocates_dic[word]:
										sub_cluster_cnt += collocate[1]
										cluster_cnt += collocate[1]
										cluster_wno += 1
										Sub_Cluster_Details.append((collocate[0],collocate[1]))
										##記錄Label
										if collocate[1] > max_cnt:
											max_cnt = collocate[1]
											label_candi = collocate[0]

							## 如果 Sub-Cluster 裡面至少 1 個字才呈現這個 sub-cluster
							if len(Sub_Cluster_Details) > 0:
								## 開始排序
								Sub_Cluster_Details.sort(key = lambda x:x[1], reverse = True)

								## 進行格式化
								now_datas = {}
								now_datas['count'] = sub_cluster_cnt
								now_datas['percent'] = ConvertPercentage(sub_cluster_cnt*100/total_no)
								temp_data = [(query_in[0]+" <strong>"+data[0]+"</strong>",ConvertFreq(data[1]),ConvertPercentage(data[1]*100/total_no)) for data in Sub_Cluster_Details]
								now_datas['data'] = temp_data

								Sub_Clusters.append(now_datas)

						if cluster_wno > 1: ##至少有兩個字以上在這個cluster
							## Sub-Cluster 依照總次數排序
							Sub_Clusters.sort(key = lambda x:x['count'], reverse = True)

							now_datas = {}
							now_datas['count'] = cluster_cnt
							now_datas['percent'] = ConvertPercentage(cluster_cnt*100/total_no)
							now_datas['tag'] = label_candi.upper()
							now_datas['data'] = Sub_Clusters
							Result_Clusters.append(now_datas)

					Result_Clusters.sort(key = lambda x:x['count'], reverse = True)

					for cluster in Result_Clusters:
						cluster['count'] = ConvertFreq(cluster['count'])

					Final_Result.append(("new",Result_Clusters))

				elif query_in[1] == "$V": ##SUBJ $V
					print "SUBJ_$V"
					collocates = [(data[0].replace("<strong>","").replace("</strong>","").split(),data[1]) for data in getSearchResults_Inside(" ".join(query_in))[:CLUSTER_RESULT_LIMIT]]
					##去除不必要的 strong 標記，並且記錄原型化  做為 cluster　次數的查詢來源
					collocates_dic = defaultdict(list)
					total_no = 0.0
					for data in collocates:
						collocates_dic[lemmatizer.lemmatize(data[0][1],'n')].append((data[0][1],data[1]))
						total_no += data[1]

					clusters = sv_clusters_dic[query_in[0]]

					Result_Clusters = []

					for cluster in clusters:
						Sub_Clusters = [] ##記錄所有 sub-cluster 的內容
						cluster_cnt = 0.0
						cluster_wno = 0 ##記錄此 cluster 的總字數
						max_cnt = 0.0
						label_candi = "" ##記錄此cluster的代表字

						for sub_cluster in cluster:
							Sub_Cluster_Details = [] ##記錄目前處理的 sub-cluster (level 2)的內容
							sub_cluster_cnt = 0.0
							##取得該cluster(level 2)個別字出現的次數 以便之後sub cluster排序
							for word in sub_cluster:
								if len(collocates_dic[word]) > 0:
									for collocate in collocates_dic[word]:
										sub_cluster_cnt += collocate[1]
										cluster_cnt += collocate[1]
										cluster_wno += 1
										Sub_Cluster_Details.append((collocate[0],collocate[1]))
										##記錄Label
										if collocate[1] > max_cnt:
											max_cnt = collocate[1]
											label_candi = collocate[0]

							## 如果 Sub-Cluster 裡面至少 1 個字才呈現這個 sub-cluster
							if len(Sub_Cluster_Details) > 0:
								## 開始排序
								Sub_Cluster_Details.sort(key = lambda x:x[1], reverse = True)

								## 進行格式化
								now_datas = {}
								now_datas['count'] = sub_cluster_cnt
								now_datas['percent'] = ConvertPercentage(sub_cluster_cnt*100/total_no)
								temp_data = [(query_in[0]+" <strong>"+data[0]+"</strong>",ConvertFreq(data[1]),ConvertPercentage(data[1]*100/total_no)) for data in Sub_Cluster_Details]
								now_datas['data'] = temp_data

								Sub_Clusters.append(now_datas)

						if cluster_wno > 1: ##至少有兩個字以上在這個cluster
							## Sub-Cluster 依照總次數排序
							Sub_Clusters.sort(key = lambda x:x['count'], reverse = True)

							now_datas = {}
							now_datas['count'] = cluster_cnt
							now_datas['percent'] = ConvertPercentage(cluster_cnt*100/total_no)
							now_datas['tag'] = label_candi.upper()
							now_datas['data'] = Sub_Clusters
							Result_Clusters.append(now_datas)

					Result_Clusters.sort(key = lambda x:x['count'], reverse = True)

					for cluster in Result_Clusters:
						cluster['count'] = ConvertFreq(cluster['count'])

					Final_Result.append(("new",Result_Clusters))
			# condition: $A_beach, $V_cultivate
			elif len(query_in) == 2 and query_in[0] in ["$V","$N","$A"] and query_in[1].isalpha(): ##Verb (or Adjective) for object: $V NOUN, $A NOUN; sv: $N Verb
				POS_Map_Dic = {"$N":{"POS":"n"},"$V":{"POS":'v'},"$A":{"POS":'a'}}
				##去除不必要的 strong 標記，並且記錄原型化  做為 cluster　次數的查詢來源
				collocates = [(data[0].replace("<strong>","").replace("</strong>","").split(),data[1]) for data in getSearchResults_Inside(" ".join(query_in))[:CLUSTER_RESULT_LIMIT]]

				collocates_dic = defaultdict(list)
				total_no = 0.0
				for data in collocates:

					# origin version
					# collocates_dic[lemmatizer.lemmatize(data[0][0],POS_Map_Dic[query_in[0]]["POS"])].append((data[0][0],data[1]))

					# edited by Maxis
					# solve the issue: "leading car" occurs in the results of "$V car"
					collocates_dic[data[0][0]].append((data[0][0],data[1]))

					total_no += data[1]

				##取得 cluster 狀況

				##跟據第二個字最有可能的詞性進行搜尋

				POS_Candi = [data[1] for data in BNC_POS_Dic[query_in[1].lower()] if data[1] in "nva"][0]

				if POS_Candi == "n":
					if query_in[0] == "$V":
						clusters = ov_clusters_dic[query_in[1]]
					else:
						clusters = na_clusters_dic[query_in[1]]
				elif POS_Candi == "v":
					clusters = vs_clusters_dic[query_in[1]]

				Result_Clusters = []

				for cluster in clusters:
					Sub_Clusters = [] ##記錄所有 sub-cluster 的內容
					cluster_cnt = 0.0
					cluster_wno = 0 ##記錄此 cluster 的總字數
					max_cnt = 0.0
					label_candi = "" ##記錄此cluster的代表字

					for sub_cluster in cluster:
						Sub_Cluster_Details = [] ##記錄目前處理的 sub-cluster (level 2)的內容
						sub_cluster_cnt = 0.0
						##取得該cluster(level 2)個別字出現的次數 以便之後sub cluster排序
						for word in sub_cluster:
							if len(collocates_dic[word]) > 0:
								for collocate in collocates_dic[word]:
									sub_cluster_cnt += collocate[1]
									cluster_cnt += collocate[1]
									cluster_wno += 1
									Sub_Cluster_Details.append((collocate[0],collocate[1]))
									##記錄Label
									if collocate[1] > max_cnt:
										max_cnt = collocate[1]
										label_candi = collocate[0]

						## 如果 Sub-Cluster 裡面至少 1 個字才呈現這個 sub-cluster
						if len(Sub_Cluster_Details) > 0:
							## 開始排序
							Sub_Cluster_Details.sort(key = lambda x:x[1], reverse = True)

							## 進行格式化
							now_datas = {}
							now_datas['count'] = sub_cluster_cnt
							now_datas['percent'] = ConvertPercentage(sub_cluster_cnt*100/total_no)

							temp_data = [("<strong>"+data[0]+"</strong> " + query_in[1], ConvertFreq(data[1]), ConvertPercentage(data[1]*100/total_no)) for data in Sub_Cluster_Details]
							now_datas['data'] = temp_data

							Sub_Clusters.append(now_datas)

					if cluster_wno > 1: ##至少有兩個字以上在這個cluster
						## Sub-Cluster 依照總次數排序
						Sub_Clusters.sort(key = lambda x:x['count'], reverse = True)

						now_datas = {}
						now_datas['count'] = cluster_cnt
						now_datas['percent'] = ConvertPercentage(cluster_cnt*100/total_no)
						now_datas['tag'] = label_candi.upper()
						now_datas['data'] = Sub_Clusters
						Result_Clusters.append(now_datas)

				Result_Clusters.sort(key = lambda x:x['count'], reverse = True)

				for cluster in Result_Clusters:
					cluster['count'] = ConvertFreq(cluster['count'])

				Final_Result.append(("new",Result_Clusters))
				# end if condition $A_beach, $V_cultivate

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

			resp = Response(json.dumps(Final_Result), status=200, mimetype='application/json')
			return resp
		elif query_in[0].isalpha():##查一個字預設是查 similar word
			query_word = query_in[0]
			Final_Result = []
			Joanne_Sim_Map_Dic = {"a":adj_clusters_dic,"v":verb_clusters_dic,"n":noun_clusters_dic}
			##未查先猜詞性
			try:
				POS_Candi = [data[1] for data in BNC_POS_Dic[query_in[0].lower()] if data[1] in "avn"][0]
			except:##猜不到詞性 預設名詞
				POS_Candi = "n"
				
			Sim_Dic = Joanne_Sim_Map_Dic[POS_Candi] ##使用對應的字典

			try:
				clusters = Sim_Dic[query_word]
			except:
				clusters = []
			
			##先產生傳統 (non-cluster)的結果
			Result = []
			
			for cluster in clusters:
				for sub_cluster in cluster:
					Result.extend(sub_cluster)

			##格式化
						
			Result.sort(key = lambda x:x[1], reverse = True)
			
			Result = [{"count":0,"phrase":data[0],"percent":str(data[1]).strip(),"count_str":""} for data in Result]
					
			Final_Result.append(("old",Result))
			
			##產生 cluster 的結果
			Result_Clusters = []

			for cluster in clusters:
				Sub_Clusters = [] ##記錄所有 sub-cluster 的內容
				label_candi = cluster[0][0][0].upper() ##記錄此cluster的代表字

				for sub_cluster in cluster:
					Sub_Cluster_Details = [ (data[0],str(data[1]).strip(),"") for data in sub_cluster] ##記錄目前處理的 sub-cluster (level 2)的內容

					## 如果 Sub-Cluster 裡面至少 1 個字才呈現這個 sub-cluster
					if len(Sub_Cluster_Details) > 0:
						## 進行格式化
						now_datas = {}
						now_datas['count'] = 0
						now_datas['percent'] = ""
						now_datas['data'] = Sub_Cluster_Details
						Sub_Clusters.append(now_datas)


				now_datas = {}
				now_datas['count'] = 0
				now_datas['percent'] = ""
				now_datas['tag'] = label_candi
				now_datas['data'] = Sub_Clusters
				Result_Clusters.append(now_datas)

				for cluster in Result_Clusters:
					cluster['count'] = ConvertFreq(cluster['count'])			
			
			Final_Result.append(("new",Result_Clusters))
			resp = Response(json.dumps(Final_Result), status=200, mimetype='application/json')
			return resp		
			
		else:##無法處理
			Final_Result = [("old",[])]
			resp = Response(json.dumps(Final_Result), status=200, mimetype='application/json')
			return resp			
			

    else:
        Final_Result = [("old",[])]
        resp = Response(json.dumps(Final_Result), status=200, mimetype='application/json')
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

    app.run(**app_options)

