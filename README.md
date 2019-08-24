# guitarlette

Work in progress.

**Requirements**: Python 3.7+

## What?

This an attempt to write my ideal songwriting app for guitar as well as an experiment using a few different libraries that I find interesting.

## Setup

### Backend

Create a virtual environment, install the dependencies, then run the migrations:

```shell
cd backend
python3.7 -m venv venv
. venv/bin/activate
pip install -r requirements.txt
alembic upgrade head
```

Then run the server:

```shell
uvicorn app.asgi:app
```

### Frontend

```shell
cd frontend
npm install
```

Then run the server:

```shell
npm run dev
```
