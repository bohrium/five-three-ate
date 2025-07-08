#   author: samtenka
#   change: 2025-07-07
#   create: 2025-07-07
#   descrp: TODO
#   to use: TODO

import sys

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

SCALES_53_from_7 = {
    #
    #         9   8   9   5 * 8   9   5     89 989
    'LYD':[ 0,  9,  17, 26, 31, 39, 48,],
    #                   |
    #                   |                               | 4
    #       * 9   8   5 | 9   8   9   5     98 989
    'MAJ':[ 0,  9,  17, 22, 31, 39, 48,],
    #                               |
    #                               |                   | 7
    #         9   8   5 * 9   8   5 | 9     98 998
    'MIX':[ 0,  9,  17, 22, 31, 39, 44,],
    #               |
    #               |                                   | 3
    #         9   5 | 8   9   8   5 * 9     99 898
    'DOR':[ 0,  9,  14, 22, 31, 39, 44,],
    #                           |
    #                           |                       | 6
    #         9   5 * 8   9   5 | 8   9     89 899
    'MIN':[ 0,  9,  14, 22, 31, 36, 44,],
    #
}
C_NAMES = 'CDEFGAB'

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

INTERVALS_BY_NAME = {
    'M2-': 8,
    'M2' : 9,
    'M2+':10,
    'm3-':12,
    'm3' :14,
    'M3' :17,
    'M3+':19,
     '4' :22,
     't' :26,
     'T' :27,
     '5' :31,
    'm6-':34,
    'm6' :36,
    'M6' :39,
    'M6+':41,
    'M7-':43,
    'M7' :44,
    'M7+':45,
}

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


def process_chunk(c):
    flanked_staff, annotations = c.split('\nwhere\n')
    flanked_staff = flanked_staff.split('\n')
    assert len(flanked_staff) == 3+9+3
    #assert flanked_staff[0]==prefix+ruling
    #assert flanked_staff[-1]==prefix+ruling

    all_notes = {}

    staff = flanked_staff#[1:-1]
    offset_idx, offset_val = get_offset(staff)
    for i,ln in enumerate(staff):
        val_7 = offset_idx - i + offset_val
        val_53 = val_53_from_7(val_7)
        #notes = process_line(ln[len(prefix):])
        #notes = [
        #    (start, end, val_53 + mod_val_53(modstr), name)
        #    for
        #    (start, end, name, modstr) in notes
        #        ]
        for (start, end, name, modstr) in process_line(ln[len(prefix):]):
            modval_53 = val_53 + mod_val_53(modstr)
            assert name not in all_notes, "a bar's notes must have distinct names"
            all_notes[name] = (start, end, modval_53)
        #print(val_53, notes)
   #$print(all_notes)

    all_constraints = []
    constraints = annotations.split('\n')
    for ln in constraints:
        if ln=='.': continue
        lo, hi, iname = ln.split()
        interval = interval_from_name(iname)
        assert lo in all_notes
        assert hi in all_notes
        start = min(all_notes[nm][0] for nm in (lo,hi))
        loval, hival = (all_notes[nm][2] for nm in (lo,hi))
        assert loval < hival
        sortby = (start, loval, hival)
        all_constraints.append((sortby, lo, hi, interval))
    all_constraints = sorted(all_constraints)
    #print(all_constraints)

    for _, lo, hi, interval in all_constraints:
        # TODO: by precedence (before-ness or lowness)
        slo, elo, vlo = all_notes[lo]
        shi, ehi, vhi = all_notes[hi]
        new_vhi = vlo + interval
        print(all_notes[lo], all_notes[hi], interval)
        assert abs(new_vhi - vhi) < 4, str((new_vhi, vhi))
        assert vhi != vlo
        assert (new_vhi<vlo and vhi<vlo) or (new_vhi>vlo and vhi>vlo)
        all_notes[hi] = (shi, ehi, new_vhi)
    #print(all_notes)

for c in body:
    process_chunk(c)
