from qgis import *
import processing
import time, sys

#define the name of the input layer and the absolute path
#of the output directory
input_layer = ""
output_directory = ""

def get_searched_layer(layer_list, searched_layer):
    '''This function searches through all loaded layers using their names.'''
    for layer in layer_list:
        if layer.name() == searched_layer:
            return layer

def get_count_of_school_fields(layer):
    '''This function iterates over all fields of a given layer and returns the count of fields starting with "school".'''
    count = 0
    for field in layer.fields():
        if field.name() == "school*":
            count += 1
    return count

def printProgressBar(iteration, total, prefix = '', suffix = '', decimals = 1, length = 100, fill = '█'):
    """
        Call in a loop to create terminal progress bar
        @params:
        iteration   - Required  : current iteration (Int)
        total       - Required  : total iterations (Int)
        prefix      - Optional  : prefix string (Str)
        suffix      - Optional  : suffix string (Str)
        decimals    - Optional  : positive number of decimals in percent complete (Int)
        length      - Optional  : character length of bar (Int)
        fill        - Optional  : bar fill character (Str)
        """
    percent = ("{0:." + str(decimals) + "f}").format(100 * (iteration / float(total)))
    filledLength = int(length * iteration // total)
    bar = fill * filledLength + '-' * (length - filledLength)
    print('\r%s |%s| %s%% %s' % (prefix, bar, percent, suffix), end = '\r')
    # Print New Line on Complete
    if iteration == total:
        print()

def add_null_filter(layer):
    return 1

def remove_null_filter():
    return 1

def create_parameters():
    return 1

#get the searched vector layer
vector_layer = get_searched_layer(QgsProject.instance().mapLayers(), input_layer)

#get the count of all needed fields
total_iterations = get_count_of_school_fields(vector_layer)

#iterate over all fields of this layer
i = 0
printProgressBar(i, total_iterations, prefix = 'Progress:', suffix = 'Complete', length = 50)
for field in vector_layer.fields():
    if field.name() == "school*":
        
        #add a filter expression to the current field
        add_null_filter(vector_layer)

        #start the processing
        parameters = create_parameters()
        processing.run('Contour:contour', parameters)

        #update progressbar
        printProgressBar(i + 1, total_iterations, prefix = 'Progress:', suffix = 'Complete', length = 50)
        i = i + 1

