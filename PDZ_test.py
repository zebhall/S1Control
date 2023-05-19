import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import struct


def readPDZ25(fileName, start, size):
    with open(fileName, "rb") as file:
        file.seek(start)
        buffer = file.read(size * 4)  # Assuming each value is a 32-bit integer (4 bytes)
    
    # Unpack the binary buffer into an array of integers
    integers = np.frombuffer(buffer, dtype=np.uint32)
    
    return integers.tolist()

def readPDZ24(fileName, start, size):
    with open(fileName, "rb") as file:
        file.seek(start)
        buffer = file.read(size * 4)  # Assuming each value is a 32-bit integer (4 bytes)
    
    # Unpack the binary buffer into an array of integers
    integers = np.frombuffer(buffer, dtype=np.uint32)
    
    return integers.tolist()

def readPDZ25Data(filepath, filename):
    filename = filename.replace(".pdz", "")
    filename_vector = [filename] * 2020
    
    nbrOfRecords = 2020
    integers = readPDZ25(filepath, 481, nbrOfRecords)
    print(integers)
    
    sequence = list(range(1, len(integers)+1))
    
    time_est = integers[20]
    
    channels = sequence
    energy = [x * 0.02 for x in sequence]
    counts = [x / (integers[20] / 10) for x in integers]
    
    return pd.DataFrame({'Energy': energy, 'CPS': counts, 'Spectrum': filename_vector})

def readPDZ24Data(filepath, filename):
    filename = filename.replace(".pdz", "")
    filename_vector = [filename] * 2020
    
    nbrOfRecords = 2020
    integers = readPDZ24(filepath, start=357, size=nbrOfRecords)
    
    sequence = list(range(1, len(integers)+1))
    
    time_est = integers[20]
    
    channels = sequence
    energy = [x * 0.02 for x in sequence]
    counts = [x / (integers[20] / 10) for x in integers]
    
    return pd.DataFrame({'Energy': energy, 'CPS': counts, 'Spectrum': filename_vector})



def plotPDZ(data):
    plt.plot(data['Energy'], data['CPS'])
    plt.xlabel('Energy')
    plt.ylabel('CPS')
    plt.title('Spectrum Plot')
    plt.grid(True)
    plt.show()



data = readPDZ25Data("test.pdz", "test2")
print(data)
plotPDZ(data)
