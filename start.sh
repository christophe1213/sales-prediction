#!/bin/sh
set -e

git init -q

dvc remote modify origin --local auth basic
dvc remote modify origin --local user "$DAGSHUB_USER"
dvc remote modify origin --local password "$DAGSHUB_TOKEN"
dvc pull data/stores.csv data/holidays_events.csv processed/meta.json models/ 

exec uvicorn app:app --host 0.0.0.0 --port 7860