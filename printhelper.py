def create_line(note_device, pitch, hit_device, pause_length):
    if pitch:
        note_constant = f'NOTE_{note_device}_{pitch}'
    else:
        note_constant = f'NOTE_{note_device}'
    note_spacer = ' ' * (12-len(note_constant))

    hit_constant = f'HIT_{hit_device}'
    hit_spacer = ' ' * (12-len(hit_constant))
    
    if type(pause_length) == str:
        pause_constant = f'PAUSE_{pause_length}'
    else:
        pause_constant = str(pause_length)

    pause_spacer = ' ' * (20-len(pause_constant))

    output = '{'
    output += note_constant + ',' + note_spacer
    output += hit_constant + ',' + hit_spacer
    output += pause_constant + pause_spacer
    output += '}'

    return output