import math
import operator
import sqlite3
import configparser
import os
import nltk
import pickle

current_path = os.getcwd()
previous_path = os.path.abspath(os.path.dirname(os.getcwd()))

with open(previous_path + '/data/que.pkl', 'rb') as f:
    que_text = pickle.load(f)

config_path = previous_path + '/code/config.ini'
config = configparser.ConfigParser()
config.read(config_path)
K1 = float(config['DEFAULT']['k1'])
B = float(config['DEFAULT']['b'])
N = int(config['DEFAULT']['n'])
avg_l = float(config['DEFAULT']['avg_l'])

def del_punc(sent):
    english_punctuations = [',', '.', ':', ';', '?', '(', ')', '[', ']', '&', '!', '*', '@', '#', '$', '%', '-',
                            '....', '’','...', '..', "'", '"', '.?', '!?']
    result = []
    sent_token = sent.split()
    for i in range(len(sent_token)):
        if sent_token[i][0] in english_punctuations:
            for j in range(len(sent_token[i])):
                k = len(sent_token[i]) - j
                if sent_token[i][: k] in english_punctuations:
                    if len(sent_token[i][k:]) != 0:
                        result.append(sent_token[i][k:])
                    break
        elif sent_token[i][-1] in english_punctuations:
            for j in range(len(sent_token[i])):
                k = -(len(sent_token[i]) - j - 1)
                if sent_token[i][k:] in english_punctuations:
                    if len(sent_token[i][: k]) != 0:
                        result.append(sent_token[i][: k])
                    break
        else:
            result.append(sent_token[i])
    return result

def get_key_token(q_token):
    stopwords = ['i', 'me', 'my', 'myself', 'we', 'our', 'ours', 'ourselves', 'you', "you're", "you've", "you'll",
             "you'd", 'your', 'yours', 'yourself', 'yourselves', 'he', 'him', 'his', 'himself', 'she', "she's",
             'her', 'hers', 'herself', 'it', "it's", 'its', 'itself', 'they', 'them', 'their', 'theirs',
             'themselves', 'what', 'which', 'who', 'whom', 'this', 'that', "that'll", 'these', 'those', 'a', 'an',
             'the', 'and', 'but', 'if', 'or', 'because', 'when', 'where', 'why', 'how', 'do', 'does', 'did', 'doing']
    key_dict = {}
    n = 0
    for i in q_token:
        if i != ''  and i not in stopwords and not i.isdigit():
            n += 1
            key_dict[i] = key_dict.get(i, 0) + 1
    return n, key_dict

# get relevant keys from database
def fetch_from_db(term):
    db_path = previous_path + '/data/ir.db'

    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute('SELECT * FROM postings WHERE term=?', (term,))
    return (c.fetchone())

# generate BM25 list
def result_by_BM25(sentence):
    q_token = del_punc(sentence.lower())
    n, key_dict = get_key_token(q_token)

    BM25_scores = {}
    for term in key_dict.keys():
        r = fetch_from_db(term)
        if r is None:
            continue
        df = r[1]
        w = math.log2((N - df + 0.5) / (df + 0.5))
        ques = r[2].split('\n')
        for que in ques:
            idx, tf, ld = que.split('\t')
            idx = int(idx)
            tf = int(tf)
            ld = int(ld)
            s = (K1 * tf * w) / (tf + K1 * (1 - B + B * ld / avg_l)) # calculate BM25
            BM25_scores[idx] = BM25_scores.get(idx, 0) + s
    BM25_scores = sorted(BM25_scores.items(), key=operator.itemgetter(1))
    BM25_scores.reverse()

    if len(BM25_scores) == 0: # judge whether keys of the query are in the database
        return 0, []
    else:
        return 1, BM25_scores[: 10]

def BM25_similarity(query):
    flag, id_scores = result_by_BM25(query)
    ques_sel = []
    for i in range(len(id_scores)):
        q = {}
        q['text'] = que_text[id_scores[i][0]]
        q['sim'] = id_scores[i][1]
        ques_sel.append(q)
    return flag, ques_sel

def senmantic_parsing(query):
    flag, id_scores = result_by_BM25(query)

    grammar = 'NP: {<DT>*<JJ.*>*<NN.*>+}'  # None phrase
    cp = nltk.RegexpParser(grammar)

    result = []
    for i in range(len(id_scores)):
        q = {}
        q_token = del_punc(que_text[id_scores[i][0]].lower())
        q_tag = nltk.pos_tag(q_token)
        q['text'] = que_text[id_scores[i][0]].lower()
        q['ner'] = cp.parse(q_tag)
        result.append(q)
    return flag, result

def search(sentence, selected):
    if selected == 0:
        return BM25_similarity(sentence)
    elif selected == 1:
        return senmantic_parsing(sentence)