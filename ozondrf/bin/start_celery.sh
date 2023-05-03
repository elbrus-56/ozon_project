#!/bin/bash
exec celery -A core worker --concurrency=1 -l INFO -f /app/core/logs/celery.log -B --scheduler django_celery_beat.schedulers:DatabaseScheduler

