from flask import Flask, render_template, redirect, url_for
import os
import json
import pandas as pd

app = Flask(__name__)

CURR_DIR = os.path.dirname(os.path.realpath(__file__))
keyanchengguo_df = pd.read_csv('{}/data/keyantongji/2018下半年-全部-v1.csv'.format(CURR_DIR),
                                index_col=0, encoding="utf-8")
keyanchengguo_df = keyanchengguo_df.fillna('')

class WordCloudD3DTO:
    text = ""
    size = 0

    def __init__(self, text, size):
        self.text = text
        self.size = size

    def serialize(self):
        return {
            'text': self.text,
            'size': self.size
        }

def getWordCloudData():
    wordCloudData = []
    curr_path = os.path.abspath(__file__)
    filename = ''
    # Windows platform
    if '/' not in curr_path:
        filename = curr_path[:curr_path.rfind('\\')] + '\\data\\datacloud.csv'
    else:
        # Linux platform
        filename = curr_path[:curr_path.rfind('/')] + '/data/datacloud.csv'

    try:
        cityWordData = pd.read_csv(filename, encoding='utf-8')
    except FileNotFoundError:
        return None

    nameList = cityWordData['char']
    weightList = cityWordData['freq']

    dataList = nameList
    if len(nameList) > len(weightList):
        dataList = weightList

    for i in range(0, len(dataList)):
        thisName = nameList[i]
        thisWeight = int(weightList[i])
        thisWordCloudD3DTO = WordCloudD3DTO(thisName, thisWeight)
        wordCloudData.append(thisWordCloudD3DTO.serialize())

    return json.dumps(wordCloudData)

@app.route('/', methods=['GET'])
def index():
    return redirect(url_for('.jiaoshikeyantongji', curr_active='教师科研统计'))
    #return render_template('index.html', curr_active='教师科研统计')

@app.route('/教师绩效', methods=['GET'])
def jiaoshijixiao():
    wordCloudData = getWordCloudData()
    return render_template('404.html', wordCloudData=wordCloudData, curr_active='教师绩效')

@app.route('/教师科研统计', methods=['GET'])
def jiaoshikeyantongji():
    return render_template('keyantongji_index.html', curr_active='教师科研统计')

@app.route('/getdata/keyantongji/<filename>')
def get_keyantongji_data(filename):
    data_df = pd.read_csv('{}/data/keyantongji/2018下半年-全部-v1.csv'.format(CURR_DIR),
                                index_col=0, encoding="utf-8")
    data_df = data_df.fillna('')

    headers = list(data_df.columns)
    rows = []
    for index in data_df.index:
        row = [index]
        for col in data_df.columns:
            row.append(data_df.loc[index][col])
        rows.append(row)

    return render_template('_table.html', headers=headers, rows=rows)

@app.route("/keyantongji/detail/<time>/<department>", methods=['GET'])
def get_keyantongji_detail(time, department):
    df = keyanchengguo_df

    headers = list(df.columns)
    rows = []
    for index in df.index:
        row = [index]
        for col in df.columns:
            row.append(df.loc[index][col])
        rows.append(row)

    res = []
    total = 0
    for col in df.columns:
        series = [i for i in df[col] if isinstance(i, float)]
        res.append((col, sum(series)))
        total += sum(series)

    sorted_res = sorted(res, key=lambda t: t[1], reverse=True)
    
    scores = []
    for index in df.index:
        score = [df.loc[index][col] for col in df.columns if isinstance(df.loc[index][col], float)]
        scores.append((index, sum(score)))

    sorted_scores = sorted(scores, key=lambda t: t[1], reverse=True)

    return render_template('keyantongji_detail.html', total=total,
                            rank1_item=sorted_res[0][0], rank1_score=sorted_res[0][1],
                            rank2_item=sorted_res[1][0], rank2_score=sorted_res[1][1],
                            rank3_item=sorted_res[2][0], rank3_score=sorted_res[2][1],
                            headers=headers, rows=rows, 
                            items=[i for i, s in sorted_res], sum=[{'name': i, 'y': s} for i, s in sorted_res],
                            names=[i for i, s in sorted_scores], scores=[{'name': i, 'y': s} for i, s in sorted_scores], curr_active='教师科研统计')

@app.route('/save/<filename>/<data>', methods=['GET'])
def savedatafile(filename, data):
    print(filename)

@app.route('/教师画像', methods=['GET'])
def jiaoshihuaxiang():
    return render_template('404.html', curr_active='教师画像')


if __name__ == '__main__':
    app.run(debug=True)
