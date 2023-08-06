from zipfile import ZipFile
from xml.dom.minidom import parse, parseString
from collections import defaultdict

import sys

from lengthhelper import get_length_list
from printhelper import create_line
from find_tempo import get_relevant_events

def main():
    _, input_path, output_path = sys.argv
    # Parse XML from compressed musicXML
    zip_file = ZipFile(input_path)
    filename = list(el for el in zip_file.namelist() if not el.startswith('META-INF/'))[0]
    file = zip_file.open(filename)
    dom = parseString(file.read())

    DEVICE_LOOKUP = {
        'P2': 'LEFT',
        'P1': 'RIGHT',
    }

    DEVICE_DEFAULTS = {
        'P1': ('F1', 0.5, True),
        'P2': ('G1', 0.5, True),
    }

    print('Collecting Metadata')
    part_list = dom.getElementsByTagName('part-list')[0]
    part_ids = [el.getAttribute('id') for el in part_list.getElementsByTagName('score-part')]

    print('Collect Notes')
    parts = dom.getElementsByTagName('part')
    parts = {part.getAttribute('id'):part for part in parts}

    hit_dict = defaultdict(dict)
    tempo_dict = {}
    end_time = 0

    for part_id, part in parts.items():
        print(part_id)

        attributes = part.getElementsByTagName('attributes')[0]
        divisions = attributes.getElementsByTagName('divisions')[0].firstChild.nodeValue
        divisions = int(divisions)

        print('Divisions', divisions)

        events = get_relevant_events(part)

        current_count = 0

        for note in events:
            if note.tagName == 'sound':
                tempo_dict[current_count] = int(note.getAttribute('tempo'))
                continue

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
                # alter = pitch_info.getElementsByTagName('alter')[0].firstChild.nodeValue
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

            hit_dict[current_count][str(part_id)] = (pitch, note_length, muted)
            current_count += note_length

        hit_dict[current_count][part_id] = 'END'
        end_time = max(current_count, end_time)

    end_time += 1
    hit_dict[end_time] = DEVICE_DEFAULTS
    hit_dict = dict(hit_dict)
    
    print(hit_dict)
    print(tempo_dict)

    tempo_points = list(tempo_dict.keys())

    lines = []

    if 0 in tempo_dict:
        tempo_ms_32th = 60000 // (tempo_dict[0] * 8)
        lines.append(create_line('TEMPO', None, 'MS_32TH', tempo_ms_32th))

    time_stamps = sorted(hit_dict.keys())

    for i, start in enumerate(time_stamps):

        hit = hit_dict[start]

        end = time_stamps[i+1]
        duration = end - start

        new_tempo_bpm = None
        for p in tempo_points:
            if (start < p and end >= p):
                new_tempo_bpm = tempo_dict[p]
                print('After ', start, 'Tempo is ', new_tempo_bpm)
                break

        length_tag, *additional_rests = get_length_list(duration)
        mallets = list(hit.keys())

        if len(mallets) == 2:
            first = mallets[0]
            first_device = DEVICE_LOOKUP[first]
            first_pitch, _, first_muted = hit[first]

            second = mallets[1]
            second_device = DEVICE_LOOKUP[second]
            second_pitch, _, second_muted = hit[second]

            if first_muted and second_muted:
                hit_device = 'NONE'
            elif not first_muted and not second_muted:
                hit_device = 'BOTH'
            elif first_muted and not second_muted:
                hit_device = second_device
            elif not first_muted and second_muted:
                hit_device = first_device
                first_device, second_device = second_device, first_device
                first_pitch, second_pitch = second_pitch, first_pitch

            lines.append(create_line(first_device[0], first_pitch, "NONE",  "NONE"))
            lines.append(create_line(second_device[0], second_pitch, hit_device, length_tag))
        else:
            second = mallets[0]
            second_device = DEVICE_LOOKUP[second]
            second_pitch, _, muted = hit[second]

            if not muted:
                lines.append(create_line(second_device[0], second_pitch, second_device, length_tag))
            else:
                lines.append(create_line(second_device[0], second_pitch, "NONE", length_tag))

        for rest in additional_rests:
                lines.append(create_line(second_device[0], "NONE", "NONE", rest))

        if new_tempo_bpm:
            new_tempo_ms_32th = 60000 // (int(new_tempo_bpm)*8)
            lines.append(create_line('TEMPO', None, 'MS_32TH', new_tempo_ms_32th))

        if end == end_time:
            break

        with open(output_path, 'w', encoding='utf-8') as f:
            f.write('#include "chimes_note_constants.nxc";\n')
            f.write('const string filename = "song_tetris.dat";\n')
            f.write('byte SONG[][] = {\n')

            f.writelines('   ' + line + ',\n' for line in lines)

            f.write('};\n')
            f.write('#include "chimes_note_writer.nxc";')

if __name__=='__main__':
    main()
