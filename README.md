# Hangman app

This codebase implements a basic hangman app using the Django framework.

# Setup

To setup the basic website you will need to have the following installed:

- python3
- pip
- sqlite3

Pip is the package manager for Python.  You can install the remaining packages required for this task using pip. You will need to run the following:
To start you should create and activate a virtual environment:

- $ python -m venv env        # use `virtualenv env` for Python2, use `python3 ...` for Python3 on Linux & macOS
- $ source env/bin/activate   # use `env\Scripts\activate` on Windows
- $ pip install -r requirements.txt

You then need to apply the migrations by typing:

 $ python manage.py migrate

# Initialise the database

You need to initialise the database with words using the following command:
 
 $ python manage.py loaddata db_initialisation.json

You can see the words in the database using the following:

 $ sqlite3 db.sqlite3
 sqlite> select * from hangMansApp_word;

# Run the website

You can run the website by typing:

 $ python manage.py runserver

You can now browse to the url http://127.0.0.1:8000/ to view the website.

## Issues

The code has been tested on Firefox but it does not currently work on Google Chrome.
