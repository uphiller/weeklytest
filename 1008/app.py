from datetime import datetime

from flask import Flask, render_template, jsonify, request
from pymongo import MongoClient

app = Flask(__name__)

client = MongoClient("mongodb://localhost:27017/")
db = client.dbStock


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/article', methods=['POST'])
def save_post():
    title = request.form.get('title')
    content = request.form.get('content')
    article_count = db.article.count()
    if article_count == 0:
        max_value = 1
    else:
        max_value = db.article.find_one(sort=[("idx", -1)])['idx'] + 1

    post = {
        'idx': max_value,
        'title': title,
        'content': content,
        'read_count': 0,
        'reg_date': datetime.now()
    }
    db.article.insert_one(post)
    return {"result": "success"}


@app.route('/articles', methods=['GET'])
def get_posts():
    order = request.args.get('order')
    if order == "desc":
        articles = list(db.article.find({}, {'_id': False}).sort([("read_count", -1)]))
    else:
        articles = list(db.article.find({}, {'_id': False}).sort([("reg_date", -1)]))

    for a in articles:
        a['reg_date'] = a['reg_date'].strftime('%Y.%m.%d %H:%M:%S')

    return jsonify({"articles": articles})


@app.route('/article', methods=['DELETE'])
def delete_post():
    idx = request.args.get('idx')
    db.article.delete_one({'idx': int(idx)})
    return {"result": "success"}


@app.route('/article', methods=['GET'])
def get_post():
    idx = request.args['idx']
    article = db.article.find_one({'idx': int(idx)}, {'_id': False})
    return jsonify({"article": article})


@app.route('/article', methods=['PUT'])
def update_post():
    idx = request.form.get('idx')
    title = request.form.get('title')
    content = request.form.get('content')
    db.article.update_one({'idx': int(idx)}, {'$set': {'title': title, 'content': content}})
    return {"result": "success"}


@app.route('/article/<idx>', methods=['PUT'])
def update_read_count(idx):
    db.article.update_one({'idx': int(idx)}, {'$inc': {'read_count': 1}})
    article = db.article.find_one({'idx': int(idx)}, {'_id': False})
    return jsonify({"article": article})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
