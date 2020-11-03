
=====================================================================================================================

I used sqlite for ease but could used a more performant DB
I used DB request but might have used models directly

=====================================================================================================================

** BEFORE launching first, use:
==============================
$ export FLASK_APP=worklife_vacation
$ flask init-db           (first time only)

then launch with:
----------------
$ flask run

=====================================================================================================================

You can create:
 - team:
curl -i -H "Content-Type: application/json" -X POST -d '{"name":"Dev"}' http://localhost:5000/team/create

 - employee:
curl -i -H "Content-Type: application/json" -X POST -d '{"team":"Dev", "first_name":"Eric", "last_name":"Durand"}' http://localhost:5000/employee/create

- Vacation (+update & delete):
curl -i -H "Content-Type: application/json" -X POST -d '{"employee_id":"1", "start_date":"2020-10-10", "end_date": "2020-10-29", "type":"unpaid"}' http://localhost:5000/vacation/create
curl -i -H "Content-Type: application/json" -X POST -d '{"employee_id":"1", "start_date":"2020-10-10", "end_date": "2020-10-29", "type":"paid_normal"}' http://localhost:5000/vacation/create
http://localhost:5000/vacation/delete/2

print all teams / employees / vacations at:
http://localhost:5000/team
http://localhost:5000/employee
http://localhost:5000/vacation

