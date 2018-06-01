#!/usr/bin/env python

from __future__ import print_function, unicode_literals

from datetime import datetime, timedelta
import sys
import json

with open(sys.argv[1]) as f:
    data = json.load(f)

invocations = dict(enumerate(data['invocations']))


def display_name(invocation):
    return '%s v%s %s %s' % (
        invocation['package_name'],
        invocation['package_version'],
        invocation['target_kind'][0],
        invocation['kind'],
    )


output = []
seen = set()

round = 0
while invocations:
    next_seen = set()
    for (i, item) in invocations.items():
        if any(d not in seen for d in item['deps']):
            continue
        output.append((round, i, item))
        next_seen.add(i)
        del invocations[i]
    print('Round %d: %d items seen' % (round, len(next_seen)))
    round += 1
    seen.update(next_seen)

def fmtdate(d):
    return d.strftime('new Date(%Y, "%m" - 1, "%d", "%H", "%M", "%S")')

start = datetime.now()
with open('data.js', 'wb') as f:
    f.write('var build_data = [\n')
    for (round, i, item) in output:
        item_start = start + timedelta(seconds=round)
        item_end = item_start + timedelta(seconds=1)
        f.write('["%d", "%s", %s, %s, null,  100,  "%s"],\n' % (
            i, display_name(item), fmtdate(item_start), fmtdate(item_end),
            ','.join(str(d) for d in item['deps']))
        )
    f.write('];\n')
