from SPARQLWrapper import SPARQLWrapper, JSON, SPARQLExceptions
import JoostKit

ensparql = SPARQLWrapper("http://dbpedia.org/sparql")
nlsparql = SPARQLWrapper("http://nl.dbpedia.org/sparql")
ensparql.setReturnFormat(JSON)
nlsparql.setReturnFormat(JSON)
counteri = 0

def getLanguage(uri):
    #return the domain the uri is from (nl/en)
    if uri.startswith('http://nl.dbpedia.org'):
        return 'nl'
    elif uri.startswith('http://dbpedia.org'):
        return 'en'
    else:
        # print("Unknown source domain for " + uri)
        return None

def getRelations(uri):
    query = 'select ?p ?r where {<' + uri + '> ?p ?r .}'
    global counteri
    counteri+=1
    sparql = ensparql#assumes you can query English dbpedia by default, including regarding things that are not of the dbpedia domain
    if getLanguage(uri) == 'nl':
        sparql = nlsparql
    sparql.setQuery(query)
    results = sparql.query().convert()["results"]["bindings"]
    pairs = []
    for pair in results:
        if isDBPedia(pair['r']['value']) and not 'wiki' in pair['p']['value']:
            pairs.append((pair['p']['value'],pair['r']['value']))
    return pairs

def getDutchResource(srcUri):
    #go from a English source to the Dutch counterpart
    query = 'select ?p where {<' + srcUri + '> <http://www.w3.org/2002/07/owl#sameAs> ?p .}'
    ensparql.setQuery(query)
    results = ensparql.query().convert()["results"]["bindings"]
    resources = []
    for r in results:
        p = r['p']['value']
        if p.startswith('http://nl.dbpedia.org'):#filter Dutch resources
            resources.append(p)
    return resources
    
def getEnglishResource(srcUri):
    #go from a Dutch source to the English counterpart
    query = 'select ?p where {<' + srcUri + '> <http://www.w3.org/2002/07/owl#sameAs> ?p .}'
    nlsparql.setQuery(query)
    results = nlsparql.query().convert()["results"]["bindings"]
    resources = []
    for r in results:
        p = r['p']['value']
        if p.startswith('http://dbpedia.org'):#filter Dutch resources
            resources.append(p)
    return resources
    
def getOtherResource(srcUri):
    #automatically determine if you're going from English to Dutch or vice versa
    if getLanguage(srcUri) == 'nl':
        return getEnglishResource(srcUri)
    elif getLanguage(srcUri) == 'en':
        return getDutchResource(srcUri)
        
def getSameAs(srcUri):
    results = []
    source = getRelations(srcUri)
    for p,r in source:
        if 'sameAs' in p:
            results.append((p,r))
    return results
    
def isURI(s):
    #determine whether string s is a URI (rather than a data value)
    return s.startswith('http://')#TODO (good enough?)
    
def isDBPedia(s):
    #determine whether URI is from DBPedia
    return isURI(s) and 'dbpedia' in s
    
def URIname(uri):
    #get the printable name from a URI
    return uri[uri.rfind('/')+1:]
    
def printMatch(o1,p1,r1,o2,p2,r2):
    JoostKit.tablePrint('origin\tproperty\ttarget\n%s\t%s\t%s\n%s\t%s\t%s'%(o1,p1,r1,o2,p2,r2))
        
def findParallelConnections(srcUri,parUri):
    print("Finding parallels for " + str(srcUri) + " and " + str(parUri))
    srcrels = getRelations(srcUri)
    parrels = getRelations(parUri)
    print("Original has %d relations\nParallel has %d triples\nComparing %d triples"%(len(srcrels),len(parrels),len(srcrels)*len(parrels)))
    for p1,r1 in srcrels:
        #print counteri
        for p2,r2 in parrels:
            if r1 == r2:
                print("Identical match!")
                printMatch(srcUri,p1,r1,parUri,p2,r2)
            #if isDBPedia(r1) and isDBPedia(r2):
            #    overlap = set(getSameAs(r1)).intersection(set(getSameAs(r2)))
            #    if len(overlap) > 0:
            #        print(overlap)
    #print matches

target = 'http://dbpedia.org/resource/The_Hague'
# target = 'http://nl.dbpedia.org/resource/Den_Haag'
print("Starting from resource: " + str(target))
parallel = getOtherResource(target)[0]
print("Determined parallel resource: " + str(parallel))
# print('\n'.join([str(x) for x in getRelations(target)]))
findParallelConnections(target,parallel)

