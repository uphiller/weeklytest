from pymongo import MongoClient

client = MongoClient("mongodb://localhost:27017/")

db = client.dbStock

codes = [
    {"group": "market", "code": "market-1", "name": "코스피"},
    {"group": "market", "code": "market-2", "name": "코스닥"},
    {"group": "sector", "code": "sector-1", "name": "반도체와반도체장비"},
    {"group": "sector", "code": "sector-2", "name": "양방향미디어와서비스"},
    {"group": "sector", "code": "sector-3", "name": "자동차"},
    {"group": "tag", "code": "tag-1", "name": "메모리"},
    {"group": "tag", "code": "tag-2", "name": "플랫폼"},
    {"group": "tag", "code": "tag-4", "name": "전기차"},
]
db.codes.insert_many(codes)


stocks = [
        {"name": "삼성전자", "code": "005930", "sector":"sector-1", "market": "market-1", "tag": "tag-1", "isLike": False},
        {"name": "SK하이닉스", "code": "000660", "sector":"sector-1", "market": "market-1", "tag": "tag-1", "isLike": False},
        {"name": "리노공업", "code": "058470", "sector": "sector-1", "market": "market-2", "tag": "tag-1", "isLike": False},
        {"name": "DB하이텍", "code": "000990", "sector": "sector-1", "market": "market-1", "tag": "tag-1", "isLike": False},
        {"name": "솔브레인", "code": "357780", "sector": "sector-1", "market": "market-2", "tag": "tag-1", "isLike": False},
        {"name": "카카오", "code": "357780", "sector": "sector-2", "market": "market-1", "tag": "tag-2", "isLike": False},
        {"name": "네이버", "code": "035420", "sector": "sector-2", "market": "market-1", "tag": "tag-2", "isLike": False},
        {"name": "아프리카TV", "code": "067160", "sector": "sector-2", "market": "market-2", "tag": "tag-3", "isLike": False},
        {"name": "자이언트스텝", "code": "289220", "sector": "sector-2", "market": "market-2", "tag": "tag-2", "isLike": False},
        {"name": "키다리스튜디오", "code": "020120", "sector": "sector-2", "market": "market-1", "tag": "tag-2", "isLike": False},
        {"name": "현대차", "code": "005380", "sector": "sector-3", "market": "market-1", "tag": "tag-4"},
 ]
db.stocks.insert_many(stocks)