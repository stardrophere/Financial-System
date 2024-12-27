# app/models.py

from .extensions import db
import datetime
from pytz import timezone

east_asia_tz = timezone('Asia/Shanghai')

class User(db.Model):
    """
    用户模型类。
    表示应用程序中的用户。
    包含以下字段：
    - id: 用户的唯一标识符，主键。
    - username: 用户名，必须唯一且不能为空。
    - password_hash: 用户密码的哈希值，不能为空。
    """
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)

class Record(db.Model):
    """
    记录模型类。
    表示用户的财务记录。
    包含以下字段：
    - id: 记录的唯一标识符，主键。
    - user_id: 关联的用户 ID，外键，不能为空。
    - amount: 金额，不能为空。
    - category: 类别，不能为空。
    - date: 记录的日期和时间，默认为当前时间。
    - type: 记录的类型（收入或支出），不能为空。
    - note: 备注，可选字段。
    """
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    category = db.Column(db.String(50), nullable=False)
    date = db.Column(db.DateTime, default=lambda: datetime.datetime.now(east_asia_tz))
    type = db.Column(db.String(10), nullable=False)
    note = db.Column(db.String(255), nullable=True)