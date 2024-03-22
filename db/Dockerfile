FROM mysql:latest

# Set the environment variables
ENV MYSQL_USER=user
ENV MYSQL_PASSWORD=password
# Set the root password for MySQL
ENV MYSQL_ROOT_PASSWORD=password

# Create a new database named "kerdos"
ENV MYSQL_DATABASE=kerdos

# Copy the SQL script to the Docker image
COPY db/db_backup_plateforme_2024-01-10_010001.sql /docker-entrypoint-initdb.d/

# Expose the MySQL port
EXPOSE 3306