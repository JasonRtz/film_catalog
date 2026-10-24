import os
import secrets
from flask import Flask, render_template, request, url_for, redirect, flash

from sql_queries.actor import get_actors, del_actor, insert_actor, get_actor_by_id, edit_actor
from sql_queries.category import get_categories, del_category, insert_category, get_category_by_id, edit_category
from sql_queries.film import parse_film_form, get_films, del_film, insert_film, get_film_by_id, edit_film
from sql_queries.language import get_languages, del_language, insert_language, get_language_by_id, edit_language
from sql_queries.known_queries import process_query

FILMS_PER_PAGE = 25

# Renders the film list for the given films, filtered by ?q= and split into pages (?page=)
def render_films_index(films_list):
	search = request.args.get('q', '').strip()
	if search:
		needle = search.lower()
		films_list = [f for f in films_list if needle in f[1].lower() or needle in (f[2] or '').lower()]
	total = len(films_list)
	pages = max(1, -(-total // FILMS_PER_PAGE))
	try:
		page = int(request.args.get('page', 1))
	except ValueError:
		page = 1
	page = min(max(page, 1), pages)
	start = (page - 1) * FILMS_PER_PAGE
	language_names = {l[0]: l[1] for l in get_languages()}
	return(render_template('/films/index.html', heading="Films", films=films_list[start:start + FILMS_PER_PAGE], page=page, pages=pages, total=total, search=search, language_names=language_names, show_film_link=url_for("show_film"), update_film_link=url_for("update_film"), delete_film_link=url_for("delete_film"), create_film_link=url_for("create_film")))


app = Flask(__name__)
# Set FLASK_SECRET_KEY to keep flash messages/sessions valid across restarts; otherwise a random key is used
app.secret_key = os.environ.get("FLASK_SECRET_KEY") or secrets.token_hex(32)

@app.route('/', methods=['GET', 'POST'])
def index():
	# Uncomment categories, films and languages (depending on your case) once you implement them
	return(render_template('index.html', heading="Index page", submit_query_link=url_for("free_txt_queries"), index_actor_link=url_for("actors_index"), index_category_link=url_for("categories_index"), index_film_link=url_for("films_index"), index_language_link=url_for("languages_index"),))

# =============================================================================================
# ACTORS
# =============================================================================================

# ACTORS INDEX
@app.route('/actors/index', methods=['GET', 'POST'])
def actors_index():
	actors_list = get_actors() # Example output [(38, "TOM", "MCKELLEN", "2024-12-19 16:39:39"), (42, "TOM", "MIRANDA", "2024-12-19 16:39:39")]
	return(render_template('/actors/index.html', heading="Listing actors", actors=actors_list, show_actor_link=url_for("show_actor"), update_actor_link=url_for("update_actor"), delete_actor_link=url_for("delete_actor"), create_actor_link=url_for("create_actor")))

# ACTORS DELETE
@app.route('/actors/delete', methods=['POST'])
def delete_actor():
	try:
		del_actor()
		flash("Actor deleted.", "success")
		return(redirect(url_for("actors_index")))
	except Exception as e:
		flash(f"Error deleting actor: {str(e)}")
		return(redirect(url_for("actors_index")))	

# ACTORS CREATE
@app.route('/actors/create', methods=['GET', 'POST'])
def create_actor():
	return(render_template("/actors/create.html", heading="Create a new Actor", index_actor_link=url_for("actors_index"), save_actor_link=url_for("save_actor")))

# ACTORS CREATE SAVE
@app.route('/actors/save', methods=['POST'])
def save_actor():
	all_ok = True
	if len(request.form.get('first_name', '').strip()) == 0:
		all_ok = False
		flash("Sorry the actor's first name cannot be empty. Try again.")
	if all_ok:
		try:
			actors_list = insert_actor()
			flash("Actor created.", "success")
		except Exception as e:
			flash(f"Error saving actor: {str(e)}")
			return(redirect(url_for("create_actor")))
		return(render_template('/actors/index.html', heading="Listing actors", actors=actors_list, show_actor_link=url_for("show_actor"), update_actor_link=url_for("update_actor"), delete_actor_link=url_for("delete_actor"), create_actor_link=url_for("create_actor")))
	else:
		return(redirect(url_for("create_actor")))

# ACTORS UPDATE
@app.route('/actors/update', methods=['POST'])
def update_actor():
	actor_info = get_actor_by_id()
	if not actor_info:
		flash("Actor not found. It may have been deleted.")
		return(redirect(url_for("actors_index")))
	return(render_template("/actors/update.html", heading="Editing actor", actor=actor_info, show_actor_link=url_for("show_actor"), index_actor_link=url_for("actors_index"), update_actor_save_link=url_for("save_actor_changes")))

# ACTORS UPDATE SAVE
@app.route('/actors/update_save', methods=['POST'])
def save_actor_changes():
	if len(request.form.get('first_name', '').strip()) == 0:
		flash("Sorry the actor's first name cannot be empty. Try again.")
		return(update_actor())
	try:
		actors_list = edit_actor()
		flash("Actor updated.", "success")
	except Exception as e:
		flash(f"Error updating actor: {str(e)}")
		return(update_actor())
	return(render_template('/actors/index.html', heading="Listing actors", actors=actors_list, show_actor_link=url_for("show_actor"), update_actor_link=url_for("update_actor"), delete_actor_link=url_for("delete_actor"), create_actor_link=url_for("create_actor")))

# ACTORS SHOW
@app.route('/actors/show', methods=['POST'])
def show_actor():
	actor_info = get_actor_by_id() # [(38, "TOM", "MCKELLEN", "2024-12-19 16:39:39")]
	if not actor_info:
		flash("Actor not found. It may have been deleted.")
		return(redirect(url_for("actors_index")))
	return(render_template('/actors/show.html', actor=actor_info, index_actor_link=url_for("actors_index"), update_actor_link=url_for("update_actor")))

# =============================================================================================
# CATEGORIES
# =============================================================================================

# CATEGORIES INDEX
@app.route('/categories/index', methods=['GET', 'POST'])
def categories_index():
	categories_list = get_categories() # Example output [(1, "Action", "2006-02-15 04:46:27"), (2, "Animation", "2006-02-15 04:46:27")]
	return(render_template('/categories/index.html', heading="Listing categories", categories=categories_list, show_category_link=url_for("show_category"), update_category_link=url_for("update_category"), delete_category_link=url_for("delete_category"), create_category_link=url_for("create_category")))

# CATEGORIES DELETE
@app.route('/categories/delete', methods=['POST'])
def delete_category():
	try:
		del_category()
		flash("Category deleted.", "success")
		return(redirect(url_for("categories_index")))
	except Exception as e:
		flash(f"Error deleting category: {str(e)}")
		return(redirect(url_for("categories_index")))	

# CATEGORIES CREATE
@app.route('/categories/create', methods=['GET', 'POST'])
def create_category():
	return(render_template("/categories/create.html", heading="Create a new Category", index_category_link=url_for("categories_index"), save_category_link=url_for("save_category")))

# CATEGORIES CREATE SAVE
@app.route('/categories/save', methods=['POST'])
def save_category():
	all_ok = True
	if len(request.form.get('name', '').strip()) == 0:
		all_ok = False
		flash("Sorry the category name cannot be empty. Try again.")
	if all_ok:
		try:
			categories_list = insert_category()
			flash("Category created.", "success")
		except Exception as e:
			flash(f"Error saving category: {str(e)}")
			return(redirect(url_for("create_category")))
		return(render_template('/categories/index.html', heading="Listing categories", categories=categories_list, show_category_link=url_for("show_category"), update_category_link=url_for("update_category"), delete_category_link=url_for("delete_category"), create_category_link=url_for("create_category")))
	else:
		return(redirect(url_for("create_category")))

# CATEGORIES UPDATE
@app.route('/categories/update', methods=['POST'])
def update_category():
	category_info = get_category_by_id()
	if not category_info:
		flash("Category not found. It may have been deleted.")
		return(redirect(url_for("categories_index")))
	return(render_template("/categories/update.html", heading="Editing category", category=category_info, show_category_link=url_for("show_category"), index_category_link=url_for("categories_index"), update_category_save_link=url_for("save_category_changes")))

# CATEGORIES UPDATE SAVE
@app.route('/categories/update_save', methods=['POST'])
def save_category_changes():
	all_ok = True
	if len(request.form.get('name', '').strip()) == 0:
		all_ok = False
		flash("Sorry the category name cannot be empty. Try again.")
	if all_ok:
		try:
			categories_list = edit_category()
			flash("Category updated.", "success")
		except Exception as e:
			flash(f"Error updating category: {str(e)}")
			return(update_category())
		return(render_template('/categories/index.html', heading="Listing categories", categories=categories_list, show_category_link=url_for("show_category"), update_category_link=url_for("update_category"), delete_category_link=url_for("delete_category"), create_category_link=url_for("create_category")))
	else:
		return(update_category())

# CATEGORIES SHOW
@app.route('/categories/show', methods=['POST'])
def show_category():
	category_info = get_category_by_id()
	if not category_info:
		flash("Category not found. It may have been deleted.")
		return(redirect(url_for("categories_index")))
	return(render_template('/categories/show.html', category=category_info, index_category_link=url_for("categories_index"), update_category_link=url_for("update_category")))

# =============================================================================================
# FILMS
# =============================================================================================

# FILMS INDEX
@app.route('/films/index', methods=['GET', 'POST'])
def films_index():
	films_list = get_films()
	return(render_films_index(films_list))

# FILMS DELETE
@app.route('/films/delete', methods=['POST'])
def delete_film():
	try:
		del_film()
		flash("Film deleted.", "success")
		return(redirect(url_for("films_index")))
	except Exception as e:
		flash(f"Error deleting film: {str(e)}")
		return(redirect(url_for("films_index")))	

# FILMS CREATE
@app.route('/films/create', methods=['GET', 'POST'])
def create_film():
	return(render_template("/films/create.html", heading="Create a new Film", languages=get_languages(), index_film_link=url_for("films_index"), save_film_link=url_for("save_film")))

# FILMS CREATE SAVE
@app.route('/films/save', methods=['POST'])
def save_film():
	_, errors = parse_film_form()
	for error in errors:
		flash(error)
	all_ok = len(errors) == 0
	
	if all_ok:
		try:
			films_list = insert_film()
			flash("Film created.", "success")
			return(render_films_index(films_list))
		except Exception as e:
			flash(f"Error saving film: {str(e)}")
			return(redirect(url_for("create_film")))
	else:
		return(redirect(url_for("create_film")))

# FILMS UPDATE 
@app.route('/films/update', methods=['POST'])
def update_film():
	film_info = get_film_by_id()
	if not film_info:
		flash("Film not found. It may have been deleted.")
		return(redirect(url_for("films_index")))
	return(render_template("/films/update.html", heading="Editing film", film=film_info, languages=get_languages(), show_film_link=url_for("show_film"), index_film_link=url_for("films_index"), update_film_save_link=url_for("save_film_changes")))

# FILMS UPDATE SAVE
@app.route('/films/update_save', methods=['POST'])
def save_film_changes():
	_, errors = parse_film_form()
	for error in errors:
		flash(error)
	all_ok = len(errors) == 0
	
	if all_ok:
		try:
			films_list = edit_film()
			flash("Film updated.", "success")
			return(render_films_index(films_list))
		except Exception as e:
			flash(f"Error updating film: {str(e)}")
			return(update_film())
	else:
		return(update_film())

# FILMS SHOW
@app.route('/films/show', methods=['POST'])
def show_film():
	film_info = get_film_by_id()
	if not film_info:
		flash("Film not found. It may have been deleted.")
		return(redirect(url_for("films_index")))
	return(render_template('/films/show.html', film=film_info, languages=get_languages(), index_film_link=url_for("films_index"), update_film_link=url_for("update_film")))



# =============================================================================================
# LANGUAGES
# =============================================================================================

# LANGUAGES INDEX
@app.route('/languages/index', methods=['GET', 'POST'])
def languages_index():
	languages_list = get_languages()
	return(render_template('/languages/index.html', heading="Listing languages", languages=languages_list, show_language_link=url_for("show_language"), update_language_link=url_for("update_language"), delete_language_link=url_for("delete_language"), create_language_link=url_for("create_language")))

# LANGUAGES DELETE
@app.route('/languages/delete', methods=['POST'])
def delete_language():
	try:
		del_language()
		flash("Language deleted.", "success")
		return(redirect(url_for("languages_index")))
	except ValueError as e:
		flash(str(e))
		return(redirect(url_for("languages_index")))
	except Exception as e:
		flash(f"Error deleting language: {str(e)}")
		return(redirect(url_for("languages_index")))	

# LANGUAGES CREATE
@app.route('/languages/create', methods=['GET', 'POST'])
def create_language():
	return(render_template("/languages/create.html", heading="Create a new Language", index_language_link=url_for("languages_index"), save_language_link=url_for("save_language")))

# LANGUAGES CREATE SAVE
@app.route('/languages/save', methods=['POST'])
def save_language():
	all_ok = True
	if len(request.form.get('name', '').strip()) == 0:
		all_ok = False
		flash("Sorry the language name cannot be empty. Try again.")
	if all_ok:
		try:
			languages_list = insert_language()
			flash("Language created.", "success")
		except Exception as e:
			flash(f"Error saving language: {str(e)}")
			return(redirect(url_for("create_language")))
		return(render_template('/languages/index.html', heading="Listing languages", languages=languages_list, show_language_link=url_for("show_language"), update_language_link=url_for("update_language"), delete_language_link=url_for("delete_language"), create_language_link=url_for("create_language")))
	else:
		return(redirect(url_for("create_language")))

# LANGUAGES UPDATE
@app.route('/languages/update', methods=['POST'])
def update_language():
	language_info = get_language_by_id()
	if not language_info:
		flash("Language not found. It may have been deleted.")
		return(redirect(url_for("languages_index")))
	return(render_template("/languages/update.html", heading="Editing language", language=language_info, show_language_link=url_for("show_language"), index_language_link=url_for("languages_index"), update_language_save_link=url_for("save_language_changes")))

# LANGUAGES UPDATE SAVE
@app.route('/languages/update_save', methods=['POST'])
def save_language_changes():
	all_ok = True
	if len(request.form.get('name', '').strip()) == 0:
		all_ok = False
		flash("Sorry the language name cannot be empty. Try again.")
	if all_ok:
		try:
			languages_list = edit_language()
			flash("Language updated.", "success")
		except Exception as e:
			flash(f"Error updating language: {str(e)}")
			return(update_language())
		return(render_template('/languages/index.html', heading="Listing languages", languages=languages_list, show_language_link=url_for("show_language"), update_language_link=url_for("update_language"), delete_language_link=url_for("delete_language"), create_language_link=url_for("create_language")))
	else:
		return(update_language())

# LANGUAGES SHOW
@app.route('/languages/show', methods=['POST'])
def show_language():
	language_info = get_language_by_id()
	if not language_info:
		flash("Language not found. It may have been deleted.")
		return(redirect(url_for("languages_index")))
	return(render_template('/languages/show.html', language=language_info, index_language_link=url_for("languages_index"), update_language_link=url_for("update_language")))

# =============================================================================================
# FREE TEXT QUERIES INDEX
# =============================================================================================

# FREE TEXT QUERIES INDEX
@app.route('/queries', methods=['GET', 'POST'])
def free_txt_queries():
	query = request.form.get('query', '').strip()
	if len(query) == 0:
		flash("Sorry the query cannot be empty. Try again.")
		return(redirect(url_for("index")))
	try:
		results, sql, truncated = process_query(query)
	except Exception as e:
		flash(str(e))
		return(redirect(url_for("index")))

	if len(results) > 0:
		field_names = list(dict(results[0]).keys())
	else:
		field_names = ["Empty result set."]

	return(render_template('/free_text_queries/show_dynamic_table.html', results=results, sql=sql, truncated=truncated, field_names=field_names, index_link=url_for("index")))
