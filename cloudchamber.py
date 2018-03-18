import numpy as np
import matplotlib.pyplot as plt
import cv2
import imreg_dft as ird
import imageio # Newer than 2.2.0 must be used to use pilmode e.g. pip install git+https://github.com/imageio/imageio.git
from multiprocessing import Pool

import os
import pandas
import time
from argparse import ArgumentParser
import sys

import util  # Selfmade library

# Source: https://stackoverflow.com/questions/2507808/python-check-whether-a-file-is-empty-or-not?noredirect=1&lq=1
def is_zero_file(fpath):
    '''Checks if a file does not exist or is empty.'''
    return not(os.path.isfile(fpath) and os.path.getsize(fpath) > 0)

def plot_result_images(images):
    def plot_result_image(image, lines_unfiltered, lines_filtered):
        file, ending = os.path.splitext(image)

        fig, axes = plt.subplots(nrows=2, ncols=2)

        axes[0][0].imshow(imageio.imread(file + ending, pilmode='L'), cmap='gist_gray')
        axes[0][0].set_title('Image to be analyzed')
        axes[0][0].axis('off')

        axes[0][1].imshow(imageio.imread(file + '_wo_bkgnd' + ending, pilmode='L'), cmap='gist_gray')
        axes[0][1].set_title('Removed backround')
        axes[0][1].axis('off')

        axes[1][0].imshow(imageio.imread(file + '_unfiltered_lines' + ending, pilmode='L'), cmap='gist_gray')
        axes[1][0].set_title('Detected ' + lines_unfiltered + ' lines before filtering')
        axes[1][0].axis('off')

        axes[1][1].imshow(imageio.imread(file + '_filtered_lines' + ending, pilmode='L'), cmap='gist_gray')
        axes[1][1].set_title('Detected ' + lines_filtered + ' lines after filtering')
        axes[1][1].axis('off')

        print('.', end='', flush=True)
        file, ending = os.path.splitext(image)
        plt.savefig(
            file + '_result' + ending,
            dpi=400,
            bbox_inches='tight',
            pad_inches=0,
            transparent="True",)

    df_unfiltered = pandas.read_csv('lines_unfiltered.csv')
    df_filtered = pandas.read_csv('lines_filtered.csv')

    filenames_unfiltered = set(df_unfiltered.filename)
    filenames_filtered = set(df_filtered.filename)
    for image in images:

        df_filename_unfiltered = df_unfiltered[df_unfiltered.filename == image]
        df_filename_filtered = df_filtered[df_filtered.filename == image]

        plot_result_image(image, str(len(df_filename_unfiltered)), str(len(df_filename_filtered)))

# Install pyfftw for better performance.
def align_images(images):
    def align_image(path_analyse, img_background):
        print('Image alignment:', path_analyse, end='', flush=True)
        start = time.time()

        # Load analyse image
        img_analyse = imageio.imread(path_analyse, pilmode='L')

        # Align img_analyse to img_background
        # It has to be Homography transformation(very slow), because images are shifted, twisted, scaled and distorted (3D)
        # First tried to use opencv (https://www.learnopencv.com/image-alignment-ecc-in-opencv-c-python/), but got miserable results
        # Found on github https://github.com/matejak/imreg_dft a pretty good library
        #img_analyse_aligned = ird.similarity(img_background, img_analyse, numiter=3)['timg']
        img_analyse_aligned = img_analyse # TODO: Remove, fast variant for testing

        end = time.time()
        print(', %.1fs' % (end - start))
        return img_analyse_aligned

    # Start here
    img_background = imageio.imread(os.path.join('background', 'background.jpg'), pilmode='L')
    # ‘L’ (8-bit pixels, black and white)

    for path_analyse in images:
        img_aligned = align_image(path_analyse, img_background)

        file, ending = os.path.splitext(path_analyse)
        imageio.imsave(file + '_align' + ending, img_aligned, format='jpg')

    # Use multithreader, number in Pool defines number of processes
    # with Pool(1) as p:
    #     p.map(align_image, images)

def remove_backgrounds(images):
    def remove_background(img_analyse, img_background):
        print('Background removal:', path_analyse, end='', flush=True)
        start = time.time()

        # Convert images to int16 to allow negative values so that the negative values (background) can be filtered.
        img_analyse = np.int16(img_analyse) - np.int16(img_background) * 2
        for x, y in zip(np.where(img_analyse < 5)[0], np.where(img_analyse < 5)[1]):
            img_analyse[x, y] = 0

        end = time.time()
        print(', %.1fs' % (end - start))
        return np.uint8(img_analyse)

    images = {x.replace('.', '_align.') for x in images}

    img_background = imageio.imread(os.path.join('background', 'background_with_stripes.jpg'), pilmode='L')
    # ‘L’ (8-bit pixels, black and white)

    for path_analyse in images:
        img_analyse = imageio.imread(path_analyse, format='JPEG-PIL', pilmode='L')
        img_analyse_wo_bkgnd = remove_background(img_analyse, img_background)

        file, ending = os.path.splitext(path_analyse)
        imageio.imsave(file[:-6] + '_wo_bkgnd' + ending, img_analyse_wo_bkgnd, format='jpg')

def detect_lines(images):
    def detect_line(path_analyse, img_analyse):
        print('Line detection:', path_analyse, end='', flush=True)
        start = time.time()

        # Followed code example on https://stackoverflow.com/questions/39752235/python-how-to-detect-vertical-and-horizontal-lines-in-an-image-with-houghlines-w
        # Canny makes edges visible in the image
        edges = cv2.Canny(image=img_analyse, threshold1=20, threshold2=40)
        # Houghlines detects lines in the image
        lines = cv2.HoughLinesP(edges, rho=1, theta=np.pi / 180, threshold=10, minLineLength=150, maxLineGap=80)

        if lines is None:
            return []

        lines = lines.reshape(len(lines), 4).tolist()

        end = time.time()
        print(', %.1fs' % (end - start))
        return util.createLinesWithClass(lines, path_analyse.replace('_wo_bkgnd', ''))

    # Start here
    images = {x.replace('.', '_wo_bkgnd.') for x in images}

    if is_zero_file('lines_unfiltered.csv'):
        with open('lines_unfiltered.csv', 'a') as file_results:
            file_results.write('angle,filename,length,p1_x,p1_y,p2_x,p2_y\n')

    already_analysed = list(set(pandas.read_csv('lines_unfiltered.csv').filename))
    images_wo_duplicates = [x for x in images if x not in already_analysed]

    for path_analyse in images_wo_duplicates:
        img_analyse = imageio.imread(path_analyse, pilmode='L')
        lines = detect_line(path_analyse, img_analyse)
        util.linesToDataFrame(lines).to_csv('lines_unfiltered.csv', mode='a', header=False, index=False)

        img_analyse_lines = util.colorImageWithLines(lines, img_analyse)
        file, ending = os.path.splitext(path_analyse)
        imageio.imsave(file[:-9] + '_unfiltered_lines' + ending, img_analyse_lines, format='jpg')


def filter_lines(images):
    if is_zero_file('lines_unfiltered.csv'):
        print('The file lines_unfiltered.csv is empty. \nCall only_filter after only_detect.')
        return

    with open('lines_filtered.csv', 'w') as file_results:
        file_results.write('angle,filename,length,p1_x,p1_y,p2_x,p2_y\n')

    df_unfiltered = pandas.read_csv('lines_unfiltered.csv')

    filenames = set(df_unfiltered.filename)

    for filename in filenames:
        print('Line filtering:', filename, end='', flush=True)
        start = time.time()

        df_filename = df_unfiltered[df_unfiltered.filename == filename]

        lines_filename = []
        for _, data in df_filename.iterrows():
            lines_filename.append(util.Line(int(data.p1_x), int(data.p1_y), int(data.p2_x), int(data.p2_y), data.filename))

        lines_filtered = util.filterLines(lines_filename) # Maybe work directly in the dataframe from panda

        util.linesToDataFrame(lines_filtered).to_csv('lines_filtered.csv', mode='a', header=False, index=False)
        end = time.time()
        print(', %.1fs' % (end - start))

        file, ending = os.path.splitext(filename)
        img_analyse = imageio.imread(file + '_wo_bkgnd' + ending, pilmode='L')
        img_analyse_lines = util.colorImageWithLines(lines_filtered, img_analyse)

        imageio.imsave(file + '_filtered_lines' + ending, img_analyse_lines, format='jpg')

def complete(images):
    align_images(images)
    remove_backgrounds(images)
    detect_lines(images)
    filter_lines(images)
    plot_result_images(images)

def main():
    parser = ArgumentParser(prog="Cloudchamber", description="Automatic line detection for the cloud chamber")
    group = parser.add_mutually_exclusive_group()
    group.add_argument('-c', '--complete', action='store_const', dest='type', help='execute the complete program, be careful, takes time', const=complete)
    group.add_argument('-a', '--only_align', action='store_const', dest='type', help='align images to the background image', const=align_images)
    group.add_argument('-b', '--only_back', action='store_const', dest='type', help='remove the backgrounds in the images', const=remove_backgrounds)
    group.add_argument('-d', '--only_detect', action='store_const', dest='type', help='detect lines in the images', const=detect_lines)
    group.add_argument('-f', '--only_filter', action='store_const', dest='type', help='filter duplicate lines.', const=filter_lines)
    group.add_argument('-p', '--only_plot', action='store_const', dest='type', help='plot the results.', const=plot_result_images)
    parser.add_argument('-v', '--version', action='version', version='%(prog)s 1.0')
    parser.add_argument('images', metavar='images', type=str, nargs='+', help='images to be analysed')
    parser.set_defaults(type=complete)

    args = parser.parse_args()

    # Call function depending on cli argument
    images = {x.replace('_align', '').replace('_wo_bkgnd', '').replace('_unfiltered_lines', '').replace('_filtered_lines', '').replace('_result', '')  for x in args.images}
    args.type(sorted(images))

if __name__ == "__main__":
    main()
