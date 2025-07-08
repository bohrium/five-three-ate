#   author: samtenka
#   change: 2025-07-07
#   create: 2025-07-07
#   descrp: TODO
#   to use: TODO

import sys

#in_name = sys.argv[1]
#with open(in_name) as f:
#    text = f.read()


text = '''6 x 12

.   |           |           |           |           |           |           |
.
.
.
.
.
.   |-----------------------------------------------------------------------|
.   |                                                                       |
.   |-----------------------------------------------------------------------|
.   |                                                                       |
.   |(=========)------------------------------------------------------------|
.   |                                                                       |
G4  |-----------------------------------------------------------------------|
.   |                                                                       |
.   |-----------------------------------------------------------------------|
.
.       (==)
.
.
.
.   |           |           |           |           |           |           |
where
null


'''

chunks = list(filter(None, map(str.strip, text.split('\n\n'))))

header, body = chunks[0], chunks[1:]
beats_per_bar, ticks_per_beat = map(int, header.split('x'))

prefix = '.   '
ruling = ('|'+' '*(ticks_per_beat-1))*beats_per_bar + '|'

def process_line(ln):
    notes = []
    start = None
    name = ''
    for i,c in enumerate(ln):
        if c=='(':
            assert start is None
            start = i
            name = ''
        elif c ==')':
            notes.append((start, i, name))
            start = None
            name = ''
        elif start is not None:
            name += c
    assert start is None
    return notes

FOURTH_7tet = 3
FIFTH_7tet  = 4
CLEF_ANCHOR_VALS_BY_NAME = {'F3':-FIFTH_7tet, 'C4':0, 'G4':+FIFTH_7tet}

def get_offset(staff):
    starts = [(i,ln.split()[0]) for i,ln in enumerate(staff)]
    starts = [(i,s) for i,s in starts if s != '.']
    print(starts)
    assert len(starts)==1
    idx, name = starts[0]
    assert name in CLEF_ANCHOR_VALS_BY_NAME, 'clef unrecognized!'
    val = CLEF_ANCHOR_VALS_BY_NAME[name]
    return (idx, val)

def process_chunk(c):
    flanked_staff, annotations = c.split('\nwhere\n')
    flanked_staff = flanked_staff.split('\n')
    assert len(flanked_staff) == 1+5+9+5+1
    assert flanked_staff[0]==prefix+ruling
    assert flanked_staff[-1]==prefix+ruling

    staff = flanked_staff[1:-1]
    offset_idx, offset_val = get_offset(staff)
    for i,ln in enumerate(staff):
        val = offset_idx - i + offset_val
        notes = process_line(ln[len(prefix):])
        print(val, notes)

for c in body:
    process_chunk(c)
