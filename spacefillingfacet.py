import numpy as np
import spatialfacet
from itertools import product
from shapely.geometry import Polygon, Point
from tqdm import tqdm


class SimpleClusterConfiguration:
    bounds = [-11,11,-3, 12] # xxyy
    database="databases/simple_cluster"
    step = [3,3]
    query = "black"

class AppleOnTwitterConfiguration:
    bounds = [-180,180,-90, 90] # xxyy
    database="contrib/twitter/twitter-h5"
    step = [10,10]
    query = "apple"

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

def supervised_spatial_facet (se,query, U, first_result=1, last_result=10, min_visits=10000):
    se.query(query,first_result, last_result, min_visits)
    c0, c1, docs,wt = se.getSpyData();
    the_facet = get_facet(c0,c1,U) # ids of the facet
    aug_keywords= augment(se, query, [docs[i] for i in the_facet])
    return aug_keywords, the_facet, c0,c1,docs,wt




if __name__=="__main__":
    cfg = SimpleClusterConfiguration();
    cfg = AppleOnTwitterConfiguration();
    s = spatialfacet.SpatialFacetMiner()
    s.add_database(cfg.database,"english")
    s.query(cfg.query,1,20,1000)
    f = open("spacefillingfacet.csv","w")
    print("wkt; top_keyword; weight", file=f)
    workload = [x for x in product(np.arange(cfg.bounds[0], cfg.bounds[1], cfg.step[0]),np.arange(cfg.bounds[0], cfg.bounds[1], cfg.step[1]))]
    # by materializing workload as a list, we waste memory, but we get a max on tqdm for free
    for x,y in tqdm(workload):
        U = Polygon([[x,y],[x+cfg.step[0],y],[x+cfg.step[0],y+cfg.step[1]],[x,y+cfg.step[1]],[x,y]])
        kw, facet, c0,c1, docs, wt= supervised_spatial_facet(s, cfg.query,U)
        if(len(facet) != 0):
            kw = [(x,y) for x,y in kw if not x  in cfg.query]
            print("%s; %s; %.2f" %(str(U),str(kw),kw[0][1]), file=f)
        
