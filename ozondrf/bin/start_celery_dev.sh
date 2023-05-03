#!/bin/bash
exec celery -A core worker -l INFO -f /mnt/d/projects/taxiber/core/logs/celery.tmp.log -B --scheduler django_celery_beat.schedulers:DatabaseScheduler
