// Usage: $ cd ~/www; go run /path/to/go-http-server.go
// Usage: $ /path/to/go-http-server ~/www 80
// Courtesy of Kuma
/* How to BUILD:
#!/bin/bash

# App name
APP="go-http-server"

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
*/

package main

import (
	"fmt"
	"net/http"
	"os"
)

func main() {
	dir := "."
	if len(os.Args) > 1 {
		dir = os.Args[1]
	}

	port := "80"
	if len(os.Args) > 2 {
		port = os.Args[2]
	}

	changeHeaderThenServe := func(h http.Handler) http.HandlerFunc {
		return func(w http.ResponseWriter, r *http.Request) {
			// Set some header.
			w.Header().Set("Access-Control-Allow-Origin", "*")
			// Serve with the actual handler.
			h.ServeHTTP(w, r)
		}
	}

	fileServer := http.FileServer(http.Dir(dir))

	http.Handle("/", changeHeaderThenServe(fileServer))

	fmt.Printf("Starting server on port %s, serving directory: %s\n", port, dir)
	err := http.ListenAndServe(":"+port, nil)
	if err != nil {
		fmt.Printf("Error starting server: %s\n", err)
		os.Exit(1)
	}
}
