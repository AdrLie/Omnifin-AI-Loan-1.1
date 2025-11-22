#!/usr/bin/env sh
set -e

# Apply database migrations (default DB)
echo "Applying database migrations (default)"
python manage.py migrate --noinput

# Try to migrate knowledge DB if configured
KB_CFG=$(python - <<'PY'
import sys
from decouple import config
kb_host = config('KNOWLEDGE_DB_HOST', default='')
kb_name = config('KNOWLEDGE_DB_NAME', default='')
print('1' if (kb_host or kb_name) else '0')
PY
)
if [ "$KB_CFG" = "1" ]; then
  echo "Applying database migrations (knowledge)"
  python manage.py migrate --database=knowledge --noinput || echo "Knowledge DB migrate skipped"
fi

# Collect static files
echo "Collecting static files"
python manage.py collectstatic --noinput

# Start ASGI server via Uvicorn
exec uvicorn omnifin.asgi:application --host 0.0.0.0 --port 8000
