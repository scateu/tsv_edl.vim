package main

// Usage:
// go run /Users/k/.vim/pack/plugins/start/tsv_edl.vim/html/rcut-server.go . 80  /Users/k/.vim/pack/plugins/start/tsv_edl.vim/utils/tsv2roughcut.py

import (
	"bufio"
	"bytes"
	"fmt"
	"io"
	"net/http"
	"os"
	"os/exec"
)

// Helper function to read from a pipe and print in realtime
func pipeReader(pipe io.Reader, prefix string) {
	scanner := bufio.NewScanner(pipe)
	for scanner.Scan() {
		fmt.Printf("%s: %s\n", prefix, scanner.Text())
	}
}

func handlePost(pythonScript string) http.HandlerFunc {
	return func(w http.ResponseWriter, r *http.Request) {
		if r.Method != http.MethodPost {
			http.Error(w, "Method not allowed", http.StatusMethodNotAllowed)
			return
		}

		// Read and print the request body
		bodyBytes, err := io.ReadAll(r.Body)
		if err != nil {
			http.Error(w, "Error reading request body", http.StatusInternalServerError)
			fmt.Printf("Error reading request body: %v\n", err)
			return
		}

		// Print the request body for debugging
		fmt.Printf("Received POST body:\n%s\n", string(bodyBytes))

		// Create a new reader with the body content for further processing
		r.Body = io.NopCloser(bytes.NewBuffer(bodyBytes))

		// Create command to run Python script
		cmd := exec.Command("python3", pythonScript)

		// Get stdin pipe
		stdin, err := cmd.StdinPipe()
		if err != nil {
			http.Error(w, "Internal server error", http.StatusInternalServerError)
			fmt.Printf("Error getting stdin pipe: %v\n", err)
			return
		}

		// Set up pipes for both stdout and stderr
		stdout, err := cmd.StdoutPipe()
		if err != nil {
			http.Error(w, "Internal server error", http.StatusInternalServerError)
			fmt.Printf("Error getting stdout pipe: %v\n", err)
			return
		}

		stderr, err := cmd.StderrPipe()
		if err != nil {
			http.Error(w, "Internal server error", http.StatusInternalServerError)
			fmt.Printf("Error getting stderr pipe: %v\n", err)
			return
		}

		// Create a buffer to capture the output for the HTTP response
		var outputBuffer bytes.Buffer

		// Start goroutines to handle output in realtime while also capturing stdout
		go pipeReader(stderr, "STDERR")
		go io.Copy(io.MultiWriter(&outputBuffer, WriteFunc(func(p []byte) (int, error) {
			fmt.Printf("STDOUT: %s", string(p))
			return len(p), nil
		})), stdout)

		// Start the command
		if err := cmd.Start(); err != nil {
			http.Error(w, "Internal server error", http.StatusInternalServerError)
			fmt.Printf("Error starting command: %v\n", err)
			return
		}

		// Copy POST body to script's stdin
		_, err = io.Copy(stdin, r.Body)
		if err != nil {
			http.Error(w, "Internal server error", http.StatusInternalServerError)
			fmt.Printf("Error copying to stdin: %v\n", err)
			return
		}
		stdin.Close()

		// Wait for the command to finish
		if err := cmd.Wait(); err != nil {
			fmt.Printf("Error waiting for command: %v\n", err)
			return
		}

		// Write the output to the response
		w.Header().Set("Access-Control-Allow-Origin", "*")
		w.Header().Set("Content-Type", "text/plain")
		w.Write(outputBuffer.Bytes())
	}
}

// WriteFunc implements io.Writer for a function
type WriteFunc func([]byte) (int, error)

func (f WriteFunc) Write(p []byte) (int, error) {
	return f(p)
}

func main() {
	dir := "."
	if len(os.Args) > 1 {
		dir = os.Args[1]
	}

	port := "80"
	if len(os.Args) > 2 {
		port = os.Args[2]
	}

	pythonScript := "script.py"
	if len(os.Args) > 3 {
		pythonScript = os.Args[3]
	}

	changeHeaderThenServe := func(h http.Handler) http.HandlerFunc {
		return func(w http.ResponseWriter, r *http.Request) {
			w.Header().Set("Access-Control-Allow-Origin", "*")
			h.ServeHTTP(w, r)
		}
	}

	fileServer := http.FileServer(http.Dir(dir))

	// Handle static files
	http.Handle("/", changeHeaderThenServe(fileServer))

	// Handle POST requests to /process endpoint
	http.HandleFunc("/tsv2roughcut", handlePost(pythonScript))

	fmt.Printf("Starting server on port %s, serving directory: %s\n", port, dir)
	fmt.Printf("POST requests to /tsv2roughcut will be handled by Python script: %s\n", pythonScript)

	err := http.ListenAndServe(":"+port, nil)
	if err != nil {
		fmt.Printf("Error starting server: %s\n", err)
		os.Exit(1)
	}
}
