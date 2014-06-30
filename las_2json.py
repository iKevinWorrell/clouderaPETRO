# Used to convert LAS (Log ASCII Standard) files into json
# TODO (kw@cloudera.com): add versions beyond 2.0

__author__ = 'Kevin Worrell'
__copyright__ = "Copyright (c) 2014, Kevin Worrell <kw@cloudera.com>, All rights reserved"
__license__ = "Apache License"
__version__ = "2.0"

import sys
import re
import uuid
import json

if len(sys.argv) < 3:
    sys.stderr.write('Usage: python las_2json.py myLASfile delimiter output [#doc2test]')
    sys.exit(1)

if (sys.argv[3].lower() in ('json', 'file')):
    #print('Writting output to: ' + sys.argv[3])
    None
else:
    raise Exception('sript requires an output type of json or file')

delim = str(sys.argv[2])
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
            metainfo.append((curr_block, myline[0].strip(), (myline[1].strip()) + '_~VERSION'))
            metavalues.append((myline[0].strip()))

        elif curr_block == '~WELL' and line.startswith('#') is False:
            myline = line.rsplit(':')
            #print('Processing -----> WELL')
            if myline[1].strip().lower().replace(' ', '_') in (
                    'unique_well_id', 'well_name', 'company_name', 'service_company_name', 'location', 'field_name'):
                metainfo.append((curr_block, myline[0].strip(), myline[1].strip()))
            else:
                metainfo.append((curr_block, myline[0].strip(), (myline[1].strip()) + '_~WELL'))
            metavalues.append((myline[0].strip()))

        elif curr_block == '~OTHER' and line.startswith('#') is False:
            myline = line.rsplit(':')
            #print('Processing -----> OTHER')
            otherinfo.append((curr_block, (myline[0].strip()) + '_~OTHER'))

        elif curr_block == '~CURVE' and line.startswith('#') is False:
            myline = line.rsplit(':')
            #print('Processing -----> CURVE')
            curveinfo.append((myline[0].strip(), (myline[1].strip()) + '_~CURVE'))

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
    rowmeta.insert(0, 'hdfs://jerryjones.localdomain/user/kw/bh/' + str(fLAS.name))
    rowmeta.insert(0, (str(a + 1) + '-' + str(uniqueid)))
    print('[' + (json.dumps(dict((zip(rowlabels, rowmeta))))) + ']')

    if sys.argv.__len__() == 5 and int(sys.argv[4]) == a:
        break
    else:
        None
