# SimpleQS： A Simple Qustion Search Engine Based on BM25
![Python Versions](https://img.shields.io/pypi/pyversions/stanfordnlp.svg?colorB=blue)

The engine consists of three parts: 

* Spider, which aims to crawl data from websites;
* Database, which helps to store filtering data; and
* Website, which provides visualization about simple analysis.

## Requirements
The codebase is implemented in Python 3.6.8 package versions used for development are just below.
```
bs4 == 0.0.4
Flask == 1.1.1
nltk == 3.4.3
tdqm == 4.32.1
```

## Usage
* You need to run the file `code/crawler.py` firstly to get questions from websites. 
```bash
crawler(n=1000, core_num=6)
```
n represents how many pages user wants to crawl, and core_num depends on the amount of cpu.
* Then you should run the file `code/db_index.py`. The step will generate a database about key words
based on BM25.
```bash
construct_database(previous_path + '/data/ir.db')
```
* `web/main.py` is supposed to run finally, and enter the http://127.0.0.1:5000/ to test the engine.

## Thanks
* Flask: [official code](https://github.com/mitsuhiko/flask), [tutorial](http://www.bjhee.com/flask-1.html)
* nltk: [official code](https://github.com/nltk/nltk)
