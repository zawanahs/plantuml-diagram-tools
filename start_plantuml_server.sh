#!/bin/bash

# Start PlantUML local server
# The server will run on http://localhost:8080/plantuml

echo "Starting PlantUML server on port 8080..."
java -jar plantuml.jar -picoweb:8080