# Categories API
Simple REST API with couple endpoints which allow to create and retreive
"Categories" objects and create parent/child/sibling relations between them.

# Setup
Need `virtualenv` to create virtual environment and `python 3.6`. Application
was created on Ubuntu-17.10. It should also work on MacOS, and other
Linux like machines.

* `git clone https://github.com/mikhsol/categories_api.git categories`
* `cd categoires`
* `virtualenv -p python3.6 env_categories`
* `source env_categories/bin/activate`
* `cd categories_api`
* `pip install -r requirements.txt`

# Run application
* Initialise database and admin user:
  * `./manage.py makemigrations`
  * `./manage.py migrate`

* Starting server:
  * `./manage.py runserver [[ip:]<port>]`

# Testing
Run test with pytest test engine:
  * `pytest`