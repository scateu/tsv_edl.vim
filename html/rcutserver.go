package main

import (
	"bufio"
	"bytes"
	"flag"
	"fmt"
	"io"
	"net/http"
	"os"
	"os/exec"
)

type Config struct {
	dir          string
	host         string
	port         string
	pythonScript string
}

func parseArgs() Config {
	var config Config

	// Define flags
	flag.StringVar(&config.dir, "d", ".", "Directory to serve")
	flag.StringVar(&config.host, "l", "0.0.0.0", "Host to listen on")
	flag.StringVar(&config.port, "p", "80", "Port to listen on")
	flag.StringVar(&config.pythonScript, "s", "/usr/local/bin/tsv2roughcut", "Python script to handle POST requests")

	// Custom usage message
	flag.Usage = func() {
		fmt.Fprintf(os.Stderr, "Usage: %s [options]\n\n", os.Args[0])
		fmt.Fprintf(os.Stderr, "rcutserver: A simple HTTP server that can serve static files and handle POST requests with Python scripts\n\n")
		fmt.Fprintf(os.Stderr, "Options:\n")
		flag.PrintDefaults()
		fmt.Fprintf(os.Stderr, "\nExamples:\n")
		fmt.Fprintf(os.Stderr, "  Serve current directory on default host and port:\n")
		fmt.Fprintf(os.Stderr, "    %s\n", os.Args[0])
		fmt.Fprintf(os.Stderr, "  Serve specific directory on custom port:\n")
		fmt.Fprintf(os.Stderr, "    %s -d /path/to/dir -p 8080\n", os.Args[0])
		fmt.Fprintf(os.Stderr, "  Handle POST requests with Python script:\n")
		fmt.Fprintf(os.Stderr, "    %s -s /path/to/script.py\n", os.Args[0])
	}

	// Parse flags
	flag.Parse()

	return config
}

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
		cmd := exec.Command("python3", pythonScript, "roughcut")

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
	config := parseArgs()

	changeHeaderThenServe := func(h http.Handler) http.HandlerFunc {
		return func(w http.ResponseWriter, r *http.Request) {
			w.Header().Set("Access-Control-Allow-Origin", "*")
			h.ServeHTTP(w, r)
		}
	}

	fileServer := http.FileServer(http.Dir(config.dir))

	// Handle static files
	http.Handle("/", changeHeaderThenServe(fileServer))

	// Only set up POST handling if a Python script was specified
	if config.pythonScript != "" {
		http.HandleFunc("/tsv2roughcut", handlePost(config.pythonScript))
		fmt.Printf("POST requests to /tsv2roughcut will be handled by Python script: %s\n", config.pythonScript)
	}

	address := fmt.Sprintf("%s:%s", config.host, config.port)
	fmt.Printf("Starting server at http://%s, serving directory: %s\n", address, config.dir)

	err := http.ListenAndServe(address, nil)
	if err != nil {
		fmt.Printf("Error starting server: %s\n", err)
		os.Exit(1)
	}
}
