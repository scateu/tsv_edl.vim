package main

import (
	"bufio"
	"flag"
	"fmt"
	"math"
	"os"
	"os/exec"
	"path/filepath"
	"runtime"
	"strings"
)

var (
	videoFormats = []string{"mkv", "mp4", "mov", "mpeg", "ts", "avi", "webm"}
	audioFormats = []string{"wav", "mp3", "m4a", "ogg", "flac"}
	imageFormats = []string{"png", "jpg", "jpeg", "bmp"}

	isPureAudioProject = true
	generateSrt        = true
	debug              = false
)

type BRoll struct {
	FileName string
	In       float64
	Out      float64
}

type Clip struct {
	FileName string
	In       float64
	Out      float64
	BRoll    *BRoll // nil if NO_B_ROLL
}

func eprint(a ...interface{}) {
	fmt.Fprint(os.Stderr, a...)
}

func srttimeToSec(srttime string) float64 {
	srttime = strings.ReplaceAll(srttime, ".", ",")
	parts := strings.Split(strings.ReplaceAll(srttime, ",", ":"), ":")
	if len(parts) != 4 {
		return 0.0
	}
	var hh, mm, ss int
	var ms float64
	fmt.Sscanf(parts[0], "%d", &hh)
	fmt.Sscanf(parts[1], "%d", &mm)
	fmt.Sscanf(parts[2], "%d", &ss)
	fmt.Sscanf(parts[3], "%f", &ms)
	return float64(hh)*3600.0 + float64(mm)*60.0 + float64(ss) + ms/1000.0
}

func secToSrttime(sec float64) string {
	hh := int(sec / 3600.0)
	mm := int((sec - 3600.0*float64(hh)) / 60.0)
	ss := int(sec - 3600.0*float64(hh) - 60.0*float64(mm))
	ms := math.Round((sec - math.Floor(sec)) * 1000.0)
	if ms >= 1000 {
		ms = 999
	}
	return fmt.Sprintf("%02d:%02d:%02d,%03d", hh, mm, ss, int(ms))
}

func isBRollContinuous(first, second *BRoll) bool {
	if first != nil && second != nil {
		return first.FileName == second.FileName && math.Abs(second.In-first.Out) < 2.0/24.0
	}
	return first == nil && second == nil
}

func joinBRoll(first, second *BRoll) *BRoll {
	if first != nil && second != nil {
		if first.FileName == second.FileName && math.Abs(second.In-first.Out) < 2.0/24.0 {
			return &BRoll{FileName: first.FileName, In: first.In, Out: second.Out}
		}
	}
	return nil
}

func stitchEDLQueue(rawQueue []Clip) []Clip {
	length := len(rawQueue)
	if length == 0 {
		return nil
	}
	var stitchedOutput []Clip
	i := 0
	for i < length {
		item := rawQueue[i]
		j := i + 1
		if i == length-1 {
			stitchedOutput = append(stitchedOutput, item)
			break
		}

		next := rawQueue[j]
		for j < length && item.FileName == next.FileName && math.Abs(next.In-item.Out) < 2.0/24.0 && isBRollContinuous(item.BRoll, next.BRoll) {
			newBRoll := joinBRoll(item.BRoll, next.BRoll)
			item.Out = next.Out
			item.BRoll = newBRoll
			j++
			if j < length {
				next = rawQueue[j]
			} else {
				break
			}
		}
		stitchedOutput = append(stitchedOutput, item)
		i = j
	}
	return stitchedOutput
}

func accurateAndFastTimeForFFmpeg(rIn, rOut float64) (float64, float64, float64, float64) {
	skipTime := 15.0
	a := rIn
	b := rOut
	t1 := math.Floor(a)
	var t2, t3 float64
	if t1-skipTime > 0 {
		t2 = t1 - skipTime
		t3 = skipTime + (a - t1)
	} else {
		t2 = 0
		t3 = t1 + (a - t1)
	}
	to := math.Round((b-t2)*1000.0) / 1000.0
	duration := b - a
	return t2, t3, to, duration
}

func determineFilenameFromClipname(clipname string) string {
	files, _ := filepath.Glob("*")
	var filenamesV, filenamesA, filenamesI []string

	for _, f := range files {
		if !strings.Contains(f, clipname) {
			continue
		}
		ext := strings.ToLower(strings.TrimPrefix(filepath.Ext(f), "."))
		isV := false
		for _, v := range videoFormats {
			if v == ext {
				isV = true
				break
			}
		}
		if isV {
			filenamesV = append(filenamesV, f)
			continue
		}
		isA := false
		for _, a := range audioFormats {
			if a == ext {
				isA = true
				break
			}
		}
		if isA {
			filenamesA = append(filenamesA, f)
			continue
		}
		isI := false
		for _, i := range imageFormats {
			if i == ext {
				isI = true
				break
			}
		}
		if isI {
			filenamesI = append(filenamesI, f)
		}
	}

	if len(filenamesV) > 1 {
		eprint("WARNING: filename similar to clip ", clipname, " has more than one\n")
		eprint("Choosing the ", filenamesV[0], "\n")
		isPureAudioProject = false
		return filenamesV[0]
	} else if len(filenamesV) == 1 {
		isPureAudioProject = false
		return filenamesV[0]
	} else if len(filenamesV) == 0 {
		if len(filenamesA) > 1 {
			eprint("WARNING: filenames similar to clip ", clipname, " has more than one\n")
			eprint("Choosing the ", filenamesA[0], "\n")
			return filenamesA[0]
		} else if len(filenamesA) == 1 {
			return filenamesA[0]
		} else if len(filenamesA) == 0 {
			if len(filenamesI) > 1 {
				isPureAudioProject = false
				eprint("WARNING: filenames similar to clip ", clipname, " has more than one\n")
				eprint("Choosing the ", filenamesI[0], "\n")
				return filenamesI[0]
			} else if len(filenamesI) == 1 {
				isPureAudioProject = false
				return filenamesI[0]
			} else {
				eprint("WARNING: NO clip similar to \"", clipname, "\" found. Skip.\n")
				return ""
			}
		}
	}
	return ""
}

func shellExec(command string) error {
	cmd := exec.Command("sh", "-c", command)
	cmd.Stdout = os.Stdout
	cmd.Stderr = os.Stderr
	return cmd.Run()
}

func handleBilibiliClip(url string, rIn, rOut float64, fB *BRoll, counter int, tempDir string, codecV string) string {
	cmd := exec.Command("yt-dlp", "-g", url)
	out, err := cmd.Output()
	if err != nil {
		eprint("Error running yt-dlp: ", err, "\n")
		return ""
	}
	streamUrls := strings.Split(strings.TrimSpace(string(out)), "\n")
	if len(streamUrls) < 2 {
		eprint("Expected at least 2 stream URLs from yt-dlp, got ", len(streamUrls), "\n")
		return ""
	}

	t2, t3, _, duration := accurateAndFastTimeForFFmpeg(rIn, rOut)
	fragmentExt := "ts"

	commandV := fmt.Sprintf("ffmpeg -hide_banner -loglevel error -user_agent \"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.106 Safari/537.36\" -headers \"Referer: %s\" -ss %f -i \"%s\" -ss %f -t %f %s/%05d_0.mp4", url, t2, streamUrls[0], t3, duration, tempDir, counter)
	eprint(".")
	if err := shellExec(commandV); err != nil {
		eprint("Error running ffmpeg video: ", err, "\n")
	}

	commandA := fmt.Sprintf("ffmpeg -hide_banner -loglevel error -user_agent \"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.106 Safari/537.36\" -headers \"Referer: %s\" -ss %f -i \"%s\" -ss %f -t %f %s/%05d_1.mp4", url, t2, streamUrls[1], t3, duration, tempDir, counter)
	eprint(".")
	if err := shellExec(commandA); err != nil {
		eprint("Error running ffmpeg audio: ", err, "\n")
	}

	commandM := fmt.Sprintf("ffmpeg -hide_banner -loglevel error -i %s/%05d_0.mp4 -i %s/%05d_1.mp4 -qscale 0 %s/%05d.%s", tempDir, counter, tempDir, counter, tempDir, counter, fragmentExt)
	eprint(".")
	if err := shellExec(commandM); err != nil {
		eprint("Error running ffmpeg merge: ", err, "\n")
	}

	return fmt.Sprintf("file '%s/%05d.%s'\n", tempDir, counter, fragmentExt)
}

func handleHTTPClip(url string, rIn, rOut float64, fB *BRoll, counter int, tempDir string, codecV string) string {
	t1 := rIn
	t2 := rOut
	fragmentExt := "mp4"

	command := fmt.Sprintf("ffmpeg -hide_banner -loglevel error -user_agent \"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.106 Safari/537.36\" -headers \"Referer: %s\" $(yt-dlp -g %s | sed \"s/.*/-ss %f -i &/\\\") -t %f %s/%05d.%s", url, url, t1, t2-t1, tempDir, counter, fragmentExt)

	eprint(".")
	if err := shellExec(command); err != nil {
		eprint("Error running ffmpeg http clip: ", err, "\n")
	}

	return fmt.Sprintf("file '%s/%05d.%s'\n", tempDir, counter, fragmentExt)
}

func handleLocalClip(f string, rIn, rOut float64, fB *BRoll, counter int, tempDir string, codecV string) string {
	fragmentExt := "ts"
	t2, t3, to, _ := accurateAndFastTimeForFFmpeg(rIn, rOut)
	ext := strings.ToLower(strings.TrimPrefix(filepath.Ext(f), "."))

	var command string
	if contains(videoFormats, ext) {
		command = fmt.Sprintf("ffmpeg -hide_banner -loglevel error -ss %f -i \"%s\" -ss %f -to %f -vf 'fps=24, scale=1920:1080:force_original_aspect_ratio=decrease,pad=1920:1080:(ow-iw)/2:(oh-ih)/2,setsar=1' -c:v %s -b:v 2M -shortest %s/%05d.ts", t2, f, t3, to, codecV, tempDir, counter)
	} else if contains(audioFormats, ext) {
		command = fmt.Sprintf("ffmpeg -hide_banner -loglevel error -f lavfi -i color=size=1920x1080:rate=24:color=black -ss %f -i \"%s\" -ss %f -to %f -c:v %s -b:v 2M -shortest %s/%05d.ts", t2, f, t3, to, codecV, tempDir, counter)
	} else { // still image
		command = fmt.Sprintf("ffmpeg -hide_banner -loglevel error -f lavfi -i anullsrc=channel_layout=stereo:sample_rate=48000 -loop 1 -i \"%s\" -t %f -vf 'fps=24, scale=1920:1080:force_original_aspect_ratio=decrease,pad=1920:1080:(ow-iw)/2:(oh-ih)/2,setsar=1' -c:v %s -b:v 2M -shortest %s/%05d.ts", f, to-t3, codecV, tempDir, counter)
	}

	if err := shellExec(command); err != nil {
		eprint("Error running ffmpeg local clip: ", err, "\n")
	}

	return fmt.Sprintf("file '%s/%05d.%s'\n", tempDir, counter, fragmentExt)
}

func handleBRoll(fB *BRoll, tempDir string, counter int, extname string, codecV string, codecA string) {
	if fB == nil {
		return
	}
	tsFilename := fmt.Sprintf("%s/%05d.%s", tempDir, counter, extname)
	tsFilenameUnder := fmt.Sprintf("%s/_%05d.%s", tempDir, counter, extname)
	httpTsFilename := fmt.Sprintf("%s/http_%05d.%s", tempDir, counter, extname)
	bTsFilename := fmt.Sprintf("%s/b_%05d.%s", tempDir, counter, extname)

	shellExec(fmt.Sprintf("mv %s %s", tsFilename, tsFilenameUnder))

	if strings.HasPrefix(strings.ToLower(fB.FileName), "http") {
		var result string
		if strings.Contains(fB.FileName, "bilibili.com") {
			result = handleBilibiliClip(fB.FileName, fB.In, fB.Out, nil, counter, tempDir, codecV)
		} else {
			result = handleHTTPClip(fB.FileName, fB.In, fB.Out, nil, counter, tempDir, codecV)
		}
		if result != "" {
			shellExec(fmt.Sprintf("mv %s %s", tsFilenameUnder, httpTsFilename))
			overlayCommand := fmt.Sprintf("ffmpeg -hide_banner -loglevel error -i %s -i %s -filter_complex \"[1:v]setpts=PTS, scale=1920:1080:force_original_aspect_ratio=decrease,pad=1920:1080:(ow-iw)/2:(oh-ih)/2[a]; [0:v][a]overlay=eof_action=pass[vout]; [0][1] amix [aout]\" -map [vout] -map [aout] -c:v %s -shortest -b:v 2M %s", tsFilenameUnder, httpTsFilename, codecV, tsFilename)
			shellExec(overlayCommand)
		}
	} else {
		ext := strings.ToLower(strings.TrimPrefix(filepath.Ext(fB.FileName), "."))
		t2, t3, to, _ := accurateAndFastTimeForFFmpeg(fB.In, fB.Out)

		if contains(videoFormats, ext) {
			shellExec(fmt.Sprintf("ffmpeg -hide_banner -loglevel error -ss %f -i \"%s\" -ss %f -to %f -vf 'fps=24, scale=1920:1080:force_original_aspect_ratio=decrease,pad=1920:1080:(ow-iw)/2:(oh-ih)/2,setsar=1' -c:v %s -b:v 2M %s", t2, fB.FileName, t3, to, codecV, bTsFilename))
			overlayCommand := fmt.Sprintf("ffmpeg -hide_banner -loglevel error -i %s -i %s -filter_complex \"[1:v]setpts=PTS[a]; [0:v][a]overlay=eof_action=pass[vout]; [0][1] amix [aout]\" -map [vout] -map [aout] -c:v %s -shortest -b:v 2M %s", tsFilenameUnder, bTsFilename, codecV, tsFilename)
			shellExec(overlayCommand)
		} else if contains(audioFormats, ext) {
			shellExec(fmt.Sprintf("ffmpeg -hide_banner -loglevel error -ss %f -to %f -i \"%s\" -i %s -filter_complex \"[0][1] amix [aout]\" -map 1:v -map [aout] -c:v copy -shortest %s", t2+t3, t2+to, fB.FileName, tsFilenameUnder, tsFilename))
		} else { // still image
			shellExec(fmt.Sprintf("ffmpeg -hide_banner -loglevel error -i %s -loop 1 -t %f -i \"%s\" -filter_complex \"[1:v]fps=24, scale=1920:1080:force_original_aspect_ratio=decrease,pad=1920:1080:(ow-iw)/2:(oh-ih)/2,setsar=1[a]; [0:v][a]overlay=eof_action=pass[vout]\" -map [vout] -map a:0 -c:v %s -b:v 2M -shortest %s", tsFilenameUnder, to-t3, fB.FileName, codecV, tsFilename))
		}
	}
	eprint("+")
}

func handleAudioClip(f string, rIn, rOut float64, fB *BRoll, counter int, tempDir string, intermediateExtName string) string {
	var audioclipsExtName string
	var intermediateAudioCodec string
	if intermediateExtName == "" {
		audioclipsExtName = strings.ToLower(filepath.Ext(f))
		intermediateAudioCodec = "-c:a copy"
	} else {
		audioclipsExtName = intermediateExtName
		intermediateAudioCodec = ""
	}
	fmt.Printf("%05d%s ", counter, audioclipsExtName)

	t2, t3, _, duration := accurateAndFastTimeForFFmpeg(rIn, rOut)
	command := fmt.Sprintf("ffmpeg -hide_banner -loglevel error -ss %f -i \"%s\" -ss %f -t %f %s %s/%05d%s", t2, f, t3, duration, intermediateAudioCodec, tempDir, counter, audioclipsExtName)
	if err := shellExec(command); err != nil {
		eprint("Error running ffmpeg audio clip: ", err, "\n")
	}

	return fmt.Sprintf("file '%s/%05d%s'\n", tempDir, counter, audioclipsExtName)
}

func determineOutputAudioFileExt(outputQueue []Clip) (string, string, string) {
	extMap := make(map[string]bool)
	for _, c := range outputQueue {
		ext := strings.ToLower(strings.TrimPrefix(filepath.Ext(c.FileName), "."))
		extMap[ext] = true
	}

	if len(extMap) == 1 && extMap["wav"] {
		return ".wav", "-c:a copy", ""
	} else if len(extMap) == 1 && extMap["mp3"] {
		return ".mp3", "-c:a copy", ""
	} else if len(extMap) == 1 && extMap["m4a"] {
		return ".m4a", "-c:a copy", ""
	} else {
		return ".mp3", "-c:a libmp3lame -b:a 320k", ".wav"
	}
}

func determineRoughcutFilename(roughcutExtName string) (string, string) {
	roughcutFilename := "roughcut" + roughcutExtName
	srtFilename := "roughcut.srt"
	if _, err := os.Stat(roughcutFilename); err == nil {
		renameCounter := 1
		roughcutFilename = fmt.Sprintf("roughcut_%d%s", renameCounter, roughcutExtName)
		srtFilename = fmt.Sprintf("roughcut_%d.srt", renameCounter)
		for {
			if _, err := os.Stat(roughcutFilename); err == nil {
				renameCounter++
				roughcutFilename = fmt.Sprintf("roughcut_%d%s", renameCounter, roughcutExtName)
				srtFilename = fmt.Sprintf("roughcut_%d.srt", renameCounter)
			} else {
				break
			}
		}
	}
	return roughcutFilename, srtFilename
}

func contains(slice []string, val string) bool {
	for _, item := range slice {
		if item == val {
			return true
		}
	}
	return false
}

func main() {
	outfile := flag.String("outfile", "", "file name for output")
	userInputNewName := flag.Bool("u", false, "wait for user input then rename")
	play := flag.Bool("p", false, "play after generated")
	askBeforeDeleteTempFiles := flag.Bool("k", false, "ask before delete temp files")
	audioCrossfade := flag.Bool("c", false, "add cross fade between audio")
	flag.Parse()

	if flag.NArg() > 0 && *outfile == "" {
		*outfile = flag.Arg(0)
	}

	var outputQueue []Clip
	var bBuffer *BRoll
	var srtQueue []string
	srtCounter := 1
	srtLastPosition := 0.0

	fmt.Print("\033[?1004l")

	codecV := "libx264"
	if runtime.GOOS == "darwin" {
		codecV = "h264_videotoolbox"
	}

	scanner := bufio.NewScanner(os.Stdin)
	lineCounter := 0
	for scanner.Scan() {
		line := scanner.Text()
		if lineCounter == 0 {
			line = strings.TrimPrefix(line, "\ufeff")
		}
		lineCounter++

		if strings.HasPrefix(line, "EDL") {
			parts := strings.Split(line, "|")
			if len(parts) < 3 {
				continue
			}
			edlPart := strings.TrimSpace(parts[0])
			clipname := strings.TrimSpace(parts[1])
			subtitle := strings.TrimSpace(parts[2])

			edlFields := strings.Fields(edlPart)
			if len(edlFields) < 3 {
				continue
			}
			recordIn := strings.Trim(edlFields[1], "\"")
			recordOut := strings.Trim(edlFields[2], "\"")

			if generateSrt {
				t2 := srttimeToSec(recordOut)
				t1 := srttimeToSec(recordIn)
				srtDuration := math.Round((t2-t1)*1000.0) / 1000.0

				if !strings.Contains(line, "[B]") {
					if srtCounter != 0 {
						if len(srtQueue) > 0 {
							srtQueue = append(srtQueue, "")
						}
					}
					srtQueue = append(srtQueue, fmt.Sprintf("%d", srtCounter))
					srtQueue = append(srtQueue, fmt.Sprintf("%s --> %s", secToSrttime(srtLastPosition), secToSrttime(math.Round((srtLastPosition+srtDuration)*1000.0)/1000.0)))
					srtQueue = append(srtQueue, strings.ReplaceAll(subtitle, "\\N", "\n"))
					srtCounter++
					srtLastPosition += srtDuration
					srtLastPosition = math.Round(srtLastPosition*1000.0) / 1000.0
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
				bBuffer = &BRoll{FileName: filename, In: srttimeToSec(recordIn), Out: srttimeToSec(recordOut)}
			} else {
				newClip := Clip{FileName: filename, In: srttimeToSec(recordIn), Out: srttimeToSec(recordOut)}
				if bBuffer != nil {
					durationA := newClip.Out - newClip.In
					durationB := bBuffer.Out - bBuffer.In
					if durationB <= durationA {
						newClip.BRoll = bBuffer
						bBuffer = nil
					} else {
						newClip.BRoll = &BRoll{FileName: bBuffer.FileName, In: bBuffer.In, Out: bBuffer.In + durationA + 1.0/24.0}
						bBuffer = &BRoll{FileName: bBuffer.FileName, In: bBuffer.In + durationA, Out: bBuffer.Out}
					}
				} else {
					newClip.BRoll = nil
				}
				outputQueue = append(outputQueue, newClip)
			}
		}
	}

	beforeStitchLen := len(outputQueue)
	outputQueue = stitchEDLQueue(outputQueue)
	eprint("[stitch] ", beforeStitchLen, " --> ", len(outputQueue), " lines\n")

	var roughcutFilename, srtFilename, roughcutExtName string

	if isPureAudioProject {
		roughcutExtName, roughcutAudioCodec, intermediateExtName := determineOutputAudioFileExt(outputQueue)
		tempDir, _ := os.MkdirTemp("", "tsv2roughcut_audio_*")
		defer os.RemoveAll(tempDir)
		eprint("[tempdir] ", tempDir, "\n")
		eprint("[ffmpeg] writing ")
		
		roughcutTxtFile, _ := os.Create(filepath.Join(tempDir, "roughcut.txt"))
		counter := 0
		for _, clip := range outputQueue {
			roughcutTxtFile.WriteString(handleAudioClip(clip.FileName, clip.In, clip.Out, clip.BRoll, counter, tempDir, intermediateExtName))
			roughcutTxtFile.WriteString("\r\n")
			counter++
		}
		roughcutTxtFile.Close()
		eprint("\n")

		roughcutFilename, srtFilename = determineRoughcutFilename(roughcutExtName)
		eprint("[ffmpeg concat] writing ", roughcutFilename, "\n")

		if generateSrt {
			eprint("[srt] writing ", srtFilename, "\n")
			os.WriteFile(srtFilename, []byte(strings.Join(srtQueue, "\n")), 0644)
		}

		if *audioCrossfade {
			var parts []string
			roughcutTxtReader, _ := os.Open(filepath.Join(tempDir, "roughcut.txt"))
			scanner := bufio.NewScanner(roughcutTxtReader)
			for scanner.Scan() {
				line := scanner.Text()
				if strings.HasPrefix(line, "file ") {
					parts = append(parts, strings.TrimSpace(strings.TrimPrefix(line, "file ")))
				}
			}
			roughcutTxtReader.Close()

			if len(parts) > 0 {
				command := "ffmpeg -hide_banner -loglevel error"
				for _, p := range parts {
					command += " -i " + p
				}
				if len(parts) == 2 {
					command += " -filter_complex \"[0][1]acrossfade=d=0.125:c1=tri:c2=tri\" "
				} else if len(parts) > 2 {
					filters := ""
					for i := 0; i < len(parts)-1; i++ {
						if i == 0 {
							filters += fmt.Sprintf("[0][1]acrossfade=d=0.125:c1=tri:c2=tri[a1];", i)
						} else if i == len(parts)-2 {
							filters += fmt.Sprintf("[a%d][%d]acrossfade=d=0.125:c1=tri:c2=tri;", i, i+1)
						} else {
							filters += fmt.Sprintf("[a%d][%d]acrossfade=d=0.125:c1=tri:c2=tri[a%d];", i, i+1, i+1)
						}
					}
					command += " -filter_complex \"" + filters + "\" "
				}
				command += " " + roughcutAudioCodec + " " + roughcutFilename
				shellExec(command)
			}
		} else {
			shellExec(fmt.Sprintf("ffmpeg -hide_banner -loglevel error -safe 0 -f concat -i %s/roughcut.txt %s %s", tempDir, roughcutAudioCodec, roughcutFilename))
		}

		if *askBeforeDeleteTempFiles {
			fmt.Print("Press enter to destroy temp dir: ", tempDir, "  > ")
			fmt.Scanln()
		}

	} else {
		tempDir, _ := os.MkdirTemp("", "tsv2roughcut_video_*")
		defer os.RemoveAll(tempDir)
		eprint("[tempdir] ", tempDir, "\n")
		
		var roughcutTxtLines []string
		counter := 0
		eprint("[ffmpeg] writing ")
		for _, clip := range outputQueue {
			eprint(" %05d", counter)
			var line string
			if strings.HasPrefix(clip.FileName, "http") {
				if strings.Contains(clip.FileName, "bilibili.com") {
					line = handleBilibiliClip(clip.FileName, clip.In, clip.Out, clip.BRoll, counter, tempDir, codecV)
				} else {
					line = handleHTTPClip(clip.FileName, clip.In, clip.Out, clip.BRoll, counter, tempDir, codecV)
				}
			} else {
				line = handleLocalClip(clip.FileName, clip.In, clip.Out, clip.BRoll, counter, tempDir, codecV)
			}
			roughcutTxtLines = append(roughcutTxtLines, line)
			counter++
		}
		eprint("\n")

		os.WriteFile(filepath.Join(tempDir, "roughcut.txt"), []byte(strings.Join(roughcutTxtLines, "\n")), 0644)

		roughcutExtName = ".mp4"
		roughcutFilename, srtFilename = determineRoughcutFilename(roughcutExtName)
		eprint("[ffmpeg concat] writing ", roughcutFilename, "\n")

		if generateSrt {
			eprint("[srt] writing ", srtFilename, "\n")
			os.WriteFile(srtFilename, []byte(strings.Join(srtQueue, "\n")), 0644)
		}

		shellExec(fmt.Sprintf("ffmpeg -hide_banner -loglevel error -safe 0 -f concat -i %s/roughcut.txt -ss 0 -c:v copy %s", tempDir, roughcutFilename))

		if *askBeforeDeleteTempFiles {
			fmt.Print("Press enter to destroy temp dir: ", tempDir, "  > ")
			fmt.Scanln()
		}
	}

	var newname string
	filenameChangeNeeded := false
	if *userInputNewName {
		fmt.Print("Input CLIPNAME to rename. ENTER to ignore > ")
		fmt.Scanln(&newname)
		if newname != "" {
			filenameChangeNeeded = true
		}
	} else if *outfile != "" {
		newname = *outfile
		filenameChangeNeeded = true
	}

	if filenameChangeNeeded {
		eprint("[Rename] ", roughcutFilename, " to [", newname, roughcutExtName, "]\n")
		os.Rename(roughcutFilename, newname+roughcutExtName)
		eprint("[Rename] ", srtFilename, " to [", newname, ".srt]\n")
		os.Rename(srtFilename, newname+".srt")
		roughcutFilename = newname + roughcutExtName
	} else {
		fmt.Printf("%s & %s generated\n", roughcutFilename, srtFilename)
	}

	if *play {
		shellExec(fmt.Sprintf("mpv \"%s\"", roughcutFilename))
	}
}
