from flask import (
    Blueprint, request
)
from werkzeug.exceptions import abort

from worklife_vacation.db import get_db
from flask import jsonify, make_response

bp = Blueprint('employee', __name__, url_prefix='/employee')

#utils
def get_team_id(name):
    db = get_db()
    team_id = db.execute(
        'SELECT id'
        ' FROM team WHERE name = ?',
        (name,)
    ).fetchone()

    return team_id


@bp.route('/')
def get_all():
    db = get_db()
    employees = db.execute(
        'SELECT e.first_name, e.last_name, t.name as Team'
        ' FROM employee e JOIN team t ON e.team_id = t.id'
        ' ORDER BY e.id'
    ).fetchall()

    data = list()
    for e in employees:
        data.append(dict(e))
        print(dict(e))

    return jsonify(data)


@bp.route('/create', methods=['POST'])
def create():
    """TODO: check if employee already exists"""
    if not request.json:
        abort(400)
    elif not 'first_name' in request.json:
        return make_response(jsonify({'error': 'first_name is required'}), 400)
    elif not 'last_name' in request.json:
        return make_response(jsonify({'error': 'last_name is required'}), 400)
    elif not 'team' in request.json:
        return make_response(jsonify({'error': 'team is required'}), 400)

    #get the team
    team = get_team_id(request.json['team'])
    print(team['id'])

    if not team:
        return make_response(jsonify({'error': 'team not found'}), 400)
    else:
        db = get_db()
        db.execute(
            'INSERT INTO employee (first_name, last_name, team_id)'
            ' VALUES (?, ?, ?)',
            (request.json['first_name'], request.json['last_name'], team['id'])
        )
        db.commit()

    return jsonify({'success':201}), 201



