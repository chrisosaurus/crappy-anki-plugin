
from aqt.utils import showInfo, showText

def showShortMsg(text):
    # force to a string in case it isn't already one
    text = '%s' %(text)
    print(text)
    showInfo(text)

def showLongMsg(text):
    # force to a string in case it isn't already one
    text = '%s' %(text)
    print(text)
    showText(text)
