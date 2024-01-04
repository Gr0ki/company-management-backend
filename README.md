## **Setup instruction**

### 1. Prepare your environment:

- Create a `.env` file based on example in `.env.sample` file.

#### [Swtch DEV\\PROD environment]:

- Set up `DEV` variable to `True` for dev environment (make avaliable tests and other dev dependencies in your container).
- Also you would want to uncoment "`tests`" volume for the `app's container` in order to update enable update container on local code change in tests folder.

### 2. Install Docker.

### 3. Build Docker images with docker-compose comand:

- Build and up docker containers:

        docker compose --env-file .env up --build

### Run commands inside Docker image:

#### Migrations (with alembic):

- Create a new revision:

        docker compose run --rm backend sh -c "/venv/bin/alembic -c ./app/migrations/alembic.ini revision --autogenerate -m '<Your message>'"

- Apply migrations (*this command runs each time you run your containers*):

        docker compose run --rm backend sh -c "/venv/bin/alembic -c ./app/migrations/alembic.ini upgrade head"

#### Testing:

[When `DEV` = `True`]: Run tests inside app container:

        docker compose run --rm backend sh -c "/venv/bin/pytest"
