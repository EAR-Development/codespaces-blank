from itertools import combinations_with_replacement

LENGTH_LOOKUP = {
    4.0     : 'FULL',
    3.0     : 'HALF_DOTTED',
    2.0     : 'HALF',
    1.5     : '04TH_DOTTED',
    1.0     : '04TH',
    0.75    : '08TH_DOTTED',
    0.5     : '08TH',
    0.25    : '16TH',
    0.125   : '32TH',
}
def get_length_list(duration: float) -> list[str]:
    found = False
    candidate = []
    for size in range(0, len(LENGTH_LOOKUP)):
        for candidate in combinations_with_replacement(LENGTH_LOOKUP.keys(), size):
            if(sum(candidate) == duration):
                found = True
                break
        if found:
            break
    return list(LENGTH_LOOKUP[c] for c in candidate)

if __name__ == "__main__":
    for duration in [0.5, 1.0, 1.5, 2.5, 3.0, 4.0, 4.5]:
        print(duration, get_length_list(duration))