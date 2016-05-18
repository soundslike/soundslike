from app import create_app
from app import db as _db
from config import TestingConfig

from alembic.command import upgrade, downgrade
from alembic.config import Config
from flask.ext.migrate import Migrate
import pytest
import os

basedir = os.path.abspath(os.path.dirname(__file__))
ALEMBIC_CONFIG = os.path.join(basedir, 'migrations/alembic.ini')

@pytest.fixture(scope='session')
def app(request):
    app = create_app('testing')

    ctx = app.app_context()
    ctx.push()

    def teardown():
        ctx.pop()

    request.addfinalizer(teardown)
    return app

def apply_migrations(app):
    """Applies all alembic migrations."""
    print(ALEMBIC_CONFIG)
    config = Config(ALEMBIC_CONFIG)
    config.set_main_option('sqlalchemy.url', app.config['SQLALCHEMY_DATABASE_URI'])
    upgrade(config, 'head')

@pytest.fixture(scope='session')
def db(app, request):
    """Session-wide test database."""

    def teardown():
        _db.session.close_all()
        config = Config(ALEMBIC_CONFIG)
        config.set_main_option('sqlalchemy.url', app.config['SQLALCHEMY_DATABASE_URI'])
        downgrade(config, 'base')

    migrate = Migrate(app, _db)
    _db.app = app
    apply_migrations(app)
    request.addfinalizer(teardown)
    return _db

@pytest.fixture
def db_class(request, db):
    if request.cls is not None:
        request.cls.db = db

@pytest.fixture(scope='function')
def session(db, request):
    """Creates a new database session for a test."""
    connection = db.engine.connect()
    transaction = connection.begin()

    options = dict(bind=connection, binds={})
    session = db.create_scoped_session(options=options)

    db.session = session

    def teardown():
        transaction.rollback()
        connection.close()
        session.remove()

    request.addfinalizer(teardown)
    return session
