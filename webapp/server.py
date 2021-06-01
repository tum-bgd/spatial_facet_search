from flask import Flask, request, jsonify
import numpy as np
import json
from shapely.geometry import Polygon, Point, shape, mapping

from engine import supervised_spatial_facet


# set the project root directory as the static folder, you can set others.
app = Flask(__name__,
            static_url_path='', 
            static_folder='static')





@app.route('/')
def root():
    return app.send_static_file('index.html')

@app.route("/supervised_facet", methods=['POST'])
def supervised_facet():
    print("Data Received: ")
    print([x for x in request.json])
    
    print("Supervised Facet Computation")
    print("Saving Debug Facet Polygon")
    with open("poly.geojson","w") as f:
        f.write(json.dumps(request.json["poly"]["geometry"]))
    U = shape(request.json["poly"]["geometry"])
    print(U)
    query = request.json["query"]
    aug_keywords, the_facet, c0,c1,docs,wt = supervised_spatial_facet (query, U)#, first_result=1, last_result=10, min_visits=1000):
    print(c0)
        
    response={"query":query,
              "aug_keywords": aug_keywords,
               #c0,c1,docs,wt
    }
                                   
    return jsonify(response), 200

    
    


if __name__=="__main__":
    app.run(host="0.0.0.0")
