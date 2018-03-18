import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import os
import csv
import math

## Constants
Z = 2                           # Ordnungszahl des Teilchens
                                #    Da es sich um ein Alpha-Teilchen handelt
n = 4.32 * 10**(25)           # Teilchendichte der bremsenden Materie
# n = 2.55 * 10**(25)           # https://www.wikiwand.com/de/Teilchendichte , 26.02.2018
Z_strich = 14                   # Ordnungszahl der bremsenden Materie
                                #    Z' = 14, es wird näherungsweise von Stickstoff ausgegangen
e = 1.602 * 10**(-19)           # Elementarladung (e = 1, 602 · 10 −19 As)
m_alpha = 6.644 * 10**(-27)     # Masse des stoßenden Teilchens (m_α = 6,644 · 10^−27 kg)
m_e = 9.109 * 10**(-31)         # Elektronenmasse (m_e = 9,109 · 10^−31 kg)
epsilon_0 = 8.854 * 10**(-12)   # Dielektrizitätskonstante (epsilon_0 = 8,854 · 10^−12)

## Variables, EDIT HERE
coinInMillimeter = 28.5
coinInPixel = 292


def loadCSV(file):
    ''' Loads the CSV file and returns a list of lists depending on the number of images.
    '''
    lengths = []
    with open(file, 'r') as csvfile:
        reader = csv.reader(csvfile, delimiter=',')
        next(reader, None)  # skip the headers
        id = -1
        for row in reader:
            newId = sum([int(s) for s in row[0].split('+') if s.isdigit()])
            if newId != id:
                lengths.append([])
                id = newId
            lengths[-1].append(float(row[1]))
    return lengths

def removePicturesWithTooManyLines(lengths, maxNumberOfLines):
    ''' Removes all entries with too many lines.
        The lines are probably wrong, because the program is not yet fully developed.
    '''
    toRemove = []
    for id, length in enumerate(lengths):
        if len(length) > maxNumberOfLines:
            toRemove.append(id)

    for i in reversed(toRemove):
        del(lengths[i])
    return lengths

def pixelToMillimeter(length):
    return coinInMillimeter * length / coinInPixel

def geiger(length):
    ''' Returns the energy of the rays calculated according to Geiger.
    '''
    return (length/3.1)**(2/3)

def betheBloch(length):
    ''' Returns the energy of the rays calculated according to Bethe-Bloch.
    '''
    return math.sqrt(Z**2 * n * Z_strich * e**4 * m_alpha / 4 / math.pi / epsilon_0**2 / m_e * length * 10**(-3)) / e /10**6


if __name__ == '__main__':
    ## Load the important line lengths from the CSV file
    lengths = loadCSV('result.csv')
    lengths = removePicturesWithTooManyLines(lengths, 10)
    lengths = [item for sublist in lengths for item in sublist] # Flattens array

    # Convert length in millimetres
    for i in range(len(lengths)):
        lengths[i] = pixelToMillimeter(lengths[i])


    # Calculate the energy from the lengths
    energy_geiger = []
    energy_bethe = []
    for length in lengths:
        energy_geiger.append(geiger(length))
        energy_bethe.append(betheBloch(length))

    # ## Plot fogstrip length with histogram
    fig = plt.figure(figsize=(15, 10))
    plt.rc('xtick', labelsize=25)
    plt.rc('ytick', labelsize=25)

    plt.hist(lengths, bins=100)
    plt.xlabel(r"Länge [mm]", fontsize=35)
    plt.ylabel(r"Häufigkeit", fontsize=35)
    plt.legend(fontsize=25)

    fig.savefig('../bilder/histogram_laenge_automatic.png', dpi=200)
    #plt.show()

    ## Plot energy calculated according to Bethe-Bloch in a histogram
    fig = plt.figure(figsize=(15, 10))
    plt.rc('xtick', labelsize=25)
    plt.rc('ytick', labelsize=25)

    plt.hist(energy_bethe, bins=100)
    line1, = plt.plot((6.28808, 6.288081), (0, 12), '-', label=r"Literaturwert $\alpha$ - Energie von $^{220}_{86}Rn$")
    line2, = plt.plot((6.7783, 6.7783), (0, 12), '-', label=r"Literaturwert $\alpha$ - Energie von $^{216}_{84}Po$")
    plt.xlabel(r"Energie [MeV]", fontsize=35)
    plt.ylabel(r"Häufigkeit", fontsize=35)
    plt.legend(fontsize=25)

    fig.savefig('../bilder/histogram_bethebloch_automatic.png', dpi=200)
    #plt.show()

    ## Plot energy calculated according to Geiger in a histogram
    fig = plt.figure(figsize=(15, 10))
    plt.rc('xtick', labelsize=25)
    plt.rc('ytick', labelsize=25)

    plt.hist(energy_geiger, bins=100)
    line1, = plt.plot((6.28808, 6.288081), (0, 12), '-', label=r"Literaturwert $\alpha$ - Energie von $^{220}_{86}Rn$")
    line2, = plt.plot((6.7783, 6.7783), (0, 12), '-', label=r"Literaturwert $\alpha$ - Energie von $^{216}_{84}Po$")
    plt.xlabel(r"Energie [MeV]", fontsize=35)
    plt.ylabel(r"Häufigkeit", fontsize=35)
    plt.legend(fontsize=25)

    fig.savefig('../bilder/histogram_geiger_automatic.png', dpi=200)
    #plt.show()
