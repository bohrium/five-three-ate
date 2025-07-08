#   author: samtenka
#   change: 2025-07-07
#   create: 2025-07-07
#   descrp: TODO
#   to use: TODO

import sys

from musical_tables import (
        C_NAMES,
        INTERVALS_BY_NAME,
        SCALES_53_from_7,
        )

#in_name = sys.argv[1]
#with open(in_name) as f:
#    text = f.read()

MOD_SYMBS = '#^vb'

text = '''
6 x 12

.
.
.
.   |-----------+-----------+-----------+-----------+-----------+-----------|
.   |                                                                       |
.   |-----------+-----------+-----------+-----------+-----------+-----------|
.   |                                                                       |
.   |----------b(==moohi====)-----------+-----------+-----------+-----------|
.   |                                                                       |
G4  |-----------(==moomid===)-----------+-----------+-----------+-----------|
.   |                                                                       |
.   |----------b(==moolo====)-----------+-----------+-----------+-----------|
.
.
.
where
moolo moomid M3
moolo moohi   5
.


'''

chunks = list(filter(None, map(str.strip, text.split('\n\n'))))

header, body = chunks[0], chunks[1:]
beats_per_bar, ticks_per_beat = map(int, header.split('x'))

prefix = '.   '
ruling = ('|'+' '*(ticks_per_beat-1))*beats_per_bar + '|'

def process_line(ln, ignore_char='='):
    notes = []
    start = None
    name = ''
    modstr = ''
    for i,c in enumerate(ln):
        if c=='(':
            assert start is None
            assert name == ''
            start = i
            name = ''
        elif c ==')':
            if ignore_char:
                name = name.replace(ignore_char,' ').strip() # TODO: factor out?
            notes.append((start, i, name, modstr))
            start = None
            name = ''
            modstr = ''
        elif start is not None:
            name += c
        elif c in MOD_SYMBS:
            modstr += c
    assert start is None
    assert name == ''
    assert modstr == ''
    return notes

FOURTH_7 = 3
FIFTH_7  = 4
CLEF_ANCHOR_VALS_BY_NAME = {'F3':-FIFTH_7, 'C4':0, 'G4':+FIFTH_7}

def get_offset(staff):
    starts = [(i,ln.split()[0]) for i,ln in enumerate(staff)]
    starts = [(i,s) for i,s in starts if s != '.']
    assert len(starts)==1
    idx, name = starts[0]
    assert name in CLEF_ANCHOR_VALS_BY_NAME, 'clef unrecognized!'
    val = CLEF_ANCHOR_VALS_BY_NAME[name]
    return (idx, val)

def val_53_from_7(val_7):
    ''' assumes C major '''
    oct, off = val_7 // 7, val_7 % 7
    return 53*oct + SCALES_53_from_7['MAJ'][off]

def mod_val_53(modstr):
    counts = {m : modstr.count(m) for m in MOD_SYMBS}
    assert sum(counts.values()) == len(modstr)
    assert counts['#']+counts['b'] <= 1
    return (
        +4 * counts['#'] +
        +1 * counts['^'] +
        -1 * counts['v'] +
        -4 * counts['b']
        )

def interval_from_name(iname):
    '''
    NOTE: no signs (+/-) allowed
    For literal numbers, precede with "="
    '''
    assert iname in INTERVALS_BY_NAME or (iname[0]=='=' and iname[1:].isnumeric())
    if iname in INTERVALS_BY_NAME:
        return INTERVALS_BY_NAME[iname]
    else:
        return int(iname[1:])

#def sortby_from_start_end_val_by_name(start_end_val_by_name):
#    def sortby(name):
#        start, end, val = start_end_val_by_name[name]
#        return (start, val)
#    return sortby

def sortby(name, start_end_val_by_name):
    start, end, val = start_end_val_by_name[name]
    return (start, val)

def process_chunk(c, MAX_NUDGE = 3):
    staff, annotations = c.split('\nwhere\n')
    staff = staff.split('\n')
    assert len(staff) == 3+9+3

    all_notes = {}

    offset_idx, offset_val = get_offset(staff)
    for i,ln in enumerate(staff):
        val_7 = offset_idx - i + offset_val
        val_53 = val_53_from_7(val_7)
        for (start, end, name, modstr) in process_line(ln[len(prefix):]):
            modval_53 = val_53 + mod_val_53(modstr)
            assert name not in all_notes, "a bar's notes must have distinct names"
            all_notes[name] = (start, end, modval_53)
   #print(all_notes)

    all_constraints = []
    constraints = annotations.split('\n')
    for ln in constraints:
        if ln=='.': continue
        base, counter, iname = ln.split()
        interval = interval_from_name(iname)
        assert base in all_notes
        assert counter in all_notes
        start = min(all_notes[nm][0] for nm in (base,counter))
        loval, hival = (all_notes[nm][2] for nm in (base,counter))
        assert sortby(base, all_notes) < sortby(counter, all_notes)
        pair_sortby = tuple(sortby(nm, all_notes) for nm in (base,counter))
        all_constraints.append((sortby, base, counter, interval))
    all_constraints = sorted(all_constraints)
    #print(all_constraints)

    for _, base, counter, interval in all_constraints:
        s_base, e_base, v_base = all_notes[base]
        s_counter, e_counter, v_counter = all_notes[counter]
        new_v_counter = v_base + interval
        all_notes[counter] = (s_counter, e_counter, new_v_counter)
        assert sortby(base, all_notes) < sortby(counter, all_notes)
    print(all_notes)

for c in body:
    process_chunk(c)
