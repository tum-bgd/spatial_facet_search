MYBOOSTINC=/home/martin/lib/boost/boost_1_71_0
MYBOOSTLIB=/usr/local/lib
CFLAGS=-std=c++11 -Ofast -fopenmp -march=native -fPIC -fpermissive


spatialfacet.so: spatialfacet.o
	g++ -shared -o spatialfacet.so spatialfacet.o `pkg-config --libs python3` -lboost_python327 -lboost_numpy27 -lboost_system -lgomp
spatialfacet.o: spatialfacet.cpp
	g++ $(CFLAGS) -o spatialfacet.o -c spatialfacet.cpp   `pkg-config --cflags python3`

clean:
	rm -f spatialfacet.o spatialfacet.so 

