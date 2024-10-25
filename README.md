## **Description**

This is a mock trading engine built with Multithreading, FastAPI, Pydantic models for validation, SQLAlchemy for ORM and websockets as the transporter for RESTful packages.

Speed is something I tried to maintain as the main focus hence the multithreading. This isn’t an application for thousands of people but a confident 100 or around that can be supported

This project taught me alot about async as it forced me to understand the core functionality of the architecture. Async works by multitasking within a thread. Within a signle thread it will cycel through each task bit by bit to appear as if it’s running in parallel however this is a facade and was shown to me in beaming lights in my first attempt where I incorporated some while loops. Unknowingly to the fact that this would block the thread removing the async nature. I then decided to build specific functions that could run on their own thread and saw improvements.

I also learnt about resource sharing. When you’re sharing resources across threads you can’t have an immutable data structure like a set for example if you’re constantly reading and writing from separate threads.

## Prerequisites

- Threading
- Async
- FastAPI
- Knowledge of classes

## **Installation**

- After initialising alembic you’re going to need to go to the [env.py](http://env.py) file and import the Base class defined in db_models.py. In the alembic.ini file you need to put your link to the database
    - **For example**: postgres://<username>:<password>@<host>:<port>/<db_name>
- There’s a script in the db_models.py to generate a fake db. You’re also going to need alembic to manage your migrations.

```bash
# Clone repo
git clone https://github.com/JadoreThompson/Trading-Engine.git

# Install requirements
pip install -r requirements.txt

# Init alembic for db management when altering the db models
alembic init alembic

# Test that alembic is running properly
alembic --autogenerate -m "test"

# Start the server
uvicorn run app:app --port <port>
```

- env.py

```bash
# DB
DB_HOST=localhost
DB_PORT=5432
DB_NAME=<db_name>
DB_USER=postgres
DB_PASSWORD=<password>

```

## Extras

In the future I want to introduce Buy Limit and Sell Limit support along with order modification support

## **Contact**

If you're interested in collaborating or have any opportunities, feel free to contact me at [jadorethompson6@gmail.com](mailto:jadorethompson6@gmail.com) or connect with me on [LinkedIn](https://www.linkedin.com/in/jadore-t-49379a295/).
