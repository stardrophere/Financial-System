# app/routes/upload.py

from flask import Blueprint, request, jsonify, current_app
from werkzeug.utils import secure_filename
import os
import pandas as pd
import datetime
from ..extensions import db
from ..models import Record
from ..utils import token_required, allowed_file
from pytz import timezone

upload_bp = Blueprint('upload', __name__)
east_asia_tz = timezone('Asia/Shanghai')

@upload_bp.route('/upload', methods=['POST'])
@token_required
def upload_file(current_user):
    """
    文件上传路由。
    接收上传的 Excel 文件（.xls 或 .xlsx 格式），解析文件内容并将记录导入数据库。
    返回上传和导入成功的消息和状态码 200。

    示例请求:
    POST /upload
    - 文件：包含时间、类别、金额、类型和备注列的 Excel 文件

    示例响应:
    {
        "message": "文件上传并导入成功。",
        "imported_records": 10
    }
    """
    if 'file' not in request.files:
        return jsonify({"error": "未找到文件。"}), 400

    file = request.files['file']

    if file.filename == '':
        return jsonify({"error": "未选择文件。"}), 400

    if not allowed_file(file.filename):
        return jsonify({"error": "无效的文件类型。只能上传 .xls 或 .xlsx 文件。"}), 400

    filename = secure_filename(file.filename)
    file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
    file.save(file_path)

    try:
        df = pd.read_excel(file_path)
        required_columns = {'时间', '类别', '金额', '类型', '备注'}
        existing_columns = set(df.columns.str.strip())
        if not required_columns.issubset(existing_columns):
            missing = required_columns - existing_columns
            return jsonify({"error": f"Excel 文件缺少必要的列。缺少列：{', '.join(missing)}"}), 400

        df.columns = [col.strip() for col in df.columns]

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
                amount = float(row['金额'])
                category = str(row['类别'])
                type_data = str(row['类型'])
                note = str(row['备注']) if not pd.isna(row['备注']) else None

                if pd.isna(row['时间']):
                    record_date = datetime.datetime.now(east_asia_tz)
                else:
                    if isinstance(row['时间'], pd.Timestamp):
                        record_date = row['时间'].to_pydatetime().replace(tzinfo=east_asia_tz)
                    else:
                        try:
                            record_date = datetime.datetime.strptime(row['时间'], '%Y-%m-%d %H:%M').replace(
                                tzinfo=east_asia_tz)
                        except ValueError:
                            record_date = datetime.datetime.strptime(row['时间'], '%Y/%m/%d %H:%M').replace(
                                tzinfo=east_asia_tz)

                type_mapping = {"收入": "income", "支出": "expense"}
                type_data = type_mapping[type_data]
                if type_data not in ['income', 'expense']:
                    raise ValueError(f"无效的类型：{type_data}")

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
                current_app.logger.error(f"导入第 {index + 2} 行时出错：{str(e)}")
                continue

        db.session.commit()
        os.remove(file_path)

        return jsonify({"message": "文件上传并导入成功。", "imported_records": imported_records}), 200

    except Exception as e:
        current_app.logger.error(f"处理上传文件时出错：{str(e)}")
        return jsonify({"error": "处理文件时出错。"}), 500