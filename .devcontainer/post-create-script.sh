#!/bin/sh

git config --global --add safe.directory /workspaces/NoCapCooking

if [ ! -f .env ]; then
    cp .env.example .env
fi

python manage.py migrate

echo ".env created"