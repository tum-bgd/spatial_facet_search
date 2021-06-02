"""
Extract all objects with an amenity tag from an osm file and list them
with their name and position.

This example shows how geometries from osmium objects can be imported
into shapely using the WKBFactory.
"""
import osmium as o
import sys
import shapely.wkb as wkblib
import json
import xapian

class cfg:
    altinput="/home/data/toarchive/2020-04-14 OSM_Kram_Join_Wikipedia_INCOMPLETETRASH/germany-latest.osm.pbf"
    input="/home/data/toarchive/2020-04-14 OSM_Kram_Join_Wikipedia_INCOMPLETETRASH/hamburg-latest.osm.pbf"



wkbfab = o.geom.WKBFactory()

db = xapian.WritableDatabase("osm", xapian.DB_CREATE_OR_OPEN)
termgenerator = xapian.TermGenerator()
termgenerator.set_stemmer(xapian.Stem("en"))


class AmenityListHandler(o.SimpleHandler):
    count = None
    def add_document(self,line_id, c1,c2, text):
        if self.count is None:
            self.count = 0
        else:
            self.count = self.count +1
        if self.count % 1000 == 0:
            print("Read so far %d " %(self.count) , end='\r')
        record = {
                "text": text,
            "coords": [c1,c2]
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

    
    def node(self, n):
        if len(n.tags) > 0: 
            
            text = "type=node "+ " ".join([tag.k+"="+ tag.v for tag in n.tags])
            self.add_document(n.id, n.location.lon, n.location.lat, text)
        
#            print("%f %f %s" %(n.location.lon, n.location.lat, text))
            #print(n.location.lon, n.location.lat,n.tags)
#        if 'amenity' in n.tags:
#            self.print_amenity(n.tags, n.location.lon, n.location.lat)

    def area(self, n):
        try:
            wkb = wkbfab.create_multipolygon(n)
            poly = wkblib.loads(wkb, hex=True)
            centroid = poly.representative_point()
            text = "type=area "+" ".join([tag.k+"="+ tag.v for tag in n.tags])
            self.add_document(n.id, centroid.x, centroid.y, text)
        except:
            print("some problem, maybe incomplete geometry")
            pass
            #            print("%f %f %s" %(n.location.lon, n.location.lat, text))
                        


def main(osmfile):

    handler = AmenityListHandler()
    handler.apply_file(osmfile)
    return 0

if __name__ == '__main__':
     main(cfg.input)
