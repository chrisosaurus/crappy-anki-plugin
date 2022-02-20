import urllib.request
import urllib.parse
import json
import re

from . import util

def fetchJishoEntry(ja):
    '''fetch Jisho.org entry for provided Japanese word'''
    ja_encoded = urllib.parse.quote_plus(ja)
    url = 'https://jisho.org/api/v1/search/words?keyword=' + ja_encoded
    f = urllib.request.urlopen(url)
    response = json.loads(f.read())
    status = response['meta']['status']
    if status != 200:
        err = "Failed to fetch from jisho (%s), result: %s" %(url, response)
        util.showShortMsg(err)
        return None
    data = response['data']
    return data

def filterWanikaniTags(tags):
    '''filter provided list of tags for those pertaining to Wanikani'''
    results = []
    for tag in tags:
        m = re.match('^wanikani(\d+)$', tag)
        if m:
            # pad with 0s to 2 places
            n = m.group(1).rjust(2, '0')
            s = 'wanikani-' + n
            results.append(s)

    return results

def partOfSpeechFilter(s):
    parts_of_speech = {
        'noun' : 'noun',
        'adverb' : 'adverb',
        'adjective' : 'adjective',
        'conjunction' : 'conjunction',
        'conjunctive' : 'conjunctive',
        'suru' : 'suru',
        'adverb': 'adverb',
        'expressions' : 'expression',
        'expression' : 'expression',
    }
    # normalize to lowercase and remove everything after first space
    s = s.lower()
    s = s.split(" ")[0]
    if s in parts_of_speech:
        return parts_of_speech[s]
    return None

def verbPartOfSpeechFilter(s):
    parts_of_speech = {
        'godan' : 'godan',
        'ichidan' : 'ichidan',
        'transitive' : 'transitive',
        'intransitive' : 'intransitive',
    }
    # normalize to lowercase and remove everything after first space
    s = s.lower()
    s = s.split(" ")[0]
    if s in parts_of_speech:
        return parts_of_speech[s]
    return None

def decodeJishoEntry(data):
    '''MVP for decoding Jisho.org entry'''
    first = data[0]

    entry = first['slug']
    # array of jlpt tags (e.g. jlpt-n3)
    jlpt = first['jlpt']
    # arrays of other tags (e.g. wanikani14, wanikani8)
    tags = first['tags']
    wanikani = filterWanikaniTags(tags)

    japanese = first['japanese']
    word = ''
    reading = ''
    for ja in japanese:
        word = ja['word']
        reading = ja['reading']
        break

    senses = first['senses']
    meanings = []
    parts_of_speech = []
    verb_categories = []
    for sense in senses:
        english_definitions = sense['english_definitions']
        for meaning in english_definitions:
            if meaning not in meanings:
                meanings.append(meaning)

        part_of_speech = sense['parts_of_speech']
        for part in part_of_speech:
            verb_part = verbPartOfSpeechFilter(part)
            if verb_part and verb_part not in verb_categories:
                verb_categories.append(verb_part)
            part = partOfSpeechFilter(part)
            if part and part not in parts_of_speech:
                parts_of_speech.append(part)

    # primary_definition = data[0]['senses'][0]['english_definitions'][0]
    primary_definition = meanings[0]

    verb_info = {'type': None, 'transitivity': None}
    if verb_categories:
        s = ''
        if 'godan' in verb_categories:
            s += 'Godan'
        if 'ichidan' in verb_categories:
            if s:
                s += ' and '
            s += 'Ichidan'
        verb_info['type'] = s

        s = ''
        if 'transitive' in verb_categories:
            s += 'Transitive'
        if 'intransitive' in verb_categories:
            if s:
                s += ' and '
            s += 'Intransitive'
        verb_info['transitivity'] = s

    result = {
      'entry': entry,
      'jlpt': jlpt,
      'wanikani': wanikani,
      'meaning': primary_definition,
      'alternatives': meanings[1:],
      'parts_of_speech': parts_of_speech,
      'verb_info': verb_info,
      'word': word,
      'reading': reading,
    }

    return result

def testPartOfSpeechFilter(test_util):
    test_util.test_print('\ntesting part of speech filter')
    test_util.test_assert('suru', partOfSpeechFilter('Suru Verb'))
    test_util.test_assert('noun', partOfSpeechFilter('Noun'))
    test_util.test_assert(None, partOfSpeechFilter('Transitive Verb'))

def testVerbPartOfSpeechFilter(test_util):
    test_util.test_print('\ntesting verb part of speech filter')
    test_util.test_assert('godan', verbPartOfSpeechFilter('Godan Verb'))
    test_util.test_assert('ichidan', verbPartOfSpeechFilter('Ichidan Verb'))
    test_util.test_assert('transitive', verbPartOfSpeechFilter('Transitive Verb'))
    test_util.test_assert('intransitive', verbPartOfSpeechFilter('Intransitive Verb'))
    test_util.test_assert(None, verbPartOfSpeechFilter('Noun'))

def testFilterWanikaniTags(test_util):
    test_util.test_print('\ntesting wanikani tags filter')
    test_util.test_assert([], filterWanikaniTags([]))
    test_util.test_assert([], filterWanikaniTags(['noun', 'suru', 'jlpt-n5']))
    test_util.test_assert(['wanikani-51'], filterWanikaniTags(['wanikani51']))
    test_util.test_assert(['wanikani-01'], filterWanikaniTags(['wanikani1']))
    test_util.test_assert(['wanikani-01', 'wanikani-02'], filterWanikaniTags(['wanikani1', 'wanikani2']))

def testDecodeJishoEntry(test_util):
    test_util.test_print("\ntesting Jisho decode")

    to_go_input = [{'slug': '行く', 'is_common': True, 'tags': ['wanikani5'], 'jlpt': ['jlpt-n5'], 'japanese': [{'word': '行く', 'reading': 'いく'}, {'word': '行く', 'reading': 'ゆく'}], 'senses': [{'english_definitions': ['to go', 'to move (in a direction or towards a specific location)'], 'parts_of_speech': ['Godan verb - Iku/Yuku special class', 'Intransitive verb']}, {'english_definitions': ['to proceed', 'to take place'], 'parts_of_speech': ['Godan verb - Iku/Yuku special class', 'Intransitive verb']}]}]
    to_go_expected = {
      'entry': '行く',
      'jlpt': ['jlpt-n5'],
      'wanikani': ['wanikani-05'],
      'meaning': 'to go',
      'alternatives':
         ['to move (in a direction or towards a specific location)', 'to proceed', 'to take place'],
      'parts_of_speech': [],
      'verb_info': {'type':'Godan', 'transitivity':'Intransitive'},
    }
    to_go_result = decodeJishoEntry(to_go_input)
    test_util.test_assert(to_go_expected, to_go_result)

    park_input = [{'slug': '公園', 'is_common': True, 'tags': ['wanikani16'], 'jlpt': ['jlpt-n5'], 'japanese': [{'word': '公園', 'reading': 'こうえん'}], 'senses': [{'english_definitions': ['(public) park'], 'parts_of_speech': ['Noun']}, {'english_definitions': ['Park'], 'parts_of_speech': ['Wikipedia definition']}]}, {'slug': '公園墓地', 'tags': [], 'jlpt': [], 'japanese': [{'word': '公園墓地', 'reading': 'こうえんぼち'}], 'senses': [{'english_definitions': ['garden cemetery', 'park cemetery', 'memorial park'], 'parts_of_speech': ['Noun']}, {'english_definitions': ['Kouen Cemetery'], 'parts_of_speech': ['Place']}]}]
    park_expected = {
      'entry': '公園',
      'jlpt': ['jlpt-n5'],
      'wanikani': ['wanikani-16'],
      'meaning': '(public) park',
      'alternatives': ['Park'],
      'parts_of_speech': ['noun'],
      'verb_info': {'type':None, 'transitivity':None},
    }
    park_result = decodeJishoEntry(park_input)
    test_util.test_assert(park_expected, park_result)

def test(test_util):
    testVerbPartOfSpeechFilter(test_util)
    testPartOfSpeechFilter(test_util)
    # don't test Fetch so that our tests don't create network traffic
    testFilterWanikaniTags(test_util)
    testDecodeJishoEntry(test_util)

if __name__ == "__main__":
    print("jisho: cannot run tests outside of Anki")

