from datetime import datetime, timedelta
from functools import wraps

from flask import Flask, render_template, jsonify, request, Response, g
from pymongo import MongoClient
import jwt
import bcrypt
from flask_socketio import SocketIO, emit

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'

client = MongoClient("mongodb://localhost:27017/")
db = client.dbStock
secret = "secrete"
algorithm = "HS256"

socketio = SocketIO(app)

def login_check(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        access_token = request.headers.get("Authorization")
        if access_token is not None:
            try:
                payload = jwt.decode(access_token, secret, "HS256")
            except jwt.InvalidTokenError:
                return Response(status=401)

            if payload is None:
                return Response(status=401)

            user_id = payload["id"]
            g.user_id = user_id
            g.user = get_user_info(user_id)
        else:
            g.user_id = "비회원"
            g.user = None
            print("access_token is empty")

        return f(*args, **kwargs)

    return decorated_function


def get_user_info(user_id):
    return db.user.find_one({"id": user_id})

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/article', methods=['POST'])
@login_check
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
        'writer': (g.user_id if hasattr(g, 'user_id') else ''),
        'reg_date': datetime.now()
    }
    db.article.insert_one(post)
    return {"result": "success"}


@app.route('/articles/<type>', methods=['GET'])
@login_check
def get_posts(type):
    order = request.args.get('order')
    per_page = request.args.get('perPage')
    cur_page = request.args.get('curPage')
    search_title = request.args.get('searchTitle')
    search_condition = {}
    if search_title is not None:
        search_condition = {"title": {"$regex": search_title}}

    if type == 'my':
        search_condition['writer'] = g.user_id

    limit = int(per_page)
    skip = limit * (int(cur_page) - 1)
    total_count = db.article.count_documents(search_condition)
    total_page = int(total_count / limit) + (1 if total_count % limit > 0 else 0)

    if order == "desc":
        articles = list(db.article.find(search_condition, {'_id': False})
                        .sort([("read_count", -1)]).skip(skip).limit(limit))
    else:
        articles = list(db.article.find(search_condition, {'_id': False})
                        .sort([("reg_date", -1)]).skip(skip).limit(limit))

    for a in articles:
        a['reg_date'] = a['reg_date'].strftime('%Y.%m.%d %H:%M:%S')

    paging_info = {
        "totalCount": total_count,
        "totalPage": total_page,
        "perPage": per_page,
        "curPage": cur_page,
        "searchTitle": search_title
    }

    return jsonify({"articles": articles, "pagingInfo": paging_info})


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
    return jsonify({"result": "success"})


@app.route('/article/<idx>', methods=['PUT'])
def update_read_count(idx):
    db.article.update_one({'idx': int(idx)}, {'$inc': {'read_count': 1}})
    article = db.article.find_one({'idx': int(idx)}, {'_id': False})
    return jsonify({"article": article})


@app.route('/join', methods=['POST'])
def create_user():
    id = request.form.get('id')
    pwd = request.form.get('pwd')
    if get_user_info(id) is not None:
        return Response(status=423)

    db.user.insert_one({"id": id, "pwd": bcrypt.hashpw(pwd.encode('UTF-8'), bcrypt.gensalt())})
    return jsonify({"result": "success"})


@app.route('/login', methods=['POST'])
def login_user():
    id = request.form.get('id')
    pwd = request.form.get('pwd')
    user = db.user.find_one({"id": id})

    if get_user_info(id) is None:
        return Response(status=401)

    if bcrypt.checkpw(pwd.encode('utf-8'), user['pwd']):
        payload = {
            "id": id,
            "exp": datetime.utcnow() + timedelta(seconds=60 * 60 * 24)
        }
        token = jwt.encode(payload, secret, "HS256")
        return jsonify({"result": "success", "token": token})
    else:
        return Response(status=401)


@app.route('/comment', methods=['POST'])
@login_check
def save_comment():
    idx = request.form.get('idx')
    comment = request.form.get('comment')
    post = {'idx': int(idx), 'comment':comment, 'writer': (g.user_id if hasattr(g, 'user_id') else '')}
    db.comment.insert_one(post)

    #알림
    article = db.article.find_one({'idx':int(idx)})
    socketio.emit(article['writer'],"ok")
    return {"result": "success"}


@app.route('/comment', methods=['GET'])
def get_comment():
    idx = request.args['idx']
    comments = list(db.comment.find({'idx': int(idx)}, {'_id': False}))
    return jsonify({"comments": comments})


if __name__ == "__main__":
    socketio.run(app, debug=True)
