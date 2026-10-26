# Film Catalog

A small Flask web app for browsing and editing the **Sakila** sample database (a DVD rental store) stored in SQLite, with a query box that answers questions in plain English using a **local AI model** (Ollama).

## Project Background

This project was originally developed as part of my coursework at IEK AKMI, where I studied software development.

Since then, I have continued improving and expanding the application beyond its original academic scope, focusing on backend functionality, database management, user interface improvements, and optional local AI integration.

<img width="1737" height="722" alt="Screenshot 2026-10-26 203023" src="https://github.com/user-attachments/assets/a97a99c9-db3d-495c-8895-bc94e3b92ea7" />

## Features

- **Dark Bootstrap UI** with a navigation bar, searchable and paginated film list, dropdowns and checkboxes in the film form, confirmation before deleting, and success/error messages.
- **CRUD pages** for actors, categories, films and languages: list, show, create, edit and delete.
- **Validation** with clear error messages (empty names, invalid numbers, invalid ratings, deleting a language that films still use, and so on).
- **Question box** on the home page:
  - Four built-in questions run instantly, for example `Actors with first name 'TOM'`, `Actor with most films`, `Count films per category` and `What is the average running time of all the films`.
  - Any other question is turned into SQL by a local LLM through [Ollama](https://ollama.com). The generated SQL is shown above the results.
- **Safe AI queries:** generated SQL runs on a read-only database connection, only `SELECT` is allowed, a query stops after 5 seconds, and results are capped at 200 rows.
- Needs an internet connection the first time a page loads, because Bootstrap is loaded from a CDN.
- Works without Ollama too. The CRUD pages and the four built-in questions don't need it.

## Requirements

- Windows 10 or 11
- [Python](https://www.python.org/downloads/) 3.10 or newer (tick **Add python.exe to PATH** in the installer)
- [Git](https://git-scm.com/download/win) (to clone the project)
- *Optional, for AI questions:* [Ollama](https://ollama.com/download) and about 5 GB of free disk space for the model. 8 GB of RAM or more is recommended.

## Setup

Open **PowerShell** and run:

```powershell
# 1. Get the project
git clone <your-repository-url> film_catalog
cd film_catalog

# 2. Create a virtual environment
python -m venv .venv

# 3. Activate it
.\.venv\Scripts\Activate.ps1

# 4. Install the dependencies
pip install -r requirements.txt
```

If step 3 fails with *"running scripts is disabled on this system"*, run this once and try again:

```powershell
Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
```

The database is already included at `db/mysakila.db`, so there is nothing else to set up.

## Run the app

With the virtual environment activated, from the project folder:

```powershell
flask --app main run
```

Then open <http://127.0.0.1:5000> in your browser. Press `Ctrl+C` in the terminal to stop it.

> The app must be started from the project folder, because it imports its modules (`sql_queries`, `myutil`, `aichat`) from there.

## Set up AI questions (optional)

1. Install Ollama from <https://ollama.com/download> and run the installer. It starts automatically in the background.
2. Download the model (about 4.7 GB, one time only):

   ```powershell
   ollama pull qwen2.5-coder:7b
   ```

3. Check that it works:

   ```powershell
   ollama run qwen2.5-coder:7b
   ```

   Type `hi`, wait for a reply, then type `/bye`.

4. Start (or restart) the app and ask something on the home page, for example:
   - `How many films are there?`
   - `List the 5 longest films with their length`
   - `Which actors appeared in the film ACADEMY DINOSAUR?`

### Use a different model

The default model is `qwen2.5-coder:7b`. Smaller computers can use a lighter model:

```powershell
ollama pull llama3.2
$env:OLLAMA_MODEL = "llama3.2"
flask --app main run
```

`$env:OLLAMA_MODEL` only applies to the current PowerShell window.

### Things to know about AI answers

- The first question after Ollama starts is slower while the model loads. After that, answers usually take a few seconds.
- A small local model can write SQL that runs but answers the wrong question. The SQL is shown with every result so you can check it.
- If Ollama isn't running or the model is missing, the app shows a message saying so and the rest of the app keeps working.

## Configuration

| Setting | Default | Purpose |
|---|---|---|
| `FLASK_SECRET_KEY` | random at each start | Signs the session cookie used for error messages. Set it to keep it stable across restarts. |
| `OLLAMA_MODEL` | `qwen2.5-coder:7b` | Which Ollama model writes the SQL. |

PowerShell example:

```powershell
$env:FLASK_SECRET_KEY = "put-a-long-random-string-here"
```

## Project structure

```
film_catalog/
├── main.py                  # Flask app: all routes
├── requirements.txt
├── db/
│   └── mysakila.db          # SQLite Sakila database
├── sql_queries/             # SQL for each entity + built-in questions
│   ├── actor.py
│   ├── category.py
│   ├── film.py              # includes film form validation
│   ├── language.py
│   └── known_queries.py
├── aichat/
│   ├── myollama.py          # natural-language -> SQL with Ollama (read-only, validated)
│   └── myollama_example.py  # standalone demo script
├── myutil/
│   └── util.py              # DB connection and timestamp helpers
└── templates/               # Jinja2 HTML templates (base.html = layout, _macros.html = shared parts)
```

## Troubleshooting

| Problem | Fix |
|---|---|
| `python` is not recognized | Reinstall Python and tick **Add python.exe to PATH**, or use `py` instead of `python`. |
| `flask` is not recognized | Activate the virtual environment first (setup step 3). |
| `ModuleNotFoundError: No module named 'sql_queries'` | Run the command from the project folder. |
| `ollama` is not recognized | Close and reopen PowerShell after installing Ollama. |
| "Could not reach Ollama" in the app | Start Ollama from the Start menu (or run `ollama serve`) and try again. |
| "Ollama error: model ... not found" | Run `ollama pull qwen2.5-coder:7b`, or set `OLLAMA_MODEL` to a model you have (`ollama list` shows them). |
| Port 5000 is already in use | Run with another port: `flask --app main run --port 5050`. |
| Deleting a film, actor or category shows an error | It is still referenced by other records (for example rentals), and the database protects them. |

## Known limitations

- Only actors, categories, films and languages have pages. The other Sakila tables (customers, rentals, payments, and so on) can only be reached through the question box.
- The `categories_translated` templates exist but are not connected yet.
- Show, edit and delete use POST forms, so those pages can't be bookmarked.
- There is no login or CSRF protection, so this is meant for local use and not for running on the public internet.

## Credits

The database is the [Sakila sample database](https://dev.mysql.com/doc/sakila/en/), originally from MySQL, converted to SQLite.
