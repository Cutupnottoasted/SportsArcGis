# SportsArcGis
Python scripts for cartography related issues in Arcgis Pro

Terms:
  ℓ: The longest road found in a fishnet cell

Problems:
  SetThinLineNetwork.pyt parameters for the field values are showing but invoking object's 'name' is not registering as STR

TODO: Debug SetRoadNetwork&RemoveSmallLines functions
  1. def setThinLineNetwork()
  2. def removeSmallLines()
      
  Figure out how to circumvent cartography partition memory issues
  1. How to target portions of entire feature and reduce lines but maintain connectivity
     1. Partition a zone around long roads and then the whole?
     2. Use fishnet to divide target feature into n, reduce lines in isolation, then aggregate cells until n = n/2
     3. Divide target feature by fishnet and find ℓ. If ℓ crosses into other cells, aggregate those cells and reduce lines.
          1. Then reduce high densisty areas and lastly the whole.
     5. Figure ratios to decided grid size based on number of objects and line density
