#!/bin/bash

gunicorn -b 0.0.0.0:8000 --access-logfile - --error-logfile - riverstart_test.wsgi
