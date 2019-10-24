import json
import logging
import subprocess
import paramiko
import platform

import boto3
import botocore
import pandas as pd
from botocore.exceptions import ClientError
from elasticsearch import Elasticsearch
import elasticsearch.helpers
from elasticsearch.helpers import bulk
from nltk.corpus import stopwords
from nltk.sentiment.vader import SentimentIntensityAnalyzer as SIA

### Read S3 credentials
cred=pd.read_csv("credentials.csv")
key_id=cred["Access key ID"][0]
access_key=cred["Secret access key"][0]
#s3 = boto3.resource('s3')

### S3 Client

s3_client = boto3.client('s3',aws_access_key_id=key_id,aws_secret_access_key=access_key)

### S3 Bucket

BUCKET_NAME = 'tweetdata'
s3_bucket = boto3.resource('s3',aws_access_key_id=key_id ,aws_secret_access_key=access_key)


def get_bucket_content(s3_client):
    try:
        response = s3_client.list_objects_v2(Bucket="tweetdata")
    except ClientError as e:
        # AllAccessDisabled error == bucket not found
        logging.error(e)

    content=response['Contents']
    return content


def download_data(s3_bucket, key):
    #s3 = boto3.client('s3')
    try:
        s3_bucket.Bucket(BUCKET_NAME).download_file(key, key)

    except botocore.exceptions.ClientError as e:
        if e.response['Error']['Code'] == "404":
            print("The object does not exist.")
        else:
            raise

    return (key)

def extract_time(x):

    h=pd.to_datetime(x).hour
    if (h >= 6 and h< 12):
        t="morning"
    elif (h >= 12 and h<18):
        t="afternoon"
    elif (h>=18 and h <20):
        t="evening"
    else:
        t="night"
    return h,t


def read_dataset(f):
    with open(f, "r", encoding="utf8") as read_file:

        col = ["created_at", "favorite_count", "id_str", "in_reply_to_user_id_str", "is_retweet", "retweet_count","source", "text"]
        data = json.load(read_file)
        df = pd.DataFrame(data, columns=col)

        df['hour'], df['time_of_day'] = zip(*df['created_at'].apply(extract_time))
        df['created_at'] = pd.to_datetime(df['created_at'])

        return df

def split_text():
    df['wrangled_text']=df['text'].str.lower().str.split()
    stop_words = set(stopwords.words('english'))

    df['wrangled_text']=df['wrangled_text'].apply(lambda x: [i for i in x if i not in stop_words])


def sentiment_classification(x):
    if x >= 0.5:
        s="positive"
    elif (x >= -0.5 and x<=0.5):
        s="neutral"
    else:
        s="nagative"
    return s

def dataset_manip(df):

    split_text()
    df['score_sentiment'] = df['text'].apply(lambda x: sia.polarity_scores(x)['compound'])
    df['label'] = df['score_sentiment'].apply(sentiment_classification)
    df['is_retweet'] = df['is_retweet'].astype(bool)
    df = df.where((pd.notnull(df)), None)
    #df = df.dropna()

    return df

def exec_win_cmds(cmd1):

    client = paramiko.SSHClient()
    client.load_system_host_keys()
    client.connect('127.0.0.1', port=54576, username='docker', password='tcuser')
    cmd2="docker inspect --format '{{ .NetworkSettings.Ports }}' elasticsearch | grep -oE '\{(.*?)}' | cut -d ' ' -f2  |  cut -d '}' -f1"
    cmd1="ip addr | grep eth1 | grep inet | grep -oE '([0-9]{1,3}.){3}[0-9]{1,3}/' | cut -d '/' -f1"
    cnx_info=[]
    for c in [cmd1,cmd2]:
        stdin, stdout, stderr = client.exec_command(c)
        for c in stdout:
            c=c.strip('\n')
            print(c)

        cnx_info.append(c)

    es_conn=':'.join(map(str, cnx_info))

    client.close()
    return es_conn



def get_osip():

    os=platform.system()

    cmd1="docker inspect --format '{{ .NetworkSettings.Ports }}' elasticsearch | grep -oE '\{(.*?)\}'"

    if os=="Windows":
        cmd_results=exec_win_cmds(cmd1)
        es_conn=cmd_results


    if os=="Linux":
        elastic = subprocess.check_output(cmd1, shell=True).decode('utf-8')
        es_conn=elastic.replace(" ",":").strip().strip("{}")


    print("Elastic ip and port", es_conn)

    return(es_conn,os)


def import_toelk(df,es):

    # from dataset create a serialize object for import
    bulk_data = df.to_dict(orient='records')

    bulk(es, bulk_data, index='tweeter', doc_type='tweets')
    #get import status
    status=es.indices.refresh()
    return status

def remove_dataset(os,fh):
        if os == "Linux":
            #result=subprocess.call(["rm","rf", fh], stdout=subprocess.PIPE, shell='True')
            result = subprocess.call(["rm", "-rf", fh], stdout=subprocess.PIPE)

        elif os == "Windows":
            result = subprocess.call(["del", fh], stdout=subprocess.PIPE, shell='True')

        if result == 0:
            print("Successfully Deleted: ", fh)


file_keys = get_bucket_content(s3_client)

[es_conn, os]=get_osip()
print(es_conn)
es=Elasticsearch(es_conn)
es.indices.delete(index="tweeter",ignore=404)

sia = SIA()

for f in file_keys:

    key = f['Key']
    fh = download_data(s3_bucket, key)
    df = read_dataset(fh)

    print(fh)
    df=dataset_manip(df)
    import_status=import_toelk(df, es)

    print(import_status)

    remove_dataset(os,fh)
