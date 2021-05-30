#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include <pybind11/numpy.h>
#include <vector>


#include <xapian.h>
#include "picojson.h"
#include<sstream>
// -------------
// Spatial Facet Implementation;
// -------------

class SpatialFacetMatchSpy: public Xapian::MatchSpy
{
public:
std::vector<std::string > values;

virtual void operator()(const Xapian::Document &doc,
                             double wt)

{
//  std::cout << "Spy on doc: " << doc.get_docid()<< "[" << wt << "]" << std::endl;
  
  std::stringstream ss;
  picojson::value coords;
  picojson::parse(coords,doc.get_value(2));
  const auto coords_a  = coords.get<picojson::array>();
   
  ss << doc.get_docid() <<  ";" << doc.get_value(1) << ";" << coords_a[0]<<";" << coords_a[1] << ";" << wt;
  
  values.push_back(ss.str());
}

};



using namespace std;
class SpatialFacetMiner
{
    Xapian::RSet rset;
    Xapian::Database db;
    Xapian::QueryParser qp;
    SpatialFacetMatchSpy spy;
    
public:
    std::string add_database(std::string database, std::string stemmer)
    {
	db.add_database(Xapian::Database(database));
	//qp = QueryParser();
	qp.set_stemmer(Xapian::Stem(stemmer));
	qp.set_database(db);
	qp.set_stemming_strategy(Xapian::QueryParser::STEM_SOME);
	return std::string("Opened a database with " + std::to_string(db.get_doccount()) + " entries.");

    }


    void query(std::string query_string, int first, int max, int check_at_least){
	Xapian::Enquire enquire(db);
        Xapian::Query query = qp.parse_query(query_string);
	enquire.set_query(query);
	enquire.add_matchspy(&spy);
    
	Xapian::MSet matches = enquire.get_mset(first, max,check_at_least, &rset);

    // Display the results.
    cout << matches.get_matches_estimated() << " results found:" << endl;

    for (Xapian::MSetIterator i = matches.begin(); i != matches.end(); ++i) {
	cout << i.get_rank() + 1 << ": " << i.get_weight() << " docid=" << *i
	     << " [" <<  i.get_document().get_data() << "]\n";
    }



    }



    void simple_compile_test(std::string database, std::string query_string ){
     // here has been an RSet
    // Parse the query string to produce a Xapian::Query object.
    
    }


};




// -------------
// pure C++ code
// -------------

std::vector<int> multiply(const std::vector<double>& input)
{
  std::vector<int> output(input.size());

  for ( size_t i = 0 ; i < input.size() ; ++i )
    output[i] = 10*static_cast<int>(input[i]);

  return output;
}

// ----------------
// Python interface
// ----------------

namespace py = pybind11;

// wrap C++ function with NumPy array IO
py::array_t<int> py_multiply(py::array_t<double, py::array::c_style | py::array::forcecast> array)
{
  // allocate std::vector (to pass to the C++ function)
  std::vector<double> array_vec(array.size());

  // copy py::array -> std::vector
  std::memcpy(array_vec.data(),array.data(),array.size()*sizeof(double));

  // call pure C++ function
  std::vector<int> result_vec = multiply(array_vec);

  // allocate py::array (to pass the result of the C++ function to Python)
  auto result        = py::array_t<int>(array.size());
  auto result_buffer = result.request();
  int *result_ptr    = (int *) result_buffer.ptr;

  // copy std::vector -> py::array
  std::memcpy(result_ptr,result_vec.data(),result_vec.size()*sizeof(int));

  return result;
  }
   

// wrap as Python module
/*PYBIND11_MODULE(spatialfacet,m)
{
  m.doc() = "pybind11 example plugin";

  m.def("multiply", &py_multiply, "Convert all entries of an 1-D NumPy-array to int and multiply by 10");
  m.def("test", &py_multiply, "Convert all entries of an 1-D NumPy-array to int and multiply by 10");
}
*/

PYBIND11_MODULE(spatialfacet,m) {
    py::class_<SpatialFacetMiner>(m, "SpatialFacetMiner")
    .def(py::init<>())
    .def("add_database", &SpatialFacetMiner::add_database)
    .def("query", &SpatialFacetMiner::query)
    ;
}
