from anki.hooks import addHook
from . import addon

addHook("setupEditorButtons", addon.onSetupEditorButtons)
