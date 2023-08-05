from mido import MidiFile
from collections import defaultdict
from pprint import pprint

mid = MidiFile('simple.mid')

def is_hit_message(msg):
    return not msg.is_meta and msg.type == 'note_on' and msg.velocity == 0 and msg.time > 0

tpb = mid.ticks_per_beat

# 32nd_notes manually (TODO: get from time_signature message)
notes_per_beat = 8

ticks_32 = tpb // notes_per_beat
ticks_16 = ticks_32 * 2
ticks_8 = ticks_16 * 2
ticks_4 = ticks_8 * 2
ticks_2 = ticks_4 * 2
ticks_3_8 = ticks_8 * 3

lookup = {
    ticks_2: 'HALF',
    ticks_4: '04TH',
    ticks_3_8: '04TH_DOTTED',
    ticks_8: '08TH',
    ticks_16: '16TH',
}

print(mid)


notes = defaultdict(dict)

current_time = 0
for msg in mid.tracks[0]:
    if is_hit_message(msg):
        length_type = lookup.get(msg.time + 1, f'TRANSPILE_TIME_ERROR: {msg.time}')
        #print(f'PAUSE_{length_type}')
        notes[current_time]['LEFT'] = (msg.note, length_type)
    
    current_time += msg.time

current_time = 0
for msg in mid.tracks[1]:
    if is_hit_message(msg):
        length_type = lookup.get(msg.time + 1, f'TRANSPILE_TIME_ERROR: {msg.time}')
        #print(f'PAUSE_{length_type}')
        notes[current_time]['RIGHT'] = (msg.note, length_type)
    
    current_time += msg.time
pprint(dict(notes))
