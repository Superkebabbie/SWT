from SPARQLWrapper import SPARQLWrapper, JSON, SPARQLExceptions

ensparql = SPARQLWrapper("http://dbpedia.org/sparql")
nlsparql = SPARQLWrapper("http://nl.dbpedia.org/sparql")
ensparql.setReturnFormat(JSON)
nlsparql.setReturnFormat(JSON)

def getRelations(uri):
    query = 'select ?r ?p where {<' + uri + '> ?r ?p .}'
    ensparql.setQuery(query)
    results = ensparql.query().convert()["results"]["bindings"]
    pairs = []
    for pair in results:
        pairs.append((pair['r']['value'],pair['p']['value']))
    return pairs
    
def getSameAs(uri):
    query = 'select ?p where {<' + uri + '> <http://www.w3.org/2002/07/owl#sameAs> ?p .}'
    ensparql.setQuery(query)
    results = ensparql.query().convert()["results"]["bindings"]
    resources = []
    for r in results:
        p = r['p']['value']
        if 'dbpedia' in p:#filter out non-dbpedia resources
            resources.append(p)
    return resources
    
#print(getRelations('http://dbpedia.org/resource/The_Hague'))
print(getSameAs('http://dbpedia.org/resource/The_Hague'))

    