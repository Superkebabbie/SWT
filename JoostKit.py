#author: Joost Doornkamp
#toolbox of function for own perfectionistic ends

def tablePrint(str,minspaces=3):
    #takes a string of multiple lines with equals tabs, like a table, but makes sure all columns actually align
    table = []
    maxwidth = 0 #largest number of colums in a row
    for line in str.split('\n'):
        cols = line.split('\t')
        if len(cols) > maxwidth:
            maxwidth = len(cols)
        table.append(cols)
    maxlengths = [] #list of the largest length in each column
    for col in range(maxwidth):
        max = 0
        for row in table:
            if col<len(row):
                if len(row[col])>max:
                    max = len(row[col])
        maxlengths.append(max)
    #with all this data gathered, start printing
    for line in table:
        s = ''
        col = 0
        while col<len(line):
            s += line[col] + ' '*(maxlengths[col]-len(line[col])+minspaces)
            col += 1
        print(s)

def alignPrint(lists,headers = None):
    #for a list of lists with equal length, print the elements aligned to each other for easy comparison
    assert(len(lists) > 1)
    assert([len(l) == len(lists[0]) for l in lists[1:]])
    s = [] if headers == None else ['\t'.join(headers)]
    for idx in range(len(lists[0])):
        s.append('\t'.join([l[idx] for l in lists]))
    tablePrint('\n'.join(s))
    
def flatten(list):
    #flatten a list of lists
    return [x for l in list for x in l]
    
def uniqueCount(list):
    #return a dictionary of all elements in the list and how many times they occur
    dict = {}
    for e in list:
        if e in dict:
            dict[e] += 1
        else:
            dict[0] = 1
    return dict