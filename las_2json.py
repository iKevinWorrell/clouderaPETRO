# Used to convert LAS (Log ASCII Standard) files into json
# TODO (kw@cloudera.com): add versions beyond 2.0

__author__ = 'Kevin Worrell'
__copyright__ = "Copyright (c) 2014, Kevin Worrell <kw@cloudera.com>, All rights reserved"
__license__ = "Apache License http://www.apache.org/licenses/LICENSE-2.0.txt"
__version__ = "2.0"

import sys
import re
import uuid
import json
import ConfigParser

if len(sys.argv) < 2:
    sys.stderr.write('Usage: python las_2json.py myLASfile myConfigFile')
    sys.exit(1)

configs = ConfigParser.ConfigParser()
configs.read(str(sys.argv[2]))
debug = False

if configs.has_option('io','debug') and configs.get('io', 'debug').lower().strip() == 'true':
    debug = configs.get('io', 'debug')
    for section_name in configs.sections():
        print 'Section:', section_name
        print '  Options:', configs.options(section_name)
        for name, value in configs.items(section_name):
            print '  %s = %s' % (name, value)
        print

delim = configs.get('io', 'delimiter')
curr_block = None
metainfo = []
curveinfo = []
otherinfo = []
asciiinfo = []
metavalues = []

# Process the LAS file passed in as a cmd arg
with open(str(sys.argv[1]), 'r') as fLAS:
    for line in fLAS:
        if line.startswith('~'):

            if line.startswith('~VERSION'):
                curr_block = '~VERSION'

            elif line.startswith('~WELL'):
                curr_block = '~WELL'

            elif line.startswith('~CURVE'):
                curr_block = '~CURVE'

            elif line.startswith('~O'):
                curr_block = '~OTHER'

            elif line.startswith('~A'):
                curr_block = '~ASCIILOG'

        elif curr_block == '~VERSION' and line.startswith('#') is False:
            myline = line.rsplit(':')
            #print('Processing -----> VERSION')
            metainfo.append((curr_block, myline[0].strip(), (myline[1].strip()) + '_dyn_VERSION'))
            metavalues.append((myline[0].strip()))

        elif curr_block == '~WELL' and line.startswith('#') is False:
            myline = line.rsplit(':')

            if myline[1].strip().lower().replace(' ', '_') in (str(configs.get('solr','staticfields'))):
                metainfo.append((curr_block, myline[0].strip(), myline[1].strip().lower()))
            else:
                metainfo.append((curr_block, myline[0].strip(), (myline[1].strip().lower()) + '_dyn_WELL'))

            metafield = myline[0].strip()

            for i in (configs.get('las','stripfields').split(':')):
                if metafield.startswith(str(i)):
                    metafield = metafield[(int(i.__len__())):].strip()

            metavalues.append((metafield))

        elif curr_block == '~OTHER' and line.startswith('#') is False:
            myline = line.rsplit(':')
            #print('Processing -----> OTHER')
            otherinfo.append((curr_block, (myline[0].strip()) + '__dyn_OTHER'))

        elif curr_block == '~CURVE' and line.startswith('#') is False:
            myline = line.rsplit(':')
            #print('Processing -----> CURVE')
            curveinfo.append((myline[0].strip(), (myline[1].strip()) + '__dyn_CURVE'))

        elif curr_block == '~ASCIILOG' and line.startswith('#') is False:
            myline = re.split(r'[ \t]+', line.strip())
            asciiinfo.append((myline))

        elif line.startswith('#'):
            None

        else:
            raise Exception("Unknown section '%s'" % line)

fLAS.close()

rowheader = 'unique_id' + delim + 'original_document_url'

for i, e in enumerate(metainfo):
    rowheader = rowheader + delim + str(e[2].replace(' ', '_')).strip()

for i, e in enumerate(curveinfo):
    rowheader = rowheader + delim + str(e[1].replace(' ', '_')).strip()

rowlabels = rowheader.split(delim)

uniqueid = uuid.uuid4()

for a, ae in enumerate(asciiinfo):
    rowmeta = (metavalues + (ae))
    rowmeta.insert(0, str(configs.get('solr', 'basedir')) + str(fLAS.name))
    rowmeta.insert(0, (str(a + 1) + '-' + str(uniqueid)))
    print('[' + (json.dumps(dict((zip(rowlabels, rowmeta))))) + ']')

    if a == 10 and bool(debug) is True:
        break
    else:
        None
