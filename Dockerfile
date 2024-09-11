# Use the official Keycloak image as the base image
FROM quay.io/keycloak/keycloak:25.0.4

# Copy your custom theme into the Keycloak themes directory
COPY themes /opt/keycloak/themes

# Set environment variables (you can adjust these as needed)
ENV KEYCLOAK_ADMIN=admin
ENV KEYCLOAK_ADMIN_PASSWORD=admin

# Expose the Keycloak port
EXPOSE 8080

# # Set the default command to start Keycloak
# CMD ["start-dev"]
