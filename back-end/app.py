from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
import datetime
from functools import wraps
from pytz import timezone
import pandas as pd
from werkzeug.utils import secure_filename
import os
from sqlalchemy import extract, func, case

app = Flask(__name__)
CORS(app)

# 配置 SQLAlchemy 数据库路径
db_path = "sqlite:///user_info.db"
app.config['SQLALCHEMY_DATABASE_URI'] = db_path
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'manwhatcanisay'  # 用于生成和验证 JWT 的密钥

# 配置上传文件夹
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# 确保上传文件夹存在
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

db = SQLAlchemy(app)

# 配置东八区时区
east_asia_tz = timezone('Asia/Shanghai')


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
    date = db.Column(db.DateTime, default=lambda: datetime.datetime.now(east_asia_tz))  # 日期，东八区
    type = db.Column(db.String(10), nullable=False)  # 类型：收入或支出
    note = db.Column(db.String(255), nullable=True)  # 备注字段（可选）


# 使用 session.get() 替代 query.get() 解决警告问题
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')  # 从请求头中获取令牌
        if not token:
            return jsonify({"error": "令牌缺失。"}), 401

        try:
            # 解码令牌，验证合法性，并提取用户信息
            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=["HS256"])
            # 使用用户 ID 从数据库中获取当前用户对象
            current_user = db.session.get(User, data['user_id'])
            if not current_user:
                raise ValueError("用户不存在。")
        except Exception as e:
            return jsonify({"error": f"令牌无效：{str(e)}"}), 401

        # 将 current_user 传递给被装饰的函数
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
    失败：{"error": "用户不存在。" 或 "账号或密码错误。"}
    状态码：200 或 401
    """
    try:
        data = request.json
        username = data.get('username')
        password = data.get('password')

        # 检查用户是否存在
        user = User.query.filter_by(username=username).first()
        if not user:
            return jsonify({"error": "用户不存在。"}), 400

        # 验证密码
        if not check_password_hash(user.password_hash, password):
            return jsonify({"error": "账号或密码错误。"}), 400

        # 生成 JWT 令牌
        token = jwt.encode({
            'user_id': user.id,
            'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=2)
        }, app.config['SECRET_KEY'], algorithm="HS256")

        return jsonify({"message": "登录成功。", "token": token}), 200

    except Exception as e:
        return jsonify({"error": "登陆失败"}), 400


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
        "type": "income 或 expense",
        "note": "备注（可选）",
        "timeStamp": int  # 时间戳（可选，单位为秒）
    }
    返回：
    成功：{"message": "记录添加成功。"}
    失败：{"error": "记录添加失败"}
    状态码：200 或 400
    """
    data = request.json
    amount = float(data.get('amount'))
    category = data.get('category')
    type_data = data.get('type')
    note = data.get('note')  # 可选字段
    timestamp = data.get('timeStamp')  # 时间戳（可选）

    # 如果时间戳存在，则将其转换为 datetime 对象，否则使用默认值
    try:
        if timestamp:
            timestamp = timestamp / 1000  # 从毫秒转换为秒
            record_date = datetime.datetime.fromtimestamp(timestamp, tz=east_asia_tz)
        else:
            record_date = datetime.datetime.now(east_asia_tz)
    except (ValueError, TypeError):
        return jsonify({"error": "无效的时间戳。"}), 400

    record = Record(user_id=current_user.id, amount=amount, category=category, type=type_data, note=note,
                    date=record_date)
    try:
        db.session.add(record)
        db.session.commit()
        return jsonify({"message": "记录添加成功。"}), 200
    except Exception as e:
        return jsonify({"error": "记录添加失败", "details": str(e)}), 400


@app.route('/records', methods=['GET'])
@token_required
def get_records(current_user):
    """
    获取所有记录。
    返回与当前用户关联的所有收入或支出记录。

    返回：
    成功：记录列表，包括备注
    状态码：200
    """
    records = Record.query.filter_by(user_id=current_user.id).all()
    records_list = [
        {
            "id": record.id,
            "amount": record.amount,
            "category": record.category,
            "date": record.date.strftime('%Y-%m-%d %H:%M'),
            "time": record.date.strftime('%Y-%m-%d %H:%M'),
            "timeStamp": int(record.date.timestamp()) * 1000,  # 返回时间戳
            "type": record.type,
            "note": record.note  # 返回备注字段
        } for record in records
    ]
    return jsonify(records_list), 200


@app.route('/records/<int:record_id>', methods=['PUT'])
@token_required
def update_record(current_user, record_id):
    """
    更新记录。
    用户可以更新指定记录的金额、类别、类型、日期或备注。

    请求数据：
    {
        "amount": 新金额,
        "category": "新类别",
        "type": "income 或 expense",
        "timeStamp": 日期时间戳 (可选，单位：秒),
        "note": "备注（可选）"
    }
    返回：
    成功：{"message": "记录更新成功。"}
    失败：{"error": "记录未找到。" 或 "无效的时间戳。"}
    状态码：200 或 404
    """
    data = request.json
    record = Record.query.filter_by(id=record_id, user_id=current_user.id).first()

    if not record:
        return jsonify({"error": "记录未找到。"}), 404

    # 更新记录字段
    record.amount = data.get('amount', record.amount)
    record.category = data.get('category', record.category)
    record.type = data.get('type', record.type)
    record.note = data.get('note', record.note)  # 更新备注内容

    # 如果前端传递了时间戳，则将其转换为 datetime 对象
    if 'timeStamp' in data:
        try:
            record.date = datetime.datetime.fromtimestamp(data['timeStamp'] / 1000, tz=east_asia_tz)
        except (ValueError, TypeError):
            return jsonify({"error": "无效的时间戳。"}), 400

    db.session.commit()
    return jsonify({"message": "记录更新成功。", "updated_date": record.date.strftime('%Y-%m-%d %H:%M')}), 200


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
    根据前端指定的时间粒度（年、月、日，或自定义时间范围），返回当前用户的收入、支出和结余的汇总信息。

    请求参数：
    - period: string (可选，'year'、'month'、'day' 或 'overall' 或 'custom')
    - start_date: string (可选，开始日期，仅在 period 为 'custom' 时有效)
    - end_date: string (可选，结束日期，仅在 period 为 'custom' 时有效)

    返回：
    成功：
    {
        "period": "year" | "month" | "day" | "overall" | "custom",
        "summary": [
            {
                "year": 2024,
                "month": 5,
                "total_income": 50000,
                "total_expense": 30000,
                "balance": 20000
            },
            ...
        ]
    }
    """
    # 获取查询参数 'period' 和可选的时间范围
    period = request.args.get('period', default='overall').lower()
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')

    if period not in ['year', 'month', 'day', 'overall', 'custom']:
        return jsonify({"error": "无效的 period 参数。可选值为 'year'、'month'、'day'、'overall' 或 'custom'."}), 400

    try:
        # 自定义时间范围处理
        filters = [Record.user_id == current_user.id]
        # 转换字符串为 datetime 对象
        if start_date and end_date:
            start_date = datetime.datetime.strptime(start_date, '%Y-%m-%d')
            end_date = datetime.datetime.strptime(end_date + " 23:59", '%Y-%m-%d %H:%M')

            filters.append(Record.date >= start_date)
            filters.append(Record.date <= end_date)

        if period == 'year':
            summary_query = db.session.query(
                extract('year', Record.date).label('year'),
                func.sum(case(
                    (Record.type == 'income', Record.amount),
                    else_=0
                )).label('total_income'),
                func.sum(case(
                    (Record.type == 'expense', Record.amount),
                    else_=0
                )).label('total_expense')
            ).filter(*filters).group_by('year').order_by('year').all()

            summary = [
                {
                    "year": int(row.year),
                    "total_income": row.total_income or 0,
                    "total_expense": row.total_expense or 0,
                    "balance": (row.total_income or 0) - (row.total_expense or 0)
                }
                for row in summary_query
            ]

        elif period == 'month':
            summary_query = db.session.query(
                extract('year', Record.date).label('year'),
                extract('month', Record.date).label('month'),
                func.sum(case(
                    (Record.type == 'income', Record.amount),
                    else_=0
                )).label('total_income'),
                func.sum(case(
                    (Record.type == 'expense', Record.amount),
                    else_=0
                )).label('total_expense')
            ).filter(*filters).group_by('year', 'month').order_by('year', 'month').all()

            summary = [
                {
                    "year": int(row.year),
                    "month": int(row.month),
                    "total_income": row.total_income or 0,
                    "total_expense": row.total_expense or 0,
                    "balance": (row.total_income or 0) - (row.total_expense or 0)
                }
                for row in summary_query
            ]

        elif period == 'day':
            summary_query = db.session.query(
                extract('year', Record.date).label('year'),
                extract('month', Record.date).label('month'),
                extract('day', Record.date).label('day'),
                func.sum(case(
                    (Record.type == 'income', Record.amount),
                    else_=0
                )).label('total_income'),
                func.sum(case(
                    (Record.type == 'expense', Record.amount),
                    else_=0
                )).label('total_expense')
            ).filter(*filters).group_by('year', 'month', 'day').order_by('year', 'month', 'day').all()

            summary = [
                {
                    "year": int(row.year),
                    "month": int(row.month),
                    "day": int(row.day),
                    "total_income": row.total_income or 0,
                    "total_expense": row.total_expense or 0,
                    "balance": (row.total_income or 0) - (row.total_expense or 0)
                }
                for row in summary_query
            ]

        elif period == 'overall':
            overall_summary = db.session.query(
                func.sum(case(
                    (Record.type == 'income', Record.amount),
                    else_=0
                )).label('total_income'),
                func.sum(case(
                    (Record.type == 'expense', Record.amount),
                    else_=0
                )).label('total_expense')
            ).filter(*filters).one()

            summary = [{
                "total_income": overall_summary.total_income or 0,
                "total_expense": overall_summary.total_expense or 0,
                "balance": (overall_summary.total_income or 0) - (overall_summary.total_expense or 0)
            }]

        elif period == 'custom':
            summary_query = db.session.query(
                extract('year', Record.date).label('year'),
                extract('month', Record.date).label('month'),
                extract('day', Record.date).label('day'),
                func.sum(case(
                    (Record.type == 'income', Record.amount),
                    else_=0
                )).label('total_income'),
                func.sum(case(
                    (Record.type == 'expense', Record.amount),
                    else_=0
                )).label('total_expense')
            ).filter(*filters).group_by('year', 'month', 'day').order_by('year', 'month', 'day').all()

            summary = [
                {
                    "year": int(row.year),
                    "month": int(row.month),
                    "day": int(row.day),
                    "total_income": row.total_income or 0,
                    "total_expense": row.total_expense or 0,
                    "balance": (row.total_income or 0) - (row.total_expense or 0)
                }
                for row in summary_query
            ]

        return jsonify({
            "period": period,
            "summary": summary
        }), 200

    except Exception as e:
        app.logger.error(f"获取汇总信息时出错：{str(e)}")
        return jsonify({"error": "获取汇总信息时出错。"}), 500


@app.route('/summary_pie', methods=['GET'])
@token_required
def get_summary_pie(current_user):
    """
    获取分类汇总信息（饼图数据）。
    根据指定的时间粒度（年、月、日、整体），返回当前用户的收入和支出按类别的汇总信息。

    请求参数：
    - period: string (可选，'year'、'month'、'day'、'overall')
    - year: int (可选，当 period=year, month, day 时需要)
    - month: int (可选，当 period=month, day 时需要)
    - day: int (可选，当 period=day 时需要)

    返回：
    成功：
    {
        "period": "year" | "month" | "day" | "overall",
        "year": 2024,          # 当 period 不为 'overall' 时返回
        "month": 4,            # 当 period 为 'month' 或 'day' 时返回
        "day": 27,             # 当 period 为 'day' 时返回
        "income_categories": [
            {"category": "工资", "amount": 10000},
            {"category": "投资", "amount": 5000},
            ...
        ],
        "expense_categories": [
            {"category": "餐饮", "amount": 7000},
            {"category": "交通", "amount": 2000},
            ...
        ]
    }
    """
    # 获取查询参数 'period'
    period = request.args.get('period', default='overall').lower()

    if period not in ['year', 'month', 'day', 'overall']:
        return jsonify({"error": "无效的 period 参数。可选值为 'year'、'month'、'day' 或 'overall'."}), 400

    # 根据 period 获取相应的时间参数
    year = request.args.get('year', type=int)
    month = request.args.get('month', type=int)
    day = request.args.get('day', type=int)

    try:
        # 构建查询条件
        filters = [Record.user_id == current_user.id]

        if period == 'year':
            if not year:
                return jsonify({"error": "缺少必要的参数：year。"}), 400
            filters.append(extract('year', Record.date) == year)
        elif period == 'month':
            if not year or not month:
                return jsonify({"error": "缺少必要的参数：year 或 month。"}), 400
            filters.append(extract('year', Record.date) == year)
            filters.append(extract('month', Record.date) == month)
        elif period == 'day':
            if not year or not month or not day:
                return jsonify({"error": "缺少必要的参数：year、month 或 day。"}), 400
            filters.append(extract('year', Record.date) == year)
            filters.append(extract('month', Record.date) == month)
            filters.append(extract('day', Record.date) == day)

        # 查询收入按类别汇总
        income_summary = db.session.query(
            Record.category,
            func.sum(Record.amount).label('amount')
        ).filter(*filters, Record.type == 'income').group_by(Record.category).all()

        # 查询支出按类别汇总
        expense_summary = db.session.query(
            Record.category,
            func.sum(Record.amount).label('amount')
        ).filter(*filters, Record.type == 'expense').group_by(Record.category).all()

        # 构建响应数据
        response_data = {
            "period": period,
            "income_categories": [{"category": row.category, "amount": row.amount} for row in income_summary],
            "expense_categories": [{"category": row.category, "amount": row.amount} for row in expense_summary]
        }

        if period != 'overall':
            response_data["year"] = year
        if period in ['month', 'day']:
            response_data["month"] = month
        if period == 'day':
            response_data["day"] = day

        return jsonify(response_data), 200

    except Exception as e:
        app.logger.error(f"获取分类汇总信息时出错：{str(e)}")
        return jsonify({"error": "获取分类汇总信息时出错。"}), 500


@app.route('/upload', methods=['POST'])
@token_required
def upload_file(current_user):
    """
    上传 Excel 文件并将数据导入数据库。
    接受一个 Excel 文件，解析文件内容，根据列名将数据插入 Record 表。

    请求：
    multipart/form-data
    - file: Excel 文件 (.xls 或 .xlsx)

    返回：
    成功：{"message": "文件上传并导入成功。", "imported_records": 导入的记录数量}
    失败：{"error": "错误信息"}
    状态码：200 或 400
    """
    if 'file' not in request.files:
        return jsonify({"error": "未找到文件。"}), 400

    file = request.files['file']

    if file.filename == '':
        return jsonify({"error": "未选择文件。"}), 400

    if not allowed_file(file.filename):
        return jsonify({"error": "无效的文件类型。只能上传 .xls 或 .xlsx 文件。"}), 400

    filename = secure_filename(file.filename)
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(file_path)

    try:
        # 读取 Excel 文件
        df = pd.read_excel(file_path)

        # 定义所需的列（中文）
        required_columns = {'时间', '类别', '金额', '类型', '备注'}

        # 检查是否所有必需的列都存在
        existing_columns = set(df.columns.str.strip())
        if not required_columns.issubset(existing_columns):
            missing = required_columns - existing_columns
            return jsonify({"error": f"Excel 文件缺少必要的列。缺少列：{', '.join(missing)}"}), 400

        # 规范化列名（去除空格）
        df.columns = [col.strip() for col in df.columns]

        # 创建一个映射，将中文列名映射到数据库字段
        column_mapping = {
            '时间': 'date',
            '类别': 'category',
            '金额': 'amount',
            '类型': 'type',
            '备注': 'note'
        }

        imported_records = 0

        for index, row in df.iterrows():
            try:
                # 提取并映射数据
                amount = float(row['金额'])
                category = str(row['类别'])
                type_data = str(row['类型'])
                note = str(row['备注']) if not pd.isna(row['备注']) else None

                # 处理日期
                if pd.isna(row['时间']):
                    record_date = datetime.datetime.now(east_asia_tz)
                else:
                    if isinstance(row['时间'], pd.Timestamp):
                        record_date = row['时间'].to_pydatetime().replace(tzinfo=east_asia_tz)
                    else:
                        # 尝试解析字符串日期
                        try:
                            record_date = datetime.datetime.strptime(row['时间'], '%Y-%m-%d %H:%M').replace(
                                tzinfo=east_asia_tz)
                        except ValueError:
                            # 尝试其他日期格式
                            record_date = datetime.datetime.strptime(row['时间'], '%Y/%m/%d %H:%M').replace(
                                tzinfo=east_asia_tz)

                # 验证类型
                type_mapping = {"收入": "income", "支出": "expense"}
                type_data = type_mapping[type_data]
                if type_data not in ['income', 'expense']:
                    raise ValueError(f"无效的类型：{type_data}")

                # 创建 Record 对象
                record = Record(
                    user_id=current_user.id,
                    amount=amount,
                    category=category,
                    type=type_data,
                    note=note,
                    date=record_date
                )
                db.session.add(record)
                imported_records += 1
            except Exception as e:
                # 如果某一行有问题，跳过并记录错误
                app.logger.error(f"导入第 {index + 2} 行时出错：{str(e)}")  # Excel 行从 1 开始，标题行为第1行
                continue

        db.session.commit()

        # 删除上传的文件（可选）
        os.remove(file_path)

        return jsonify({"message": "文件上传并导入成功。", "imported_records": imported_records}), 200

    except Exception as e:
        app.logger.error(f"处理上传文件时出错：{str(e)}")
        return jsonify({"error": "处理文件时出错。"}), 500


def allowed_file(filename):
    allowed_extensions = {'xls', 'xlsx'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_extensions


# 初始化数据库
with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
