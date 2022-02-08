# TODO FIXME still some weirdness around auto tagging a new card
# doesn't show updated tags in gui, will show after save
# but seems to forget them sometimes maybe
# ohhh so it seems to only occur if I have already added my own tags to a new note?
#
# now it looks like for existing cards we are handling it correct but not all gui updates
# but changes are being saved

# import the main window object (mw) from aqt
from aqt import mw
from aqt.utils import qconnect, tooltip, askUser
# import all of the Qt GUI library
from aqt.qt import *

import re

from . import verbs
from . import jisho
from . import clipboard
from . import util
from . import test_util

CONFIG = {
    # allow list of note types we operate on, other note types will be ignored.
    'safe_note_types' : [
      'Ja Vocabulary',
      'Ja Sentences',
      'Ja Grammar',
    ],
    'verb_note_types' : [
      'Ja Verbs',
    ],

    # fields to populate & format examples in
    'example_fields' : [
      #'Example sentence', # 'Ja Vocabulary' # renamed now
      'Examples', # 'Ja Sentences', 'Ja Verbs', 'Ja Grammar', 'Ja Vocabulary'
    ],
    # fields to format whitespace for
    'whitespace_fields' : [
      'Word',
      'Reading',
    ],
    # fields to format using as list of meanings
    'meaning_list_fields' : [
      'English',
      'Alternatives',
    ],

    # fields to use for Jisho lookup, tried in order first non empty is used.
    'lookup_key_fields' : [
        'Word',
        'Reading',
        'Dictionary',
        'Dictionary Reading',
    ],
    'verb_lookup_key_fields' : [
        'Dictionary',
        'Dictionary Readings',
    ],
}

def onSetupEditorButtons(buttons, editor):
    return buttons + [
        editor.addButton(
            None,
            "FillAll",
            lambda ed: fillCard(ed, None),
            tip=(u"Paste all (Ctrl+1"),
            keys=(u"Ctrl+1"),
            label=(u"Fill All")
        ),
        editor.addButton(
            None,
            "FillThree",
            lambda ed: fillCard(ed, 3),
            tip=(u"Paste 3 (Ctrl+2"),
            keys=(u"Ctrl+2"),
            label=(u"Fill 3")
        ),
        editor.addButton(
            None,
            "FillFour",
            lambda ed: fillCard(ed, 4),
            tip=(u"Paste 4 (Ctrl+3"),
            keys=(u"Ctrl+3"),
            label=(u"Fill 4")
        ),
        editor.addButton(
            None,
            "FillFive",
            lambda ed: fillCard(ed, 5),
            tip=(u"Paste 5 (Ctrl+4"),
            keys=(u"Ctrl+4"),
            label=(u"Fill 5")
        ),
        editor.addButton(
            None,
            "FillExamples",
            fillExamples,
            tip=(u"Paste examples (Ctrl+5"),
            keys=(u"Ctrl+5"),
            label=(u"Examples")
        ),
        editor.addButton(
            None,
            "FillVerbInflections",
            fillVerbInflections,
            tip=(u"Fill Verb (Ctrl+6"),
            keys=(u"Ctrl+6"),
            label=(u"Fill Verb")
        ),
        editor.addButton(
            None,
            "GenerateVerbInflections",
            generateVerbInflections,
            tip=(u"Verb Readings (Ctrl+7"),
            keys=(u"Ctrl+7"),
            label=(u"Verb Readings")
        ),
        editor.addButton(
            None,
            "AutoTag",
            autoTag,
            tip=(u"Auto Tag (Ctrl+8"),
            keys=(u"Ctrl+8"),
            label=(u"Auto Tag")
        ),
        editor.addButton(
            None,
            "Cleanup",
            cleanup,
            tip=(u"Cleanup (Ctrl+9"),
            keys=(u"Ctrl+9"),
            label=(u"Cleanup")
        ),
        editor.addButton(
            None,
            "RunTest",
            runTests,
            label=(u"Run tests")
        ),
    ]

def commitChanges(editor):
    note = editor.note
    # reload note to show changes in gui, need to flush to write changes and updateTags mabe
    editor.loadNote()
    editor.updateTags()
    # this note.flush() will break things for new notes hahaha
    if note.id != 0:
        note.flush()

def isSafe(note):
    safe_note_types = CONFIG['safe_note_types']
    note_type_name = note.note_type()['name']
    if note_type_name in safe_note_types:
        return True
    util.showShortMsg("unsafe note '%s'" %(note_type_name))
    return False

def isVerbNote(note):
    verb_note_types = CONFIG['verb_note_types']
    note_type_name = note.note_type()['name']
    if note_type_name in verb_note_types:
        return True
    util.showShortMsg("non-verb note '%s'" %(note_type_name))
    return False

def isSafeOrVerbNote(note):
    safe_note_types = CONFIG['safe_note_types']
    verb_note_types = CONFIG['verb_note_types']
    note_type_name = note.note_type()['name']
    if note_type_name in safe_note_types:
        return True
    if note_type_name in verb_note_types:
        return True
    util.showShortMsg("unsafe non-verb note '%s'" %(note_type_name))
    return False

def fieldNotFoundError(note, field):
    all_fields = note.note_type()['flds']
    err = "field not found '%s', fields '%s'" %(field, all_fields)
    util.showShortMsg(err)

def fieldNotEmptyError(note, field):
    err = "field not empty '%s' : '%s'" %(field, note[field])
    util.showShortMsg(err)

def checkFieldsEmpty(note, fields):
    for field in fields:
        if not field in note:
            fieldNotFoundError(note, field)
            return False
        if note[field]:
            fieldNotEmptyError(note, field)
            return False
    return True

def writeField(note, field, text):
    if not text:
        return
    if not field in note:
        fieldNotFoundError(note, field)
        return
    if note[field]:
        fieldNotEmptyError(note, field)
        return
    note[field] = text

def writeExampleField(note, text):
    for field in CONFIG['example_fields']:
        if field in note:
            writeField(note, field, text)
            return

    fieldNotFoundError(note, field_names[0])

def formatTextWhitespace(text):
    # trim trailing and leading whitespace
    text = text.strip()
    # convert newlines to br tags
    text = text.replace('\n', '<br>')
    # replace div end/start pairs with <br> as copy/paste from Gdocs uses these
    text = re.sub('</div><div>', '<br>', text)
    # remove all non <br> tags
    text = re.sub('<([^b>][^r>][^>]*|.)>', '', text)
    # remove redundant br tags
    text = re.sub('(<br>)+', '<br>', text)
    # remove all leading and trailing tags
    # as we often end up with <div><br></div> leading
    #text = re.sub('^<\[^>\]+>', '', text)
    # remove leading and trailing br tags
    text = re.sub('^(<br>)+', '', text)
    text = re.sub('(<br>)+$', '', text)
    return text

def formatExample(text):
    text = formatTextWhitespace(text)
    # remote trailing whitespace after fullstops.
    text = re.sub('\.\s+<br>', '.<br>', text)
    # add an extra br between entries (after en section)
    text = re.sub('\.<br>', '.<br><br>', text)
    text = re.sub('\?<br>', '?<br><br>', text)
    text = re.sub('!<br>', '!<br><br>', text)
    text = re.sub('\'<br>', '\'<br><br>', text)
    text = re.sub('"<br>', '"<br><br>', text)
    ## re-remove trailing br tags
    text = re.sub('(<br>)+$', '', text)
    return text

def formatFieldWhitespace(note, field):
    if not field in note:
        return
    if not note[field]:
        return
    note[field] = formatTextWhitespace(note[field])

def formatFieldExample(note, field):
    if not field in note:
        return
    if not note[field]:
        return
    note[field] = formatExample(note[field])

# supports formats like
# Alt aux verb: meow, wof
# Noun: foo, bar
# ~ Foo, Bar, Baz
# Foo, Bar, Baz ~
# TODO FIXME
# ~ Al, Like, Noun->Adjective > includes a semicolon hahahahah
# (the) whole face
def formatFieldList(note, field):
    if field not in note:
        return
    if not note[field]:
        return

    val = note[field].strip()

    suffix = False
    if re.match('^~', val):
        suffix = True
        val = re.sub('^~', '', val)

    val = val.strip().replace(';', ',')
    lines = []
    for line in val.split('<br>'):
        head = ''
        rest = line
        if ':' in line:
            parts = line.split(':')
            head = parts[0].strip().capitalize() + ': '
            rest = ':'.join(parts[1:])

        pieces = []
        for part in rest.split(','):
            part = part.strip()
            part = part.capitalize()
            pieces.append(part)
        rest = ', '.join(pieces)

        lines.append(head + rest)

    val = '<br>'.join(lines)

    if suffix:
        val = '~ ' + val

    # fixup brackets
    matches = re.findall('\([^)]+\)', val)
    for m in matches:
        val = val.replace(m, m.lower())

    note[field] = val

def cleanup(editor):
    '''perform appropriate formatting tasks for config specified fields'''
    note = editor.note
    if not isSafeOrVerbNote(note):
        return

    for field in CONFIG['whitespace_fields']:
        formatFieldWhitespace(note, field)

    for field in CONFIG['example_fields']:
        formatFieldExample(note, field)

    for field in CONFIG['meaning_list_fields']:
        formatFieldList(note, field)

    commitChanges(editor)

def fillExamples(editor):
    '''fill example field from clipboard'''
    note = editor.note
    if not isSafeOrVerbNote(note):
        return

    text = clipboard.getClipboardText()
    text = formatExample(text)
    writeExampleField(note, text)

    commitChanges(editor)

def fillCard(editor, limit):
    '''fill first |limit| fields on card from first |limit| TSV values from clipboard'''
    note = editor.note
    if not isSafe(note):
        return

    fields = getFields(note)
    cols = clipboard.getClipboardTSV()

    if limit:
        cols = cols[:limit]

    fields = fields[:len(cols)]

    if not checkFieldsEmpty(note, fields):
        # do not overwrite data in fields
        return

    if len(cols) > len(fields):
        wasted_cols = cols[len(fields):]
        err = "would have unused data '%s' from '%s'" %(wasted_cols, cols)
        util.showShortMsg(err)
        return

    while cols:
        field = fields.pop(0)
        col = cols.pop(0)
        writeField(note, field, col)

    cleanup(editor)

    commitChanges(editor)

def getFields(note):
    fields = []
    for field in note.note_type()['flds']:
        field_name = field['name']
        fields.append(field_name)
        # order seems preserved
        #field_ord = field['ord'] # 0...n
    return fields


def stripFurigana(s):
    s = re.sub('\[[^\]]*\]', '', s)
    s = re.sub('\s+', '', s)
    return s

def getLookupString(note):
    for field in CONFIG['lookup_key_fields']:
        if field in note:
            if note[field]:
                val = note[field]
                val = stripFurigana(val)
                return val
    err = "Failed to find string worth looking up"
    util.showShortMsg(err)
    return None

def getVerbLookupString(note):
    for field in CONFIG['verb_lookup_key_fields']:
        if field in note:
            if note[field]:
                val = note[field]
                val = stripFurigana(val)
                return val
    err = "Failed to find string worth looking up"
    util.showShortMsg(err)
    return None


def autoTag(editor):
    note = editor.note
    if not isSafeOrVerbNote(note):
        return

    lookup_str = getLookupString(note)
    if not lookup_str:
        return

    result = jisho.fetchJishoEntry(lookup_str)
    if not result:
        return

    entry = jisho.decodeJishoEntry(result)
    if not entry:
        return

    # if found entry isn't a perfect match, check with user
    if lookup_str != entry['entry']:
        prompt = "lookup of '%s' found '%s' meaning '%s', is this a match?" %(
                lookup_str, entry['entry'], entry['meaning']
        )
        if not askUser(prompt):
            return

    verb_info = entry['verb_info']
    verb_type = verb_info['type']
    verb_trans = verb_info['transitivity']
    if verb_type and 'Type' in note and not note['Type']:
        writeField(note, 'Type', verb_type)

    if verb_trans and 'Transitivity' in note and not note['Transitivity']:
        writeField(note, 'Transitivity', verb_trans)

    newTags = []

    newTags += entry['parts_of_speech']

    jlpt_tags = entry['jlpt']
    if jlpt_tags:
        newTags.append('jlpt')
        if len(jlpt_tags) == 1:
            newTags += jlpt_tags
        else:
            util.showShortMsg("found multiple jlpt tags '%s'" %(jlpt_tags))

    wanikani_tags = entry['wanikani']
    if wanikani_tags:
        newTags.append('wanikani')
        if len(wanikani_tags) == 1:
            newTags += wanikani_tags
        else:
            util.showShortMsg("found multiple wanikani tags '%s'" %(wanikani_tags))

    currentTags = getCurrentTags(note)
    newTags = [x for x in newTags if x not in currentTags]

    prompt = "from '%s' meaning '%s' should I add tags '%s'?" %(
        entry['entry'],
        entry['meaning'],
        newTags,
    )
    if newTags and askUser(prompt):
        for tag in newTags:
            note.add_tag(tag)

    # only take first N unique alternatives
    alternatives = entry['alternatives'][:10]
    alternatives = ", ".join(alternatives)
    prompt = "from '%s' meaning '%s' should I add alternative meanings '%s'?" %(
        entry['entry'],
        entry['meaning'],
        alternatives,
    )
    # Populate 'English' without prompt (if empty).
    if (entry['meaning'] and
        'English' in note and
        not note['English']):
        writeField(note, 'English', entry['meaning'])
        formatFieldList(note, 'English')
    elif entry['meaning']:
        # otherwise, if English is full, save primary meaning as
        # alternative. TODO consider this wrt. filtering, English
        # might already contain this meaning.
        alternatives = entry['meaning'] + ', ' + alternatives

    # TODO filter alternatives for items already present in meaning
    # ('English') field.

    # TODO FIXME tidy this up
    if (alternatives and
       'Alternatives' in note and
       not note['Alternatives']):
        if askUser(prompt):
            writeField(note, 'Alternatives', alternatives)
            formatFieldList(note, 'Alternatives')

    commitChanges(editor)

def getCurrentTags(note):
    return note.string_tags().split(" ")

def fillVerbInflections(editor):
    note = editor.note
    if not isVerbNote(note):
        return

    lookup_str = getVerbLookupString(note)
    if not lookup_str:
        return

    (masu, te) = clipboard.getClipboardInflections(lookup_str)
    if not masu or not te:
        return

    note['Masu'] = masu
    note['Te'] = te

    commitChanges(editor)

# TODO FIXME consider using mecab.
def generateVerbInflections(editor):
    note = editor.note
    if not isVerbNote(note):
        return

    inflections = {
        'kanji': note['Dictionary'],
        'kana': note['Dictionary Reading'],
        'masu': note['Masu'],
        'masuKana': note['Masu Reading'],
        'te': note['Te'],
        'teKana': note['Te Reading'],
    }

    inflections = verbs.fillInBlanks(inflections)

    note['Dictionary'] = inflections['kanji']
    note['Dictionary Reading'] = inflections['kana']
    note['Masu'] = inflections['masu']
    note['Masu Reading'] = inflections['masuKana']
    note['Te'] = inflections['te']
    note['Te Reading'] = inflections['teKana']

    commitChanges(editor)

def runTests(editor):
    verbs.test(test_util)
    clipboard.test(test_util)
    jisho.test(test_util)
    test_util.test_report_results(util.showLongMsg)

