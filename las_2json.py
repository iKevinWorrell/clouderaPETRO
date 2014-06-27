# Used to convert LAS (Log ASCII Standard) files into json
# TODO (kw@cloudera.com): add versions beyond 2.0

__author__ = 'Kevin Worrell - kw@cloudera.com'

import sys
import re
import uuid
import json

if len(sys.argv) < 2:
    sys.stderr.write('Usage: python las_flatten.py myLASfile delimiter')
    sys.exit(1)


delim = str(sys.argv[2])
curr_block = None
metainfo = []
curveinfo = []
otherinfo = []
asciiinfo = []
metavalues = []

with open(str(sys.argv[1]), 'r') as fLAS:
    for line in fLAS:
        if line.startswith('~'):

            if line.startswith('~VERSION'):
                curr_block = 'VERSION'

            elif line.startswith('~WELL'):
                curr_block = 'WELL'

            elif line.startswith('~CURVE'):
                curr_block = 'CURVE'

            elif line.startswith('~O'):
                curr_block = 'OTHER'

            elif line.startswith('~A'):
                curr_block = 'DATA'

        elif curr_block == 'VERSION' and line.startswith('#') is False:
            myline = line.rsplit(':')
            #print('Processing -----> VERSION')
            metainfo.append((curr_block, myline[0].strip(), myline[1].strip()))
            metavalues.append((myline[0].strip()))

        elif curr_block == 'WELL' and line.startswith('#') is False:
            myline = line.rsplit(':')
            #print('Processing -----> WELL')
            metainfo.append((curr_block, myline[0].strip(), myline[1].strip()))
            metavalues.append((myline[0].strip()))

        elif curr_block == 'OTHER' and line.startswith('#') is False:
            myline = line.rsplit(':')
            #print('Processing -----> OTHER')
            otherinfo.append((curr_block, myline[0].strip()))

        elif curr_block == 'CURVE' and line.startswith('#') is False:
            myline = line.rsplit(':')
            #print('Processing -----> CURVE')
            curveinfo.append((myline[0].strip(), myline[1].strip()))

        elif curr_block == 'DATA' and line.startswith('#') is False:
            myline = re.split(r'[ \t]+', line.strip())
            asciiinfo.append((myline))

        elif line.startswith('#'):
            None

        else:
            raise Exception("Unknown section '%s'" % line)
fLAS.close()

rowheader = 'unique_id'

for i, e in enumerate(metainfo):
    #    print ('|' + '%03d) %s' % (i, ', '.join(e)))
    rowheader = rowheader + delim + str(e[2].replace(' ', '_')).strip()

for i, e in enumerate(curveinfo):
    #    print ('|' + '%03d) %s' % (i, ', '.join(e)))
    rowheader = rowheader + delim + str(e[1].replace(' ', '_')).strip()

rowlabels = rowheader.split(delim)

uniqueid = uuid.uuid4()

for a, ae in enumerate(asciiinfo):
    rowmeta = ''
    rowmeta = (metavalues + (ae))
    rowmeta.insert(0,(str(a + 1) + '-' + str(uniqueid)))
    print(json.dumps(dict((zip(rowlabels, rowmeta)))))

    if a > 10:
        break





