#!/bin/bash

# Variables
UPLOAD_BACKUP_FILE_PATH="my_backup.sql"
CONTAINER_NAME="keycloak_db_1"
DB_NAME="keycloak"
DB_USER="root"
CONTAINER="keycloak_db_1"
BACKUP_FILE_COPY_PATH="/my_backup.sql"
RESTART_CONTAINER="keycloak_keycloak_1"
DB_SERVICE="db"

# Terminate active sessions and drop the Keycloak database
echo "Terminating active sessions and dropping the existing '$DB_NAME' database..."
docker-compose exec -T $DB_SERVICE psql -U $DB_USER -d postgres -c "SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE datname = '$DB_NAME';"
docker-compose exec -T $DB_SERVICE psql -U $DB_USER -d postgres -c "DROP DATABASE IF EXISTS $DB_NAME;"

# Recreate the Keycloak database
echo "Creating a fresh '$DB_NAME' database..."
docker-compose exec -T $DB_SERVICE psql -U $DB_USER -d postgres -c "CREATE DATABASE $DB_NAME;"

# Copy the backup file to the container
echo "Copying backup file to the container..."
docker cp $UPLOAD_BACKUP_FILE_PATH $CONTAINER_NAME:$BACKUP_FILE_COPY_PATH

# Restore the database from the backup file
echo "Restoring the '$DB_NAME' database from the backup file..."
docker exec -it $CONTAINER_NAME psql -U $DB_USER -d $DB_NAME -f $BACKUP_FILE_COPY_PATH

docker restart $RESTART_CONTAINER
echo "Database restoration completed."
