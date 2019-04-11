# -*- coding: utf-8 -*-

from PyQt5.QtCore import QCoreApplication, QDir
from qgis.core import (QgsProcessing,
                       QgsFeatureSink,
                       QgsProcessingParameterString,
                       QgsProcessingParameterFolderDestination,
                       QgsProcessingParameterNumber,
                       QgsProcessingAlgorithm,
                       QgsProject,
                       QgsFieldConstraints,
                       QgsProcessingParameterVectorLayer,
                       QgsProcessingFeedback,
                       QgsCoordinateReferenceSystem)
import processing
import traceback
import os

class ExampleProcessingAlgorithm(QgsProcessingAlgorithm):
    # Constants used to refer to parameters and outputs. They will be
    # used when calling the algorithm from another algorithm, or when
    # calling from the QGIS console.

    CHAINAGE = 'CHAINAGE'
    EQUIDISTANCE = 'EQUIDISTANCE'
    OUTPUT = 'OUTPUT'
    DATABASE = 'DATABASE'

    def tr(self, string):
        '''Returns a translatable string with the self.tr() function.'''
        return QCoreApplication.translate('Processing', string)

    def createInstance(self):
        return ExampleProcessingAlgorithm()

    def name(self):
        '''Returns the algorithm name, used for identifying the algorithm.'''
        return 'contour_batch'

    def displayName(self):
        '''Returns the translated algorithm name, which should be used for any user-visible display of the algorithm name.'''
        return self.tr('Grid preparation')

    def group(self):
        '''Returns the name of the group this algorithm belongs to. '''
        return self.tr('Lunis')

    def groupId(self):
        '''Returns the unique ID of the group this algorithm belongs to.'''
        return 'lunis'

    def initAlgorithm(self, config=None):
        '''Here we define the inputs and output of the algorithm, along with some other properties.'''
        
        self.addParameter(
            QgsProcessingParameterVectorLayer(
                self.CHAINAGE,
                self.tr('Chainaged Network layer (used for filled contours)'),
                [QgsProcessing.TypeVectorPoint]
            )
        )
        
        self.addParameter(
            QgsProcessingParameterNumber(
                self.EQUIDISTANCE,
                self.tr('Equidistance of Contour Lines (m)'),
                defaultValue=500,
                minValue=1
            )
        )
        
        self.addParameter(
            QgsProcessingParameterFolderDestination(
                self.OUTPUT,
                self.tr('Output folder for temporary files'),
            )
        )
        
        self.addParameter(
            QgsProcessingParameterString(
                self.DATABASE,
                self.tr('Database name'),
            )
        )
        

    def processAlgorithm(self, parameters, context, feedback):
        '''
        Here is where the processing itself takes place.
        '''
        
        chainage_layer = self.parameterAsVectorLayer(
            parameters,
            self.CHAINAGE,
            context
        )
        
        equidistance = self.parameterAsDouble(
            parameters,
            self.EQUIDISTANCE,
            context
        )
        
        output_directory = self.parameterAsString(
            parameters,
            self.OUTPUT,
            context
        )
        
        database = self.parameterAsString(
            parameters,
            self.DATABASE,
            context
        )
        
        #get the count of all needed fields
        count_of_school_fields = self.get_count_of_school_fields(chainage_layer)
        total = 100.0 / count_of_school_fields if count_of_school_fields > 0 else 0
        feedback.setProgress(0)
        
        #init the result map
        result = {}
        
        #init parts of the different file names
        prefix_contour = 'contour_'
        prefix_clip = 'clip_'
        prefix_points = 'regular_points'
        prefix_points_joined = 'points_joined_'
        prefix_grid_joined = 'grid_joined_'
        suffix_polygon = '_polygon.geojson'
        suffix_linestring = '_linestring.geojson'
        suffix_file_format = '.geojson'
        
        #iterate over all fields of this layer
        for current, field in enumerate(chainage_layer.fields()):
            #print(str(current))
            # Stop the algorithm if cancel button has been clicked
            if feedback.isCanceled():
                break
            
            #evaluate the name of the current field
            if field.name().startswith("school_id"):
                #add a filter expression to the current field
                chainage_layer.setSubsetString(field.name() + " is not null")
                
                #start the processing
                count_of_contours = self.getNumberOfContours(chainage_layer, field.name(), equidistance)
                
                try:
                    #create polygons
                    processing.run('contourplugin:generatecontours',
                                   {'ContourInterval' : equidistance,
                                    'DuplicatePointTolerance': 0.0,
                                    'ContourLevels' : '',
                                    'ContourMethod' : 3,
                                    'ContourType' : 1,
                                    'ExtendOption' : 0,
                                    'InputField' : field.name(),
                                    'InputLayer' : chainage_layer,
                                    'LabelTrimZeros' : False,
                                    'LabelDecimalPlaces' : 0,
                                    'LabelUnits' : 'm',
                                    'MaxContourValue' : None,
                                    'MinContourValue' : None,
                                    'NContour' : 1000000,
                                    'OutputLayer' : QDir.toNativeSeparators(output_directory + '/' + prefix_contour + field.name() + suffix_polygon)})
                
                    result.update({'1 - ' + field.name() + ' - filled contours': 'ok'})
                except:
                    result.update({'1 - ' + field.name() + ' - filled contours': traceback.format_exc()})
                
                #import the new file/layer into a PostgreSQL-DB
                try:
                    #create polygons
                    processing.run('qgis:importintopostgis',
                                   {'INPUT' : QDir.toNativeSeparators(output_directory + '/' + prefix_contour + field.name() + suffix_polygon),
                                    'DATABASE': database,
                                    'SCHEMA' : 'grid_preparation',
                                    'TABLENAME' : 'filled_contours',
                                    'PRIMARY_KEY' : 'id',
                                    'GEOMETRY_COLUMN' : 'geom',
                                    'ENCODING' : 'UTF-8',
                                    'OVERWRITE' : True,
                                    'CREATEINDEX' : True,
                                    'LOWERCASE_NAMES' : True,
                                    'DROP_STRING_LENGTH' : True,
                                    'FORCE_SINGLEPART' : True})
                
                    result.update({'2 - ' + field.name() + ' - database import': 'ok'})
                except:
                    result.update({'2 - ' + field.name() + ' - database import': traceback.format_exc()})
                
                #calculate new grid values
                try:
                    sql = ("ALTER TABLE grid_preparation.grid \n" +
                           "ADD COLUMN \"" + field.name() + "\" DOUBLE PRECISION; \n" + 
                           "WITH regular_points_with_values AS ( \n" + 
                           "SELECT a.id, ((b." + field.name() + "_max + b." + field.name() + "_min) / 2) AS distance_value, a.geom \n" + 
                           "FROM grid_preparation.regular_points a, grid_preparation.filled_contours b \n" +
                           "WHERE st_intersects(a.geom, b.geom)), \n" +
                           "grid_with_null_values AS ( \n" +
                           "SELECT a.id, avg(b.distance_value) AS distance_value \n" +
                           "FROM grid_preparation.grid a \n" +
                           "LEFT JOIN regular_points_with_values b \n" +
                           "ON st_intersects(a.geom, b.geom) \n" +
                           "GROUP BY a.id) \n" +
                           "UPDATE grid_preparation.grid a \n" +
                           "SET " + field.name() + " = b.distance_value \n" +
                           "FROM grid_with_null_values b \n" +
                           "WHERE a.id = b.id; \n" +
                           "UPDATE grid_preparation.grid \n" +
                           "SET " + field.name() + " = -99 \n" +
                           "WHERE " + field.name() + " IS NULL;")
                    
                    print(sql)
                    print(database)
                    
                    processing.run('qgis:postgisexecutesql',
                                   {'DATABASE' : database,
                                    'SQL' : sql})
                
                    result.update({'3 - ' + field.name() + ' - SQL to calculate grid values': 'ok'})
                except:
                    result.update({'3 - ' + field.name() + ' - SQL to calculate grid values': traceback.format_exc()})
                
                #remove the filter expression of the current field
                chainage_layer.setSubsetString("")
                
                #update progressbar
                feedback.setProgress(int(current * total))
                
        #remove all temporary files
        #self.removeTempFiles(output_directory, prefix_contour, suffix_polygon)
        #self.removeTempFiles(output_directory, prefix_points, suffix_file_format)
        
        #load the grid
        
        return result
    
    def get_count_of_school_fields(self, layer):
        '''This function iterates over all fields of a given layer and returns the count of fields starting with *school*.'''
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
    
    def removeTempFiles(self, directory, prefix, suffix):
        '''This function removes all temporary files from the given directory.'''
        for entry in os.listdir(directory):
            absolute_path = QDir.toNativeSeparators(directory + '/' + entry)
            if os.path.isfile(absolute_path):
                if os.path.basename(entry).startswith(prefix) and os.path.basename(entry).endswith(suffix):
                    os.remove(absolute_path)
