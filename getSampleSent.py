#-*- coding: utf8 -*-
#!/usr/bin/python
'''
Created on 2013/04/24

@author: wujc
'''
####==================================================
####    從 DB 中取得 ngram 的例句
####==================================================
import sqlite3 as sqlite
from time import ctime
import sys


##==================================================
##   從 DB 中取得 ngram 的例句
##==================================================
print ctime()
from nltk.corpus import stopwords
# conn = sqlite.connect("/corpus/Linggle/LinggleSamples.db3")
# cursor = conn.cursor()
Corpus_List = ["BNC","NYT"]

Eng_stops = dict([(word,1) for word in list(set(stopwords.words('english')))])

##stoplist:
##all just being over both through yourselves its before with had should to only under
##ours has do them his very they not during now him nor did these t each where because
##doing theirs some are our ourselves out what for below does above between she be we
##after here hers by on about of against s or own into yourself down your from her whom
##there been few too themselves was until more himself that but off herself than those
##he me myself this up will while can were my and then is in am it an as itself at have
##further their if again no when same any how other which you who most such why a don i
##having so the yours once'

def getSamples(query, cursor):

    print 'input:',query
    query = query.strip()

    words = query.split()
    print 'words:',words
    if len(words) == 1:
        print '1'
        for Corpus in Corpus_List:
            SQL = "select sent_ids from %s_Ngram1_IL where ngram == '%s'" % (Corpus,query.replace("'","''"))
            try:
                records = cursor.execute(SQL).fetchone()[0].split()
            except:
                continue
            
            ##先取第一個句子
            if len(records) == 0:
                continue ##找下一個 corpus
            elif query.lower() in Eng_stops:
                return {"status": 'stopword', "sent": '', "source": ''}
            else:
                SQL = "select sentence from %s_Samples where sent_id == %s" % (Corpus,records[0])                
                sentence = " "+cursor.execute(SQL).fetchone()[0]+" "
                sentence_candidate = sentence.replace(" "+query+" "," <strong>"+query+"</strong> ")
                return {"status": 'ok', "sent": sentence_candidate[1:-1], "source": Corpus}
            
        return {"status": 'empty', "sent": "", "source": ""}

    else: ##超過2個字 就用組合搜尋       
        print '>2'
        for Corpus in Corpus_List:

            Records_List = []##記錄

            words = [word for word in words if word.lower() not in Eng_stops]
            #print "===>" ,words
            print 'new words: ', words

            if len(words) == 0:
                return {"status": 'stopword', "sent": '', "source": ''}
           
            for i in range(len(words)):
                subquery = words[i]
                print 'subquery:',subquery
                if subquery not in Eng_stops: ##不是 stop words才處理，是的話，應該很容易碰到
                    SQL = "select sent_ids from %s_Ngram1_IL where ngram == '%s'" % (Corpus,subquery.replace("'","''"))
                    try:
                        records = cursor.execute(SQL).fetchone()[0]
                    except:

                        Records_List = []
                        break ##找下一個 corpus

                Records_List.append(records)

            # print 'Records_List:',Records_List
            if len(Records_List) > 0:
                ##unigram都存在 開始取交集
                Records_List = [data.strip().split() for data in Records_List]
                Records_List.sort(key = lambda x:len(x))
                ##利用 set 取交集比字典快
                temp_list = Records_List[0]
                for i in range(2,len(Records_List)):
                    if len(Records_List[i]) > 500000: ##太多句子有  就不要過濾了  很容易碰到
                        continue
                    temp_list = list(set(temp_list) & set(Records_List[i]))
                    if len(temp_list) == 0: ##找不到有重疊的機會
                        break

                ##判斷是否有句子可篩選
                if len(temp_list) == 0:
                    continue ##找下一個 Corpus
                else: ##開始尋找是否真的包含該 ngram
                    for sent_id in temp_list[:10000]:
                        SQL = "select sentence from %s_Samples where sent_id == %s" % (Corpus,sent_id)
                        sentence_candidate = " "+cursor.execute(SQL).fetchone()[0]+" "
                        if sentence_candidate.count(" "+query+" ") > 0:
                            sentence_candidate = sentence_candidate.replace(" "+query+" "," <strong>"+query+"</strong> ")
                            return {"status": 'ok', "sent": sentence_candidate[1:-1], "source": Corpus}
        ##都找完了 沒有找到
        print 'empty'
        return {"status": 'empty', "sent": "", "source": ""}
if __name__ == "__main__":
    while True:
        query = raw_input("input the query:")
        print getSamples(query)







    
