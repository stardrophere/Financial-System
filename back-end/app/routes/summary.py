# app/routes/summary.py

from flask import Blueprint, request, jsonify, current_app
from ..extensions import db
from ..models import Record
from ..utils import token_required
from sqlalchemy import extract, func, case
import datetime

summary_bp = Blueprint('summary', __name__)

@summary_bp.route('/summary', methods=['GET'])
@token_required
def get_summary(current_user):
    """
    获取汇总信息路由。
    根据 period 参数（year、month、day、overall、custom）获取汇总信息。
    可选的 start_date 和 end_date 参数用于自定义时间范围。
    返回汇总信息和状态码 200。

    示例请求:
    GET /summary?period=month&start_date=2021-01-01&end_date=2021-12-31

    示例响应:
    {
        "period": "month",
        "summary": [
            {
                "year": 2021,
                "month": 1,
                "total_income": 1000.0,
                "total_expense": 500.0,
                "balance": 500.0
            },
            ...
        ]
    }
    """
    period = request.args.get('period', default='overall').lower()
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')

    if period not in ['year', 'month', 'day', 'overall', 'custom']:
        return jsonify({"error": "无效的 period 参数。可选值为 'year'、'month'、'day'、'overall' 或 'custom'."}), 400

    try:
        filters = [Record.user_id == current_user.id]
        if start_date and end_date:
            start_date = datetime.datetime.strptime(start_date, '%Y-%m-%d')
            end_date = datetime.datetime.strptime(end_date + " 23:59", '%Y-%m-%d %H:%M')
            filters.append(Record.date >= start_date)
            filters.append(Record.date <= end_date)

        summary = []

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
        current_app.logger.error(f"获取汇总信息时出错：{str(e)}")
        return jsonify({"error": "获取汇总信息时出错。"}), 500

@summary_bp.route('/summary_pie', methods=['GET'])
@token_required
def get_summary_pie(current_user):
    """
    获取分类汇总信息路由。
    根据 period 参数（year、month、day、overall）获取分类汇总信息。
    返回分类汇总信息和状态码 200。

    示例请求:
    GET /summary_pie?period=month&year=2021&month=1

    示例响应:
    {
        "period": "month",
        "year": 2021,
        "month": 1,
        "income_categories": [
            {"category": "Salary", "amount": 5000.0},
            ...
        ],
        "expense_categories": [
            {"category": "Food", "amount": 200.0},
            ...
        ]
    }
    """
    period = request.args.get('period', default='overall').lower()

    if period not in ['year', 'month', 'day', 'overall']:
        return jsonify({"error": "无效的 period 参数。可选值为 'year'、'month'、'day' 或 'overall'."}), 400

    year = request.args.get('year', type=int)
    month = request.args.get('month', type=int)
    day = request.args.get('day', type=int)

    try:
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

        income_summary = db.session.query(
            Record.category,
            func.sum(Record.amount).label('amount')
        ).filter(*filters, Record.type == 'income').group_by(Record.category).all()

        expense_summary = db.session.query(
            Record.category,
            func.sum(Record.amount).label('amount')
        ).filter(*filters, Record.type == 'expense').group_by(Record.category).all()

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
        current_app.logger.error(f"获取分类汇总信息时出错：{str(e)}")
        return jsonify({"error": "获取分类汇总信息时出错。"}), 500