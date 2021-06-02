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
    std::vector<double> coords[2];
    std::vector<double> weights;
    std::vector<int> docids;
    std::vector<std::string> value1;


    void clear()
    {
	values.clear();
	coords[0].clear(); coords[1].clear();
	weights.clear();
	docids.clear();
	value1.clear();
    }
virtual void operator()(const Xapian::Document &doc,
                             double wt)

{
//  std::cout << "Spy on doc: " << doc.get_docid()<< "[" << wt << "]" << std::endl;
  
  std::stringstream ss;
  picojson::value vcoords;
  picojson::parse(vcoords,doc.get_value(2));
  const auto coords_a  = vcoords.get<picojson::array>();
  coords[0].push_back(coords_a[0].get<double>());
  coords[1].push_back(coords_a[1].get<double>());
  docids.push_back(doc.get_docid());
  value1.push_back(doc.get_value(1));
  weights.push_back(wt);
  
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

    // ret is get_matches_estimated, rank, weight, docid, data
    std::tuple<int, std::vector<int>, std::vector<double>, std::vector<unsigned int>, std::vector<std::string>>
    query(std::string query_string, int first, int max, int check_at_least, bool query_with_data=false){
	Xapian::Enquire enquire(db);
        Xapian::Query query = qp.parse_query(query_string);
	enquire.set_query(query);
	spy.clear();
	enquire.add_matchspy(&spy);

	Xapian::MSet matches = enquire.get_mset(first, max,check_at_least); // here we had &rset, but I dont want it
	
	std::vector<int> ranks;
	std::vector<double> weights;
	std::vector<unsigned int> docids;
	std::vector<std::string> data;
	for (Xapian::MSetIterator i = matches.begin(); i != matches.end(); ++i) {
	    ranks.push_back(i.get_rank()+1);
	    weights.push_back(i.get_weight());
	    docids.push_back(*i);
	    if (query_with_data)
	       data.push_back(i.get_document().get_data());
	}

	return std::make_tuple(matches.get_matches_estimated(), ranks, weights, docids, data); 
    }
    

    // eset query
    void augment_query_from_documents(std::string query_string, std::vector<int> documents, int n_terms,
				      std::vector<std::string> &terms, std::vector<double> &weights, std::string &query_out)
    {
	std::vector<std::pair<std::string, double>> ret;
	Xapian::RSet rset;
	for (auto d: documents)
	    rset.add_document(d);
	Xapian::Query query = qp.parse_query(query_string);
	Xapian::Enquire enquire(db);
        enquire.set_query(query);
	Xapian::ESet eset = enquire.get_eset(n_terms, rset);

	Xapian::ESetIterator t;
	Xapian::Query query2 = query; // copy query and extend

	for (t = eset.begin(); t != eset.end(); ++t) {
//	    if ((*t)[0] == 'Q') continue; // not a real proposal
	    //cout << *t << ": weight = " << t.get_weight() << endl;
	    //esetfile << *t << ";" << t.get_weight() << std::endl;
	    terms.push_back(*t);
	    weights.push_back(t.get_weight());
	    query2 |= Xapian::Query(*t);
	}
//	cout << "ESET query is: " << query2.get_description() << endl;
	query_out = query2.get_description();
    
    
    }

    SpatialFacetMatchSpy &getSpy(){ return spy;};


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

template<typename vtype>
py::array wrap(vtype v)
{
   return py::array(v.size(),v.data()); // does a copy
}


PYBIND11_MODULE(spatialfacet,m) {
    py::class_<SpatialFacetMiner>(m, "SpatialFacetMiner")
    .def(py::init<>())
    .def("add_database", &SpatialFacetMiner::add_database)
    .def("query", [](SpatialFacetMiner &m,std::string query_string, int first, int max, int check_at_least){return m.query(query_string,first,max,check_at_least, false);})
    .def("query_with_data", [](SpatialFacetMiner &m,std::string query_string, int first, int max, int check_at_least){return m.query(query_string,first,max,check_at_least, true);})
    .def("getSpyData", [](SpatialFacetMiner &m){
	auto &spy = m.getSpy();
	return py::make_tuple(
	    wrap(spy.coords[0]),
	    wrap(spy.coords[1]),
	    wrap(spy.docids),
	    wrap(spy.weights)
	 );
	 })
   .def("getSpyStringData",[](SpatialFacetMiner &m){
      auto &spy = m.getSpy();
      return py::make_tuple(spy.value1, spy.values);

      })

    .def ("augment",[](SpatialFacetMiner &m, std::string query_string,
		       py::array_t<double, py::array::c_style | py::array::forcecast> documents,
		       int n_terms)
    {
	    std::vector<int> stl_documents;
	    auto r = documents.unchecked<1>();
	    for (py::ssize_t i =0; i < r.shape(0); i++)
	      stl_documents.push_back(r(i));
	    
	    std::vector<string> terms; std::vector<double> weights; std::string query_out;	    
//    void augment_query_from_documents(std::string query_string, std::vector<int> documents, int n_terms,
//				      std::vector<std::string> &terms, std::vector<double> &weights, std::string &query_out)
	    
	    m.augment_query_from_documents(query_string, stl_documents,n_terms, terms, weights, query_out);
	   return py::make_tuple(terms, weights, query_out);
	    
    });



      ;
    
}
