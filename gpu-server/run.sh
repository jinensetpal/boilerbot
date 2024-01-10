#!/bin/bash

dvc pull -r http

uvicorn main:app --host 0.0.0.0 --port 8000
