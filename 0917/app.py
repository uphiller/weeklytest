from flask import Flask, render_template, jsonify, request
from pymongo import MongoClient
import requests
from bs4 import BeautifulSoup

app = Flask(__name__)

client = MongoClient("mongodb://localhost:27017/")
db = client.dbStock


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/base/codes', methods=['GET'])
def get_base_codes():
    codes = list(db.codes.find({}).distinct("group"))
    return jsonify(codes)


@app.route('/codes', methods=['GET'])
def get_codes():
    group = request.args.get('group')
    codes = list(db.codes.find({'group': group}, {'_id': False}))
    return jsonify(codes)


@app.route('/stocks', methods=['POST'])
def save_info():
    info = request.json
    stocks = list(db.stocks.find(info, {'_id': False}))
    db.searchs.insert_one(info)
    return jsonify(stocks)



@app.route('/stock/like', methods=['PUT'])
def set_like():
    info = request.json
    db.stocks.update_one({"code": info['code']}, {"$set": {"isLike": True}})
    return "success"


@app.route('/stock/unlike', methods=['PUT'])
def set_unlike():
    info = request.json
    db.stocks.update_one({"code": info['code']}, {"$set": {"isLike": False}})
    return "success"

@app.route('/stocks/like', methods=['GET'])
def get_stocks():
    stocks = list(db.stocks.find({"isLike": True}, {'_id': False}))
    return jsonify(stocks)


@app.route('/stock', methods=['GET'])
def get_info():
    code = request.args.get('code')
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.86 Safari/537.36'}

    data = requests.get('https://finance.naver.com/item/main.nhn?code=' + code, headers=headers)
    soup = BeautifulSoup(data.text, 'html.parser')
    amount = soup.select_one('#_market_sum').text
    amount = amount.replace('\n', '')
    amount = amount.replace('\t', '')
    if soup.select_one('#_per') is None:
        per = 'N/A'
    else:
        per = soup.select_one('#_per').text
    price = soup.select_one(
        '#content > div.section.trade_compare > table > tbody > tr:nth-child(1) > td:nth-child(2)').text

    return jsonify({'amount': amount, 'per': per, 'price': price})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
