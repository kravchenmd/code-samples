from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import MetaData

from sqlalchemy.engine import Engine
from sqlalchemy import event

# for proper migrations
# https://stackoverflow.com/questions/62640576/flask-migrate-valueerror-constraint-must-have-a-name
convention = {
    "ix": 'ix_%(column_0_label)s',
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s"
}
metadata = MetaData(naming_convention=convention)
db = SQLAlchemy(metadata=metadata)


# force to enable foreign keys for SQLite
# https://stackoverflow.com/questions/5033547/sqlalchemy-cascade-delete#5034070
@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()
