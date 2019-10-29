# -*- coding: utf-8 -*-

"""
***************************************************************************
*                                                                         *
*   This program is free software; you can redistribute it and/or modify  *
*   it under the terms of the GNU General Public License as published by  *
*   the Free Software Foundation; either version 2 of the License, or     *
*   (at your option) any later version.                                   *
*                                                                         *
***************************************************************************
"""

from PyQt5.QtCore import QCoreApplication, QVariant
from qgis.core import (QgsProcessing,
                       QgsFeatureSink,
                       QgsProcessingException,
                       QgsProcessingAlgorithm,
                       QgsProcessingParameterFeatureSource,
                       QgsProcessingParameterFeatureSink,
                       QgsField,
                       QgsProcessingParameterField,
                       QgsProcessingParameterVectorLayer)
import processing


class ExampleProcessingAlgorithm(QgsProcessingAlgorithm):
    """
    This is an example algorithm that takes a vector layer and
    creates a new identical one.

    It is meant to be used as an example of how to create your own
    algorithms and explain methods and variables used to do it. An
    algorithm like this will be available in all elements, and there
    is not need for additional work.

    All Processing algorithms should extend the QgsProcessingAlgorithm
    class.
    """

    # Constants used to refer to parameters and outputs. They will be
    # used when calling the algorithm from another algorithm, or when
    # calling from the QGIS console.

    NETWORK = 'NETWORK'
    CHAINAGE = 'CHAINAGE'
    SCHOOLS = 'SCHOOLS'
    SCHOOLS_ID = 'SCHOOLS_ID'

    def tr(self, string):
        """
        Returns a translatable string with the self.tr() function.
        """
        return QCoreApplication.translate('Processing', string)

    def createInstance(self):
        return ExampleProcessingAlgorithm()

    def name(self):
        """
        Returns the algorithm name, used for identifying the algorithm. This
        string should be fixed for the algorithm, and must not be localised.
        The name should be unique within each provider. Names should contain
        lowercase alphanumeric characters only and no spaces or other
        formatting characters.
        """
        return 'distance_calculations'

    def displayName(self):
        """
        Returns the translated algorithm name, which should be used for any
        user-visible display of the algorithm name.
        """
        return self.tr('Distance Calculations')

    def group(self):
        """
        Returns the name of the group this algorithm belongs to. This string
        should be localised.
        """
        return self.tr('Lunis')

    def groupId(self):
        """
        Returns the unique ID of the group this algorithm belongs to. This
        string should be fixed for the algorithm, and must not be localised.
        The group id should be unique within each provider. Group id should
        contain lowercase alphanumeric characters only and no spaces or other
        formatting characters.
        """
        return 'lunis'

    def shortHelpString(self):
        """
        Returns a localised short helper string for the algorithm. This string
        should provide a basic description about what the algorithm does and the
        parameters and outputs associated with it..
        """
        return self.tr("Example algorithm short description")

    def initAlgorithm(self, config=None):
        """
        Here we define the inputs and output of the algorithm, along
        with some other properties.
        """
        
        self.addParameter(
            QgsProcessingParameterVectorLayer(
                self.NETWORK,
                self.tr('Network layer'),
                [QgsProcessing.TypeVectorLine]
            )
        )
        
        self.addParameter(
            QgsProcessingParameterVectorLayer(
                self.CHAINAGE,
                self.tr('Chainaged network layer'),
                [QgsProcessing.TypeVectorPoint]
            )
        )
        
        self.addParameter(
            QgsProcessingParameterVectorLayer(
                self.SCHOOLS,
                self.tr('Schools layer'),
                [QgsProcessing.TypeVectorPoint]
            )
        )
        
        self.addParameter(
            QgsProcessingParameterField(
                self.SCHOOLS_ID,
                self.tr('ID of the schools layer (has to be unique))'),
                parentLayerParameterName=self.SCHOOLS,
                type=QgsProcessingParameterField.Any
            )
        )

    def processAlgorithm(self, parameters, context, feedback):
        """
        Here is where the processing itself takes place.
        """

        network = self.parameterAsVectorLayer(
            parameters,
            self.NETWORK,
            context
        )
        
        chainaged_network = self.parameterAsVectorLayer(
            parameters,
            self.CHAINAGE,
            context
        )
        
        schools = self.parameterAsVectorLayer(
            parameters,
            self.SCHOOLS,
            context
        )
        
        schools_id = self.parameterAsString(
            parameters,
            self.SCHOOLS_ID,
            context
        )

        # If source was not found, throw an exception to indicate that the algorithm
        # encountered a fatal error. The exception text can be any string, but in this
        # case we use the pre-built invalidSourceError method to return a standard
        # helper text for when a source cannot be evaluated
        if network is None:
            raise QgsProcessingException(self.invalidSourceError(parameters, self.NETWORK))
            
        if chainaged_network is None:
            raise QgsProcessingException(self.invalidSourceError(parameters, self.CHAINAGED))
            
        if schools is None:
            raise QgsProcessingException(self.invalidSourceError(parameters, self.SCHOOLS))
            
        if schools_id is None:
            raise QgsProcessingException(self.invalidSourceError(parameters, self.SCHOOLS_ID))

        # Send some information to the user
        feedback.pushInfo('CRS of network is {}'.format(network.sourceCrs().authid()))
        feedback.pushInfo('CRS of chainaged network is {}'.format(chainaged_network.sourceCrs().authid()))
        feedback.pushInfo('CRS of schools is {}'.format(schools.sourceCrs().authid()))

        # Compute the number of steps to display within the progress bar and
        # get features from source
        total = 100.0 / schools.featureCount() if schools.featureCount() else 0
        schools_features = schools.getFeatures()
        
        for current, feature in enumerate(schools_features):
            
            #start the edit mode for the chainaged network
            chainaged_network.startEditing()
            
            # Stop the algorithm if cancel button has been clicked
            if feedback.isCanceled():
                chainaged_network.rollBack()
                break
            
            #find the nearest point on the network for the current school
            nearest_point = self.getNearestPoint(network, feature.geometry())
            
            #create a new field for the current school
            field_name = 'school_id_' + str(feature['id'])
            check = chainaged_network.addAttribute(QgsField(field_name, QVariant.Double))
            chainaged_network.updateFields()
            if check is False:
                feedback.pushInfo('cannot create a new attribute with the name ' + field_name)
                chainaged_network.rollBack()
                break
            
            #create routing to each chainaged point and store the result
            for current_chainage, feature_chainage in enumerate(chainaged_network.getFeatures()):
                #get start and end point
                start = str(nearest_point.asPoint().x()) + ',' + str(nearest_point.asPoint().y())
                end = str(feature_chainage.geometry().asPoint().x()) + ',' + str(feature_chainage.geometry().asPoint().y())
                
                #find shortest path
                distance = processing.run("native:shortestpathpointtopoint", {
                    'INPUT': network,
                    'STRATEGY': 0,
                    'DEFAULT_SPEED': 30,
                    'TOLERANCE': 0.1,
                    'START_POINT': start,
                    'END_POINT': end,
                    'OUTPUT': 'memory:routing'
                })['TRAVEL_COST']
                
                #add the result to the chainage layer
                feature_chainage[field_name] = distance
                chainaged_network.updateFeature(feature_chainage)
                
            # Update the progress bar and commit changes
            feedback.setProgress(int(current * total))
            chainaged_network.commitChanges()
        
        return ''
    
    def getNearestPoint(self, layer, geometry):
        distance = -1
        nearest_point = None
        
        for feature in layer.getFeatures():
            nearest_point_on_feature = feature.geometry().nearestPoint(geometry)
            new_distance = nearest_point_on_feature.distance(geometry)
            
            if new_distance < distance or distance < 0:
                distance = new_distance
                nearest_point = nearest_point_on_feature
            
        return nearest_point
        
