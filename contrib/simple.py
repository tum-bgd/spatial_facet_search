import numpy as np;
import h5py;
from matplotlib import pyplot as plt
import xapian
import json

class cfg:
    n_blac=110
    n_red=10
    n_blue=5
    n_green=5

def uniform_rect(size):
    return np.random.uniform(size=2*size).reshape(-1,2)

if __name__=="__main__":
    np.random.seed(42)
    # black everywhere
#    black = uniform_rect(cfg.n_red)*[2.2,1.1] - [1.1,0.05]
    # left
    green = uniform_rect(cfg.n_blue) - [1,0]
    #right
    blue = uniform_rect(cfg.n_blue)
    #both
    red = uniform_rect(cfg.n_red)*[2,1] - [1,0]
    
#    plt.scatter(black[:,0],black[:,1],color="black")
    plt.scatter(red[:,0],red[:,1],color="red")
    plt.scatter(green[:,0],green[:,1],color="green")
    plt.scatter(blue[:,0],blue[:,1],color="blue")
    plt.show()
#    plt.savefig("simple-overview.png")


    ### build a xapian database for these
    db = xapian.WritableDatabase("simple", xapian.DB_CREATE_OR_OPEN)
    termgenerator = xapian.TermGenerator()
    termgenerator.set_stemmer(xapian.Stem("en"))

    
    for i,x in enumerate(green):
        doc = xapian.Document()
        termgenerator.set_document(doc)
        obj = {"color": "red green","location": [x[0],x[1]],"id":"green_%05d"% (i)}
        termgenerator.index_text(obj["color"], 1)
        doc.set_data(json.dumps(obj))
        doc.add_value(1, obj["color"])
        doc.add_value(2, json.dumps(obj["location"]))
        idterm = u"Q" + obj["id"]
        doc.add_boolean_term(idterm)
        db.replace_document(idterm, doc)

    for i,x in enumerate(blue):
        doc = xapian.Document()
        termgenerator.set_document(doc)
        obj = {"color": "red blue","location": [x[0],x[1]],"id":"blue_%05d"% (i)}
        termgenerator.index_text(obj["color"], 1)
        doc.set_data(json.dumps(obj))
        doc.add_value(1, obj["color"])
        doc.add_value(2, json.dumps(obj["location"]))
        idterm = u"Q" + obj["id"]
        doc.add_boolean_term(idterm)
        db.replace_document(idterm, doc)

    
