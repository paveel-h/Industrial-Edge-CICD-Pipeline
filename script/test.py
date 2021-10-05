import sys
import json

if json.load(sys.stdin)['versions'] == []:
    pass
else:
    json.load(sys.stdin)['versions'][0]['versionNumber']
