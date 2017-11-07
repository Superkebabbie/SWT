from subprocess import call

propfile = 'mined_links.csv'

for filenum in range(1,1522):
    filename = 'data/infobox_properties_en_part%d.ttl'%filenum
    print("Batch %d"%filenum)
    call(['python','./makePropPairs.py',filename,propfile])