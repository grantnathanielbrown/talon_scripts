from talon.voice import Word, Context, Key, Rep, RepPhrase, Str, press
from talon import ctrl, clip
from talon_init import TALON_HOME, TALON_PLUGINS, TALON_USER
import string

alpha_alt = 'air bat cap drum each fine gust harp sit jury crunch look made near bob pit quench red sun trap urge vest whale plex yank zip'.split()
###
alnum = list(zip(alpha_alt, string.ascii_lowercase)) + [(str(i), str(i)) for i in range(0, 10)]

alpha = {}
alpha.update(dict(alnum))
alpha.update({'ship %s' % word: letter for word, letter in zip(alpha_alt, string.ascii_uppercase)})

# modifier key mappings
fkeys = [(f'F {i}', f'f{i}') for i in range(1, 13)]
keys = [
    'left', 'right', 'up', 'down', 'shift', 'tab', 'escape', 'enter', 'space',
    'backspace', 'delete', 'home', 'pageup', 'pagedown', 'end',
]
keys = alnum + [(k, k) for k in keys]
keys += [
    ('tilde', '`'),
    ('comma', ','),
    ('dot', '.'),
    ('slash', '/'),
    ('(semi | semicolon)', ';'),
    ('quote', "'"),
    ('[left] square', '['),
    ('(right | are) square', ']'),
    ('backslash', '\\'),
    ('minus', '-'),
    ('equals', '='),
] + fkeys
alpha.update({word: Key(key) for word, key in fkeys})
alpha.update({'control %s' % k: Key('ctrl-%s' % v) for k, v in keys})
alpha.update({'control shift %s' % k: Key('ctrl-shift-%s' % v) for k, v in keys})
alpha.update({'control alt %s' % k: Key('ctrl-alt-%s' % v) for k, v in keys})
alpha.update({'command %s' % k: Key('cmd-%s' % v) for k, v in keys})
alpha.update({'command shift %s' % k: Key('cmd-shift-%s' % v) for k, v in keys})
alpha.update({'command alt shift %s' % k: Key('cmd-alt-shift-%s' % v) for k, v in keys})
alpha.update({'alt %s' % k: Key('alt-%s' % v) for k, v in keys})
alpha.update({'alt shift %s' % k: Key('alt-%s' % v) for k, v in keys})

# cleans up some Dragon output from <dgndictation>
mapping = {
    'semicolon': ';',
    'new-line': '\n',
    'new-paragraph': '\n\n',
}
# used for auto-spacing
punctuation = set('.,-!?')

def parse_word(word):
    word = str(word).lstrip('\\').split('\\', 1)[0]
    word = mapping.get(word, word)
    return word

def join_words(words, sep=' '):
    out = ''
    for i, word in enumerate(words):
        if i > 0 and word not in punctuation:
            out += sep
        out += word
    return out

def parse_words(m):
    return list(map(parse_word, m.dgndictation[0]._words))

def insert(s):
    Str(s)(None)

def text(m):
    insert(join_words(parse_words(m)).lower())

def sentence_text(m):
    text = join_words(parse_words(m)).lower()
    insert(text.capitalize())

def word(m):
    text = join_words(list(map(parse_word, m.dgnwords[0]._words)))
    insert(text.lower())

def surround(by):
    def func(i, word, last):
        if i == 0: word = by + word
        if last: word += by
        return word
    return func

def rot13(i, word, _):
    out = ''
    for c in word.lower():
        if c in string.ascii_lowercase:
            c = chr((((ord(c) - ord('a')) + 13) % 26) + ord('a'))
        out += c
    return out

formatters = {
    'dunder': (True,  lambda i, word, _: '__%s__' % word if i == 0 else word),
    'camel':  (True,  lambda i, word, _: word if i == 0 else word.capitalize()),
    'snake':  (True,  lambda i, word, _: word if i == 0 else '_'+word),
    'smash':  (True,  lambda i, word, _: word),
    # spinal or kebab?
    'kebab':  (True,  lambda i, word, _: word if i == 0 else '-'+word),
    # 'sentence':  (False, lambda i, word, _: word.capitalize() if i == 0 else word),
    'title':  (False, lambda i, word, _: word.capitalize()),
    'allcaps': (False, lambda i, word, _: word.upper()),
    'dubstring': (False, surround('"')),
    'string': (False, surround("'")),
    'padded': (False, surround(" ")),
    'rot-thirteen':  (False, rot13),
}

def FormatText(m):
    fmt = []
    for w in m._words:
        if isinstance(w, Word):
            fmt.append(w.word)
    try:
        words = parse_words(m)
    except AttributeError:
        with clip.capture() as s:
            press('cmd-c')
        words = s.get().split(' ')
        if not words:
            return

    tmp = []
    spaces = True
    for i, word in enumerate(words):
        word = parse_word(word)
        for name in reversed(fmt):
            smash, func = formatters[name]
            word = func(i, word, i == len(words)-1)
            spaces = spaces and not smash
        tmp.append(word)
    words = tmp

    sep = ' '
    if not spaces:
        sep = ''
    Str(sep.join(words))(None)

ctx = Context('input')

keymap = {}
keymap.update(alpha)
keymap.update({




    'phrase <dgndictation> [over]': text,

    'sentence <dgndictation> [over]': sentence_text,
    'comma <dgndictation> [over]': [', ', text],
    'period <dgndictation> [over]': ['. ', sentence_text],
    'more <dgndictation> [over]': [' ', text],
    'word <dgnwords>': word,

    '(%s)+ [<dgndictation>]' % (' | '.join(formatters)): FormatText,

    'tab':   Key('tab'),
    'left':  Key('left'),
    'right': Key('right'),
    'up':    Key('up'),
    'down':  Key('down'),
    'delete': Key('backspace'),

    'slap': [Key('cmd-right enter')],
    'enter': Key('enter'),
    'escape': Key('esc'),
    'question [mark]': '?',
    'tilde': '~',
    '(bang | exclamation point)': '!',
    'dollar [sign]': '$',
    'downscore': '_',
    '(semi | semicolon)': ';',
    'colon': ':',
    '(square | left square [bracket])': '[', '(rsquare | are square | right square [bracket])': ']',
    '(paren | left paren)': '(', '(rparen | are paren | right paren)': ')',
    '(brace | left brace)': '{', '(rbrace | are brace | right brace)': '}',
    '(angle | left angle | less than)': '<', '(rangle | are angle | right angle | greater than)': '>',

    '(star | asterisk)': '*',
    '(pound | hash [sign] | octo | thorpe | number sign)': '#',
    'percent [sign]': '%',
    'caret': '^',
    'at sign': '@',
    '(and sign | ampersand | amper)': '&',
    'pipe': '|',

    '(dubquote | double quote)': '"',
    'quote': "'",
    'triple quote': "'''",
    '(dot | period)': '.',
    'comma': ',',
    'space': ' ',
    '[forward] slash': '/',
    'backslash': '\\',

    '(dot dot | dotdot)': '..',
    'cd': 'cdls ',
    'cd talon home': 'cd {}'.format(TALON_HOME),
    'cd talon user': 'cd {}'.format(TALON_USER),
    'cd talon plugins': 'cd {}'.format(TALON_PLUGINS),

    'run make (durr | dear)': 'mkdir ',
    'run get': 'git ',
    'run get (R M | remove)': 'git rm ',
    'run get add': 'git add ',
    'run get bisect': 'git bisect ',
    'run get branch': 'git branch ',
    'run get checkout': 'git checkout ',
    'run get clone': 'git clone ',
    'run get commit': 'git commit ',
    'run get diff': 'git diff ',
    'run get fetch': 'git fetch ',
    'run get grep': 'git grep ',
    'run get in it': 'git init ',
    'run get log': 'git log ',
    'run get merge': 'git merge ',
    'run get move': 'git mv ',
    'run get pull': 'git pull ',
    'run get push': 'git push ',
    'run get rebase': 'git rebase ',
    'run get reset': 'git reset ',
    'run get show': 'git show ',
    'run get status': 'git status ',
    'run get tag': 'git tag ',
    'run (them | vim)': 'vim ',
    'run L S': 'ls\n',
    'dot pie': '.py',
    'run make': 'make\n',
    'run jobs': 'jobs\n',

    'const': 'const ',
    # 'static': 'static ',
    'tip pent': 'int ',
    'tip char': 'char ',
    'tip byte': 'byte ',
    'tip pent 64': 'int64_t ',
    'tip you went 64': 'uint64_t ',
    'tip pent 32': 'int32_t ',
    'tip you went 32': 'uint32_t ',
    'tip pent 16': 'int16_t ',
    'tip you went 16': 'uint16_t ',
    'tip pent 8': 'int8_t ',
    'tip you went 8': 'uint8_t ',
    'tip size': 'size_t',
    'tip float': 'float ',
    'tip double': 'double ',

    'args': ['()', Key('left')],
    'index': ['[]', Key('left')],
    'block': [' {}', Key('left enter')],
    'empty array': '[]',
    'empty dict': '{}',

    'state (def | deaf | deft)': 'def ',
    'state else if': 'elif ',
    'state if': 'if ()',
    'state else if': [' else if ()', Key('left')],
    'state while': ['while ()', Key('left')],
    'state for': ['for ()', Key('left')],
    'state for': 'for ',
    'state switch': ['switch ()', Key('left')],
    'state case': ['case \nbreak;', Key('up')],
    'state goto': 'goto ',
    'state import': 'import ',
    'state class': 'class ',

    'state include': '#include ',
    'state include system': ['#include <>', Key('left')],
    'state include local': ['#include ""', Key('left')],
    'state type deaf': 'typedef ',
    'state type deaf struct': ['typedef struct {\n\n};', Key('up'), '\t'],

    'comment see': '// ',
    'comment py': '# ',

    'word queue': 'queue',
    'word eye': 'eye',
    'word bson': 'bson',
    'word iter': 'iter',
    'word no': 'NULL',
    'word cmd': 'cmd',
    'word dup': 'dup',
    'word streak': ['streq()', Key('left')],
    'word printf': 'printf',
    'word (dickt | dictionary)': 'dict',
    'word shell': 'shell',

    'word lunixbochs': 'lunixbochs',
    'word talon': 'talon',
    'word Point2d': 'Point2d',
    'word Point3d': 'Point3d',
    'title Point': 'Point',
    'word angle': 'angle',

    'dunder in it': '__init__',
    'self taught': 'self.',
    'dickt in it': ['{}', Key('left')],
    'list in it': ['[]', Key('left')],
    'string utf8': "'utf8'",
    'state past': 'pass',

    'equals': '=',
    '(minus | dash)': '-',
    'plus': '+',
    'fat arrow': '=> ',
    # 'call': '()',
    'indirect': '&',
    'dereference': '*',
    '(op equals | assign)': ' = ',
    'op (minus | subtract)': ' - ',
    'op (plus | add)': ' + ',
    'op (times | multiply)': ' * ',
    'op divide': ' / ',
    'op mod': ' % ',
    '[op] (minus | subtract) equals': ' -= ',
    '[op] (plus | add) equals': ' += ',
    '[op] (times | multiply) equals': ' *= ',
    '[op] divide equals': ' /= ',
    '[op] mod equals': ' %= ',

    '(op | is) greater [than]': ' > ',
    '(op | is) less [than]': ' < ',
    '(op | is) equal': ' == ',
    '(op | is) not equal': ' != ',
    '(op | is) greater [than] or equal': ' >= ',
    '(op | is) less [than] or equal': ' <= ',
    '(op (power | exponent) | to the power [of])': ' ** ',
    'operation and': ' && ',
    'operation or': ' || ',
    '[op] (logical | bitwise) and': ' & ',
    '[op] (logical | bitwise) or': ' | ',
    '(op | logical | bitwise) (ex | exclusive) or': ' ^ ',
    '[(op | logical | bitwise)] (left shift | shift left)': ' << ',
    '[(op | logical | bitwise)] (right shift | shift right)': ' >> ',
    '(op | logical | bitwise) and equals': ' &= ',
    '(op | logical | bitwise) or equals': ' |= ',
    '(op | logical | bitwise) (ex | exclusive) or equals': ' ^= ',
    '[(op | logical | bitwise)] (left shift | shift left) equals': ' <<= ',
    '[(op | logical | bitwise)] (right shift | shift right) equals': ' >>= ',

    'shebang bash': '#!/bin/bash -u\n',

    'new window': Key('cmd-n'),
    'next window': Key('cmd-`'),
    # 'last window': Key('cmd-shift-`'),
    # 'next app': Key('cmd-tab'),
    # 'last app': Key('cmd-shift-tab'),
    # 'next tab': Key('ctrl-tab'),
    # 'new tab': Key('cmd-t'),
    # 'last tab': Key('ctrl-shift-tab'),

    'next space': Key('cmd-alt-ctrl-right'),
    'last space': Key('cmd-alt-ctrl-left'),

    'scroll down': [Key('down')] * 30,
    'scroll up': [Key('up')] * 30,

# this is the end of the premade script.


    # GRANT COMMANDS
    'revert': Key('cmd-z'),
    'super': [Key('up')] * 130,
    'drop': [Key('down')] * 130,
    'grabby': Key('cmd-a'),
    'rover': Key('cmd-f'),
    'remove':[Key('shift-alt-left'), Key('delete')],
    'login laptop': ['JV4stock', Key('enter')],
    'starchy': Key('cmd-space'),
    'copy': Key('cmd-c'),
    'paste': Key('cmd-v'),
    'cut': Key('cmd-x'),
    'plaintext paste': Key('cmd-alt-v'),
    'shield': Key('cmd-s'),
    'select line': [Key('home'), Key('shift-end')],
    'fast forward line': Key('end'),  
    'quit application': Key('cmd-q'),
    'rearrange up': Key('alt-up'),
    'rearrange down': Key('alt-down'),
    'continue thought': Key('shift-enter'),
    'chrome back': Key('cmd-left'),
    'rewind line': Key('home'),
    'rinse': [Key('home'), Key('delete')],
    'bold': Key('cmd-b'),
    'api': 'API',
    'hometown': 'McLean',
    '(mongo | mungo)': 'MongoDB',                      
    # JAVASCRIPT / VSCODE
    'javascript console': ['console.log();', Key('left'), Key('left')],
    'comment out': [Key('cmd-/')],
    'develop': Key('cmd-alt-i'),
    'let': 'let ',
    'sequence': 'Array',
    'function': 'function ',
    'skittish': 'string',
    'classic loop': "for (i = 0; i < x; i++) ",
    'classic conditional': ['if () {}', Key('left'), Key('enter'), Key('up')],
    'binder': Key('cmd-b'),
    'close studio tabs':[Key('cmd-k'), Key('w')],
    'super rover': Key('cmd-shift-f'),
    'select similar': Key('cmd-d'),
    'storm select similar': Key('ctrl-g'),
    'storm ultimate select similar': Key('ctrl-cmd-g'),
    'super select similar': [Key('cmd-d')] * 10,
    'ultimate select similar': [Key('cmd-d')] * 100,
    'chrome reload': Key('cmd-r'),
    'chrome hard reload': Key('cmd-r'),
    'chrome reopen': Key('cmd-shift-t'),
    'new variable': 'var ',
    'tiny skittish': 'str',
    'sprout': Key('cmd-enter'),
    'grant email': 'gnb225@nyu.edu',
    'trillian e-mail': 'gbrown@ttsiglobal.com',
    'storage room': 'GitHub',
    'studio consul': Key('ctrl-`'),
    'divider': '<div ',
    'evict': [Key('backspace')] * 10,
    'ultimate evict': [Key('backspace')] * 100,
    'get remove': Key('ctrl-w'),
    'ticker': Key('`'),
    'latex': Key('cmd-enter'),
    'possess':Key('shift-alt-left'),
    'alternate': Key('cmd-tab'),
    'new jack': Key('cmd-t'),
    'anterior': Key('ctrl-shift-tab'),
    'posterior': Key('ctrl-tab'),
    'close window': Key('cmd-w'),
    'deliver': 'import ',
    'grants website': 'https://grantnbrown.com/',
    'frontal mount': Key('ctrl-p'),
    'japan': 'Anime',
    'cultivate': Key('cmd-k'),
    'lightsaber': 'https://www.linkedin.com/in/grantnbkbrown/',
    'grant phone': '571-249-8475',
    'coliseum': 'Reddit',
    'redux': 'redux',
    'bridge':' = ',
    'walkway': ' - ',
    'jason': 'JSON',
    'access state': 'this.state.',
    'access props': 'this.props.',
    'set state': ['this.setState({})', Key('left'), Key('left')],
    'grant address': '829 Whann Avenue',
    'grant full name': 'Grant Nathaniel Brown',
    'bold': Key('cmd-b'),
    'normalized text': Key('cmd-alt-0'),      
    'arrow skeleton': [' () => {}', Key('left'), Key('enter')],
    'initialize react class': ['constructor() {}', Key('left'), Key('enter'), 'super()'],
    'important skeleton': "import  from ''; ",
    'reactor': 'React',
    "doesn't change": 'constants',
    "genesis": 'create-react-app',
    "combination": ".com",
    "jester": "jest",
    "engraving": "title",
    "assist": "bootstrap",
    "binding skeleton": "this. = this..bind(this);",
    "rewind indent": Key('shift-tab'),
    "motel": "modal",
    "paramus": "params",
    "open fema": "OpenFEMA",
    "last company": "Trillion Technology Solutions",
    "finder uber": Key('cmd-up'),
    "edit time jobs": "EDITOR=nano crontab -e",
    "pringles": "stack",
    "grant storage room": "https://github.com/grantnathanielbrown",
    # "pointer finger": "index",
# SCRIPT OPTIMIZATION IDEAS
# - automatically capitalize i
# - phrase toggle
# - unlock function keys
# - 





    # TERMINAL
    'showy': ['ls', Key('enter')],
    'hidden showy': ['ls -a', Key('enter')],
    'terminal delete': Key('ctrl-c'),
    # 'run ad': 'git add .',
    # 'run commit': ['git commit -m ""', Key('left')],
    'run gp': 'git push origin ',
    'run get remote': 'git remote -v',
    'package manager server': ['npm start', Key('enter')],
    'package manager install': 'npm i ',
    'package manager build': ['npm run build', Key('enter')],
    'package manager deploy': ['npm run deploy', Key('enter')],
    'package manager upload': ['npm run build && npm run deploy', Key('enter')],  
    'package manager test': ['npm run test', Key('enter')],
    'save dev': '--save-dev',    
    'open in studio': ['code .', Key('enter')],
    'heroic': 'heroku',
    'uber': ['cdls ..', Key('enter')],
    'note': 'node',
    'no demons': 'nodemon',
    'get check out': 'git checkout',
    'heroic push': 'git push heroku master',
    


    
    
    
})
ctx.keymap(keymap)  