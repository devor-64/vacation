from flask import (
    Blueprint, request
)
from werkzeug.exceptions import abort

from worklife_vacation.db import get_db
from flask import jsonify, make_response
from datetime import datetime

bp = Blueprint('vacation', __name__, url_prefix='/vacation')


#util
def check_vacation(employee_id, start_date, end_date, vacation_type):
    operation = 'create'
    error = ''
    corrected_start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
    corrected_end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
    id = 0

    if start_date > end_date:
        operation = 'error'
        error = 'starting date > ending date'

    db = get_db()

    employee = db.execute(
        'SELECT *'
        ' FROM employee WHERE id=?',
        (employee_id,)
    ).fetchone()

    if not employee:
        operation = 'error'
        error = 'employee not found'
    else:
        vacations = db.execute(
            'SELECT id, type, start_date, end_date'
            ' FROM vacation WHERE employee_id=?',
            (employee_id,)
        ).fetchall()

        for v in vacations:
            print("start: {}".format(v['start_date']))
            print("corrected: {}".format(corrected_start_date))
            if (v['start_date'] < corrected_start_date) and (v['end_date'] > corrected_start_date):
                if v['type'] != vacation_type:
                    operation = 'error'
                    error = 'Vacation with other type already existing at that date'
                else:
                    if v['end_date'] >= corrected_end_date:
                        operation = 'nothing'
                    else:
                        operation = 'update'
                        id = v['id']
                        corrected_start_date = min(v['start_date'], corrected_start_date)
                        corrected_end_date = max(v['end_date'], corrected_end_date)
            elif (v['start_date'] > corrected_start_date) and (v['start_date'] < corrected_end_date):
                if v['type'] != vacation_type:
                    operation = 'error'
                    error = 'Vacation with other type already existing at that date'
                else:
                    if v['end_date'] <= corrected_end_date:
                        operation = 'nothing'
                    else:
                        operation = 'update'
                        id = v['id']
                        corrected_start_date = min(v['start_date'], corrected_start_date)
                        corrected_end_date = max(v['end_date'], corrected_end_date)
            elif ((v['type'] == vacation_type) and ((v['start_date'] == corrected_end_date) or
                                                    (v['end_date'] == corrected_start_date) or
                                                    (v['start_date'] == corrected_start_date) or
                                                    (v['end_date'] == corrected_end_date))):
                operation = 'update'
                id = v['id']
                corrected_start_date = min(v['start_date'], corrected_start_date)
                corrected_end_date = max(v['end_date'], corrected_end_date)
            elif ((v['type'] != vacation_type) and ((v['start_date'] == corrected_start_date) or
                                                    (v['end_date'] == corrected_end_date))):
                print("Different type !!")
                operation = 'error'
                error = 'Vacation with other type already existing at that date'

    print("Done checking")

    return {'operation': operation,
            'error': error,
            'start_date': corrected_start_date,
            'end_date': corrected_end_date,
            'id': id}


def validate_date_format(date_text):
    try:
        datetime.strptime(date_text, '%Y-%m-%d')
    except ValueError:
        return False
    return True


@bp.route('/')
def get_all():
    db = get_db()
    vacations = db.execute(
        'SELECT e.first_name, e.last_name, v.type, v.start_date, v.end_date'
        ' FROM employee e JOIN vacation v ON e.id = v.employee_id'
        ' ORDER BY v.id'
    ).fetchall()

    data = list()
    for v in vacations:
        data.append(dict(v))
        print(dict(v))

    return jsonify(data)


@bp.route('/create', methods=['POST'])
def create():
    if not request.json:
        abort(400)
    elif not 'employee_id' in request.json:
        return make_response(jsonify({'error': 'employee_id is required'}), 400)
    elif not 'start_date' in request.json:
        return make_response(jsonify({'error': 'start_date is required'}), 400)
    elif not 'end_date' in request.json:
        return make_response(jsonify({'error': 'end_date is required'}), 400)
    elif not validate_date_format(request.json['start_date']) or not validate_date_format(request.json['end_date']):
        return make_response(jsonify({'error': 'dates must be "YYYY-MM-DD"'}), 400)

    if 'type' in request.json:
        if request.json['type'] not in ['unpaid', 'paid_rtt', 'paid_normal']:
            return make_response(jsonify({'error': 'unknown vacation type'}), 400)
        else:
            vacation_type = request.json['type']
    else:
        vacation_type = 'paid_normal'

    vacation = check_vacation(request.json['employee_id'], request.json['start_date'], request.json['end_date'], vacation_type)

    if vacation['operation'] == 'error':
        return jsonify({'error' : vacation['error']}), 400
    elif vacation['operation'] == 'update':
        print("updating {}".format(vacation['id']))
        return update_vacations(vacation['start_date'], vacation['end_date'], vacation_type, vacation['id'])
    else:
        db = get_db()
        db.execute(
            'INSERT INTO vacation (employee_id, type, start_date, end_date)'
            ' VALUES (?, ?, ?, ?)',
            (request.json['employee_id'], vacation_type, vacation['start_date'], vacation['end_date'])
        )
        db.commit()

    return jsonify({'success':201}), 201


@bp.route('/update', methods=['GET', 'POST'])
def update():
    if not request.json:
        abort(400)
    elif not 'id' in request.json:
        return make_response(jsonify({'error': 'id is required'}), 400)
    elif not 'start_date' in request.json:
        return make_response(jsonify({'error': 'start_date is required'}), 400)
    elif not 'end_date' in request.json:
        return make_response(jsonify({'error': 'end_date is required'}), 400)

    if 'type' in request.json:
        if request.json['type'] not in ['unpaid', 'paid_rtt', 'paid_normal']:
            return make_response(jsonify({'error': 'unknown vacation type'}), 400)
        else:
            vacation_type = request.json['type']
    else:
        vacation_type = 'paid_normal'

    return update_vacations(request.json['start_date'], request.json['end_date'],vacation_type, request.json['id'])


def update_vacations(start_date, end_date, vacation_type, id):
    db = get_db()
    db.execute(
        'UPDATE vacation SET start_date = ?, end_date = ?, type = ?'
        ' WHERE id = ?',
        (start_date, end_date, vacation_type, id)
    )
    db.commit()

    return jsonify({'success': 204}), 204


@bp.route('/delete/<int:id>', methods=['GET', 'POST'])
def delete(id):
    db = get_db()
    db.execute(
        'DELETE FROM vacation'
        ' WHERE id = ?',
        (id,)
    )
    db.commit()

    return jsonify({'success': 200}), 200