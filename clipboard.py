# clipboard access
from PyQt5.QtWidgets import QApplication
from PyQt5.QtWidgets import QApplication
import re

from . import util

def getClipboardText():
    clipboard = QApplication.clipboard()
    # Mac OSX doesn't support selection
    mode = clipboard.Clipboard
    if clipboard.supportsSelection():
        mode = clipboard.Selection

    # copy from clipboard
    text = clipboard.text(mode)
    # trim leading whitespace
    text = text.strip()
    return text

def getClipboardTSV():
    text = getClipboardText()
    # split by newlines and columns
    cols = re.split('\t|\n', text)
    return cols

# MVP verb support be to populate from clipboard in one go.  This is very
# specific, and will search clipboard expecting a very specific format.
# this is only used as I couldn't find and API endpoint for verbs.
def getClipboardInflections(root):
    '''searches clipboard for Jisho.org formatted verb inflected table'''
    cols = getClipboardTSV()

    # keep going until we find provided |root| form
    while cols:
        if cols[0].strip() == root:
            break
        cols.pop(0)

    if not cols:
        util.showShortMsg("failed to root '%s' form in clipboard" %(root))
        return [None, None]

    if len(cols) < 14:
        util.showShortMsg("insufficient data in clipboard")
        return [None, None]

    masu = cols[3].strip()
    te = cols[12].strip()

    util.showShortMsg("found masu '%s' and te '%s'" %(masu, te))
    return [masu, te]

def rawGetClipboard():
    clipboard = QApplication.clipboard()
    mode = clipboard.Clipboard
    if clipboard.supportsSelection():
        mode = clipboard.Selection

    # copy to clipboard
    text = clipboard.text(mode)
    return text

def rawSetClipboard(text):
    clipboard = QApplication.clipboard()
    mode = clipboard.Clipboard
    if clipboard.supportsSelection():
        mode = clipboard.Selection

    # copy to clipboard
    clipboard.setText(text, mode)

def testGetClipboardText(test_util):
    print("\ntesting getClipboardText")

    data = '\n  \t hello world\n how are you doing   '

    rawSetClipboard(data)

    expected = 'hello world\n how are you doing'
    result = getClipboardText()

    test_util.test_assert(expected, result)

def testGetClipboardTSV(test_util):
    print("\ntesting getClipboardTSV")

    data = "\ta\tb \t\tc\n\td\t"

    rawSetClipboard(data)

    expected = ['a', 'b ', '', 'c', '', 'd']
    result = getClipboardTSV()

    test_util.test_assert(expected, result)

def testGetClipboardInflections(test_util):
    print("\ntesting getClipboardInflections")

    data = """行く 	行かない
    Non-past, polite 	行きます 	行きません
    Past 	行った 	行かなかった
    Past, polite 	行きました 	行きませんでした
    Te-form 	行って 	行かなくて
    Potential 	行ける 	行けない
    Passive 	行かれる 	行かれない
    Causative 	行かせる 	行かせない
    Causative Passive 	行かせられる 	行かせられない
    Imperative 	行け 	行くな"""

    rawSetClipboard(data)

    lookup_str = '行く'
    expected = ['行きます', '行って']
    result = getClipboardInflections(lookup_str)

    test_util.test_assert(expected, result)

def test(test_util):
    # track & restore clipboard after testing.
    clipboardTextBackup = rawGetClipboard()

    testGetClipboardText(test_util)
    testGetClipboardTSV(test_util)
    testGetClipboardInflections(test_util)

    rawSetClipboard(clipboardTextBackup)

if __name__ == "__main__":
    print("clipboard: cannot run tests outside of Anki")

