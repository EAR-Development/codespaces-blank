from zipfile import ZipFile
from xml.dom.minidom import parse, parseString
from collections import defaultdict
from pprint import pprint

# Parse XML from compressed musicXML
zip = ZipFile('with-ghost.mxl')
filename = list(el for el in zip.namelist() if not el.startswith('META-INF/'))[0]
file = zip.open(filename)
dom = parseString(file.read())

LENGTH_LOOKUP = {
    1: '04TH',
    2: 'HALF',
    0.5: '08TH',
    1.5: '04TH_DOTTED',
}

DEVICE_LOOKUP = {
    'P2': 'LEFT',
    'P1': 'RIGHT',
}

print('Collecting Metadata')
part_list = dom.getElementsByTagName('part-list')[0]
part_ids = [el.getAttribute('id') for el in part_list.getElementsByTagName('score-part')]

print('Collect Notes')
parts = dom.getElementsByTagName('part')
parts = {part.getAttribute('id'):part for part in parts}

hit_dict = defaultdict(dict)

for part_id, part in parts.items():
    print(part_id)

    attributes = part.getElementsByTagName('attributes')[0]
    divisions = attributes.getElementsByTagName('divisions')[0].firstChild.nodeValue
    divisions = int(divisions)

    print('Divisions', divisions)
    
    notes = part.getElementsByTagName('note')

    current_count = 0

    for note in notes:
        if note.getElementsByTagName('rest'):
            duration = note.getElementsByTagName('duration')[0].firstChild.nodeValue
            duration = int(duration)

            note_length = duration / divisions
            current_count += note_length
            continue

        if note.getElementsByTagName('tie') and note.getElementsByTagName('tie')[0].getAttribute('type') == 'stop':
            duration = note.getElementsByTagName('duration')[0].firstChild.nodeValue
            duration = int(duration)

            note_length = duration / divisions
            current_count += note_length
            continue

        pitch_info = note.getElementsByTagName('pitch')[0]
        step = pitch_info.getElementsByTagName('step')[0].firstChild.nodeValue
        octave = int(pitch_info.getElementsByTagName('octave')[0].firstChild.nodeValue) - 4

        # Alter
        if pitch_info.getElementsByTagName('alter'):
            alter = pitch_info.getElementsByTagName('alter')[0].firstChild.nodeValue
            pitch = step + 'S' + str(octave) 
        else:
            pitch = step + str(octave)

        # Muted Notes
        muted = False
        if note.getElementsByTagName('notehead'):
            if note.getElementsByTagName('notehead')[0].firstChild.nodeValue == 'x':
                print('found muted')
                muted = True

        duration = note.getElementsByTagName('duration')[0].firstChild.nodeValue
        duration = int(duration)

        note_length = duration / divisions
        length_tag = LENGTH_LOOKUP.get(note_length, f'UNKNOWN_NOTE_LENGTH_{note_length}')
        
        hit_dict[current_count][str(part_id)] = (pitch, note_length, muted)
        current_count += note_length

    hit_dict[current_count][part_id] = 'END'
    end_time = current_count

hit_dict = dict(hit_dict)
print(hit_dict)

lines = [] 

time_stamps = sorted(hit_dict.keys())

for i, start in enumerate(time_stamps):
    print(start)

    hit = hit_dict[start]

    print(hit)
    end = time_stamps[i+1]
    duration = end - start
    
    length_tag = LENGTH_LOOKUP.get(duration, f'UNKNOWN_NOTE_LENGTH_{duration}')
    mallets = list(hit.keys())

    if len(mallets) == 2:
        hitting_device = 'BOTH'
        
        first = mallets[0]
        first_device = DEVICE_LOOKUP[first]
        first_pitch, _, first_muted = hit[first]

        spacer = '' if 'S' in first_pitch else ' '

        lines.append(f'{{NOTE_{first_device[0]}_{first_pitch}, {spacer}HIT_NONE,  PAUSE_NONE }}')

        second = mallets[1]
        second_device = DEVICE_LOOKUP[second]
        second_pitch, _, second_muted = hit[second]
        
        spacer = '' if 'S' in second_pitch else ' '

        if first_muted and second_muted:
            hit_device = 'HIT_NONE'
        elif not first_muted and not second_muted:
            hit_device = 'HIT_BOTH'
        elif first_muted and not second_muted:
            hit_device = f'HIT_{second_device}'
        elif not first_muted and second_muted:
            hit_device = f'HIT_{first_device}'
        
        
        lines.append(f'{{NOTE_{second_device[0]}_{second_pitch}, {spacer}{hit_device},  PAUSE_{length_tag} }}')

    else:
        second = mallets[0]
        second_device = DEVICE_LOOKUP[second]
        second_pitch, _, muted = hit[second]

        spacer = '' if 'S' in second_pitch else ' '
        spacer_2 = '' if 'RIGHT' in second_device else ' '
        
        if not muted:
            lines.append(f'{{NOTE_{second_device[0]}_{second_pitch}, {spacer}HIT_{second_device}, {spacer_2}PAUSE_{length_tag} }}')
        else:
            lines.append(f'{{NOTE_{second_device[0]}_{second_pitch}, {spacer}HIT_NONE, {spacer_2}PAUSE_{length_tag} }}')

    if end == end_time:
        break


    with open('out.nxc', 'w') as f:
        f.write('#include "chimes_note_constants.nxc";\n')
        f.write('const string filename = "song_tetris.dat";\n')
        f.write('byte SONG[][] = {\n')

        f.writelines('   ' + line + ',\n' for line in lines)

        f.write('};\n')
        f.write('#include "chimes_note_writer.nxc";')