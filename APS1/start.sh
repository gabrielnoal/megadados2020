export PYTHONPATH=/usr/bin/python3;

cd \tasklist\;

uvicorn tasklist.main:app --reload
