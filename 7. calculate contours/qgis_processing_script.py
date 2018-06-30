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
                       QgsProcessingParameterVectorLayer,
                       QgsProcessingFeedback)
import processing
import traceback


class ExampleProcessingAlgorithm(QgsProcessingAlgorithm):
    # Constants used to refer to parameters and outputs. They will be
    # used when calling the algorithm from another algorithm, or when
    # calling from the QGIS console.

    INPUT = 'INPUT'
    EQUIDISTANCE = 'EQUIDISTANCE'
    CLIP = 'CLIP'
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
            QgsProcessingParameterVectorLayer(
                self.CLIP,
                self.tr('Clip layer'),
                [QgsProcessing.TypeVectorPolygon]
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
        
        input_layer = self.parameterAsVectorLayer(
            parameters,
            self.INPUT,
            context
        )
        
        equidistance = self.parameterAsDouble(
            parameters,
            self.EQUIDISTANCE,
            context
        )
        
        clip_layer = self.parameterAsVectorLayer(
            parameters,
            self.CLIP,
            context
        )
        
        output_directory = self.parameterAsString(
            parameters,
            self.OUTPUT,
            context
        )
        
        #get the count of all needed fields
        count_of_school_fields = self.get_count_of_school_fields(input_layer)
        total = 100.0 / count_of_school_fields if count_of_school_fields > 0 else 0
        
        #init the result map
        result = {}
        
        #iterate over all fields of this layer
        for current, field in enumerate(input_layer.fields()):
            #print(str(current))
            # Stop the algorithm if cancel button has been clicked
            if feedback.isCanceled():
                break
            
            #evaluate the name of the current field
            if field.name().startswith("school_id"):
                #add a filter expression to the current field
                #input_layer.setSubsetString(field.name() + " is not null")
                
                #start the processing
                count_of_contours = self.getNumberOfContours(input_layer, field.name(), equidistance)
                output_linestring = output_directory + '/' + input_layer.name() + '_' + field.name() + '_linestring.geojson'
                output_polygon = output_directory + '/' + input_layer.name() + '_' + field.name() + '_polygon.geojson'
                
                try:
                    #create polygons
                    processing.run("contourplugin:generatecontours",
                                   {'ContourInterval' : equidistance,
                                   'DuplicatePointTolerance': 0.0,
                                   'ContourLevels' : '',
                                   'ContourMethod' : 3,
                                   'ContourType' : 1,
                                   'ExtendOption' : 0,
                                   'InputField' : '"' + field.name() + ' is not null"',
                                   'InputLayer' : input_layer,
                                   'LabelTrimZeros' : False,
                                   'LabelUnits' : 'm',
                                   'MaxContourValue' : None,
                                   'MinContourValue' : None,
                                   'NContour' : None,
                                   'OutputLayer' : output_polygon})
                
                    result.update({'1 - ' + field.name() + ' - polygon': 'ok'})
                except:
                    result.update({'1 - ' + field.name() + ' - polygon': traceback.format_exc()})
                
                try:
                    #create linestrings
                    processing.run("contourplugin:generatecontours",
                                   {'ContourInterval' : equidistance,
                                   'DuplicatePointTolerance': 0.0,
                                   'ContourLevels' : '',
                                   'ContourMethod' : 3,
                                   'ContourType' : 0,
                                   'ExtendOption' : 0,
                                   'InputField' : '"' + field.name() + ' is not null"',
                                   'InputLayer' : input_layer,
                                   'LabelTrimZeros' : False,
                                   'LabelUnits' : 'm',
                                   'MaxContourValue' : None,
                                   'MinContourValue' : None,
                                   'NContour' : None,
                                   'OutputLayer' : output_linestring})
                    
                    result.update({'2 - ' + field.name() + ' - linestring': 'ok'})
                except:
                    result.update({'2 - ' + field.name() + ' - linestring': traceback.format_exc()})
                
                try:
                    #clip the contours
                    general.run('qgis:clip', [output_polygon, clip_layer, output_polygon])
                    general.run('qgis:clip', [output_linestring, clip_layer, output_linestring])
                    
                    result.update({'3 - ' + field.name() + ' - clip': 'ok'})
                
                except:
                    result.update({'3 - ' + field.name() + ' - clip': traceback.format_exc()})
                
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
