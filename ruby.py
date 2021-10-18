# example usage
# cat index.html | python3 ruby.py | vim -

import re
import sys

def stripHtml(text):
    text = re.sub('<[^>]+>', '', text)
    return text

def convertRuby(text):
    '''convert ruby Japanese reading formatting to square bracket notation'''
    # <ruby> -> space
    text = re.sub('<ruby>', ' ', text)
    # remove close ruby tags
    text = re.sub('</ruby>', '', text)
    # change <rt> markers to brackets
    text = re.sub('<rt>', '[', text)
    text = re.sub('</rt>', ']', text)
    return text

def stripRuby(text):
    '''strip ruby Japanese reading formatting'''
    # remove open ruby tags
    text = re.sub('<ruby>', '', text)
    # remove close ruby tags
    text = re.sub('</ruby>', '', text)
    # remove everything between rt tags
    text = re.sub('<rt>[^<]*</rt>', '', text)
    return text

def convertHTML(text):
    text = re.sub('</p>', '\n', text)
    text = re.sub('</div>', '\n', text)
    text = re.sub('<br>', '\n', text)
    text = re.sub('<br\s*/>', '\n', text)
    text = re.sub('\n\n\n+', '\n\n\n', text)
    text = stripHtml(text)
    text = text.strip()
    # 0x3000 space used a lot in some Japanese texts (e.g. karafuru).
    text = re.sub('　', ' ', text)
    text = re.sub('^[^\S\n]+', '', text, flags=re.MULTILINE)
    text = re.sub('[^\S\n]+$', '', text, flags=re.MULTILINE)
    #text = re.sub('^\s+([^\s])', '\\1', text, flags=re.MULTILINE)
    #text = re.sub('\s+$', '', text, flags=re.MULTILINE)
    return text

# if we wanted to fully strip reading we would also need to strip space inserted
# by |convertHtml|.
def stripReading(text):
    text = re.sub('\[[^]]*\]', '', text)
    return text

#print(convertRuby(example))
#print(stripRuby(example))
#print(convertHtml(example))
#print(convertHTML(convertRuby(snippet)))

# this file is also written to be invoked as a script.
def main():
    # if |showBoth| is truthy then we print line both with and without reading.
    showBoth = True
    text = sys.stdin.read()
    text = convertRuby(text)
    text = convertHTML(text)
    for line in text.split('\n'):
        print(line)
        if showBoth and '[' in line:
            print(stripReading(line))
    #print(text)

if __name__ == "__main__":
    main()

