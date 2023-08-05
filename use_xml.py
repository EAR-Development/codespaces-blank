from zipfile import ZipFile
from xml.dom.minidom import parse, parseString
from collections import defaultdict
from pprint import pprint

# Parse XML from compressed musicXML
zip = ZipFile('simple.mxl')
filename = zip.filelist[0].filename
file = zip.open(filename)
dom = parseString(file.read())

LENGTH_LOOKUP = {
    1: '04TH',
    2: 'HALF',
    0.5: '08TH',
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
        pitch_info = note.getElementsByTagName('pitch')[0]
        step = pitch_info.getElementsByTagName('step')[0].firstChild.nodeValue
        octave = pitch_info.getElementsByTagName('octave')[0].firstChild.nodeValue
        pitch = step + octave

        duration = note.getElementsByTagName('duration')[0].firstChild.nodeValue
        duration = int(duration)

        note_length = duration / divisions
        length_tag = LENGTH_LOOKUP.get(note_length, 'UNKNOWN_NOTE_LENGTH')

        print(current_count, '>>', pitch, ':', length_tag)
        
        hit_dict[current_count][part_id] = (pitch, length_tag)
        current_count += duration

hit_dict = dict(hit_dict)
pprint(hit_dict)