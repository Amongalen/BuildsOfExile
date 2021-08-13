from pathlib import Path
from pprint import pprint

from apps.pob_wrapper import PathOfBuilding

TEST_ITEM_1 = r'''
Rarity: Rare
Hypnotic Circle
Opal Ring
--------
Requirements:
Level: 80
--------
Item Level: 80
--------
Your Meteor Towers drop an additional Meteor
--------
24% increased Elemental Damage (implicit)
--------
+48 to Intelligence
Adds 21 to 40 Fire Damage to Attacks
+46 to maximum Energy Shield
+15% to all Elemental Resistances
+17 to Strength and Intelligence (crafted)
--------
Note: ~price 4 exa
'''

TEST_ITEM_2 = r'''
Rarity: RARE
Soul Bite
Quartz Wand
Unique ID: abf731ac59271d328d5507a324fba0a9b4099bc62d053c5b52ac75ee678fe99d
Item Level: 76
Quality: 0
Sockets: B-B-B
LevelReq: 72
Implicits: 1
22% increased Spell Damage
70% increased Spell Damage
Adds 3 to 133 Lightning Damage to Spells
+4 Life gained on Kill
13% increased Projectile Speed
Gain 5% of Non-Chaos Damage as extra Chaos Damage
{crafted}Trigger a Socketed Spell when you Use a Skill
'''

def run():
    pob_install = r'D:\PathOfBuildingForWebapp'
    pob_path = r'D:\PathOfBuildingForWebapp'  # or %ProgramData%\Path of Building` for installed version

    pob = PathOfBuilding(pob_path, pob_install, verbose=True)
    pob2 = PathOfBuilding(pob_path, pob_install, verbose=True)

    builds_path = pob.get_builds_dir()
    print("POB Builds:", builds_path)

    print('\nLoading build:')
    pob.load_build(rf'{builds_path}test.xml')
    pprint(pob.get_build_info())

    print('\nGenerating HTML from item effects test: ./test-item1.html')
    Path('test-item1.html').write_text(pob.item_as_html(TEST_ITEM_1))
    Path('test-item2.html').write_text(pob2.item_as_html(TEST_ITEM_2))
    Path('test-item3.html').write_text(pob.item_as_html(TEST_ITEM_2))

    print('\nFetch data directly from Lua:')
    print('  build.spec.curAscendClassName = ', end='')
    pprint(pob.fetch('build.spec.curAscendClassName'))

    # `pob` is killed automatically

    return pob


if __name__ == '__main__':
    pob = run()
