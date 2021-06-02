from spatialfacet import SpatialFacetMiner
import numpy as np
from matplotlib import pyplot as plt
from shapely.geometry import Polygon, Point

from sklearn.cluster import DBSCAN, OPTICS

class cfg:
    databasetw="../contrib/twitter/twitter-h5"
    database="../contrib/osm"


def simple_query(query_string,minresult,maxresult):
    se = SpatialFacetMiner()
    se.add_database(cfg.database,"english")
    matches, ranks, weights, docids, data =  se.query_with_data(query_string,minresult,maxresult,1)
    return {"num_matches":matches, "ranks": ranks, "weights": weights, "docids" : docids,"data": data}



def default_facet_plot(se):
    c0, c1, docs,wt = se.getSpyData();
    v1,values = se.getSpyStringData()
    plt.scatter(c0,c1, s=(15*wt)**2+5)
    plt.show()
def augment(facetminer, query, documents, n=50, retain_only_real = True):
    "a helper function for simpler query augmentation. Does remove all prefixed terms if wanted and zips results from C library  for a more pythonic user"
    #print(facetminer, query, documents, n)
    terms, weights, query = facetminer.augment(query,documents,n)
    the_filter = lambda x: True
    if retain_only_real:
        the_filter = lambda x: not x[0].isupper()
    return([(x,y) for x,y in zip(terms, weights) if the_filter(x)])

def get_facet (c0,c1,U):
    return ([rowid for x,y,rowid in zip(c0,c1,range(c0.shape[0])) if Point([x,y]).within(U)])

def supervised_spatial_facet (query, U, first_result=1, last_result=10, min_visits=10000):
    se = SpatialFacetMiner()
    se.add_database("../contrib/twitter/twitter-h5","english")
    print("Running the Query")
    se.query(query,first_result, last_result, min_visits)
    print("eating the spy data")
    c0, c1, docs,wt = se.getSpyData();
    the_facet = get_facet(c0,c1,U) # ids of the facet
    print("Facet",the_facet)
    aug_keywords= augment(se, query, [docs[i] for i in the_facet])
    return aug_keywords, the_facet, c0,c1,docs,wt





