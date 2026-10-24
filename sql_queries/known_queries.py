from myutil.util import get_connection_cursor
from aichat.myollama import ai_query

known_queries_lst = [
    "Actors with first name 'TOM'", "Actors with first name 'TOM'.",
    "Actor with most films", "Actor with most films.",
    "Count films per category", "Count films per category.",
    "What is the average running time of all the films", "What is the average running time of all the films?"
]

# Maps a normalized question (lowercase, no trailing '.' or '?') to its SQL
known_queries_sql = {
    known_queries_lst[0].rstrip(".").lower():
        "SELECT * FROM actor WHERE first_name = 'TOM'",
    known_queries_lst[2].rstrip(".").lower():
        "SELECT a.actor_id, a.first_name, a.last_name, COUNT(fa.film_id) AS film_count "
        "FROM actor a JOIN film_actor fa ON fa.actor_id = a.actor_id "
        "GROUP BY a.actor_id "
        "HAVING film_count = (SELECT MAX(c) FROM (SELECT COUNT(*) AS c FROM film_actor GROUP BY actor_id))",
    known_queries_lst[4].rstrip(".").lower():
        "SELECT c.name AS category, COUNT(fc.film_id) AS film_count "
        "FROM category c LEFT JOIN film_category fc ON fc.category_id = c.category_id "
        "GROUP BY c.category_id ORDER BY film_count DESC",
    known_queries_lst[6].rstrip("?").lower():
        "SELECT AVG(length) AS average_running_time FROM film",
}

def normalize_query(q):
    return q.strip().rstrip(".?").strip().lower()

# Returns (rows, sql, truncated): rows is a list of sqlite3.Row. Questions that are not one of the known ones are
# answered by the local Ollama model. Raises ValueError (with a message for the user) on failure.
def process_query(q):
    sql = known_queries_sql.get(normalize_query(q))
    if sql is None:
        return ai_query(q)

    connection, cursor = get_connection_cursor(row_factory_enabled = True)
    try:
        cursor.execute(sql)
        return cursor.fetchall(), sql, False
    finally:
        connection.close()
