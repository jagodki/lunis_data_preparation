from qgis import *
import processing
import time, sys

#define the name of the input layer and the absolute path
#of the output directory
input_layer = "edge_data_chainage"
output_directory = "/Users/Christoph/Desktop"
equidistance = 500

def get_searched_layer(layer_list, searched_layer):
    '''This function searches through all loaded layers using their names.'''
    for name, layer in layer_list.items():
        if name.startswith(searched_layer):
            return layer

def get_count_of_school_fields(layer):
    '''This function iterates over all fields of a given layer and returns the count of fields starting with "school".'''
    count = 0
    for field in layer.fields():
        if field.name().startswith("school"):
            count += 1
    return count

def printProgressBar(iteration, total, prefix = '', suffix = '', decimals = 1, length = 100, fill = '█'):
    '''
        Call in a loop to create terminal progress bar
        @params:
        iteration   - Required  : current iteration (Int)
        total       - Required  : total iterations (Int)
        prefix      - Optional  : prefix string (Str)
        suffix      - Optional  : suffix string (Str)
        decimals    - Optional  : positive number of decimals in percent complete (Int)
        length      - Optional  : character length of bar (Int)
        fill        - Optional  : bar fill character (Str)
        '''
    percent = ("{0:." + str(decimals) + "f}").format(100 * (iteration / float(total)))
    filledLength = int(length * iteration / total)
    bar = fill * filledLength + '-' * (length - filledLength)
    print('\r%s |%s| %s%% %s' % (prefix, bar, percent, suffix), end = '\r')
    # Print New Line on Complete
    if iteration == total:
        print()

def add_null_filter(layer, field_name):
    layer.setSubsetString(field_name + " is not null")

def remove_null_filter(layer):
    layer.setSubsetString("")

def create_parameters(layer, field_name):
    #get the highest value in the given field
    field_id = layer.dataProvider().fieldNameIndex(field_name)
    maximum_value = layer.maximumValue(field_id)
    
    #calculate the count of needed contours depending of the equidistance
    count_of_contours = (int) (maximum_value / equidistance)
    if (maximum_value % equidistance) != 0:
        count_of_contours = count_of_contours + 1
    return 1

#get the searched vector layer
vector_layer = get_searched_layer(QgsProject.instance().mapLayers(), input_layer)

#get the count of all needed fields
total_iterations = get_count_of_school_fields(vector_layer)

#iterate over all fields of this layer
i = 0
printProgressBar(i, total_iterations, prefix = 'Progress:', suffix = 'Complete', length = 50)
for field in vector_layer.fields():
    if field.name().startswith("school"):
        
        #add a filter expression to the current field
        add_null_filter(vector_layer, field.name())
        
        #start the processing
        parameters = create_parameters(vector_layer, field.name())
        try:
            processing.run('Contour:contour', parameters)
        except:
            print("Cannot process field " + field.name())
        
        #remove null filter
        remove_null_filter(vector_layer)
        
        #update progressbar
        printProgressBar(i + 1, total_iterations, prefix = 'Progress:', suffix = 'Complete', length = 50)
        i = i + 1
