// Usage: cd ~/www; go run /path/to/go-http-server.go
// Courtesy of Kuma

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

	fileServer := http.FileServer(http.Dir(dir))

	http.Handle("/", fileServer)

	fmt.Printf("Starting server on port %s, serving directory: %s\n", port, dir)
	err := http.ListenAndServe(":"+port, nil)
	if err != nil {
		fmt.Printf("Error starting server: %s\n", err)
		os.Exit(1)
	}
}
