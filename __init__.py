from anki.hooks import addHook
from aqt import gui_hooks
from . import addon
from . import deck_jump

addHook("setupEditorButtons", addon.onSetupEditorButtons)

deck_jump.attach()
