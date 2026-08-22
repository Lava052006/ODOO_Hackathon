#!/bin/bash
set -e

git config --global --add safe.directory '*'

DB_ROOT_PASSWORD="${DB_ROOT_PASSWORD:-123}"
ADMIN_PASSWORD="${ADMIN_PASSWORD:-admin}"
DB_HOST="postgres"

echo "Waiting for PostgreSQL..."
while ! pg_isready -h "$DB_HOST" -U postgres > /dev/null 2>&1; do
    sleep 2
done
echo "PostgreSQL is ready!"

cd /home/frappe

if [ ! -d "/home/frappe/frappe-bench/sites" ]; then
    echo "Initializing new bench at /home/frappe/frappe-bench..."
    rm -rf /home/frappe/frappe-bench
    bench init --skip-redis-config-generation --frappe-branch develop /home/frappe/frappe-bench
fi

cd /home/frappe/frappe-bench

# Auto-apply PostgreSQL compatibility driver patches
if [ -f "/workspace/docker/patch_postgres.py" ]; then
    /home/frappe/frappe-bench/env/bin/python /workspace/docker/patch_postgres.py || true
fi

# Ensure bind address is 0.0.0.0 and service hosts are configured
bench set-mariadb-host "$DB_HOST"
bench set-redis-cache-host redis://redis:6379
bench set-redis-queue-host redis://redis:6379
bench set-redis-socketio-host redis://redis:6379
bench set-config -g webserver_port 8000
bench set-config -g socketio_port 9000

sed -i '/redis/d' ./Procfile
sed -i '/watch/d' ./Procfile
sed -i 's/bench serve.*/bench serve --host 0.0.0.0 --port 8000/g' ./Procfile

if [ ! -d "/home/frappe/frappe-bench/apps/erpnext" ]; then
    echo "Getting ERPNext..."
    bench get-app erpnext --branch develop
fi

if [ ! -d "/home/frappe/frappe-bench/apps/hrms" ]; then
    echo "Linking local HRMS app into bench apps..."
    ln -s /workspace/code /home/frappe/frappe-bench/apps/hrms
fi

mkdir -p /home/frappe/frappe-bench/sites/assets
ln -sfn /home/frappe/frappe-bench/apps/hrms/hrms/public /home/frappe/frappe-bench/sites/assets/hrms

printf 'frappe\nerpnext\nhrms\n' > sites/apps.txt

echo "Installing HRMS Python package..."
/home/frappe/frappe-bench/env/bin/pip install -e /home/frappe/frappe-bench/apps/hrms

if [ ! -d "/home/frappe/frappe-bench/sites/hrms.localhost" ]; then
    echo "Creating site hrms.localhost..."
    bench new-site hrms.localhost \
        --force \
        --db-type postgres \
        --db-host "$DB_HOST" \
        --db-port 5432 \
        --db-root-password "$DB_ROOT_PASSWORD" \
        --admin-password "$ADMIN_PASSWORD"

    echo "Installing apps to site..."
    bench --site hrms.localhost install-app erpnext
    bench --site hrms.localhost install-app hrms
    bench --site hrms.localhost set-config developer_mode 1
    bench --site hrms.localhost enable-scheduler
    bench --site hrms.localhost clear-cache
    bench use hrms.localhost
fi

bench use hrms.localhost
echo "Starting Frappe backend on 0.0.0.0:8000..."
bench start