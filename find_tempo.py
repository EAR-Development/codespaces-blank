from zipfile import ZipFile
from xml.dom.minidom import parse, parseString, Element
from collections import defaultdict

import sys

from lengthhelper import get_length_list

from printhelper import create_line

def get_relevant_events(part):
    events = []

    for measure in part.getElementsByTagName('measure'):
        for child in measure.childNodes:
            if not isinstance(child, Element):
                continue

            if child.tagName == 'note':
                events.append(child)
                continue
            elif child.tagName != 'direction':
                continue

            if child.getElementsByTagName('sound'):
                sound_directive = child.getElementsByTagName('sound')[0]
                events.append(sound_directive)
    return events

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
        
        events = get_relevant_events(part)        
        print(events)

if __name__ == "__main__":
    main()