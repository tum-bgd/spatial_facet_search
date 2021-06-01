import h5py
import xapian
import sys
import numpy as np
import json
from tqdm import tqdm 


if __name__=="__main__":

    twitter = h5py.File("/data/twitter.h5","r")
    print("Indexing from HDF5 Table mapped [coords, text, lang, id]")
    print([x for x in twitter])

    db = xapian.WritableDatabase("twitter-h5", xapian.DB_CREATE_OR_OPEN)
    termgenerator = xapian.TermGenerator()
    termgenerator.set_stemmer(xapian.Stem("en"))
    for line_id in tqdm(range(twitter["coords"].shape[0])):
        record = {
            "text": twitter["text"][line_id,0].decode(),
            "coords": twitter["coords"][line_id,:].tolist()
        }
        
        doc = xapian.Document()
        termgenerator.set_document(doc)
        termgenerator.index_text(record["text"], 1)
        doc.set_data(json.dumps(record))
        #doc.add_value(1, obj["color"])
        doc.add_value(2, json.dumps(record["coords"]))
        idterm = u"Q" + "%10d" %(line_id)
        doc.add_boolean_term(idterm)
        db.replace_document(idterm, doc)

   #for i,x in enumerate(green):
   #     doc = xapian.Document()
   #     termgenerator.set_document(doc)
   #     obj = {"color": "red green","location": [x[0],x[1]],"id":"green_%05d"% (i)}
   #     termgenerator.index_text(obj["color"], 1)
   #     doc.set_data(json.dumps(obj))
   #     doc.add_value(1, obj["color"])
   #     doc.add_value(2, json.dumps(obj["location"]))
   #     idterm = u"Q" + obj["id"]
   #     doc.add_boolean_term(idterm)
   #     db.replace_document(idterm, doc)

    
