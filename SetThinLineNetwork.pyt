# -*- coding: utf-8 -*-

import arcpy

# always has one of Toolbox(object), do not change the name
class Toolbox(object):
    def __init__(self):
        """Define the toolbox (the name of the toolbox is the name of the
        .pyt file)."""
        self.label = "Toolbox"
        self.alias = "toolbox"

        # List of tool classes associated with this toolbox
        self.tools = [SetThinLineNetwork]

# Script implementation 
class SetThinLineNetwork(object):
    def __init__(self):
        """Define the tool (tool name is the name of the class)."""
        self.label = "Set Thin Line Network"
        self.description = ""
        self.canRunInBackground = False

    def getParameterInfo(self):
        """Define parameter definitions"""
        # User selects inputs road feature
        in_feature = arcpy.Parameter(
            displayName = 'Road Feature Class',
            name = 'in_feature',
            datatype = "GPString",
            parameterType = 'Required',
            direction = 'Input')
        # a list of feature classes in alphabetical order
        in_feature.filter.list = sorted(row for row in arcpy.ListFeatureClasses())
        
        # User selects fields in desired hierarchy order
        in_field = arcpy.Parameter(
            displayName = 'Field Hierarchy',
            name = "in_field",
            datatype = "Field",
            parameterType = "Required",
            direction = "Input"
        )
        
        in_field.parameterDependencies = [in_feature.name]
        
        field_values = arcpy.Parameter(
            displayName = 'Unique Field Values for Hierarchy',
            name = "field_values",
            datatype = "GPString",
            parameterType = "Required",
            direction = "Input",
            multiValue = True
        )
        
        min_length = arcpy.Parameter(
            displayName = 'Minimal Road Segment Length (Meters)',
            name = "min_length",
            datatype = "GPDouble",
            parameterType = "Required",
            direction = "Input"
        )
        params = [in_feature, in_field, field_values, min_length]
        return params
        

    def isLicensed(self):
        """Set whether tool is licensed to execute."""
        return True

    def updateParameters(self, parameters):
        """Modify the values and properties of parameters before internal
        validation is performed.  This method is called whenever a parameter
        has been changed."""
        # Matches field names to given feature class, sorts in alphabetical order
        if parameters[0].altered:
            fields = arcpy.ListFields(parameters[0].valueAsText)
            parameters[1].filter.list = sorted(field.name for field in fields)
            
        return

    def updateMessages(self, parameters):
        """Modify the messages created by internal validation for each tool
        parameter.  This method is called after internal validation."""
        return
    
    # actual implemention 
    def execute(self, parameters, messages):
        """The source code of the tool."""
        arcpy.env.overwriteOutput = True
        
        # targetFeature = chosen feature class
        # hierarchy_order = contains user chosen order
        # outFeature = destination path and name
        targetFeature = parameters[0].valueAsText
        outFeature = arcpy.env.workspace + targetFeature + "_Roads_Thinned"
        
        # target fields
        invis = "Invisibility"
        hierarchy = "Hierarchy"
        
        # if file does not exist then create it
        if not arcpy.Exists(outFeature):
            arcpy.conversion.ExportFeatures(targetFeature, outFeature) 
        # else overwrite
        else:
            # check if the fields exist, write in if not
            targetFields = [field.name for field in arcpy.ListFields(outFeature)]
            if invis not in targetFields:
                arcpy.AddField_management(outFeature, invis, "LONG")
            if hierarchy not in targetFields:
                arcpy.AddField_managment(outFeature, hierarchy, "LONG")
         
        # manually written hierarchy
        hierarchy_order = parameters[2].valueAsText.split(';')
        # if not empty
        if hierarchy_order:
            # each field_name is paired with unique integer
            fclass_mapping = {field_name: order + 1 for order, field_name in enumerate(hierarchy_order)}
            default_value = len(hierarchy_order) + 1
        else:
            # follow Kami's default
            fclass_mapping = { 1:1, 3:2, 4:3, 5:4, 2:4, } 
            default_value = 5
        # update outFeature hierarchy field using user selected field  (parameters[1].valueAsText) as qualifier
        with arcpy.da.UpdateCursor(outFeature, [parameters[1].valueAsText, hierarchy]) as cursor:
            for row in cursor:
                road_type = row[0]
                order = fclass_mapping.get(road_type, default_value) # if road_type matches, find ordered pair
                row[1] = order    
                cursor.updateRow(row)
                
        arcpy.ThinRoadNetwork_cartography(outFeature, parameters[3], invis, hierarchy)    
        
        outDesc = arcpy.Describe(outFeature)
        wkt = outDesc.spatialReference
        wkt = wkt.exportToString()
        outExtent = outDesc.extent
        outExtent = f"{outExtent.XMin} {outExtent.YMin} {outExtent.XMax} {outExtent.YMax} {wkt}"
        outFeatureDisolved = outFeature + "_Dissolved" 
        
        
        with arcpy.EnvManager(extent = outExtent, outputCoordinateSystem = wkt, workspace = arcpy.env.workspace):
            arcpy.analysis.PairwiseDissolve(in_feature = outFeature, 
                                            out_feature_class = outFeatureDisolved,
                                            multi_part = "SINGLE_PART")
        inTable = ""
        arcpy.analysis.SpatialJoin(target_feature = outFeatureDisolved,
                                    join_feature = outFeatureDisolved,
                                    out_feature_class = inTable, 
                                    join_operation = "JOIN_ONE_TO_MANY",
                                    match_option = "OBJECTID")
        outTable = ""
        arcpy.analysis.Statistics(in_table = inTable, out_table = outTable, 
                                  statistics_field = [["JOIN_FID", "COUNT"]], case_field = ["TARGET_FID"])
        
        dissolved_roads = arcpy.management.JoinField(in_data = outFeatureDisolved,
                                                     in_field = "OBJECTID", 
                                                     join_table = outTable,
                                                     join_field = "OBJECTID",
                                                     fields = ["COUNT_JOIN_FID"])[0]
        
        arcpy.management.SelectLayerByAttribute(in_layer_or_view = dissolved_roads,
                                                        where_clause = "COUNT_JOIN_FID = 1")
        arcpy.management.DeleteFeatures(in_features = dissolved_roads)
                     
        return

    def postExecute(self, parameters):
        """This method takes place after outputs are processed and
        added to the display."""
        return
