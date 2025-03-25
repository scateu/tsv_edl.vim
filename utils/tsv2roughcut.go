package main

import (
	"bufio"
	"flag"
	"fmt"
	"io/ioutil"
	"math"
	"os"
	"os/exec"
	"path/filepath"
	"runtime"
	"strconv"
	"strings"
)

var (
	videoFormats = []string{"mkv", "mp4", "mov", "mpeg", "ts", "avi", "webm"}
	audioFormats = []string{"wav", "mp3", "m4a", "ogg", "flac"}
	imageFormats = []string{"png", "jpg", "jpeg", "bmp"}

	isPureAudioProject = true
	generateSRT        = true
	debug              = false

	codecV string
)

// OutputQueueItem represents an item in the output queue
type OutputQueueItem struct {
	Filename string
	StartTC  float64
	EndTC    float64
	BRoll    interface{} // Can be "NO_B_ROLL" or a slice [filename, in, out]
}

// BRollItem represents a B-roll item
type BRollItem []interface{} // [filename, in, out]

func eprint(a ...interface{}) {
	fmt.Fprintln(os.Stderr, a...)
}

func eprintNoNewline(a ...interface{}) {
	fmt.Fprint(os.Stderr, a...)
}

func srttimeToSec(srttime string) float64 {
	srttime = strings.Replace(srttime, ".", ",", -1)
	if strings.Count(srttime, ":") != 2 || strings.Count(srttime, ",") != 1 {
		panic("Invalid SRT time format")
	}

	parts := strings.Split(strings.Replace(srttime, ",", ":", -1), ":")
	HH, _ := strconv.Atoi(parts[0])
	MM, _ := strconv.Atoi(parts[1])
	SS, _ := strconv.Atoi(parts[2])
	MS, _ := strconv.Atoi(parts[3])

	return float64(HH)*3600 + float64(MM)*60 + float64(SS) + float64(MS)/1000.0
}

func secToSrttime(sec float64) string {
	HH := int(sec / 3600.0)
	MM := int((sec - 3600.0*float64(HH)) / 60.0)
	SS := int(sec - float64(HH)*3600.0 - float64(MM)*60.0)
	MS := (sec - float64(int(sec))) * 1000.0

	return fmt.Sprintf("%02d:%02d:%02d,%03d", HH, MM, SS, int(MS))
}

func isBRollContinuous(first, second interface{}) bool {
	// B roll has padding by 1/24.0 to prevent ffmpeg leak one frame of A clip.
	if first == "NO_B_ROLL" && second == "NO_B_ROLL" {
		return true
	}

	if firstSlice, ok1 := first.([]interface{}); ok1 {
		if secondSlice, ok2 := second.([]interface{}); ok2 {
			if firstSlice[0] == secondSlice[0] {
				firstOut := firstSlice[2].(float64)
				secondIn := secondSlice[1].(float64)
				if abs(secondIn-firstOut) < 2/24.0 {
					return true
				}
			}
		}
	}

	return false
}

func joinBRoll(first, second interface{}) interface{} {
	if first == "NO_B_ROLL" && second == "NO_B_ROLL" {
		return "NO_B_ROLL"
	}

	if firstSlice, ok1 := first.([]interface{}); ok1 {
		if secondSlice, ok2 := second.([]interface{}); ok2 {
			if firstSlice[0] == secondSlice[0] {
				firstOut := firstSlice[2].(float64)
				secondIn := secondSlice[1].(float64)
				if abs(firstOut-secondIn) < 2/24.0 {
					return []interface{}{firstSlice[0], firstSlice[1], secondSlice[2]}
				}
			}
		}
	}

	return nil
}

func abs(x float64) float64 {
	if x < 0 {
		return -x
	}
	return x
}

func stitchEdlQueue(rawQueue []OutputQueueItem) []OutputQueueItem {
	length := len(rawQueue)
	stitchedOutput := []OutputQueueItem{}
	i := 0

	for i < length {
		clip := rawQueue[i]
		j := i + 1

		if i == length-1 {
			stitchedOutput = append(stitchedOutput, rawQueue[i])
			break
		}

		clipNext := rawQueue[j]
		item := clip

		for clip.Filename == clipNext.Filename && clip.EndTC == clipNext.StartTC && isBRollContinuous(clip.BRoll, clipNext.BRoll) {
			item = OutputQueueItem{
				Filename: clip.Filename,
				StartTC:  clip.StartTC,
				EndTC:    clipNext.EndTC,
				BRoll:    joinBRoll(clip.BRoll, clipNext.BRoll),
			}

			clip = item
			j++

			if j == length {
				break
			}

			clipNext = rawQueue[j]
		}

		stitchedOutput = append(stitchedOutput, item)
		i = j
	}

	return stitchedOutput
}

func accurateAndFastTimeForFFmpeg(rIn, rOut float64, skipTime float64) (t2, t3, to, duration float64) {
	a := rIn
	b := rOut
	t1 := float64(int(a))

	if t1-skipTime > 0 {
		t2 = t1 - skipTime
		t3 = skipTime + (a - t1)
	} else {
		t2 = 0
		t3 = t1 + (a - t1)
	}

	to = round(b-t2, 3)
	duration = b - a

	return t2, t3, to, duration
}

func round(num float64, precision int) float64 {
	scale := math.Pow10(precision)
	return math.Round(num*scale) / scale
}

func determineFilenameFromClipname(clipname string) string {
	// Get all files in current directory
	files, err := ioutil.ReadDir(".")
	if err != nil {
		eprint("Error reading directory:", err)
		return ""
	}

	var filenamesV, filenamesA, filenamesI []string

	for _, file := range files {
		if strings.Contains(file.Name(), clipname) {
			ext := strings.ToLower(filepath.Ext(file.Name())[1:])
			if contains(videoFormats, ext) {
				filenamesV = append(filenamesV, file.Name())
				isPureAudioProject = false
			} else if contains(audioFormats, ext) {
				filenamesA = append(filenamesA, file.Name())
			} else if contains(imageFormats, ext) {
				filenamesI = append(filenamesI, file.Name())
				isPureAudioProject = false
			}
		}
	}

	if len(filenamesV) > 1 {
		eprint("WARNING: filename similar to clip", clipname, "has more than one")
		eprint("Choosing the", filenamesV[0])
		return filenamesV[0]
	} else if len(filenamesV) == 1 {
		return filenamesV[0]
	} else if len(filenamesA) > 1 {
		eprint("WARNING: filenames similar to clip", clipname, "has more than one")
		eprint("Choosing the", filenamesA[0])
		return filenamesA[0]
	} else if len(filenamesA) == 1 {
		return filenamesA[0]
	} else if len(filenamesI) > 1 {
		isPureAudioProject = false
		eprint("WARNING: filenames similar to clip", clipname, "has more than one")
		eprint("Choosing the", filenamesI[0])
		return filenamesI[0]
	} else if len(filenamesI) == 1 {
		isPureAudioProject = false
		return filenamesI[0]
	} else {
		eprint("WARNING: NO clip similar to \"", clipname, "\" found. Skip.")
		return ""
	}
}

func contains(slice []string, item string) bool {
	for _, a := range slice {
		if a == item {
			return true
		}
	}
	return false
}

// ... more functions would be implemented here ...

func handleBilibilClip(url string, rIn, rOut float64, bRoll interface{}, counter int, tempDirname string) string {
	fragmentExt := "ts" // ts will make A-V sync better

	// Get stream URLs
	cmd := exec.Command("yt-dlp", "-g", url)
	output, err := cmd.Output()
	if err != nil {
		eprint("Error running yt-dlp:", err)
		return ""
	}

	streamURLs := strings.Split(strings.TrimSpace(string(output)), "\n")
	if len(streamURLs) != 2 {
		eprint("Expected 2 stream URLs, got:", len(streamURLs))
		return ""
	}

	t2, t3, _, duration := accurateAndFastTimeForFFmpeg(rIn, rOut, 15)

	// Download video stream
	command := fmt.Sprintf("ffmpeg -hide_banner -loglevel error -user_agent \"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.106 Safari/537.36\" -headers \"Referer: %s\" -ss %v -i \"%s\" -ss %v -t %v %s/%05d_0.mp4",
		url, t2, streamURLs[0], t3, duration, tempDirname, counter)

	eprintNoNewline(".")
	if debug {
		eprint("")
		eprint("[yt-dlp:bilibili] " + command)
	}

	cmd = exec.Command("sh", "-c", command)
	cmd.Run()

	// Download audio stream
	command = fmt.Sprintf("ffmpeg -hide_banner -loglevel error -user_agent \"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.106 Safari/537.36\" -headers \"Referer: %s\" -ss %v -i \"%s\" -ss %v -t %v %s/%05d_1.mp4",
		url, t2, streamURLs[1], t3, duration, tempDirname, counter)

	eprintNoNewline(".")
	if debug {
		eprint("[yt-dlp:bilibili] " + command)
	}

	cmd = exec.Command("sh", "-c", command)
	cmd.Run()

	// Combine streams
	command = fmt.Sprintf("ffmpeg -hide_banner -loglevel error -i %s/%05d_0.mp4 -i %s/%05d_1.mp4 -qscale 0 %s/%05d.%s",
		tempDirname, counter, tempDirname, counter, tempDirname, counter, fragmentExt)

	eprintNoNewline(".")
	if debug {
		eprint("[yt-dlp:bilibili] " + command)
	}

	cmd = exec.Command("sh", "-c", command)
	cmd.Run()

	handleBRoll(bRoll, tempDirname, counter, fragmentExt, codecV, "")

	return fmt.Sprintf("file '%s/%05d.%s'", tempDirname, counter, fragmentExt)
}

func handleHttpClip(url string, rIn, rOut float64, bRoll interface{}, counter int, tempDirname string) string {
	t1 := rIn
	t2 := rOut
	fragmentExt := "mp4"

	command := fmt.Sprintf("ffmpeg -hide_banner -loglevel error -user_agent \"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.106 Safari/537.36\" -headers \"Referer: %s\" $(yt-dlp -g %s | sed \"s/.*/-ss %v -i &/\") -t %v %s/%05d.%s",
		url, url, t1, t2-t1, tempDirname, counter, fragmentExt)

	eprintNoNewline(".")
	if debug {
		eprint("")
		eprint("[yt-dlp] " + command)
	}

	cmd := exec.Command("sh", "-c", command)
	cmd.Run()

	handleBRoll(bRoll, tempDirname, counter, fragmentExt, codecV, "")

	return fmt.Sprintf("file '%s/%05d.%s'", tempDirname, counter, fragmentExt)
}

func handleLocalClip(f string, rIn, rOut float64, bRoll interface{}, counter int, tempDirname string) string {
	fragmentExt := "ts"

	t2, t3, to, _ := accurateAndFastTimeForFFmpeg(rIn, rOut, 15)

	ext := strings.ToLower(filepath.Ext(f)[1:])

	if contains(videoFormats, ext) {
		command := fmt.Sprintf("ffmpeg -hide_banner -loglevel error -ss %v -i \"%s\" -ss %v -to %v -vf 'fps=24, scale=1920:1080:force_original_aspect_ratio=decrease,pad=1920:1080:(ow-iw)/2:(oh-ih)/2,setsar=1' -c:v %s -b:v 2M -shortest %s/%05d.ts",
			t2, f, t3, to, codecV, tempDirname, counter)
		cmd := exec.Command("sh", "-c", command)
		cmd.Run()
	} else if contains(audioFormats, ext) {
		command := fmt.Sprintf("ffmpeg -hide_banner -loglevel error -f lavfi -i color=size=1920x1080:rate=24:color=black -ss %v -i \"%s\" -ss %v -to %v -c:v %s -b:v 2M -shortest %s/%05d.ts",
			t2, f, t3, to, codecV, tempDirname, counter)
		cmd := exec.Command("sh", "-c", command)
		cmd.Run()
	} else { // still image
		command := fmt.Sprintf("ffmpeg -hide_banner -loglevel error -f lavfi -i anullsrc=channel_layout=stereo:sample_rate=48000 -loop 1 -i \"%s\" -t %v -vf 'fps=24, scale=1920:1080:force_original_aspect_ratio=decrease,pad=1920:1080:(ow-iw)/2:(oh-ih)/2,setsar=1' -c:v %s -b:v 2M -shortest %s/%05d.ts",
			f, to-t3, codecV, tempDirname, counter)
		cmd := exec.Command("sh", "-c", command)
		cmd.Run()
	}

	handleBRoll(bRoll, tempDirname, counter, fragmentExt, codecV, "")

	return fmt.Sprintf("file '%s/%05d.%s'\n", tempDirname, counter, fragmentExt)
}

func handleBRoll(bRoll interface{}, tempDirname string, counter int, extname, codecV, codecA string) {
	if bRoll == "NO_B_ROLL" {
		return
	}

	// Convert bRoll interface{} to appropriate type
	bRollSlice, ok := bRoll.([]interface{})
	if !ok || len(bRollSlice) != 3 {
		eprint("Invalid B-roll format")
		return
	}

	tsFilename := fmt.Sprintf("%s/%05d.%s", tempDirname, counter, extname)
	tsTsFilename := fmt.Sprintf("%s/_%05d.%s", tempDirname, counter, extname)
	httpTsFilename := fmt.Sprintf("%s/http_%05d.%s", tempDirname, counter, extname)
	bTsFilename := fmt.Sprintf("%s/b_%05d.%s", tempDirname, counter, extname)

	bFilename := bRollSlice[0].(string)
	bIn := bRollSlice[1].(float64)
	bOut := bRollSlice[2].(float64)

	// Rename original ts file
	cmd := exec.Command("mv", tsFilename, tsTsFilename)
	cmd.Run()

	if strings.HasPrefix(strings.ToLower(bFilename), "http") {
		if strings.Contains(bFilename, "bilibili.com") {
			handleBilibilClip(bFilename, bIn, bOut, "NO_B_ROLL", counter, tempDirname)
		} else {
			handleHttpClip(bFilename, bIn, bOut, "NO_B_ROLL", counter, tempDirname)
		}

		cmd = exec.Command("mv", tsFilename, httpTsFilename)
		cmd.Run()

		command := fmt.Sprintf("ffmpeg -hide_banner -loglevel error -i %s -i %s -filter_complex \"[1:v]setpts=PTS, scale=1920:1080:force_original_aspect_ratio=decrease,pad=1920:1080:(ow-iw)/2:(oh-ih)/2[a]; [0:v][a]overlay=eof_action=pass[vout]; [0][1] amix [aout]\" -map [vout] -map [aout] -c:v %s -shortest -b:v 2M %s",
			tsTsFilename, httpTsFilename, codecV, tsFilename)
		cmd = exec.Command("sh", "-c", command)
		cmd.Run()
	} else { // local file as B roll
		bT2, bT3, bTo, _ := accurateAndFastTimeForFFmpeg(bIn, bOut, 15)

		ext := strings.ToLower(filepath.Ext(bFilename)[1:])
		if contains(videoFormats, ext) {
			command := fmt.Sprintf("ffmpeg -hide_banner -loglevel error -ss %v -i \"%s\" -ss %v -to %v -vf 'fps=24, scale=1920:1080:force_original_aspect_ratio=decrease,pad=1920:1080:(ow-iw)/2:(oh-ih)/2,setsar=1' -c:v %s -b:v 2M %s",
				bT2, bFilename, bT3, bTo, codecV, bTsFilename)
			cmd := exec.Command("sh", "-c", command)
			cmd.Run()

			command = fmt.Sprintf("ffmpeg -hide_banner -loglevel error -i %s -i %s -filter_complex \"[1:v]setpts=PTS[a]; [0:v][a]overlay=eof_action=pass[vout]; [0][1] amix [aout]\" -map [vout] -map [aout] -c:v %s -shortest -b:v 2M %s",
				tsTsFilename, bTsFilename, codecV, tsFilename)
			cmd = exec.Command("sh", "-c", command)
			cmd.Run()
		} else if contains(audioFormats, ext) { // B roll is pure audio
			command := fmt.Sprintf("ffmpeg -hide_banner -loglevel error -ss %v -to %v -i \"%s\" -i %s -filter_complex \"[0][1] amix [aout]\" -map 1:v -map [aout] -c:v %s -shortest %s",
				bT2+bT3, bT2+bTo, bFilename, tsTsFilename, "copy", tsFilename)
			cmd = exec.Command("sh", "-c", command)
			cmd.Run()
		} else { // still image
			command := fmt.Sprintf("ffmpeg -hide_banner -loglevel error -i %s -loop 1 -t %v -i \"%s\" -filter_complex \"[1:v]fps=24, scale=1920:1080:force_original_aspect_ratio=decrease,pad=1920:1080:(ow-iw)/2:(oh-ih)/2,setsar=1[a]; [0:v][a]overlay=eof_action=pass[vout]\" -map [vout] -map a:0 -c:v %s -b:v 2M -shortest %s",
				tsTsFilename, bTo-bT3, bFilename, codecV, tsFilename)
			cmd = exec.Command("sh", "-c", command)
			cmd.Run()
		}
	}

	eprintNoNewline("+") // indicates B roll generated
}

func handleAudioClip(f string, rIn, rOut float64, bRoll interface{}, counter int, tempDirname string, intermediateExtName string) string {
	var audioclipsExtName, intermediateAudioCodec string

	if intermediateExtName == "" {
		audioclipsExtName = filepath.Ext(f)
		intermediateAudioCodec = "-c:a copy"
	} else {
		audioclipsExtName = intermediateExtName
		intermediateAudioCodec = ""
	}

	eprintNoNewline(fmt.Sprintf("%05d%s ", counter, audioclipsExtName))

	t2, t3, _, duration := accurateAndFastTimeForFFmpeg(rIn, rOut, 15)

	command := fmt.Sprintf("ffmpeg -hide_banner -loglevel error -ss %v -i \"%s\" -ss %v -t %v %s %s/%05d%s",
		t2, f, t3, duration, intermediateAudioCodec, tempDirname, counter, audioclipsExtName)
	cmd := exec.Command("sh", "-c", command)
	cmd.Run()

	return fmt.Sprintf("file '%s/%05d%s'", tempDirname, counter, audioclipsExtName)
}

func determineOutputAudioFileExt(outputQueue []OutputQueueItem) (string, string, string) {
	exts := make(map[string]bool)

	for _, item := range outputQueue {
		ext := strings.ToLower(filepath.Ext(item.Filename)[1:])
		exts[ext] = true
	}

	if len(exts) == 1 {
		if exts["wav"] {
			return ".wav", "-c:a copy", ""
		} else if exts["mp3"] {
			return ".mp3", "-c:a copy", ""
		} else if exts["m4a"] {
			return ".m4a", "-c:a copy", ""
		}
	}

	return ".mp3", "-c:a libmp3lame -b:a 320k", ".wav"
}

func determineRoughcutFilename(roughcutExtName string) (string, string) {
	roughcutFilename := "roughcut" + roughcutExtName
	srtFilename := "roughcut.srt"

	if _, err := os.Stat(roughcutFilename); err == nil {
		renameCounter := 1
		roughcutFilename = fmt.Sprintf("roughcut_%d%s", renameCounter, roughcutExtName)
		srtFilename = fmt.Sprintf("roughcut_%d.srt", renameCounter)

		for {
			if _, err := os.Stat(roughcutFilename); err != nil {
				break
			}
			renameCounter++
			roughcutFilename = fmt.Sprintf("roughcut_%d%s", renameCounter, roughcutExtName)
			srtFilename = fmt.Sprintf("roughcut_%d.srt", renameCounter)
		}
	}

	return roughcutFilename, srtFilename
}

func createTempDir() (string, func(), error) {
	tempDir, err := ioutil.TempDir("", "tsv2roughcut-")
	if err != nil {
		return "", nil, err
	}

	cleanup := func() {
		os.RemoveAll(tempDir)
	}

	return tempDir, cleanup, nil
}

func main() {
	// Parse command line arguments
	userInputNewname := flag.Bool("u", false, "wait for user input then rename")
	play := flag.Bool("p", false, "play after generated")
	askBeforeDeleteTempFiles := flag.Bool("k", false, "ask before delete temp files")
	audioCrossfade := flag.Bool("c", false, "add cross fade between audio")
	roughcutFilename := ""
	srtFilename := ""

	flag.Parse()

	outfile := ""
	if flag.NArg() > 0 {
		outfile = flag.Arg(0)
	}

	// Set codec based on OS
	if runtime.GOOS == "darwin" {
		codecV = "h264_videotoolbox"
	} else if runtime.GOOS == "linux" {
		codecV = "libx264"
	} else {
		codecV = "libx264"
	}

	// Initialize queues
	outputQueue := []OutputQueueItem{}
	bBuffer := []interface{}{}
	srtQueue := []string{}
	srtCounter := 1
	srtLastPosition := 0.0

	// Process input lines
	scanner := bufio.NewScanner(os.Stdin)
	lineCounter := 0

	for scanner.Scan() {
		line := scanner.Text()

		if lineCounter == 0 && strings.HasPrefix(line, "\ufeff") {
			// Remove BOM header
			line = line[1:]
		}

		lineCounter++

		if strings.HasPrefix(line, "EDL") {
			l := strings.TrimSpace(line)
			var clipname, subtitle string

			if strings.Contains(l, "|") {
				parts := strings.Split(l, "|")
				for i := range parts {
					parts[i] = strings.TrimSpace(parts[i])
				}

				l = parts[0]
				if len(parts) > 1 {
					clipname = parts[1]
				}
				if len(parts) > 2 {
					subtitle = parts[2]
				}
			} else {
				continue
			}

			fields := strings.Fields(l)
			recordIn := strings.Replace(fields[1], "\"", "", -1)
			recordOut := strings.Replace(fields[2], "\"", "", -1)

			if generateSRT {
				t2 := srttimeToSec(recordOut)
				t1 := srttimeToSec(recordIn)
				srtDuration := round(t2-t1, 3)

				if !strings.Contains(line, "[ SPACE") && !strings.Contains(line, "|\t[B]") {
					s := strings.Split(strings.TrimSpace(line), "\t")
					if len(s) > 4 { // subtitle is not empty
						if srtCounter != 0 { // not first block
							srtQueue = append(srtQueue, "")
						}
						srtQueue = append(srtQueue, fmt.Sprintf("%d", srtCounter))
						srtQueue = append(srtQueue, fmt.Sprintf("%s --> %s",
							secToSrttime(srtLastPosition),
							secToSrttime(round(srtLastPosition+srtDuration, 3))))
						srtQueue = append(srtQueue, strings.Replace(s[4], "\\N", "\n", -1))
						srtCounter++
					}
				}

				if !strings.Contains(line, "|\t[B]") {
					srtLastPosition += srtDuration
					srtLastPosition = round(srtLastPosition, 3)
				}
			}

			var filename string
			if strings.HasPrefix(clipname, "http") {
				isPureAudioProject = false
				filename = clipname
			} else {
				filename = determineFilenameFromClipname(clipname)
				if filename == "" {
					continue
				}
			}

			if strings.HasPrefix(subtitle, "[B]") {
				// B-roll
				bBuffer = []interface{}{
					filename,
					srttimeToSec(recordIn),
					srttimeToSec(recordOut),
				}
			} else {
				// Normal lines
				item := OutputQueueItem{
					Filename: filename,
					StartTC:  srttimeToSec(recordIn),
					EndTC:    srttimeToSec(recordOut),
					BRoll:    "B_ROLL_UNDETERMINED",
				}

				outputQueue = append(outputQueue, item)

				if len(bBuffer) == 3 {
					// Handle B roll buffer
					_ = outputQueue[len(outputQueue)-1].Filename // fA
					sA := outputQueue[len(outputQueue)-1].StartTC
					eA := outputQueue[len(outputQueue)-1].EndTC

					fB := bBuffer[0].(string)
					sB := bBuffer[1].(float64)
					eB := bBuffer[2].(float64)

					durationA := eA - sA
					durationB := eB - sB

					if durationB <= durationA {
						outputQueue[len(outputQueue)-1].BRoll = bBuffer
						bBuffer = []interface{}{}
					} else {
						outputQueue[len(outputQueue)-1].BRoll = []interface{}{
							fB, sB, sB + durationA + 1.0/24.0,
						}
						bBuffer = []interface{}{fB, sB + durationA, eB}
					}
				} else {
					outputQueue[len(outputQueue)-1].BRoll = "NO_B_ROLL"
				}
			}
		}
	}

	if err := scanner.Err(); err != nil {
		eprint("Error reading input:", err)
		os.Exit(1)
	}

	if len(outputQueue) > 99999 {
		eprint("Too much. That's too much.")
		os.Exit(1)
	}

	// Stitch adjacent clips in outputQueue
	beforeStitchLines := len(outputQueue)
	outputQueue = stitchEdlQueue(outputQueue)
	eprint(fmt.Sprintf("[stitch] %d --> %d lines", beforeStitchLines, len(outputQueue)))

	// Process based on project type
	if isPureAudioProject {
		// Audio-only project processing
		roughcutExtName, roughcutAudioCodec, intermediateExtName := determineOutputAudioFileExt(outputQueue)

		tempDirname, cleanup, err := createTempDir()
		if err != nil {
			eprint("Failed to create temp directory:", err)
			os.Exit(1)
		}

		defer func() {
			if !*askBeforeDeleteTempFiles {
				cleanup()
			}
		}()

		eprint("[tempdir]", tempDirname)

		counter := 0
		eprintNoNewline("[ffmpeg] writing ")

		roughcutTxtPath := filepath.Join(tempDirname, "roughcut.txt")
		roughcutTxt, err := os.Create(roughcutTxtPath)
		if err != nil {
			eprint("Failed to create roughcut.txt:", err)
			os.Exit(1)
		}

		for _, item := range outputQueue {
			line := handleAudioClip(item.Filename, item.StartTC, item.EndTC, item.BRoll, counter, tempDirname, intermediateExtName)
			roughcutTxt.WriteString(line + "\r\n")
			counter++
		}

		roughcutTxt.Close()
		eprint("")

		roughcutFilename, srtFilename := determineRoughcutFilename(roughcutExtName)
		eprint("[ffmpeg concat] writing", roughcutFilename)

		if generateSRT {
			eprint("[srt] writing", srtFilename)
			srtFile, err := os.Create(srtFilename)
			if err != nil {
				eprint("Failed to create SRT file:", err)
			} else {
				srtFile.WriteString(strings.Join(srtQueue, "\n"))
				srtFile.Close()
			}
		}

		// Process audio (with or without crossfade)
		if *audioCrossfade {
			// Read the list of audio chunks from roughcut.txt
			roughcutTxt, err := ioutil.ReadFile(roughcutTxtPath)
			if err != nil {
				eprint("Failed to read roughcut.txt:", err)
				os.Exit(1)
			}

			audioChunksFileList := []string{}
			scanner := bufio.NewScanner(strings.NewReader(string(roughcutTxt)))
			for scanner.Scan() {
				line := scanner.Text()
				if strings.HasPrefix(line, "file ") {
					// Drop the leading 'file ' and any trailing whitespace/quotes
					filePath := strings.TrimSpace(line[5:])
					filePath = strings.Trim(filePath, "'\"")
					audioChunksFileList = append(audioChunksFileList, filePath)
				}
			}

			if len(audioChunksFileList) == 0 {
				eprint("No audio chunks found in roughcut.txt")
				os.Exit(1)
			}

			// Build the ffmpeg command with crossfade filter
			command := "ffmpeg -hide_banner -loglevel error"

			// Add all input files
			for _, filePath := range audioChunksFileList {
				command += fmt.Sprintf(" -i %s", filePath)
			}

			// Build the filter complex string based on number of files
			if len(audioChunksFileList) == 1 {
				// Only one chunk, no crossfade needed
				command += fmt.Sprintf(" %s %s", roughcutAudioCodec, roughcutFilename)
			} else if len(audioChunksFileList) == 2 {
				// Two chunks, single crossfade
				command += " -filter_complex \"[0][1]acrossfade=d=0.125:c1=tri:c2=tri\""
				command += fmt.Sprintf(" %s %s", roughcutAudioCodec, roughcutFilename)
			} else {
				// More than two chunks, complex crossfade chain
				command += " -filter_complex \""

				for i := 0; i < len(audioChunksFileList)-1; i++ {
					if i == 0 {
						command += "[0][1]acrossfade=d=0.125:c1=tri:c2=tri[a1];"
					} else {
						if i == len(audioChunksFileList)-2 {
							// Last pair of clips
							command += fmt.Sprintf("[a%d][%d]acrossfade=d=0.125:c1=tri:c2=tri;", i, i+1)
						} else {
							command += fmt.Sprintf("[a%d][%d]acrossfade=d=0.125:c1=tri:c2=tri[a%d];", i, i+1, i+1)
						}
					}
				}

				command += "\""
				command += fmt.Sprintf(" %s %s", roughcutAudioCodec, roughcutFilename)
			}

			// Execute the command
			eprint("[ffmpeg crossfade] executing complex filter")
			if debug {
				eprint(command)
			}

			cmd := exec.Command("sh", "-c", command)
			if err := cmd.Run(); err != nil {
				eprint("Error executing ffmpeg crossfade command:", err)

				// Fallback to regular concat if crossfade fails
				eprint("[ffmpeg] Falling back to regular concat without crossfade")
				fallbackCmd := fmt.Sprintf("ffmpeg -hide_banner -loglevel error -safe 0 -f concat -i %s/roughcut.txt %s %s",
					tempDirname, roughcutAudioCodec, roughcutFilename)
				exec.Command("sh", "-c", fallbackCmd).Run()
			}
		} else {
			// Regular concat without crossfade
			command := fmt.Sprintf("ffmpeg -hide_banner -loglevel error -safe 0 -f concat -i %s/roughcut.txt %s %s",
				tempDirname, roughcutAudioCodec, roughcutFilename)
			cmd := exec.Command("sh", "-c", command)
			if err := cmd.Run(); err != nil {
				eprint("Error running ffmpeg concat:", err)
			}
		}

		if *askBeforeDeleteTempFiles {
			fmt.Printf("Press enter to destroy temp dir: %s > ", tempDirname)
			var input string
			fmt.Scanln(&input)
			cleanup()
		}
	} else {
		// Video project processing
		roughcutTxtLines := []string{} // to generate roughcut.txt

		tempDirname, cleanup, err := createTempDir()
		if err != nil {
			eprint("Failed to create temp directory:", err)
			os.Exit(1)
		}

		defer func() {
			if !*askBeforeDeleteTempFiles {
				cleanup()
			}
		}()

		eprint("[tempdir]", tempDirname)
		counter := 0
		eprint("[ffmpeg] writing ", "")

		for _, item := range outputQueue {
			eprintNoNewline(fmt.Sprintf(" %05d", counter))

			if strings.HasPrefix(item.Filename, "http") {
				// Handle online clips
				if strings.Contains(item.Filename, "bilibili.com") {
					// Bilibili
					line := handleBilibilClip(item.Filename, item.StartTC, item.EndTC, item.BRoll, counter, tempDirname)
					roughcutTxtLines = append(roughcutTxtLines, line)
				} else {
					// YouTube, Twitter, etc.
					line := handleHttpClip(item.Filename, item.StartTC, item.EndTC, item.BRoll, counter, tempDirname)
					roughcutTxtLines = append(roughcutTxtLines, line)
				}
			} else {
				// Local media files
				line := handleLocalClip(item.Filename, item.StartTC, item.EndTC, item.BRoll, counter, tempDirname)
				roughcutTxtLines = append(roughcutTxtLines, line)
			}

			counter++
		}

		eprint("") // .ts segments written

		// Generate roughcut.txt
		roughcutTxtPath := filepath.Join(tempDirname, "roughcut.txt")
		err = ioutil.WriteFile(roughcutTxtPath, []byte(strings.Join(roughcutTxtLines, "\n")), 0644)
		if err != nil {
			eprint("Failed to write roughcut.txt:", err)
			os.Exit(1)
		}

		// Determine output filenames
		roughcutExtName := ".mp4" // or ".mkv"
		roughcutFilename, srtFilename = determineRoughcutFilename(roughcutExtName)
		eprint("[ffmpeg concat] writing", roughcutFilename)

		if generateSRT {
			eprint("[srt] writing", srtFilename)
			err = ioutil.WriteFile(srtFilename, []byte(strings.Join(srtQueue, "\n")), 0644)
			if err != nil {
				eprint("Failed to write SRT file:", err)
			}
		}

		// To make preview in macOS work, re-encode audio
		command := fmt.Sprintf("ffmpeg -hide_banner -loglevel error -safe 0 -f concat -i %s/roughcut.txt -ss 0 -c:v copy %s",
			tempDirname, roughcutFilename)
		cmd := exec.Command("sh", "-c", command)
		err = cmd.Run()
		if err != nil {
			eprint("Error running ffmpeg concat:", err)
		}

		// Handle temp directory cleanup
		if *askBeforeDeleteTempFiles {
			fmt.Printf("Press enter to destroy temp dir: %s > ", tempDirname)
			var input string
			fmt.Scanln(&input)
			cleanup()
		}

		// Handle rename if needed
		filenameChangeNeeded := false
		var newname string

		if *userInputNewname {
			fmt.Print("Input CLIPNAME to rename. ENTER to ignore > ")
			fmt.Scanln(&newname)
			newname = strings.TrimSpace(newname)

			filenameChangeNeeded = len(newname) > 0
			if !filenameChangeNeeded {
				eprint("ignored. keeping name [", roughcutFilename, "] [", srtFilename, "]")
			}
		} else if outfile != "" {
			newname = outfile
			filenameChangeNeeded = true
		}

		if filenameChangeNeeded {
			eprint("[Rename] ", roughcutFilename, "to", "["+newname+roughcutExtName+"]")
			err = os.Rename(roughcutFilename, newname+roughcutExtName)
			if err != nil {
				eprint("Error renaming video file:", err)
			} else {
				roughcutFilename = newname + roughcutExtName // for play
			}

			eprint("[Rename] ", srtFilename, "to", "["+newname+".srt"+"]")
			err = os.Rename(srtFilename, newname+".srt")
			if err != nil {
				eprint("Error renaming SRT file:", err)
			} else {
				srtFilename = newname + ".srt" // for play
			}
		} else {
			eprint(fmt.Sprintf("%s & %s generated", roughcutFilename, srtFilename))
		}

		// Play if requested
		if *play {
			cmd := exec.Command("mpv", roughcutFilename)
			cmd.Run()
		}
	}
}
