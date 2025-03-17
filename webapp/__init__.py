import os
from flask import Flask, render_template
from flask_executor import Executor
from werkzeug.middleware.dispatcher import DispatcherMiddleware
from werkzeug.wrappers import Response

executor = None
task_meta_data = {}


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    prefix = os.getenv('APP_ROUTE_PREFIX', '')
    workers = os.getenv('EXECUTOR_MAX_WORKERS', '2')
    exec_type = os.getenv('EXECUTOR_TYPE', 'process')
    app.config.from_mapping(
        SECRET_KEY=os.urandom(12).hex(),
        EXECUTOR_MAX_WORKERS=workers,
        EXECUTOR_PROPAGATE_EXCEPTIONS=True,
        EXECUTOR_TYPE=exec_type,
        APPLICATION_ROOT=prefix
    )

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    global executor
    executor = Executor(app)

    from . import views
    app.register_blueprint(views.bp)
    app.wsgi_app = DispatcherMiddleware(
        Response('Not Found', status=404),
        {prefix: app.wsgi_app}
    )
    return app
