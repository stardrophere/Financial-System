# app/utils.py

from functools import wraps
from flask import request, jsonify
import jwt
from .extensions import db
from .models import User
from flask import current_app

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token:
            return jsonify({"error": "令牌缺失。"}), 401

        try:
            data = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=["HS256"])
            current_user = db.session.get(User, data['user_id'])
            if not current_user:
                raise ValueError("用户不存在。")
        except Exception as e:
            return jsonify({"error": f"令牌无效：{str(e)}"}), 401

        return f(current_user, *args, **kwargs)

    return decorated

def allowed_file(filename):
    allowed_extensions = {'xls', 'xlsx'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_extensions
