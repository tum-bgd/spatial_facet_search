import spatialfacet
import numpy as np
from matplotlib import pyplot as plt
from shapely.geometry import Polygon, Point


U = Polygon([[-1,-1],
             [-1,1],
             [0,1],
             [0,-1],
             [-1,-1]])

V = Polygon([[0,-1],
             [0,1],
             [1,1],
             [1,-1],
             [0,-1]])


U_minus = Polygon([[-1,0.75],
             [-1,1],
             [0,1],
             [0,0.75],
             [-1,0.75]])

print(U)


s = spatialfacet.SpatialFacetMiner()
s.add_database("databases/simple","german")
s.query("red blue",1,20,1000)

c0, c1, docs,wt = s.getSpyData();
v1,values = s.getSpyStringData();

print(c0)
print("="*50)
print(c1)
print("="*50)
print(docs)
print("="*50)
print(wt)
print("="*50)
print(v1)
print("="*50)
print(values)
print("="*50)




plt.scatter(c0,c1, s=(15*wt)**2+5)
plt.savefig("test.png")



## facet

def get_facet (c0,c1,U):
    return ([rowid for x,y,rowid in zip(c0,c1,range(c0.shape[0])) if Point([x,y]).within(U)])

facet = {
    "U": get_facet(c0,c1,U),
    "V": get_facet(c0,c1,V),
    "U-": get_facet(c0,c1,U_minus),
}
print(facet)

## now propose query terms
out = s.augment("red", [1,2,3], 5)
print(out)
