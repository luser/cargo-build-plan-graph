#!/usr/bin/env python

from __future__ import print_function, unicode_literals

import argparse
from datetime import datetime, timedelta
import os
import sys
import json


parser = argparse.ArgumentParser(
    description='Add timing info from cargo profile to cargo build plan')
parser.add_argument('build_plan', help='A cargo build plan in JSON format')
parser.add_argument('profile', help='A cargo profile in JSON format')
args = parser.parse_args()

with open(args.build_plan) as f:
    build_plan = json.load(f)

with open(args.profile) as f:
    # The profile isn't well-formed JSON, so fix it up.
    # It has a trailing comma and is missing a closing bracket.
    data = f.read() + '{} ]'
    profile = json.loads(data)


def key(d):
    return (d['package_name'], d['package_version'], d['kind'], ','.join(d['target_kind']))


def us_to_ms(u):
    return u / 1000


times = {}
build_script_times = {}
for p in profile:
    if p.get('name', '').startswith('building:'):
        k = key(p['args'])
        v = (us_to_ms(p['ts']), us_to_ms(p['ts'] + p['dur']))
        if p['args']['build_script']:
            build_script_times[k] = v
        else:
            times[k] = v

for i in build_plan['invocations']:
    k = key(i)
    if i['target_kind'] == ['custom-build'] and not os.path.basename(i['program']).startswith('rustc'):
        src = build_script_times
    else:
        src = times
    if k not in src:
        raise Exception('Missing timing info for invocation: %s' % str(k))
    start, end = src[k]
    i['start'] = start
    i['end'] = end

json.dump(build_plan, sys.stdout)
