import arcpy 
import os

# CONSTANTS
INVIS = "Invisibilty"
HIERARCHY = "Hierarchy"

""" *********************************** SET VARIABLES TO MATCH WORKSPACE *********************************** """
workspace = str(arcpy.env.workspace)
targetFeature = "RR" # Feature class to be thinned
targetField = "MTFCC" # Field Header that the hierarchy is based on
min_road_seg = "100 unknown" # Minimal length for a road segment (meters)
feature_count = 500 # Number of features per square

# Unique identifiers from the FIELD_HEADER column 
hierarchy_map = {
    "S1100" : 1,
    "S1740" : 2,
    "S1780" : 3,
    "S1400" : 4,
}
DEFAULT = 5
        
"""" **************************************** FUNCTIONS **************************************************** """

# ************************************** setThinLineNetwork() **********************************************
# Exports targetFeature (outFeature) and runs CreateCartographicPartitions.
# It then iterates through each partition and selects objects from outFeature to run ThinRoadNetwork tool 
def setThinLineNetwork():
    outFeature = workspace + '\\' + targetFeature + "_Roads_Thinned" # set path for output
    outPartition = workspace + '\\' + targetFeature + "_Partition"
    outFeature = outFeature.replace("\\", "\\\\")
    outPartition = outPartition.replace("\\", "\\\\")
    
    if not arcpy.Exists(outFeature): # Create feature if it does not exist
        arcpy.AddMessage(f"{outFeature} has been created!")
        print(f"{outFeature} has been created!")
        arcpy.conversion.ExportFeatures(
            in_features = targetFeature,
            out_features = outFeature,
            use_field_alias_as_name = "NOT_USE_ALIAS"
        )
        
        field_names = [field.name for field in arcpy.ListFields(outFeature)] # find all field names
        # If INVIS and HIERARCHY are not in the table then add it
        if INVIS not in field_names:
            arcpy.AddField_management(outFeature, INVIS, "LONG")
            arcpy.AddMessage(f"Created field {INVIS}.")
            print(f"Created field {INVIS}.")
        if HIERARCHY not in field_names:
            arcpy.AddField_management(outFeature, HIERARCHY, "LONG")
            arcpy.AddMessage(f"Created field {HIERARCHY}.")
            print(f"Created field {HIERARCHY}.")  
  
              
    else: 
        arcpy.AddMessage(f"{outFeature} exists and will be overwritten!")
        print(f"{outFeature} exists and will be overwritten!")
        field_names = [field.name for field in arcpy.ListFields(outFeature)] # find all field names
        
        # If INVIS and HIERARCHY are not in the table then add it
        if INVIS not in field_names:
            arcpy.AddField_management(outFeature, INVIS, "LONG")
            arcpy.AddMessage(f"Created field {INVIS}.")
            print(f"Created field {INVIS}.")

        if HIERARCHY not in field_names:
            arcpy.AddField_management(outFeature, HIERARCHY, "LONG")
            arcpy.AddMessage(f"Created field {HIERARCHY}.")
            print(f"Created field {HIERARCHY}.")

    # Search for outFeature's Hierarchy/targetField and set placement
    with arcpy.da.UpdateCursor(outFeature, [targetField, HIERARCHY]) as cursor:
        for row in cursor:
            roadType = row[0]
            placement = hierarchy_map.get(roadType, DEFAULT)
            row[1] = placement
            cursor.updateRow(row)

    if not arcpy.Exists(outPartition): # Create partition if it does not exist
        arcpy.AddMessage(f"{outPartition} has been created!")
        print(f"{outPartition} has been created!")
        arcpy.cartography.CreateCartographicPartitions(
            in_features = outFeature, 
            out_features = outPartition, 
            feature_count = feature_count, 
            partition_method = "FEATURES")
   
    # Sort each partition by its rank in decending order
    partitions = [] 
    with arcpy.da.SearchCursor(outPartition, ["SHAPE@", "RANK"]) as cursor:
        for row in cursor:
            partitions.append([row[0], row[1]])
            
    partitions = sorted(partitions, key = lambda x:x[1], reverse = True)
    print(f"{len(partitions)} partitions have been made!")
    # Iterate through each partition and select by location
    print("Iterating through all partitions!")
    for i, partition in enumerate(partitions, start = 1):
        print(f"Partition {i} is current partition")
        arcpy.management.SelectLayerByLocation  (
                in_layer = targetFeature + "_Roads_Thinned",
                overlap_type = "INTERSECT",
                select_features = partition[0],
                search_distance = None,
                selection_type = "NEW_SELECTION",
                invert_spatial_relationship = "NOT_INVERT"
        )
        print(f"Roads in the bounds of partition {i} have been selected")
        # Then the outFeature's selected roads
        arcpy.cartography.ThinRoadNetwork (
            in_features = outFeature,
            minimum_length = min_road_seg,
            invisibility_field = INVIS,
            hierarchy_field = HIERARCHY
        )
        arcpy.AddMessage(f"Partition {i} has been thinned!")
        print(f"Partition {i} has been thinned!\n")
        
    # Delete partitions        
    arcpy.AddMessage("All partitions have been processed! Deleting partition feature...")
    print("All partitions have been processed! Deleting partition feature...")
    if arcpy.Exists(outPartition):
        arcpy.Delete_management(outPartition)

    return outFeature # return outFeature path

# ********************************** removeSmallLines(outFeature) ******************************************
def removeSmallLines(inFeature):
    outDissolved = inFeature + "_Dissolved" # Set path for output
    
    # Set feature box frame and spatial ref
    description = arcpy.Describe(inFeature)
    wkt = description.spatialReference
    wkt = wkt.exportToString()
    extent = description.extent
    extent = f"{extent.XMin} {extent.YMin} {extent.XMax} {extent.YMax} {wkt}"
    
    # dissolve all roads together
    with arcpy.EnvManager(extent = extent, outputCoordinateSystem = wkt, workspace = arcpy.env.workspace):
        arcpy.analysis.PairwiseDissolve( in_feature = inFeature,
                                         out_feature_class = outDissolved,
                                         multi_part = "SINGLE_PART" )
    # Create new features with SpatialJoin and Statistics
    outSpatialJoin = workspace + "_Spatial_Join"
    arcpy.analysis.SpatialJoin(target_feature = outDissolved,
                               join_feature = outDissolved,
                               out_feature_class = outSpatialJoin,
                               join_operation = "JOIN_ONE_TO_MANY",
                               match_option = "BOUNDARY_TOUCHES")
    
    
    # Delete outDissolved after outSpatialJoin is made
    if arcpy.Exists(outDissolved):
        arcpy.Delete_management(outDissolved)
    
    
    with arcpy.da.UpdateCursor(outSpatialJoin, ["JOIN_FID"]) as cursor:
        for row in cursor:
            if row[0] == -1:
                cursor.deleteRow()
                
"""" ******************************************* MAIN ****************************************************** """ 
t = setThinLineNetwork()
