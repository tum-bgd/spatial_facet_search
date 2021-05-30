import spatialfacet

s = spatialfacet.SpatialFacetMiner()
s.add_database("../spatial_facet/NOTES/synthetic/simple","german")
s.query("red green",1,10,1000)

