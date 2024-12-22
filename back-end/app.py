from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
import datetime
from functools import wraps

app = Flask(__name__)
CORS(app)

# 配置 SQLAlchemy 数据库路径
db_path = "sqlite:///budget_system.db"
app.config['SQLALCHEMY_DATABASE_URI'] = db_path
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'your_secret_key'  # 用于生成和验证 JWT 的密钥

db = SQLAlchemy(app)

# 数据库模型
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)  # 用户名，必须唯一
    password_hash = db.Column(db.String(128), nullable=False)  # 哈希密码

class Record(db.Model):
    id = db.Column(db.Integer, primary_key=True)  # 记录唯一标识符
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)  # 关联的用户ID
    amount = db.Column(db.Float, nullable=False)  # 金额
    category = db.Column(db.String(50), nullable=False)  # 类别
    date = db.Column(db.DateTime, default=datetime.datetime.utcnow)  # 日期
    type = db.Column(db.String(10), nullable=False)  # 类型：收入或支出

# 使用 session.get() 替代 query.get() 解决警告问题
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token:
            return jsonify({"error": "令牌缺失。"}), 401

        try:
            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=["HS256"])
            # 替换 User.query.get() 为 db.session.get()
            current_user = db.session.get(User, data['user_id'])
            if not current_user:
                raise ValueError("用户不存在。")
        except Exception as e:
            return jsonify({"error": f"令牌无效：{str(e)}"}), 401

        return f(current_user, *args, **kwargs)

    return decorated


# 路由
@app.route('/register', methods=['POST'])
def register():
    """
    用户注册。
    接受用户名和密码，并在数据库中创建新用户。

    请求数据：
    {
        "username": "用户名",
        "password": "密码"
    }
    返回：
    成功：{"message": "用户注册成功。"}
    失败：{"error": "错误信息"}
    状态码：201 或 400
    """
    data = request.json
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({"error": "用户名和密码是必填项。"}), 400

    if User.query.filter_by(username=username).first():
        return jsonify({"error": "用户已存在。"}), 400

    hashed_password = generate_password_hash(password)
    user = User(username=username, password_hash=hashed_password)
    db.session.add(user)
    db.session.commit()
    return jsonify({"message": "用户注册成功。"}), 201

@app.route('/login', methods=['POST'])
def login():
    """
    用户登录。
    验证用户名和密码，如果成功，返回 JWT 令牌。

    请求数据：
    {
        "username": "用户名",
        "password": "密码"
    }
    返回：
    成功：{"message": "登录成功。", "token": "JWT 令牌"}
    失败：{"error": "无效的凭据。"}
    状态码：200 或 401
    """
    data = request.json
    username = data.get('username')
    password = data.get('password')

    user = User.query.filter_by(username=username).first()
    if not user or not check_password_hash(user.password_hash, password):
        return jsonify({"error": "无效的凭据。"}), 401

    token = jwt.encode({
        'user_id': user.id,
        'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=1)
    }, app.config['SECRET_KEY'], algorithm="HS256")

    return jsonify({"message": "登录成功。", "token": token}), 200

@app.route('/records', methods=['POST'])
@token_required
def add_record(current_user):
    """
    添加记录。
    用户可以添加一条与其账户相关联的收入或支出记录。

    请求数据：
    {
        "amount": 金额,
        "category": "类别",
        "type": "income 或 expense"
    }
    返回：
    成功：{"message": "记录添加成功。"}
    失败：{"error": "所有字段都是必填项。"}
    状态码：201 或 400
    """
    data = request.json
    amount = data.get('amount')
    category = data.get('category')
    type = data.get('type')

    if not all([amount, category, type]):
        return jsonify({"error": "所有字段都是必填项。"}), 400

    record = Record(user_id=current_user.id, amount=amount, category=category, type=type)
    db.session.add(record)
    db.session.commit()
    return jsonify({"message": "记录添加成功。"}), 201

@app.route('/records', methods=['GET'])
@token_required
def get_records(current_user):
    """
    获取所有记录。
    返回与当前用户关联的所有收入或支出记录。

    返回：
    成功：记录列表
    状态码：200
    """
    records = Record.query.filter_by(user_id=current_user.id).all()
    records_list = [
        {
            "id": record.id,
            "amount": record.amount,
            "category": record.category,
            "date": record.date.strftime('%Y-%m-%d'),
            "type": record.type
        } for record in records
    ]
    return jsonify(records_list), 200

@app.route('/records/<int:record_id>', methods=['PUT'])
@token_required
def update_record(current_user, record_id):
    """
    更新记录。
    用户可以更新指定记录的金额、类别、类型或日期。

    请求数据：
    {
        "amount": 新金额,
        "category": "新类别",
        "type": "income 或 expense",
        "date": "新日期 (可选，格式：YYYY-MM-DD)"
    }
    返回：
    成功：{"message": "记录更新成功。"}
    失败：{"error": "记录未找到。" 或 "无效的日期格式，应为 YYYY-MM-DD。"}
    状态码：200 或 404
    """
    data = request.json
    record = Record.query.filter_by(id=record_id, user_id=current_user.id).first()

    if not record:
        return jsonify({"error": "记录未找到。"}), 404

    record.amount = data.get('amount', record.amount)
    record.category = data.get('category', record.category)
    record.type = data.get('type', record.type)
    if 'date' in data:
        try:
            record.date = datetime.datetime.strptime(data['date'], '%Y-%m-%d')
        except ValueError:
            return jsonify({"error": "无效的日期格式，应为 YYYY-MM-DD。"}), 400

    db.session.commit()
    return jsonify({"message": "记录更新成功。"}), 200

@app.route('/records/<int:record_id>', methods=['DELETE'])
@token_required
def delete_record(current_user, record_id):
    """
    删除记录。
    用户可以删除指定的收入或支出记录。

    返回：
    成功：{"message": "记录删除成功。"}
    失败：{"error": "记录未找到。"}
    状态码：200 或 404
    """
    record = Record.query.filter_by(id=record_id, user_id=current_user.id).first()

    if not record:
        return jsonify({"error": "记录未找到。"}), 404

    db.session.delete(record)
    db.session.commit()
    return jsonify({"message": "记录删除成功。"}), 200

@app.route('/summary', methods=['GET'])
@token_required
def get_summary(current_user):
    """
    获取汇总信息。
    返回当前用户的总收入、总支出和余额。

    返回：
    成功：
    {
        "total_income": 总收入,
        "total_expense": 总支出,
        "balance": 结余
    }
    状态码：200
    """
    records = Record.query.filter_by(user_id=current_user.id).all()
    total_income = sum(record.amount for record in records if record.type == 'income')
    total_expense = sum(record.amount for record in records if record.type == 'expense')
    balance = total_income - total_expense
    summary = {
        "total_income": total_income,
        "total_expense": total_expense,
        "balance": balance
    }
    return jsonify(summary), 200

# 初始化数据库
with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=True)
