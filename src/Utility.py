import pickle
import os

from tkinter.filedialog import askopenfilename

def loadData(parent=None, filename=None):
    def _loadData(filename):
        with open(filename, 'rb') as filehandle:
                return pickle.load(filehandle)

    if filename == None:
        # Opens a UI dialogue window to select a file to
        filename = askopenfilename()
    else:
        if parent == None:
            filename = os.getcwd()+'\\'+filename
        else:
            filename = os.getcwd()+'\\'+parent+'\\'+filename
    try:
       return _loadData(filename)
    except:
        print("Load Error")
        return []

def writeToFile(filename, ext, data):
    with open(filename + '.' + ext, 'wb') as filehandle:
        pickle.dump(data, filehandle)
