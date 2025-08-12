#!/bin/bash

# Start PlantUML server using Docker
echo "Starting PlantUML server with Docker on port 8080..."
docker run -d -p 8080:8080 --name plantuml-server plantuml/plantuml-server

echo "PlantUML server is starting..."
echo "Server will be available at: http://localhost:8080"
echo ""
echo "To stop the server, run: docker stop plantuml-server"
echo "To remove the container, run: docker rm plantuml-server"