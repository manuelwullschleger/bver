# 3D-PrintMonitoring


Die meisten FDM-3D-Drucker besitzen keine Fehlerüberwachung, auch wenn einen Druckfehler auftritt, wird weiter gedruckt und somit Filament verschwendet oder der Drucker kann beschädigt werden. Ziel des Projektes ist es die Qualität eines FDM-3D-Drucks durch eine Kamera live zu überwachen, um so den Druck beim Auftreten eines Fehlers automatisiert pausieren oder abbrechen zu können. 

## Voraussetzungen
Das Projekt wurde mit *Python 3.7.4* umgesetzt.
Folgende Packages werden verwendet. 

```
matplotlib==3.2.1
numpy==1.18.5
opencv-python==4.2.0.34
pandas==1.0.4
seaborn==0.10.1
```
Sämmtiche verwendeten Packages können mit folgendem Befehl installiert werden
```
pip install -r requirements.txt
```


## Anleitung

Das Tool verfügt über ein CLI. Mögliche Optionen können mit dem Parameter *--help* aufgeliestet werden


```
$ python main.py --help

usage: main.py [-h] [-g PathToGCodeFile] [-w webcamId] [-v PathToVideoFile]   
               [-s] [-t] [-c]

Ultimaker 3d-Print monitoring tool by Marc Röthlisberger & Manuel Wullschleger

optional arguments:
  -h, --help          show this help message and exit
  -g PathToGCodeFile  Path to the gcode file
  -w webcamId         Define webcam to use for print monitoring
  -v PathToVideoFile  Run for pre-recorded video
  -s                  Starts print monitoring for gcode file using defined
                      webcam or video source
  -t                  Show test image to validate video source
  -c                  Configure ROIs
```


### Konfiguration
Sobald erstmals eine neue Kamera oder eine neue Videodatei verwendet wird, muss das Tool manuell konfiguriert werden.

Webcam:
```
$ python main.py -w 0 -c
```

Videodatei:
```
$ python main.py -v "path\to\video.mp4" -c
```

Danach muss zuerst die ROI des Druckkopfes, danach die ROI des Druckers ausgewählt werden. 

#### Testen der Konfiguration
Um die Verbindung zu einer Kamera zu testen, kann mit dem Parameter *-t* das aktuelle Kamerabild angezeigt werden. 

Webcam:

```
$ python main.py -w 0 -t
```

Videodatei:
```
$ python main.py -v "path\to\video.mp4" -t
```


### Starten
Die Überwachung eines Druckauftrags in Echtzeit kann folgendermassen gestartet werden. In diesem Beispiel wird die Webcam mit der Id 0 als Bildquelle verwendet.

```
$ python main.py -w 0 -g "C:\path\to\gocodefile.gcode" -s
```

Um die Überwachung mit einem Video zu testen, kann folgender Befehl ausgeführt werden

```
$ python main.py -v "C:\path\to\video.mp4" -g "C:\path\to\gocodefile.gcode" -s
```

## Running the tests

Explain how to run the automated tests for this system


## Autoren
Manuel Wullschleger & Marc Röthlisberger
