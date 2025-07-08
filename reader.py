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
.   b(==long===)------------------------------------------------------------|
.   |                                                                       |
G4  |-----------------------------------------------------------------------|
.   |                                                                       |
.   |-----------------------------------------------------------------------|
.
.       (=s)
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
    modstr = ''
    for i,c in enumerate(ln):
        if c=='(':
            assert start is None
            assert name == ''
            start = i
            name = ''
        elif c ==')':
            name = name.replace('=',' ').strip() # TODO: factor out?
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

#def pitchclass_53_from_str(s):
#    '''assumes C major base'''
#    name_7tet, mods = s[0], s[1:]
#    assert name_7tet in C_NAMES
#    base = SCALES_53_from_7['MAJ'][C_NAMES.find(name7tet)]
#    counts = {m : mods.count(m) for m in MOD_SYMBS}
#    assert sum(counts.values()) == len(mods)
#    assert counts['#']+counts['b'] <= 1
#    mods = (
#        +4 * counts['#'] +
#        +1 * counts['^'] +
#        -1 * counts['v'] +
#        -4 * counts['#']
#        )
#    return base + mods

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

def val_53_from_7(val_7tet):
    ''' assumes C major '''
    oct, off = val_7tet // 7, val_7tet % 7
    return 53*oct + SCALES_53_from_7['MAJ'][off]

def mod_val_53tet(modstr):
    counts = {m : modstr.count(m) for m in MOD_SYMBS}
    assert sum(counts.values()) == len(modstr)
    assert counts['#']+counts['b'] <= 1
    return (
        +4 * counts['#'] +
        +1 * counts['^'] +
        -1 * counts['v'] +
        -4 * counts['b']
        )

def process_chunk(c):
    flanked_staff, annotations = c.split('\nwhere\n')
    flanked_staff = flanked_staff.split('\n')
    assert len(flanked_staff) == 1+5+9+5+1
    assert flanked_staff[0]==prefix+ruling
    assert flanked_staff[-1]==prefix+ruling

    staff = flanked_staff[1:-1]
    offset_idx, offset_val = get_offset(staff)
    for i,ln in enumerate(staff):
        val_7tet = offset_idx - i + offset_val
        val_53tet = val_53_from_7(val_7tet)
        notes = process_line(ln[len(prefix):])
        notes = [
            (start, end, val_53tet + mod_val_53tet(modstr), name)
            for
            (start, end, name, modstr) in notes
                ]
        print(val_53tet, notes)

for c in body:
    process_chunk(c)
