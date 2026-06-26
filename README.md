# pk3DS_parser_for_dynamic_calc

This is an updated and rewritten version of parse.rb from https://github.com/hzla/pk3ds_for_dynamic_calc.

# How to export JSON for use in the calc:
You will need hzla's version of pk3DS (https://github.com/hzla/pk3ds_for_dynamic_calc).
Export the following files using pk3DS (if you reame them, remember to update parser.py).
- Personal Entries.txt (Personal Stats)
- Level Up Moves.txt (Level Up Moves)
- Moves.txt (Move Stats)
- Battles.txt (Trainers)
You will need Python (https://www.python.org).
Make sure the exported files are in the same directory as parser.py.
Add new forms to forms.txt.
Add replaced poks to replaced_poks.txt.
Change the GAME_TITLE in parser.py if you want.
Run parser.py.
