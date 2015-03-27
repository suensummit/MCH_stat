# coding: utf-8
import pandas as pd
import json

df = pd.read_csv(u'20150101-20150301 處置醫囑開單比例.csv')
df.columns = ["ID","YM","Date","C1", "C2"]

df['@timestamp'] = pd.to_datetime(df['Date'], format='%Y%m%d')
tmp = df.to_json(orient = "records", date_format = "iso")
df_json = json.loads(tmp)

from elasticsearch import Elasticsearch

ES_HOST = {"host" : "106.185.45.145", "port" : 9200}
es = Elasticsearch(hosts = [ES_HOST])

INDEX_NAME = 'order-mch'
TYPE_NAME = 'txt'
ID_FIELD = 'Date'
# clear index
if es.indices.exists(INDEX_NAME):
    print("deleting '%s' index..." % (INDEX_NAME))
    res = es.indices.delete(index = INDEX_NAME)
    print(" response: '%s'" % (res))

# set bulk data
bulk_data = []
for row in df_json:
    data_dict = {}
    data_dict = row
    op_dict = {
        "index": {
        	"_index": INDEX_NAME,
        	"_type": TYPE_NAME,
        	"_id": data_dict[ID_FIELD]
        }
    }
    bulk_data.append(op_dict)
    bulk_data.append(data_dict)

res = es.bulk(index = INDEX_NAME, body = bulk_data, refresh = True)
# verify
res = es.search(index = INDEX_NAME, size=2, body={"query": {"match_all": {}}})
print(" response: '%s'" % (res))

# for doc in df_json:
#     #print doc
#     es.index("order8","txt",doc)
