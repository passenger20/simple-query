from flask import Flask, render_template, request
from web import sent_analysis

app = Flask(__name__)

@app.route('/')
def main():
    return render_template('search.html', error=True)

# generate initial page
@app.route('/search/', methods=['POST'])
def search():
    try:
        global checked
        global query
        checked = ['checked="true"', '', '']
        query = request.form['key_word'] # get user input
        if query not in ['']:
            flag, ques_sel = sent_analysis.search(query, 0) # set the initial page in BM-25
            if flag == 0:
                return render_template('search.html', error=False)
            return render_template('high_search.html', checked=checked, key=query, docs=ques_sel,
                                   error=True, selected=0)
        else:
            return render_template('search.html', error=False)
    except:
        print('search error')

# generate another page for selecting patterns
@app.route('/search/<key>/', methods=['POST'], strict_slashes=False)
def high_search(key):
    try:
        selected = int(request.form['order'])
        for i in range(2):
            if i == selected:
                checked[i] = 'checked="true"'
            else:
                checked[i] = ''
        flag, ques_sel = sent_analysis.search(key, selected)
        if flag == 0:
            return render_template('search.html', error=False)
        return render_template('high_search.html', checked=checked, key=query, docs=ques_sel,
                               error=True, selected=selected)
    except:
        print('high search error')

if __name__ == '__main__':
    app.run(debug=True)