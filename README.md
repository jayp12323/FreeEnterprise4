# [Try it out here!](https://ff4fe.galeswift.com/make)

# Implemented flags:
- Omode:bosscollector: Kill X number of bosses as an objective
- Omode:goldhunter: Turn in a certain amount of gold to Tory in Agart as an objective
- Random pools: Added 2 extra 'buckets' of randomized objectives, allowing individual configuration of them
- Random:only chars: Added ability to specify that random character quests for an objective are only for certain characters
- Gated objectives: A gated objective means that you will only get the reward for that objective upon completion of all required other objectives.  So if you set "Complete the Tower of Zot" as a gated objective, you will be granted the earth crystal automatically upon completion of the other objectives.
- Hard required objectives: Hard required objectives are a # of objectives that must be completed in order to consider all objectives completed.  So if you require 4 out of 5 objectives, and 1 hard required, the hard objective must be included as part of the 4.
- KStart: Added ability to specify key items as the starting item granted
- CNopartner: Disables your starting partner.
- Cpaladin: Cecil starts as a paladin.  Ordeals is still available as an objective as usual.
- Csuperhero: This flag acts the same as Chero, except your starting character will obtain incredible stat boosts, until finding the earth crystal (their one weakness).
- Ctreasure: Cnofree is forced on, and all normally free characters are hiding in chests/pots in the Overworld.  Unrestricted characters only.
- CMiab `(wip)` : Cnoearned is forced on, and all normally earned characters are hiding in MIABs everywhere.  Includes restricted characters
- Tunrestrict: Allows ignoring the restrictions placed on tiers in the treasury/moon/underworld/overworld
- Sprice/Spricey: Changes the price of items in shops.  Can target armor/weapons/items individually
- Salways: Items are forced to be guaranteed in shops
- Sno: More options added to exclude items such as bacchus, coffin, etc.
- Ssame: Shops only sell a single item, and all shops in the game are the same. The item chosen uses the same rules as Swild.
- Ssingles: Shops only sell a single item, but follow the standard randomization rules and safety checks (unless disabled).
- Bitburns: The replacement attack will include Meganuke, Big Bang, Zanteksuken, Full party charm, and Meteo

# Wishlist/Todo Items:
- Flag to enable gaining fixed levels after boss encounters or objectives (similar to fusoya), would disable exp completely

# FreeEnterprise4

This is the open-source version of Free Enterprise 4.x. It contains the full functionality of Free Enterprise 4.x, with some omissions:

- The Z sprite and harp songs databases are not included, though the tools to generate assets in the correct format are.

- The dwarf job list is omitted; should you wish to create your own, this is a simple text file with one job per line.

- Passwords, encryption keys, and similar secrets used in the public deployment of Free Enterprise have been excluded.

Basic setup instructions are included here; for a more detailed guide, visit https://wiki.ff4fe.com/doku.php?id=dev:setup_guide

## Initial Setup

- Minimum requirements: Python 3.7
- Clone the repo.
- In the root directory, create a virtualenv and activate it.
- `pip install -r requirements.txt`
- Find the `site-packages` directory inside your virtualenv directory (should be somewhere under `<virtualenv dir>\lib\<etc>\site-packages`) and inside it, create a plain text file named `fe.pth`, containing the path to your repo root.

If you want to use the webserver:

- Install MongoDB server.
- Download the Floating IPS executable for your target platform, and place it inside `FreeEnt/server/bin`. (This file should be named either `flips.exe`, `flips-linux`, or `flips-mac` accordingly.)


## Usage

All modes of running Free Enterprise tools require specifying a path to an FF2 US v1.1 headerless ROM (not supplied in this repo).

Always run with the virtualenv active.

### Command line generator

From the repo root directory: `python -m FreeEnt <rompath> make -h`

### Web generator

Note as mentioned above that MongoDB must be installed to use the web generator, and you must have downloaded the Floating IPS binary to `FreeEnt/server/bin`.

From the repo root directory: `python -m FreeEnt <rompath> server --local`

Then navigate in a browser to `localhost:8080`.

### Tools site

From the `fetools` directory: `python tool_site.py <rompath>`

Then navigate in a browser to `localhost:8082`.

### Contributors

Free Enterprise was made possible using the extensive technical research and knowledge of PinkPuff, Grimoire LD, Chillyfeez, and Aexoden. This repo contains code written and designed by b0ardface/HungryTenor, Crow, Myself086, Myria, mxzv, and Wylem. It also contains the graphic design work of SchalaKitty and Steph Sybydlo. It is based on the game design work of riversmccown and mxzv. And while their specific assets are not included in this repo, the musical work of Xenocat and Calmlamity contributes extensively to Free Enterprise, and was formative in the development of tools contained here.

### License

This repo is distributed under the MIT License.
