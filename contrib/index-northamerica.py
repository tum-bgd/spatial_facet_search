from pathlib import Path
import xapian
import json
from tqdm import tqdm
#        ID|NAME|CATEGORY|SUBCATEGORY|LON|LAT|SRID|WKT|INTERNATIONAL_NAME|STREET|WIKIPEDIA|PHONE|CITY|EMAIL|ALTERNATIVE_NAME|OPENING_HOURS|DESCRIPTION|WEBSITE|LAST_UPDATE|OPERATOR|POSTCODE|COUNTRY|FAX|IMAGE|HOUSENUMBER|OTHER_TAGS

class Indexer:
    key2prefix={
        "name": 'S',
        "category": "XC",
        "description": "XD"
    }
        
    
    def __init__(self, path, stemmer="en"):
        self.db = xapian.WritableDatabase(path, xapian.DB_CREATE_OR_OPEN)
        self.termgenerator = xapian.TermGenerator()
        self.termgenerator.set_stemmer(xapian.Stem(stemmer))
    def flush(self):
        self.db.commit()

    def add_document(self, obj):
        if not "id" in obj:
            raise "id is needed in each object"
        
        # We make a document and tell the term generator to use this.
        doc = xapian.Document()
        self.termgenerator.set_document(doc)
        for key in self.key2prefix:
            if (key in obj):
                prefix = self.key2prefix[key]
                self.termgenerator.index_text(obj[key], 1, prefix)
        if "text" in obj:
            self.termgenerator.index_text(obj["text"])
#            self.termgenerator.increase_termpos()
#            self.termgenerator.index_text(description)

        # Store all the fields for display purposes.
        doc.set_data(json.dumps(obj))

        # We use the identifier to ensure each object ends up in the
        # database only once no matter how many times we run the
        # indexer.
        idterm = u"Q" + obj["id"]
        doc.add_boolean_term(idterm)
        self.db.replace_document(idterm, doc)


def g_csv_files():
    for x in Path().rglob("*.csv"):
        if ("data/north-america_us-pois/" in str(x)):
            yield x


if __name__=="__main__":
    idx=Indexer("./northamerica-index")
    locations=open("locations.csv","w")
    locations.write("id, lon, lat\n")
    for x in g_csv_files():
        with open(x) as f:
            first = True
            for line in tqdm(f):
                if first:
                    first = False
                    continue
                line = line.split("|")
                obj = {
                    "id" : line[0],
                    "name": line[1],
                    "category": line[2] + "/" + line[3],
                    "coords": [float(line[4]),float(line[5])],
                    "description": line[16],
                    "line": line,
                    "text": " ".join(line)
                    }
#                print(obj)
                idx.add_document(obj)
                csvline= "%s,%f,%f\n" % (obj["id"], *obj["coords"])
                locations.write(csvline)
#                break
#        break
                
                

