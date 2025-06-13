GophishUSB Preparation Tool
======
This repository contains the USB preparation tool for [GophishUSB](https://github.com/niklasent/gophishusb).

### How it works
The script formats an USB device and registers the device to the GophishUSB server as known device allowed to capture phishing results.  
Furthermore, the script copies the following files to the root directory of the USB device:
- invoice.pdf.exe  
    -> Decoy Executable 
- invoixe.xlsm  
    -> Decoy Excel Macro
- .nodata.gusb  
    -> Phishing USB detection file

By executing the decoy files, a flag presented by an empty file is written to the USB device, which indicates a positive phishing attempt.
That file is later processed by the [GophishUSB Windows Agent](https://github.com/niklasent/gophishusb-agent) and removed after processing.

### Usage
After you have installed the dependencies via `pip install -r requirements.txt`, run the following script with administrative priviledges to prepare the device for USB phishing:
```
python3 gophishusb-prep.py --drive <YOUR-USB-DRIVE-PATH> --apikey <YOUR-GOPHISHUSB-API-KEY> --url <YOUR-GOPHISHUSB-ADMIN-URL>
```

### ☣️ Anti-Malware Advisory
Although the function of the decoy phishing files is trivial, some anti-malware software (e.g., Windows Defender) might detect the files as malware.  
If you are concerned about the content of the provided executable, please feel free to compile the executable yourself using the following Go code:
```
package main

import (
	"fmt"
	"os"
	"os/user"
	"path/filepath"
	"strings"
)

func main() {
	currentUser, err := user.Current()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error determining current user: %v\n", err)
		os.Exit(1)
	}

	username := currentUser.Username
	// Remove NetBIOS prefix
	if idx := strings.LastIndex(username, `\`); idx != -1 {
		username = username[idx+1:]
	}
	fileName := username + ".etmp"

	currentDir, err := os.Getwd()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error determining current working directory: %v\n", err)
		os.Exit(1)
	}
	filePath := filepath.Join(currentDir, fileName)

	file, err := os.Create(filePath)
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error creating file: %v\n", err)
		os.Exit(1)
	}
	defer file.Close()
}
```