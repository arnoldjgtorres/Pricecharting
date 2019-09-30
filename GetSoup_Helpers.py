import smtplib
from difflib import SequenceMatcher
from heapq import nlargest as _nlargest



pricecharting_consoles = {
        'Playstation 4': 'playstation-4',
        'Playstation 3': 'playstation-3',
        'Playstation 2': 'playstation-2',
        'Playstation One': 'playstation',
        'PS Vita': 'playstation-vita',
        'PSP': 'psp',
        'Nintendo Switch': 'nintendo-switch',
        'Nintendo Wii U': 'wii-u',
        'Nintendo Wii': 'wii',
        'Nintendo Gamecube': 'gamecube',
        'Nintendo 64': 'nintendo-64',
        'SNES': 'super-nintendo',
        'NES': 'nes',
        'Nintendo 3DS': 'nintendo-3ds',
        'Nintendo DS': 'nintendo-ds',
        'Nintendo Gameboy Advance': 'gameboy-advance',
        'Nintendo Gameboy Color': 'gameboy-color',
        'Nintendo Gameboy': 'gameboy',
        'Xbox One': 'xbox-one',
        'Xbox 360': 'xbox-360',
        'Xbox': 'xbox',
        'Sega Genesis': 'sega-genesis',
        'Sega Saturn': 'sega-saturn',
        'Sega Dreamcast': 'sega-dreamcast'
}



def has_numbers(inputString):
    return any(char.isdigit() for char in inputString)


def convert(url):
    if url.startswith('https://www.'):
        return 'https://www.' + url[len('https://www.'):]
    if url.startswith('www.'):
        return 'https://www.' + url[len('www.'):]
    if not url.startswith('https://'):
        return 'https://www.' + url
    return url

def get_close_matches_indexes(word, possibilities, n=3, cutoff=0.6):

    if not n > 0:
        raise ValueError("n must be > 0: %r" % (n,))
    if not 0.0 <= cutoff <= 1.0:
        raise ValueError("cutoff must be in [0.0, 1.0]: %r" % (cutoff,))
    result = []
    s = SequenceMatcher()
    s.set_seq2(word)
    for idx, x in enumerate(possibilities):
        s.set_seq1(x)
        if s.real_quick_ratio() >= cutoff and \
           s.quick_ratio() >= cutoff and \
           s.ratio() >= cutoff:
            result.append((s.ratio(), idx))

    # Move the best scorers to head of list
    result = _nlargest(n, result)

    # Strip scores for the best n matches
    return [x for score, x in result]

#for future email use on specific items, run on server
def send_mail():
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.ehlo()
    server.starttls()
    server.ehlo()

    server.login('arnoldjgtorres@gmail.com', 'google two way authenticatio')

    subject= 'Price fell down'
    body = 'Check the amazon link: link_here'
    msg = f"Subject: {subject}\n\n{body}"

    server.sendmail(
        'arnoldjgtorres@gmail.com',
        'anotheremail',
        msg
    )
    print("SENT EMAIL")
    server.close()
