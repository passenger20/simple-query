import sqlite3
import configparser
import pickle
import os
from tqdm import tqdm

current_path = os.getcwd()
previous_path = os.path.abspath(os.path.dirname(os.getcwd()))

# delete punctuations in sentences
def del_punc(sent):
    english_punctuations = [',', '.', ':', ';', '?', '(', ')', '[', ']', '&', '!', '*', '@', '#', '$', '%', '-',
                            '....', '’','...', '..', "'", '"', '.?', '!?']
    result = []
    sent_token = sent.split()
    for i in range(len(sent_token)):
        if sent_token[i][0] in english_punctuations: # delete punctuations at the beginning of words
            for j in range(len(sent_token[i])):
                k = len(sent_token[i]) - j # start from long punctuations
                if sent_token[i][: k] in english_punctuations:
                    if len(sent_token[i][k:]) != 0:
                        result.append(sent_token[i][k:])
                    break
        elif sent_token[i][-1] in english_punctuations: # delete punctuations at the end of words
            for j in range(len(sent_token[i])):
                k = -(len(sent_token[i]) - j - 1) # start from long punctuations
                if sent_token[i][k:] in english_punctuations:
                    if len(sent_token[i][: k]) != 0:
                        result.append(sent_token[i][: k])
                    break
        else:
            result.append(sent_token[i])
    return result

# get key_token of each sentence
def get_key_token(q_token):
    stopwords = ['i', 'me', 'my', 'myself', 'we', 'our', 'ours', 'ourselves', 'you', "you're", "you've", "you'll",
             "you'd", 'your', 'yours', 'yourself', 'yourselves', 'he', 'him', 'his', 'himself', 'she', "she's",
             'her', 'hers', 'herself', 'it', "it's", 'its', 'itself', 'they', 'them', 'their', 'theirs',
             'themselves', 'what', 'which', 'who', 'whom', 'this', 'that', "that'll", 'these', 'those', 'a', 'an',
             'the', 'and', 'but', 'if', 'or', 'because', 'when', 'where', 'why', 'how', 'do', 'does', 'did', 'doing']
    key_dict = {}
    n = 0
    for i in q_token:
        if i != '' and i not in stopwords and not i.isdigit(): # filter stopwords and numbers in sentences
            n += 1 # calculate ld
            key_dict[i] = key_dict.get(i, 0) + 1 # calculate df
    return n, key_dict

def construct_database(db_path):
    config = configparser.ConfigParser()

    # get previous questions data
    with open(previous_path + '/data/que.pkl', 'rb') as f:
        que_text = pickle.load(f)

    ave_l = 0
    postings_lists = {}
    for i in tqdm(range(len(que_text))):
        q_token = del_punc(que_text[i])
        ld, key_dict = get_key_token(q_token)

        ave_l += ld

        for key, value in key_dict.items():
            d = str(i) + '\t' + str(value) + '\t' + str(ld)
            if key in postings_lists: # use words as indexes
                postings_lists[key][0] = postings_lists[key][0] + 1
                postings_lists[key][1].append(d)
            else:
                postings_lists[key] = [1, [d]]

    # store params used for calculating BM-25 score
    ave_l = ave_l/ len(que_text)
    config.set('DEFAULT', 'N', str(len(que_text)))
    config.set('DEFAULT', 'avg_l', str(ave_l))
    config.set('DEFAULT', 'k1', str(1.5))
    config.set('DEFAULT', 'b', str(0.5))
    with open(current_path + '/config.ini', 'w') as f:
        config.write(f)

    # store data in database
    conn = sqlite3.connect(db_path)
    c = conn.cursor()

    c.execute('''DROP TABLE IF EXISTS postings''')
    c.execute('''CREATE TABLE postings
                     (term TEXT PRIMARY KEY, df INTEGER, docs TEXT)''')

    for key, value in tqdm(postings_lists.items()):
        que_list = '\n'.join(map(str, value[1]))
        t = (key, value[0], que_list)
        c.execute("INSERT INTO postings VALUES (?, ?, ?)", t)

    conn.commit()
    conn.close()

if __name__ == "__main__":
    construct_database(previous_path + '/data/ir.db')
