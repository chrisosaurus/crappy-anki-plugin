# my anki plugin
if you have found this by accident, you should probably run away
this is nothing more than a hackers attempt at an MVP anki plugin
I really have no idea what I'm doing.

## configuration

This plugin is paranoid and has hard coded values in addon.py for fields and
note types, and this plugin will refuse to run for fields or notes not in these
lists.


## new buttons in edit dialogue

 - fill all
 - fill 3
 - fill 4
 - fill 5
 - (fill) examples
 - (fill) verb (inflections)
 - (generate) verb inflections
 - auto tag
 - cleanup
 - run tests

### fill all / 3 / 4 / 5
fill first N fields of current note from first N tab separated values from clipboard
this is used to allow easy copy and pasting from google sheets

### (fill) examples
fill in examples field from current clipboard

### (fill) verb (inflections)
fill in verb fields from current clipboard which is expected to contain verb inflections
as formatted by Jisho.org, this only exists because I couldn't find an appropriate API endpoin

### (generate) verb inflections
for a partially filled in verb note, this will attempt to generate verb pairs

### auto tag
search Jisho.org for appropriate JLPT and Wanikani tags to add to current note
really poorly named, as now also populates other fields from Jisho, name will
have to change soon.

### cleanup
perform cleanup and formatting for fields on current note

### run tests
run tests for this plugin


## new Jump to deck menu item (Ctrl+Shift+J / Cmd+Shift+J)
A new dialog to help a user open a deck from the keyboard only
Prompts the user for a regex and will search through all decks for first match
First match found is then opened

