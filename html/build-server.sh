#!/bin/bash

# App name
APP="rcutserver"

# Build for Mac M1
GOOS=darwin GOARCH=arm64 go build -o ${APP}-mac-arm64 ${APP}.go

# Build for Mac Intel
GOOS=darwin GOARCH=amd64 go build -o ${APP}-mac-amd64 ${APP}.go

# Build for Windows
GOOS=windows GOARCH=amd64 go build -o ${APP}-windows-amd64.exe ${APP}.go

# Optional: create zip files
zip ${APP}-mac-arm64.zip ${APP}-mac-arm64
zip ${APP}-mac-amd64.zip ${APP}-mac-amd64
zip ${APP}-windows-amd64.zip ${APP}-windows-amd64.exe
