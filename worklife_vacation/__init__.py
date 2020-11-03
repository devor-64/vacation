# TO do when starting:
# source venv/vacation_env/bin/activate
# export FLASK_APP=worklife_vacation
# export FLASK_ENV=development
# flask init-db (if necessary)

import os

from flask import Flask


def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='dev',
        DATABASE=os.path.join(app.instance_path, 'worklife_vacation.sqlite'),
    )

    if test_config is None:
        app.config.from_pyfile('config.py', silent=True)
    else:
        app.config.from_mapping(test_config)

    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # a simple page that says hello
    @app.route('/hello')
    def hello():
        return 'Hello, Worklife!'

    from . import db
    db.init_app(app)

    from . import team
    app.register_blueprint(team.bp)
    app.add_url_rule('/', endpoint='get_all')

    from . import employee
    app.register_blueprint(employee.bp)

    from . import vacation
    app.register_blueprint(vacation.bp)

    return app
