atlas-core

Simple start guide

1. Create and activate a virtual environment.
2. Install dependencies:

	```bash
	pip install -r src/requirements.txt
	```

3. Make sure PostgreSQL is running locally.
4. Create a `.env` file in the project root with these values:

	```env
	DB_ENGINE=django.db.backends.postgresql
	DB_NAME=atlas_db
	DB_USER=atlas_user
	DB_PASSWORD=atlas__secure_pass2026
	DB_HOST=localhost
	DB_PORT=5432
	```

5. Run migrations and start the server:

	```bash
	cd src
	python manage.py migrate
	python manage.py runserver
	```
