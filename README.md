# eu4-utils

Collection of scripts to help parse and analyze eu4 data

## Components

There are 2 important components:

### Simple Clausewitz

Is a limited Lexer and Parser for Clausewitz Engine files, very limited as it does not
recognize some of the fancy stuff like [[switch statement], but in any case it should
work acceptably for most cases.

Example usage:

```python
from Simple_Clausewitz import SimpleCWLexer, SimpleCWParser

lexer = SimpleCWLexer()
parser = SimpleCWParser()

with open("example_file.txt", 'r') as f:
    tokens = lexer.tokenize()
    # We can now print or use the lexed tokens, or we can go ahead and parse them
    parsed = parser.parse(tokens)
    # Print the resulting data we can work upon
    print(parsed)
```

This is the eu4 script:

```txt
DLM_ideas = {
	start = {
		naval_forcelimit_modifier = 0.2
		land_forcelimit_modifier = 0.2
	}

	bonus = {
		discipline = 0.05
	}
	
	trigger = {
		tag = DLM
	}
	free = yes		
	
	dlm_first = {
		legitimacy = 1
	}
	dlm_second = {
		land_morale = 0.2
	}
	dlm_third = {
		global_own_trade_power = 0.15
	}
	dlm_fourth = {
		army_tradition_decay = -0.01
	}
	dlm_fifth = {
		diplomatic_reputation = 1
		unjustified_demands = -0.25
	}
	dlm_sixth = {
		global_colonial_growth = 20
		cb_on_overseas = yes
	}
	dlm_seventh = {
		own_coast_naval_combat_bonus = 1
	}
}
```

And this is the generated python3 data you can write your python3 script to manipulate
to your heart's content:

```python
[ ( 'DLM_ideas',
    [ ( 'start',
        [ ('naval_forcelimit_modifier', 0.2),
          ('land_forcelimit_modifier', 0.2)]),
      ('bonus', [('discipline', 0.05)]),
      ('trigger', [('tag', 'DLM')]),
      ('free', True),
      ('dlm_first', [('legitimacy', 1)]),
      ('dlm_second', [('land_morale', 0.2)]),
      ('dlm_third', [('global_own_trade_power', 0.15)]),
      ('dlm_fourth', [('army_tradition_decay', -0.01)]),
      ( 'dlm_fifth',
        [('diplomatic_reputation', 1), ('unjustified_demands', -0.25)]),
      ('dlm_sixth', [('global_colonial_growth', 20), ('cb_on_overseas', True)]),
      ('dlm_seventh', [('own_coast_naval_combat_bonus', 1)])])]
```

### Paradox Localisation

Is a full Lexer and Parser for Paradox Localisation files. It returns a list of dicts
with the expected value

Example usage:

```python
from Paradox_Localisation import LocalisationLexer, LocalisationParser

lexer = LocalisationLexer()
parser = LocalisationParser()

with open("example_localisation_l_english.yml", 'r') as f:
    tokens = lexer.tokenize()
    # We can now print or use the lexed tokens, or we can go ahead and parse them
    parsed = parser.parse(tokens)
    # Print the resulting data we can work upon
    print(parsed)
```

This is the localisation:

```yml
l_english:
 #Arles
 ars_reunite_burgundy_title:0 "Unite the Burgundies"
 ars_reunite_burgundy_desc:0 "Arelat realm was shattered just a few years ago. We must prepare our armies and reunite it under our rule!"
```

and this is the resulting python3 data:

```python
[ 'l_english',
  { 'key': 'ars_reunite_burgundy_title',
    'value': '"Unite the Burgundies"',
    'version': 0},
  { 'key': 'ars_reunite_burgundy_desc',
    'value': '"Arelat realm was shattered just a few years ago. We must '
             'prepare our armies and reunite it under our rule!"',
    'version': 0}]
```

## lexpar

lexpar is a CLI utility to print out what the data looks like without having
to write the python first, the usage is very simple:

```python
$ lexpar --parse --pretty path/to/file.txt
[ ( 'DLM_ideas',
    [ ( 'start',
        [ ('naval_forcelimit_modifier', 0.2),
          ('land_forcelimit_modifier', 0.2)]),
      ('bonus', [('discipline', 0.05)]),
      ('trigger', [('tag', 'DLM')]),
      ('free', True),
      ('dlm_first', [('legitimacy', 1)]),
      ('dlm_second', [('land_morale', 0.2)]),
      ('dlm_third', [('global_own_trade_power', 0.15)]),
      ('dlm_fourth', [('army_tradition_decay', -0.01)]),
      ( 'dlm_fifth',
        [('diplomatic_reputation', 1), ('unjustified_demands', -0.25)]),
      ('dlm_sixth', [('global_colonial_growth', 20), ('cb_on_overseas', True)]),
      ('dlm_seventh', [('own_coast_naval_combat_bonus', 1)])])]

$ lexpar --parse --pretty --localisation path/to/loc_l_english.yml
[ 'l_english',
  { 'key': 'ars_reunite_burgundy_title',
    'value': '"Unite the Burgundies"',
    'version': 0},
  { 'key': 'ars_reunite_burgundy_desc',
    'value': '"Arelat realm was shattered just a few years ago. We must '
             'prepare our armies and reunite it under our rule!"',
    'version': 0}]
```

## Generate-Policy-Table.py

A simple script that generates a Markdown table matching Group Ideas to Policies.
It can optionally use the `Paradox_Localisation` module to localise all the
Group Ideas and Policies.

This Markdown table can then be converted to HTML and published, here are two
examples:

- [Ante Bellum Policy Table](https://maxice8.github.io/ab/policies)

Usage for the example above:

> The usage of $VARIABLE is to avoid writing the full path to the directory
> you must replace it with the proper path.

```console
$ python3 Generate-Policy-Table.py $PATH_TO_ANTE_BELLUM \
  --localise --base $PATH_TO_VANILLA_INSTALLATION \
  | python3 aux/table-md-to-html.py --highlight-first-row \
  -o $PATH_TO_STORE_THE_FILE.html
```

## count-missions.py

A simple script that generates a Markdown table of countries and how many missions it has, it has a simple heuristic to differentiate between Normal and Branching missions but it is not smart enough to differentiate branching missions by things like country flags or religion.

- [Ante Bellum Missions](https://maxice8.github.io/ab/mission-count)

Usage for the example above:

> The usage of $VARIABLE is to avoid writing the full path to the directory
> you must replace it with the proper path.

```console
$ python3 count-mission.py $PATH_TO_ANTE_BELLUM_MISSIONS_DIRECTORY/* \
  -d $PATH_TO_VANILLA_INSTALLATION --localise --lang=english --ante-bellum \
  | python3 aux/table-md-to-html.py -o $PATH_TO_STORE_THE_FILE.html
```

## TODO

Things that need to be fixed in the code:

- [ ] Make the Localisation Lexer and Parser more robust and have better error handling.
- [ ] Rewrite the Simple_Clausewitz Lexer and Parser to fully cover the Clausewitz code.
- [ ] Write tests, maybe using vanilla files from eu4 instead of mock files.
- [x] Write code that loads from multiple directories to avoid loading overridden file.
- [x] Support other languages in lexpar and general_localisation.

## Acknowledgements

Big thanks to [QAston](https://github.com/QAston/clausewitz-antlr-grammar) for having
a ANTLR Clausewitz Engine Grammar handy, it is copied in full in the `__init__.py`
of the `Simple_Clausewitz` module.

## License

This project is under the [MIT License](https://opensource.org/licenses/MIT).

See the [LICENSE](./LICENSE) file for more information.
