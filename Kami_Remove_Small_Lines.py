# -*- coding: utf-8 -*-
"""
Generated by ArcGIS ModelBuilder on : 2023-08-30 10:07:52
"""
import arcpy
from sys import argv

def KamiRemoveSmallLines(Extent="-10971737.4270496 3976858.62840177 -10935084.6805371 4002373.48605158 PROJCS[\"WGS_1984_Web_Mercator_Auxiliary_Sphere\",GEOGCS[\"GCS_WGS_1984\",DATUM[\"D_WGS_1984\",SPHEROID[\"WGS_1984\",6378137.0,298.257223563]],PRIMEM[\"Greenwich\",0.0],UNIT[\"Degree\",0.0174532925199433]],PROJECTION[\"Mercator_Auxiliary_Sphere\"],PARAMETER[\"False_Easting\",0.0],PARAMETER[\"False_Northing\",0.0],PARAMETER[\"Central_Meridian\",0.0],PARAMETER[\"Standard_Parallel_1\",0.0],PARAMETER[\"Auxiliary_Sphere_Type\",0.0],UNIT[\"Meter\",1.0]]", Workspace, Name, Input_layer, Dissolve_Fields=["Name Field", "OBJECTID"]):  # Kami_Remove_Small_Lines

    # To allow overwriting outputs change overwriteOutput option to True.
    arcpy.env.overwriteOutput = False

    Output_Coordinate_System = "PROJCS[\"WGS_1984_Web_Mercator_Auxiliary_Sphere\",GEOGCS[\"GCS_WGS_1984\",DATUM[\"D_WGS_1984\",SPHEROID[\"WGS_1984\",6378137.0,298.257223563]],PRIMEM[\"Greenwich\",0.0],UNIT[\"Degree\",0.0174532925199433]],PROJECTION[\"Mercator_Auxiliary_Sphere\"],PARAMETER[\"False_Easting\",0.0],PARAMETER[\"False_Northing\",0.0],PARAMETER[\"Central_Meridian\",0.0],PARAMETER[\"Standard_Parallel_1\",0.0],PARAMETER[\"Auxiliary_Sphere_Type\",0.0],UNIT[\"Meter\",1.0]]"
    Input_Join_Field = "OBJECTID"
    Match_Option = "BOUNDARY_TOUCHES"

    # Process: Pairwise Dissolve (Pairwise Dissolve) (analysis)
    with arcpy.EnvManager(extent=Extent, outputCoordinateSystem=Output_Coordinate_System, workspace="D:\\ArcGIS\\Projects\\TRI_City_Lake_MO\\TRI_City_Lake_MO.gdb"):
        arcpy.analysis.PairwiseDissolve(in_features=Input_layer.__str__().format(**locals(),**globals()), out_feature_class=Name.__str__().format(**locals(),**globals()), dissolve_field=Dissolve_Fields.__str__().format(**locals(),**globals()), multi_part="SINGLE_PART")

    # Process: Spatial Join (Spatial Join) (analysis)
    TexasRoads_Pairw_SpatialJoin1 = ""
    arcpy.analysis.SpatialJoin(target_features=Name.__str__().format(**locals(),**globals()), join_features=Name.__str__().format(**locals(),**globals()), out_feature_class=TexasRoads_Pairw_SpatialJoin1, join_operation="JOIN_ONE_TO_MANY", match_option=Match_Option)

    # Process: Summary Statistics (Summary Statistics) (analysis)
    TexasRoads_Pairw_Statistics1 = ""
    arcpy.analysis.Statistics(in_table=TexasRoads_Pairw_SpatialJoin1, out_table=TexasRoads_Pairw_Statistics1, statistics_fields=[["JOIN_FID", "COUNT"]], case_field=["TARGET_FID"])

    # Process: Join Field (Join Field) (management)
    TexasRoads_PairwiseDissolve100 = arcpy.management.JoinField(in_data=Name.__str__().format(**locals(),**globals()), in_field=Input_Join_Field, join_table=TexasRoads_Pairw_Statistics1, join_field="OBJECTID", fields=["COUNT_JOIN_FID"])[0]

    # Process: Select Layer By Attribute (Select Layer By Attribute) (management)
    Roadss, Count = arcpy.management.SelectLayerByAttribute(in_layer_or_view=TexasRoads_PairwiseDissolve100, where_clause="COUNT_JOIN_FID = 1")

    # Process: Delete Features (Delete Features) (management)
    Output_Feature_Class = arcpy.management.DeleteFeatures(in_features=Roadss)[0]

if __name__ == '__main__':
    # Global Environment settings
    with arcpy.EnvManager(scratchWorkspace="D:\\ArcGIS\\Projects\\Fixing_roads_project\\Fixing_roads_project.gdb", workspace="D:\\ArcGIS\\Projects\\Fixing_roads_project\\Fixing_roads_project.gdb"):
        KamiRemoveSmallLines(*argv[1:])
