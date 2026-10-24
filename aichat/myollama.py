import os
import re
import sqlite3
import time

from myutil.util import get_connection_cursor

MODEL = os.environ.get("OLLAMA_MODEL", "qwen2.5-coder:7b")
MAX_ROWS = 200
MAX_SECONDS = 5

# Everything the generated SQL is allowed to do: read data, nothing else
ALLOWED_ACTIONS = {sqlite3.SQLITE_SELECT, sqlite3.SQLITE_READ, sqlite3.SQLITE_FUNCTION, sqlite3.SQLITE_RECURSIVE}


class AIQueryError(ValueError):
	"""A problem the user can be told about (Ollama missing, bad SQL, ...)."""


# Compact description of the database, e.g. "film(film_id, title, language_id -> language.language_id, ...)"
def get_schema_description():
	connection, cursor = get_connection_cursor(read_only = True)
	lines = []
	tables = [r[0] for r in cursor.execute("SELECT name FROM sqlite_master WHERE type = 'table' AND name NOT LIKE 'sqlite_%' ORDER BY name")]
	for table in tables:
		foreign_keys = {r[3]: f"{r[2]}.{r[4]}" for r in cursor.execute(f'PRAGMA foreign_key_list("{table}")')}
		columns = []
		for r in cursor.execute(f'PRAGMA table_info("{table}")'):
			name = r[1]
			columns.append(f"{name} -> {foreign_keys[name]}" if name in foreign_keys else name)
		lines.append(f"{table}({', '.join(columns)})")
	connection.close()
	return "\n".join(lines)


def build_messages(question, schema, previous_sql = None, error = None):
	system = (
		"You translate questions into a single SQLite SELECT query for the database below.\n"
		"Respond with only the SQL, no explanation and no markdown. Use only the tables and columns listed.\n"
		"'->' marks a foreign key. Use the actor, film, category and language names as stored (actor names are uppercase).\n\n"
		f"Database schema:\n{schema}"
	)
	messages = [{"role": "system", "content": system}, {"role": "user", "content": question}]
	if previous_sql is not None:
		messages.append({"role": "assistant", "content": previous_sql})
		messages.append({"role": "user", "content": f"That query failed with: {error}\nReturn a corrected SQLite SELECT query, only the SQL."})
	return messages


def ask_model(messages):
	try:
		from ollama import Client, ResponseError
	except ImportError:
		raise AIQueryError("The 'ollama' Python package is not installed. Run: pip install ollama")
	try:
		response = Client(timeout = 120).chat(model = MODEL, messages = messages, options = {"temperature": 0})
	except ResponseError as e:
		raise AIQueryError(f"Ollama error: {e.error}. If the model is missing, run: ollama pull {MODEL}")
	except Exception:
		raise AIQueryError("Could not reach Ollama. Make sure it is installed and running (https://ollama.com/download).")
	return response["message"]["content"]


# Models like to wrap SQL in ```sql fences or add chatter; keep only the statement itself
def extract_sql(text):
	fenced = re.search(r"```(?:sql)?\s*(.*?)```", text, re.S | re.I)
	if fenced:
		text = fenced.group(1)
	start = re.search(r"\b(select|with)\b", text, re.I)
	if not start:
		raise AIQueryError("The model did not return a SELECT query. Try rephrasing your question.")
	return text[start.start():].strip().rstrip(";").strip()


def _authorizer(action, arg1, arg2, db_name, source):
	return sqlite3.SQLITE_OK if action in ALLOWED_ACTIONS else sqlite3.SQLITE_DENY


# Runs the SQL on a read-only connection that can only read, for at most MAX_SECONDS and MAX_ROWS rows
# Returns (rows, truncated)
def run_readonly(sql):
	connection, cursor = get_connection_cursor(row_factory_enabled = True, read_only = True)
	deadline = time.monotonic() + MAX_SECONDS
	connection.set_authorizer(_authorizer)
	connection.set_progress_handler(lambda: 1 if time.monotonic() > deadline else 0, 10000)
	try:
		cursor.execute(sql)
		rows = cursor.fetchmany(MAX_ROWS + 1)
		return rows[:MAX_ROWS], len(rows) > MAX_ROWS
	finally:
		connection.close()


# Returns (rows, sql, truncated). Gives the model one chance to fix a query that fails.
def ai_query(question):
	schema = get_schema_description()
	sql = extract_sql(ask_model(build_messages(question, schema)))
	try:
		rows, truncated = run_readonly(sql)
		return rows, sql, truncated
	except sqlite3.Error as first_error:
		retry_sql = extract_sql(ask_model(build_messages(question, schema, sql, first_error)))
		try:
			rows, truncated = run_readonly(retry_sql)
			return rows, retry_sql, truncated
		except sqlite3.Error as e:
			raise AIQueryError(f"The generated SQL failed: {e}. Query was: {retry_sql}")
