# -*- coding: utf-8 -*-

from PyQt5.QtCore import QCoreApplication
from qgis.core import (QgsProcessing,
                       QgsFeatureSink,
                       QgsProcessingParameterString,
                       QgsProcessingParameterFolderDestination,
                       QgsProcessingParameterNumber,
                       QgsProcessingAlgorithm,
                       QgsProject,
                       QgsFieldConstraints,
                       QgsProcessingParameterVectorLayer)
import processing
import traceback, sys


class ExampleProcessingAlgorithm(QgsProcessingAlgorithm):
    # Constants used to refer to parameters and outputs. They will be
    # used when calling the algorithm from another algorithm, or when
    # calling from the QGIS console.

    INPUT = 'INPUT'
    EQUIDISTANCE = 'EQUIDISTANCE'
    OUTPUT = 'OUTPUT'

    def tr(self, string):
        """Returns a translatable string with the self.tr() function."""
        return QCoreApplication.translate('Processing', string)

    def createInstance(self):
        return ExampleProcessingAlgorithm()

    def name(self):
        """Returns the algorithm name, used for identifying the algorithm."""
        return 'contour_batch'

    def displayName(self):
        """Returns the translated algorithm name, which should be used for any user-visible display of the algorithm name."""
        return self.tr('Contour Batch')

    def group(self):
        """Returns the name of the group this algorithm belongs to. """
        return self.tr('Lunis')

    def groupId(self):
        """Returns the unique ID of the group this algorithm belongs to."""
        return 'lunis'

    def initAlgorithm(self, config=None):
        """Here we define the inputs and output of the algorithm, along with some other properties."""
        
        self.addParameter(
            QgsProcessingParameterVectorLayer(
                self.INPUT,
                self.tr('Input layer'),
                [QgsProcessing.TypeVectorPoint]
            )
        )
        
        self.addParameter(
            QgsProcessingParameterNumber(
                self.EQUIDISTANCE,
                self.tr('Equidistance (m)'),
                defaultValue=500,
                minValue=1
            )
        )
    
        self.addParameter(
            QgsProcessingParameterFolderDestination(
                self.OUTPUT,
                self.tr('Output folder'),
            )
        )
        

    def processAlgorithm(self, parameters, context, feedback):
        '''
        Here is where the processing itself takes place.
        '''
        
        source = self.parameterAsVectorLayer(
            parameters,
            self.INPUT,
            context
        )
        
        equidistance = self.parameterAsDouble(
            parameters,
            self.EQUIDISTANCE,
            context
        )
        
        destination = self.parameterAsString(
            parameters,
            self.OUTPUT,
            context
        )
        
        #get the count of all needed fields
        count_of_school_fields = self.get_count_of_school_fields(source)
        total = 100.0 / count_of_school_fields if count_of_school_fields > 0 else 0
        
        #init the result map
        result = {}
        
        #iterate over all fields of this layer
        for current, field in enumerate(source.fields()):
            #print(str(current))
            # Stop the algorithm if cancel button has been clicked
            if feedback.isCanceled():
                break
            
            #evaluate the name of the current field
            if field.name().startswith("school_id"):
                #add a filter expression to the current field
                #source.setSubsetString(field.name() + " is not null")
                
                #start the processing
                try:
                    count_of_contours = self.getNumberOfContours(source, field.name(), equidistance)
                    output = destination + '/' + source.name() + '_' + field.name() + '.geojson'
                    processing.run('contourplugin:generatecontours',
                                    source,                                  #the input layer
                                    field.name(),                            #the field for interpolating points
                                    0.0,                                     #tolerance of duplicate points
                                    2,                                       #contour type
                                    1,                                       #extend option
                                    3,                                       #contour method
                                    count_of_contours,                       #number of contours
                                    equidistance,                            #minimum contour level
                                    count_of_contours * equidistance,       #maximum contour level
                                    equidistance,                            #contour interval
                                    0,                                       #decimal places
                                    False,                                   #remove double zeros behind comma
                                    'm',                                     #label unit
                                    output)                                  #the output path
                                    
                    result.update({field.name() : 'ok'})
                except:
                    result.update({field.name() : traceback.format_exc()})
                
                #remove null filter
                #source.setSubsetString("")
                
                #update progressbar
                feedback.setProgress(int(current * total))
                
        return result
    
    def get_count_of_school_fields(self, layer):
        '''This function iterates over all fields of a given layer and returns the count of fields starting with "school".'''
        count = 0
        for field in layer.fields():
            if field.name().startswith("school"):
                count += 1
        return count

    def getNumberOfContours(self, layer, field_name, equidistance):
        '''This function calculates the count of necessary contours.'''
        field_id = layer.dataProvider().fieldNameIndex(field_name)
        maximum_value = layer.maximumValue(field_id)
        
        number_of_contours = (int) (maximum_value / equidistance)
        
        if (maximum_value % equidistance) != 0:
            number_of_contours = number_of_contours + 1
        
        return number_of_contours
