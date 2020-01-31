from bs4 import BeautifulSoup
import requests
import re
from tqdm import tqdm
import multiprocessing
import pickle
import os

# get project path
current_path = os.getcwd()
previous_path = os.path.abspath(os.path.dirname(os.getcwd()))

# get data from url
def get_data(url, att, cla):
    html = requests.get(url)
    soup = BeautifulSoup(html.text, 'lxml') # analyze url
    data = soup.find_all(att, class_=cla) # get the special attributes and classes
    return data

# static load from stackoverflow
def get_it_que(n):
    que_text = []
    for i in tqdm(range(n)): # get n pages questions
        url = 'https://stackoverflow.com/questions?tab=Active&page=' + str(i)
        data = get_data(url, 'a', 'question-hyperlink')

        for item in data:
            q = ' '.join(item.get_text().split()).lower()
            que_text.append(q)
    return que_text

# dynamic load from yahoo answer
def get_yahoo_que(url_i):
    r = re.compile(r'(">)(\w.*?\?)')
    que_text = []
    for url in tqdm(url_i):
        try:
            html = requests.get(url)
            data = html.json().get('YANewDiscoverTabModule').get('html')
            que_text += [j[1].replace('&#039;', "'").lower() if '&#039;' in j[1] else j[1].lower() for j in
                         r.findall(data)]
        except:
            que_text += ['sad']
    return que_text

def crawler(n, core_num): # click n times 'show more'
    #     it_que = get_it_que(10)

    ## get all categories
    url_base = 'https://answers.yahoo.com'
    data = get_data(url_base, 'a', 'Mstart-3 unselected D-ib')
    index_list = [item['href'] for item in data][1:]  # subtitle index

    category = []
    for index in tqdm(index_list):
        url_i = url_base + index
        d = get_data(url_i, 'a', 'D-ib Clr-w Fz-13 Pt-8 W-32')
        idx_list = [item['href'][11:] for item in d]  # subsubtitle index
        category += idx_list

    url_list = []
    for k in tqdm(range(len(category))):  # all categories
        for i in range(1, n + 1):
            if i == 1: # updating web template from yahoo answer
                url = 'https://answers.yahoo.com/_module?name=YANewDiscoverTabModule&after=pc%d~p:0&' \
                      '%s&bpos=%d&cpos=%d' % (20 * i, category[k], i + 1, 20 * i + 1)
            else:
                url = 'https://answers.yahoo.com/_module?name=YANewDiscoverTabModule&after=pc%d~p:0&' \
                      '%s&disableLoadMore=false&bpos=%d&cpos=%d' % (20 * i, category[k], i + 1, 20 * i + 1)
            url_list.append(url)

    ## multi_process
    sub_url_len = len(url_list) // core_num # num of cpu
    sub_url = []
    for i in range(core_num): # split data
        if i != core_num - 1:
            sub_url.append(url_list[i * sub_url_len: (i + 1) * sub_url_len])
        else:
            sub_url.append(url_list[i * sub_url_len:])

    que_text = []
    pool = multiprocessing.Pool(processes=core_num)
    result = pool.map_async(get_yahoo_que, sub_url) # parallel operation
    for i in range(len(result.get())): # merge parallel results
        que_text += result.get()[i]
    que_text = list(set(que_text))
    pool.close()
    pool.join()

    with open(previous_path + '/data/que.pkl', 'wb') as f:
        pickle.dump(que_text, f)

if __name__ == '__main__':
    crawler(n=1000, core_num=6)