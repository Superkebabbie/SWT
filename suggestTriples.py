import sys, csv
from SPARQLWrapper import SPARQLWrapper, JSON, SPARQLExceptions

ensparql = SPARQLWrapper("http://dbpedia.org/sparql")
nlsparql = SPARQLWrapper("http://nl.dbpedia.org/sparql")
ensparql.setReturnFormat(JSON)
nlsparql.setReturnFormat(JSON)

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
    # global counteri
    # counteri+=1
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
    else:
        return [srcUri]
        
def isURI(s):
    #determine whether string s is a URI (rather than a data value)
    return s.startswith('http://')#TODO (good enough?)
    
def isDBPedia(s):
    #determine whether URI is from DBPedia
    return isURI(s) and 'dbpedia' in s
        
def readProppairs(filename):
    reader = csv.reader(open(filename,'r',encoding='utf-8',newline=''),delimiter='\t')
    proppairs = {}
    for line in reader:
        assert(len(line)==3)
        proppairs[(line[0],line[1])] = int(line[2])
    return proppairs

def suggestAdditions(targetURI,parUri,proppairs):
    #using the found proppairs, suggest triples that may be added to both resources
    srcrels = getRelations(targetURI)
    parrels = getRelations(parUri)#TODO: streamline the fetching of relations?
    easylookup = {}
    for p1,p2 in proppairs:
        #convert the proppairs dict to have single properties as keys so you can easily find properties it was paired with
        if proppairs[(p1,p2)] > 100:
            if p1 in easylookup:
                easylookup[p1] += [p2]
            else:
                easylookup[p1] = [p2]
            if p2 in easylookup:
                easylookup[p2] += [p1]
            else:
                easylookup[p2] = [p1]
    for p,r in parrels:
        if p in easylookup:
            sameProps = easylookup[p]
            for p2 in sameProps:
                sameRes = getOtherResource(r)
                for r2 in sameRes:
                    suggestion = (p2,r2)
                    if suggestion not in srcrels:
                        print("Based on triple\n%s\n%s\n%s,\nwe suggest adding\n%s\n%s\n%s\n"%(parUri,p,r,targetURI,p2,r2))
                            
if len(sys.argv) == 2:
    target = sys.argv[1]
    parallel = getOtherResource(target)[0]
    proppairs = readProppairs('mined_links.csv')
    suggestAdditions(target,parallel,proppairs)
else:
    print("USAGE: python suggestTripples.py [target resource]")