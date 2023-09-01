# -*- coding: utf-8 -*-
"""
Created on Thu Aug 24 09:08:47 2023

@author: Kami Denny
"""
#import modules
import arcpy
arcpy.env.overwriteOutput = True

Workspace = arcpy.GetParameterAsText(0)
RoadsFC = arcpy.GetParameterAsText(1)
field = arcpy.GetParameterAsText(2)

#define field names
invisibility_field = "Invisibility"
hierarchy_field = "Hierarchy"

outfeatures= Workspace + "/exportedRoads"
arcpy.conversion.ExportFeatures(RoadsFC, outfeatures)

#check if fields already exisit and if not create them
if not arcpy.Exists(outfeatures):
    arcpy.AddError(f"Feature class {outfeatures} does not exist.")
else:
    # Check if the fields already exist
    field_list = arcpy.ListFields(outfeatures)
    field_names = [field.name for field in field_list]

    if invisibility_field not in field_names:
        # Create the Invisibility field as a Long integer field
        arcpy.AddField_management(outfeatures, invisibility_field, "LONG")
        arcpy.AddMessage(f"Created field {invisibility_field}.")

    if hierarchy_field not in field_names:
        # Create the Hierarchy field as a Long integer field
        arcpy.AddField_management(outfeatures, hierarchy_field, "LONG")
        arcpy.AddMessage(f"Created field {hierarchy_field}.")

is_OSM_dataset = arcpy.GetParameterAsText(3)
if is_OSM_dataset:
    fclass_mapping = {
        "motorway": 1,
        "primary": 2,
        "secondary": 3,
        "tertiary": 4,
        
    }
    default_value = 5
else:
    fclass_mapping = {
        1: 1,
        3: 2,
        4: 3,
        5: 4,
        2: 4,
    }
    default_value = 5
with arcpy.da.UpdateCursor(outfeatures, [field, hierarchy_field]) as cursor:
    for row in cursor:
        road_type = row[0]
        if isinstance(road_type, str):
            road_type = road_type.lower()
        hierarchy_value = fclass_mapping.get(road_type, default_value)
        row[1] = hierarchy_value
        cursor.updateRow(row)

arcpy.AddMessage("Hierarchy field updated based on fclass attribute.")

partitions = Workspace + "/partitions"
arcpy.CreateCartographicPartitions_cartography(outfeatures, partitions, 500, "FEATURES")
arcpy.AddMessage("Cartographic partitions created.")
partition_list = arcpy.ListFeatureClasses("Partition*", "All", partitions)

minimum_length_meters = float(arcpy.GetParameterAsText(4))




    # Set the cartographicPartitions environment setting directly
arcpy.env.cartographicPartitions = partitions

    # Run the Thin Road Network tool for the current partition
arcpy.ThinRoadNetwork_cartography(outfeatures, minimum_length_meters, invisibility_field, hierarchy_field)

arcpy.AddMessage("All partitions processed.")

#add layer to map
aprx = arcpy.mp.ArcGISProject("CURRENT")
map = aprx.listMaps()[0]
layer = outfeatures 
map.addDataFromPath(layer)
aprx.save()