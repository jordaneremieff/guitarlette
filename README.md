# guitarlette

Work in progress.

**Requirements**: Python 3.7+

## What?

This an attempt to write my ideal songwriting app for guitar as well as an experiment using a few different libraries that I find interesting. It relies heavily on [Starlette](https://github.com/encode/starlette), [Tortoise ORM](https://github.com/tortoise/tortoise-orm), and [pychord](https://github.com/yuma-m/pychord).


## Setup

You can run the project with Docker:


```docker-compose up -d```

OR

```
# Setup the dev environment and install the dependencies
./scripts/setup

# Activate the virtualenv
. venv/bin/activate

# Create the database
python guitarlette/init_db.py
```

## Running

```
uvicorn guitarlette.app:app --debug
```

Then visit `http://localhost:8000/compose` to try creating a song.

## Ideas

- Horizontal and vertical scroll behaviour
- Multi-song viewer
- Chord tone audio and fingering graphics
- Transposition
- Chord dropdowns on each parsed chord in the viewer
- Voice control via microphone of viewer behaviour
- Metronome, etc.
- Tuner
- Generators