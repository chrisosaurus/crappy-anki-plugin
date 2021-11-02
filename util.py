
from aqt.utils import getText, showInfo, showText

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


def askForText(text):
    # force to a string in case it isn't already one
    text = '%s' %(text)

    # cancel: result = 0
    # okay: result = 1
    # reply is set both times
    reply, result = getText(text)

    if result == 0:
        print('asking for %s, user cancelled' %(text))
        return None

    print('asking for %s, user replied %s' %(text, reply))
    return reply
