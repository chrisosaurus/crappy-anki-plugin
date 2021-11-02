from aqt import mw
from aqt.utils import qconnect
from aqt.qt import *

from . import util
import re

def match(reply, name):
    if re.search(reply, name, re.IGNORECASE):
        return True
    return False


def jumpToDeck() -> None:
    '''prompt user for regex and then open first deck which matches'''
    reply = util.askForText("Jump to deck based on pattern:")

    if reply == None:
        # user cancelled, do nothing.
        return

    newid = None
    # DeckManager
    dm = mw.col.decks
    decks = dm.all_names_and_ids()
    # Examples of each item within decks:
    # id: 1569512537848, name: "Japanese"
    # id: 1633060544976, name: "Japanese::Context"
    # id: 1628858232103,  name: "Japanese::Context::Ace Attorney"
    # id: 1569512813760, name: "Japanese::Kana"
    # id: 1572312000615, name: "Japanese::Verbs"
    # id: 1569512603085, name: "Japanese::Vocabulary"
    # id: 1617922470740, name: "Japanese Shared::JLPT Tango N5"
    # id: 1617543742407, name: "Japanese Shared::Vocabulary Core Anime"
    for deck in decks:
        if match(reply, deck.name):
            newid = deck.id
            break

    if newid != None:
        mw.col.decks.select(newid)
        # refresh highlighted deck, probably not needed is we just immediatley
        # move to overview state below.
        mw.deckBrowser.refresh()
        # change to deck overview.
        mw.onOverview()


# called from __init__
def attach():
    # create a new menu item
    action = QAction("Jump to deck", mw)
    action.setShortcut(QKeySequence("Ctrl+Shift+j"))
    # jumpToDeck when clicked
    qconnect(action.triggered, jumpToDeck)
    # add to the tools menu
    mw.form.menuTools.addAction(action)


