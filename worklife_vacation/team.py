from flask import (
    Blueprint, request
)
from werkzeug.exceptions import abort

from worklife_vacation.db import get_db
from flask import jsonify, make_response

bp = Blueprint('team', __name__, url_prefix='/team')


@bp.route('/')
def get_all():
    db = get_db()
    teams = db.execute(
        'SELECT id, name'
        ' FROM team'
        ' ORDER BY id'
    ).fetchall()

    data = list()
    for t in teams:
        data.append(dict(t))
        print(dict(t))

    return jsonify(data)



@bp.route('/create', methods=['POST'])
def create():
    """TODO: check if employee already exists
    To create a team:
    curl -i -H "Content-Type: application/json" -X POST -d '{"name":"Manager"}' http://localhost:5000/team/create"""
    if not request.json:
        abort(400)
    elif not 'name' in request.json:
        return make_response(jsonify({'error': 'name is required'}), 400)
    else:
        db = get_db()
        db.execute(
            'INSERT INTO team (name)'
            ' VALUES (?)',
            (request.json['name'],)
        )
        db.commit()

    return jsonify({'success': 201}), 201
