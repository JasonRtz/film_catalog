import os
import sqlite3
from pathlib import Path
from datetime import datetime, timezone

# Absolute path, so the app works regardless of the directory it is started from
DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "db", "mysakila.db")

# Returns current time in UTC, in the format '%Y-%m-%d %H:%M:%S.000', e.g. 2006-02-15 05:02:19.000
def get_timestamp_now():
	return datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S.000')

# Enable 'row_factory_enabled' when processing free text queries
# Enable 'read_only' to open the database in a mode where any write fails
def get_connection_cursor(dbname = DB_PATH, row_factory_enabled = False, read_only = False):
	if read_only:
		connection = sqlite3.connect(Path(dbname).resolve().as_uri() + "?mode=ro", uri = True)
	else:
		connection = sqlite3.connect(dbname)
	connection.execute("PRAGMA foreign_keys = ON")
	if row_factory_enabled:
		connection.row_factory = sqlite3.Row
	return connection, connection.cursor()

def get_all_tables(dbname = DB_PATH):
	connection, cursor = get_connection_cursor(dbname)
	cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
	tables = cursor.fetchall()
	connection.close()
	return tables

def get_table_fields_names(dbname, table_name):
	connection, cursor = get_connection_cursor(dbname)
	# Table names can't be bound as parameters, so only accept names that exist
	if (table_name,) not in get_all_tables(dbname):
		connection.close()
		raise ValueError(f"Unknown table: {table_name}")
	cursor.execute(f'PRAGMA table_info("{table_name}")')
	names = [row[1] for row in cursor.fetchall()]
	connection.close()

	return names
