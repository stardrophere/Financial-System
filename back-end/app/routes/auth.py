# app/routes/auth.py

from flask import Blueprint, request, jsonify, current_app
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
import datetime
from ..extensions import db
from ..models import User

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['POST'])
def register():
    """
    用户注册路由。
    接收 JSON 格式的请求数据，包含用户名和密码。
    验证用户名和密码是否存在，检查用户名是否已被注册。
    如果验证通过，哈希密码并将新用户添加到数据库。
    返回注册成功的消息和状态码 201。

    示例请求:
    POST /register
    {
        "username": "example_user",
        "password": "example_password"
    }

    示例响应:
    {
        "message": "用户注册成功。"
    }
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

@auth_bp.route('/login', methods=['POST'])
def login():
    """
    用户登录路由。
    接收 JSON 格式的请求数据，包含用户名和密码。
    验证用户名和密码是否正确。
    如果验证通过，生成 JWT 令牌并返回登录成功的消息和令牌。
    返回登录失败的消息和状态码 400。

    示例请求:
    POST /login
    {
        "username": "example_user",
        "password": "example_password"
    }

    示例响应:
    {
        "message": "登录成功。",
        "token": "jwt_token_here"
    }
    """
    try:
        data = request.json
        username = data.get('username')
        password = data.get('password')

        user = User.query.filter_by(username=username).first()
        if not user:
            return jsonify({"error": "用户不存在。"}), 400

        if not check_password_hash(user.password_hash, password):
            return jsonify({"error": "账号或密码错误。"}), 400

        token = jwt.encode({
            'user_id': user.id,
            'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=2)
        }, current_app.config['SECRET_KEY'], algorithm="HS256")

        return jsonify({"message": "登录成功。", "token": token}), 200

    except Exception:
        return jsonify({"error": "登陆失败"}), 400