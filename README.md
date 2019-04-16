# Cloud chamber
Cloud chamber is a program for the automatic evaluation of a cloud chamber experiment.

## How does it work?
The program only accepts images and processes them in the following steps.
1. Align images to the background image
2. Remove the backgrounds in the images
3. Detect lines in the images
4. Filter duplicate lines
5. Plot the results

![Results](/example_data/Nebelkammer_000_result.jpg?raw=true)

## How do I use it?
Install Python (a programming language) to run the program. How to install Python can be found here: [WikiHow](https://de.wikihow.com/Python-installieren)

Install required libraries
```
pip install numpy matplotlib opencv-python imreg_dft imageio pandas argparse
```

To execute the complete program:
```bash
python cloudchamber example_data/*
```
Since aligning the images takes a very long time, you can also execute the individual parts of the program individually.
Check the help for more information.
```bash
python cloudchamber -h
```
Since the program removes the background, an image without fog strips must be packed into the background folder.
To better remove background artifacts, the artifacts in the background image should be made white. 
As in the example background_with_stripes.jpg
