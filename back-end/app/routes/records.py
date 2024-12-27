# app/routes/records.py

from flask import Blueprint, request, jsonify
from ..extensions import db
from ..models import Record
from ..utils import token_required
import datetime
from pytz import timezone

records_bp = Blueprint('records', __name__)
east_asia_tz = timezone('Asia/Shanghai')

@records_bp.route('/records', methods=['POST'])
@token_required
def add_record(current_user):
    """
    添加记录路由。
    接收 JSON 格式的请求数据，包含金额、类别、类型、备注（可选）和时间戳（可选）。
    验证时间戳是否有效，如果无效则使用当前时间。
    将新记录添加到数据库。
    返回添加成功的消息和状态码 200。

    示例请求:
    POST /records
    {
        "amount": 100.0,
        "category": "Food",
        "type": "Expense",
        "note": "Lunch",
        "timeStamp": 1633072800000
    }

    示例响应:
    {
        "message": "记录添加成功。"
    }
    """
    data = request.json
    amount = float(data.get('amount'))
    category = data.get('category')
    type_data = data.get('type')
    note = data.get('note')  # 可选字段
    timestamp = data.get('timeStamp')  # 时间戳（可选）

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

@records_bp.route('/records', methods=['GET'])
@token_required
def get_records(current_user):
    """
    获取记录路由。
    获取当前用户的所有记录。
    返回记录列表和状态码 200。

    示例请求:
    GET /records

    示例响应:
    [
        {
            "id": 1,
            "amount": 100.0,
            "category": "Food",
            "date": "2021-10-01 12:00",
            "time": "2021-10-01 12:00",
            "timeStamp": 1633072800000,
            "type": "Expense",
            "note": "Lunch"
        }
    ]
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

@records_bp.route('/records/<int:record_id>', methods=['PUT'])
@token_required
def update_record(current_user, record_id):
    """
    更新记录路由。
    接收 JSON 格式的请求数据，包含金额、类别、类型、备注（可选）和时间戳（可选）。
    验证记录是否存在，更新记录字段。
    返回更新成功的消息和状态码 200。

    示例请求:
    PUT /records/1
    {
        "amount": 150.0,
        "category": "Food",
        "type": "Expense",
        "note": "Dinner",
        "timeStamp": 1633072800000
    }

    示例响应:
    {
        "message": "记录更新成功。",
        "updated_date": "2021-10-01 12:00"
    }
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

@records_bp.route('/records/<int:record_id>', methods=['DELETE'])
@token_required
def delete_record(current_user, record_id):
    """
    删除记录路由。
    验证记录是否存在，删除记录。
    返回删除成功的消息和状态码 200。

    示例请求:
    DELETE /records/1

    示例响应:
    {
        "message": "记录删除成功。"
    }
    """
    record = Record.query.filter_by(id=record_id, user_id=current_user.id).first()

    if not record:
        return jsonify({"error": "记录未找到。"}), 404

    db.session.delete(record)
    db.session.commit()
    return jsonify({"message": "记录删除成功。"}), 200