import random
import sys
import time

FAST_TEXT = False

player = {
    "strength": 10,
    "endurance": 10,
    "vitality": 10,
    "agility": 10,
    "energy": 100,
    "morale": 100,
    "thirst": 100,
    "hunger": 100,
    "food": 5,
    "water": 5,
    "equipped_food": "Bread",
    "equipped_water": "Clean Water",
    "inventory": ["Ancient Compass", "Mother's Red Scarf"],
    "companions": [],
    "guardian_marks": [],
    "mercy": 0,
    "resolve": 0,
    "chaos_taint": 0,
    "truths": 0,
    "memory": {},
}

PYTHON_2 = "expanded_kingdom_story_memory_and_party_battles"
KINGDOM_GAMEPLAY_TARGET_HOURS = 2

day = 1
hour = 8

foods = {
    "Bread": {"hunger": 20, "morale": 5},
    "Meat": {"hunger": 35, "energy": 10},
    "Moonfruit": {"hunger": 25, "morale": 15},
    "Root Stew": {"hunger": 45, "energy": 15},
}

waters = {
    "Clean Water": {"thirst": 35},
    "Spring Water": {"thirst": 50, "morale": 5},
    "Glacier Melt": {"thirst": 45, "energy": 10},
    "Starlit Rain": {"thirst": 60, "morale": 15},
}

events = ["nothing", "enemy", "food", "water", "traveler", "omen", "memory", "kingdom_encounter"]


kingdom_profiles = {
    "Stone Kingdom": {
        "identity": "low tunnels, debt ledgers, ancestor stones, and miners who measure trust by shared weight",
        "people": ["Oren Deepdelver", "Sella Pickhand", "Apprentice Tovin", "Ledger-Keeper Marn"],
        "encounters": [
            ("cave_in", "A side gallery collapses and miners pound on stone from the other side.", "endurance"),
            ("debt_guard", "A mine guard demands tolls from families carrying rescue tools.", "strength"),
            ("singing_ore", "Blue ore hums a warning that only stops when everyone stands still.", "resolve"),
            ("ancestor_marker", "An ancestor marker has been stolen and the miners refuse to dig until it is found.", "truths"),
        ],
        "events": ["brace a cracking beam", "settle a strike without blood", "map a worm tunnel", "escort lamp-bearers"],
    },
    "Tide Kingdom": {
        "identity": "floating markets, tide bells, canal law, and families who move homes by boat",
        "people": ["Captain Ysra", "Bell-Diver Noll", "Net-Mender Sivi", "Harbor Child Renn"],
        "encounters": [
            ("tide_race", "The tide turns early and boats slam against the palace steps.", "agility"),
            ("quarantine_boat", "A quarantine boat begs for medicine while officials argue from dry balconies.", "mercy"),
            ("pearl_thief", "A pearl thief hides among evacuees and dares you to expose him publicly.", "truths"),
            ("reef_trial", "A living reef opens only for someone who returns what the sea lent.", "vitality"),
        ],
        "events": ["repair a canal gate", "dive for a bell chain", "negotiate ferry passage", "follow lantern fish"],
    },
    "Ember Kingdom": {
        "identity": "glass deserts, furnace courts, spice smoke, and citizens who treat water like gold",
        "people": ["Jara Ashcup", "Glasswright Pel", "Guard-Captain Ro", "Little Mica"],
        "encounters": [
            ("water_trial", "A public cistern is locked while children wait with cracked cups.", "mercy"),
            ("glass_storm", "A glass storm sweeps the street and every shelter has a price.", "endurance"),
            ("forge_duel", "A masked duelist challenges anyone carrying Guardian fire.", "strength"),
            ("ember_choir", "The ember choir sings courage into refugees but fear into soldiers.", "resolve"),
        ],
        "events": ["carry water under arrows", "cool a runaway forge", "hide refugees in kiln tunnels", "cross a salt-flat mirage"],
    },
    "Sky Kingdom": {
        "identity": "chain bridges, cloud farms, oath flags, and wind laws that punish careless lies",
        "people": ["Tamsin Ropewise", "Cloudherd Epp", "Flag-Judge Nara", "Falconer Soot"],
        "encounters": [
            ("bridge_sway", "A bridge begins to sway while merchants freeze halfway across.", "agility"),
            ("false_shortcut", "A smiling guide sells a shortcut that cannot possibly hold your weight.", "truths"),
            ("cloud_stampede", "Cloud sheep stampede through a sky orchard and tear loose the anchors.", "agility"),
            ("flag_oath", "Oath flags demand one honest confession before the path will steady.", "mercy"),
        ],
        "events": ["balance along a singing chain", "catch falling supplies", "race a storm elevator", "choose which bridge to cut"],
    },
    "Frost Kingdom": {
        "identity": "silent halls, memory mirrors, snow caravans, and laws written to outlast grief",
        "people": ["Archivist Linn", "Sledge-Mother Va", "Mirror Page Osk", "Hunter Brek"],
        "encounters": [
            ("whiteout", "A whiteout erases the road and voices answer from the wrong direction.", "endurance"),
            ("memory_mirror", "A mirror shows your worst choice and waits for you to name it.", "truths"),
            ("lost_caravan", "A caravan is alive but ready to leave its slowest member behind.", "mercy"),
            ("ice_debt", "A frozen contract binds a village to a queen who no longer protects it.", "resolve"),
        ],
        "events": ["share heat in a snow trench", "mark names on ice", "hunt blue-flame wolves", "carry a survivor through drifts"],
    },
    "Storm Kingdom": {
        "identity": "copper towers, curfew sirens, thunder codes, and rebels speaking in timed sparks",
        "people": ["Professor Venn", "Relay Runner Kip", "Switchmaster Ona", "Static Saint Brill"],
        "encounters": [
            ("curfew_net", "A curfew net drops from the towers and sparks across the street.", "agility"),
            ("coded_rebel", "A rebel gives a thunder code but cannot know if you are watched.", "truths"),
            ("runaway_engine", "A runaway engine pulls a worker toward spinning gears.", "strength"),
            ("law_machine", "A law machine prints a cruel sentence and asks you to stamp it legal.", "resolve"),
        ],
        "events": ["time a lightning rail", "jam a patrol automaton", "decode rebel thunder", "steal batteries for a clinic"],
    },
    "Green Kingdom": {
        "identity": "root roads, fox bargains, mushroom courts, and healing that begins by naming rot",
        "people": ["Foxguide Luma", "Mushroom Abbot Pell", "Root-Singer Ana", "Bee Knight Saff"],
        "encounters": [
            ("poison_bloom", "Poison blooms around a spring that animals still try to drink from.", "vitality"),
            ("fox_bargain", "A fox offers a perfect answer in exchange for an ugly truth.", "truths"),
            ("moss_trial", "Moss grows over an old wound and asks whether covered means healed.", "mercy"),
            ("stag_track", "Blight tracks split into many paths, and only healthy roots know the real one.", "agility"),
        ],
        "events": ["cleanse a spring", "settle a beehive dispute", "follow root-signs", "burn black flowers carefully"],
    },
    "Light Kingdom": {
        "identity": "dawn roads, confession shrines, mirror bells, and pilgrims who carry both hope and guilt",
        "people": ["Dawn Oracle", "Pilgrim Sera", "Bell-Keeper Ion", "Lantern Girl Vey"],
        "encounters": [
            ("confession_gate", "A gate of light opens only after someone admits what they fear becoming.", "truths"),
            ("hope_tax", "A priest demands payment for blessings that should have been free.", "resolve"),
            ("shadow_pilgrim", "A pilgrim's shadow walks away and begins repeating their secret shame.", "mercy"),
            ("last_lantern", "The last lantern dims whenever anyone lies about why they fight.", "truths"),
        ],
        "events": ["guide pilgrims at dawn", "answer a mirror bell", "defend a free shrine", "carry the last lantern"],
    },
    "Ashvale": {
        "identity": "bakery smoke, well ropes, repaired fences, and neighbors who remember every kindness",
        "people": ["Mara the Baker", "Pippin", "Old Fen", "Elder Rowan"],
        "encounters": [
            ("bakery_fire", "Mara's oven flares with black flame while bread for refugees burns.", "strength"),
            ("well_shadow", "The village well reflects a sky that is not above you.", "truths"),
            ("pippin_memory", "Pippin asks whether heroes still come home after the songs end.", "mercy"),
            ("fen_drill", "Old Fen insists scared hands can still learn one more guard stance.", "resolve"),
        ],
        "events": ["mend a fence", "carry well water", "guard the bakery line", "teach children where to hide"],
    },
    "Chaos": {
        "identity": "impossible roads, broken clocks, borrowed voices, and memories shuffled until choices hurt",
        "people": ["The Road That Answers", "Nine-Handed Beggar", "Lost Echo of Eronmere", "Door Without Hinges"],
        "encounters": [
            ("wrong_map", "The map redraws itself into a place you regret but never visited.", "truths"),
            ("echo_bargain", "An echo offers Kael's apology in a voice that might not be his.", "mercy"),
            ("hunger_clock", "A clock eats an hour from everyone who refuses to choose.", "resolve"),
            ("broken_camp", "You find your own camp already abandoned, with fresh footprints leaving backward.", "vitality"),
        ],
        "events": ["follow a compass that points inward", "answer a door's question", "fight a memory twice", "refuse an easy resurrection"],
    },
}


kingdom_storylines = {
    "Stone Kingdom": [
        "The chapter opens with miners refusing to enter shafts until every missing name is spoken aloud.",
        "Debt guards patrol the lift platforms, so rescue work becomes a fight against greed before monsters appear.",
        "A child offers you a cracked lamp and asks you to bring back the people who taught it to glow.",
        "The lower tunnels change layout when frightened miners lie about which supports they removed.",
        "Oren remembers old union songs, and singing them can turn strangers into helpers for one scene.",
        "A stone court asks whether a mountain can forgive if no one admits the wound first.",
        "The side story can end with saved miners, exposed ledgers, or a dangerous shortcut left sealed.",
    ],
    "Tide Kingdom": [
        "The chapter opens with bell towers ringing different tides for rich docks and poor docks.",
        "Flood maps become political weapons because whoever controls evacuation routes controls survival.",
        "A ferry family asks you to choose between cargo that feeds a district and passengers already in danger.",
        "Underwater streets contain air pockets with witnesses who saw the Admiral betray his fleet.",
        "Captain Ysra remembers whether you saved strangers or protected supplies first.",
        "The drowned archive rearranges books according to what the player has lied about.",
        "The side story can end with open canals, a public trial, or a secret mercy for the guilty.",
    ],
    "Ember Kingdom": [
        "The chapter opens at a water auction where nobles bid on survival while refugees count empty cups.",
        "Glass storms force choices about shelter, payment, and who gets left outside palace walls.",
        "Forge workers hide rebellion messages in cooling metal, making every tool a possible clue.",
        "The fire cult recruits scared citizens by promising that cruelty will make them safe.",
        "Jara remembers whether you shared water when nobody was watching.",
        "The furnace court demands a duel, a rescue, and a public answer about what strength is for.",
        "The side story can end with cisterns opened, cult masks broken, or a forge repurposed for rebuilding.",
    ],
    "Sky Kingdom": [
        "The chapter opens with a bridge festival where every oath flag tests one tiny truth.",
        "Cloud farmers lose anchors, and saving their harvest changes which routes remain open later.",
        "A false guide sells easy paths, but wind law punishes everyone nearby when a promise is broken.",
        "Falcon nests can be robbed, protected, or negotiated around if the player learned local customs.",
        "Tamsin remembers whether you trusted her rope work or inspected it first.",
        "The highest tower turns fear of falling into illusions that move the battle lanes.",
        "The side story can end with repaired bridges, exposed smugglers, or a rescued sky orchard.",
    ],
    "Frost Kingdom": [
        "The chapter opens with a silent caravan deciding which memories are too heavy to carry.",
        "Whiteouts create survival scenes where sound, warmth, and trust matter more than speed.",
        "Memory mirrors replay earlier player choices and let recurring NPCs comment on them.",
        "Old contracts freeze whole villages in place until someone challenges the queen's version of history.",
        "Archivist Linn remembers whether you preserved names even when rewards were elsewhere.",
        "The ice palace offers painless forgetting as a tempting but dangerous shortcut.",
        "The side story can end with a thawed contract, a saved caravan, or painful truth kept alive.",
    ],
    "Storm Kingdom": [
        "The chapter opens under curfew sirens that turn law into rhythm and fear into schedule.",
        "Thunder codes let rebels speak, but every decoded message risks leading patrols to civilians.",
        "Lightning rails create timing puzzles, ambushes, and quick rescues during travel.",
        "Clockwork courts print punishments before trials, making sabotage a moral question instead of a prank.",
        "Professor Venn remembers whether you protected his students or stole his batteries.",
        "The palace machine changes enemy turn order unless the player disrupts its relays.",
        "The side story can end with free thunder, broken curfew towers, or a repaired clinic grid.",
    ],
    "Green Kingdom": [
        "The chapter opens in a forest that looks healed from above and rotten at the roots.",
        "Fox bargains offer clever shortcuts that cost honesty, supplies, or future trust.",
        "Mushroom courts argue slowly, so patience can unlock allies that violence never would.",
        "Black flowers spread when people call sickness beautiful instead of treating it.",
        "Foxguide Luma remembers whether you told the truth when a lie would have made you look noble.",
        "The heart grove turns choices into living paths with different food, water, and battle risks.",
        "The side story can end with cleansed springs, named rot, or seeds planted for later epilogues.",
    ],
    "Light Kingdom": [
        "The chapter opens on a dawn road where every shrine asks for confession instead of payment.",
        "Pilgrims carry regrets as lanterns, and helping them can change the final moral score.",
        "Mirror bells ring when someone hides a selfish reason behind heroic words.",
        "False priests sell hope to desperate people, forcing a choice between exposure and immediate aid.",
        "The Dawn Oracle remembers every mercy, truth, and betrayal carried into the last chapters.",
        "The final lantern grows brighter when companions attack for reasons beyond obedience.",
        "The side story can end with free shrines, honest pilgrims, or a harder but cleaner path to Seraphine.",
    ],
    "Ashvale": [
        "The chapter opens with home chores that matter because the world is made of ordinary lives.",
        "Mara's bakery becomes a supply hub, memorial hall, and target for enemies trying to break morale.",
        "Pippin's clay bird appears in scenes where courage needs to be small before it becomes grand.",
        "Old Fen teaches defensive stances that can unlock partner tactics in later battles.",
        "Neighbors remember whether you helped before asking for help yourself.",
        "The village changes after each return: repaired fences, new graves, better shelters, warmer meals.",
        "The side story can end with stronger defenses, restored hope, or a promise to come home alive.",
    ],
    "Chaos": [
        "The chapter opens on roads that steal familiar scenes and return them with one cruel detail changed.",
        "Maps, camps, and clocks become enemies unless the player chooses truth over convenience.",
        "Echoes of Eronmere show Kael as hurt, guilty, dangerous, and still responsible for his choices.",
        "Random encounters can repeat with different meanings because Chaos remembers the player incorrectly.",
        "The Road That Answers remembers questions the player never asked and offers impossible bargains.",
        "Companions can interrupt false memories, giving party choice real story weight.",
        "The side story can end with refused resurrection, accepted grief, or extra chaos taint for easy answers.",
    ],
}


def tell_kingdom_storyline(region):
    beats = kingdom_storylines.get(region, kingdom_storylines["Chaos"])
    say(f"Storyline depth for {region}: this arc is built to support about {KINGDOM_GAMEPLAY_TARGET_HOURS} hours of play.")
    for beat in random.sample(beats, k=min(4, len(beats))):
        say(beat)
        pass_time(1)



def remember_person(name, region, impression):
    memory = player["memory"].setdefault(name, {"region": region, "meetings": 0, "impression": impression})
    memory["meetings"] += 1
    if memory["meetings"] == 1:
        say(f"You meet {name} of the {region}. {impression}")
    else:
        say(f"{name} remembers you from before ({memory['meetings']} meetings). They adjust their greeting because of what you did: {memory['impression']}")
        player["morale"] += 2
    return memory


def apply_story_reward(stat):
    if stat in player and isinstance(player[stat], int):
        player[stat] += 1
    elif stat in ("mercy", "resolve", "truths"):
        player[stat] += 1
    player["food"] += random.choice([0, 0, 1])
    player["water"] += random.choice([0, 0, 1])
    clamp()


def handle_kingdom_encounter(region):
    profile = kingdom_profiles.get(region, kingdom_profiles["Chaos"])
    person = random.choice(profile["people"])
    encounter_id, setup, stat = random.choice(profile["encounters"])
    memory = remember_person(person, region, f"They know you from the {encounter_id.replace('_', ' ')}.")
    say(setup)
    if memory["meetings"] > 1:
        say(f"Because {person} remembers you, they skip old suspicion and reveal a different detail this time.")
    choice = ask("How do you handle it?", [("1", "Help openly"), ("2", "Look for the hidden cause"), ("3", "Conserve supplies and move carefully")])
    if choice == "1":
        player["mercy"] += 1
        say(f"You make the merciful choice, and the {region} changes around that kindness.")
        if person in companion_roster and person not in player["companions"] and random.randint(1, 3) == 1:
            player["companions"].append(person)
            say(f"{person} can now be chosen as a battle partner.")
    elif choice == "2":
        player["truths"] += 1
        say(f"You uncover a local truth that would not matter in any other kingdom: {profile['identity']}.")
    else:
        player["resolve"] += 1
        pass_time(1)
        say("You spend extra time, but fewer people are hurt because you refuse to rush.")
    apply_story_reward(stat)
    if random.randint(1, 3) == 1:
        names = random.sample(region_enemies.get(region, ["Road Ghoul"]), k=1)
        if random.randint(1, 4) == 1:
            names.append(f"{region} Elite")
        enemies = []
        for name in names:
            level = max(8, power() + random.randint(-1, 4))
            enemies.append(make_enemy(name, level, level, level, level))
        battle(enemies)


def run_kingdom_sandbox(region, rounds=8):
    profile = kingdom_profiles.get(region, kingdom_profiles["Chaos"])
    say(f"This kingdom has its own two-hour-style adventure loop: {profile['identity']}.")
    say("The main story stays fixed, but side events, people, rewards, and dangers are shuffled each run.")
    tell_kingdom_storyline(region)
    for _ in range(rounds):
        pass_time(1)
        if random.randint(1, 2) == 1:
            say(f"Local event: you {random.choice(profile['events'])}.")
            if random.randint(1, 4) == 1:
                player["food"] += 1
            if random.randint(1, 4) == 1:
                player["water"] += 1
        else:
            handle_kingdom_encounter(region)
        if player["hunger"] < 35 and player["food"] > 0:
            eat()
        if player["thirst"] < 35 and player["water"] > 0:
            drink()
    clamp()

region_enemies = {
    "Ashvale": ["Smoke-Wolf", "Cinder Imp"],
    "Stone Kingdom": ["Gravel Gnawer", "Iron-Thorn Bandit"],
    "Tide Kingdom": ["Drowned Sailor", "Reef Serpent"],
    "Ember Kingdom": ["Coal Hound", "Brass Cultist"],
    "Sky Kingdom": ["Razor Gull", "Hollow Harrier"],
    "Frost Kingdom": ["White Warg", "Mirror Wraith"],
    "Storm Kingdom": ["Volt Jackal", "Glass Knight"],
    "Green Kingdom": ["Blight Stag", "Moss Revenant"],
    "Light Kingdom": ["Eclipse Choir", "Pale Sentinel"],
    "Chaos": ["Broken Echo", "Ninth Spawn"],
}


def say(text, speed=0.01):
    if FAST_TEXT:
        print(text)
        return
    for letter in text:
        sys.stdout.write(letter)
        sys.stdout.flush()
        time.sleep(speed)
    print()


def ask(prompt, choices=None):
    if choices:
        while True:
            print(prompt)
            for key, label in choices:
                print(f"{key}. {label}")
            choice = input("> ").strip().lower()
            if choice in [key for key, _ in choices]:
                return choice
            print("Choose one of the listed options.")
    return input(prompt + "\n> ").strip()


def power():
    return round((player["strength"] + player["endurance"] + player["vitality"] + player["agility"]) / 4)


def health():
    return round((player["energy"] + player["morale"] + player["thirst"] + player["hunger"]) / 4)


def clamp():
    for stat in ("energy", "morale", "thirst", "hunger"):
        player[stat] = max(0, min(100, player[stat]))


def show_time():
    print(f"Day {day} | {hour:02d}:00")


def hourly_decay():
    player["energy"] -= 1
    player["thirst"] -= 2
    player["hunger"] -= 1
    if player["thirst"] < 30 or player["hunger"] < 30:
        player["morale"] -= 1
    clamp()


def pass_time(hours):
    global day, hour
    for _ in range(hours):
        hour += 1
        if hour >= 24:
            hour = 0
            day += 1
        hourly_decay()


def equip_food(name):
    if name in foods:
        player["equipped_food"] = name


def equip_water(name):
    if name in waters:
        player["equipped_water"] = name


def eat():
    item = player["equipped_food"]
    if not item or player["food"] <= 0:
        say("You search your pack and find no food ready to eat.")
        return False
    for stat, value in foods[item].items():
        player[stat] += value
    player["food"] -= 1
    clamp()
    say(f"You eat {item}. Warmth returns to your hands.")
    return True


def drink():
    item = player["equipped_water"]
    if not item or player["water"] <= 0:
        say("Your canteen is empty.")
        return False
    for stat, value in waters[item].items():
        player[stat] += value
    player["water"] -= 1
    clamp()
    say(f"You drink {item}. The road sharpens before you.")
    return True


def random_event():
    return random.choice(events)


def make_enemy(name, strength, endurance, vitality, agility):
    return {"name": name, "strength": strength, "endurance": endurance, "vitality": vitality, "agility": agility, "energy": 100, "morale": 100, "thirst": 100, "hunger": 100}


def enemy_power(enemy):
    return round((enemy["strength"] + enemy["endurance"] + enemy["vitality"] + enemy["agility"]) / 4)


def enemy_health(enemy):
    return round((enemy["energy"] + enemy["morale"] + enemy["thirst"] + enemy["hunger"]) / 4)


companion_roster = {
    "Mira": {"power": 8, "energy": 85, "skill": "Expose Weakness"},
    "Kael, the Hooded Traveler": {"power": 9, "energy": 80, "skill": "Shadow Ward"},
    "Tamsin Ropewise": {"power": 7, "energy": 75, "skill": "Tripline"},
    "Professor Venn": {"power": 6, "energy": 70, "skill": "Static Charge"},
    "Oren Deepdelver": {"power": 8, "energy": 90, "skill": "Shield Brace"},
}


def choose_partner():
    available = [name for name in player["companions"] if name in companion_roster]
    if not available:
        return None
    choices = [(str(index + 1), name) for index, name in enumerate(available)]
    choices.append(("0", "Fight without a partner"))
    choice = ask("Choose one battle partner for this fight.", choices)
    if choice == "0":
        return None
    name = available[int(choice) - 1]
    partner = dict(companion_roster[name])
    partner["name"] = name
    say(f"{name} joins the front line with {partner['skill']}.")
    return partner


def living_enemies(enemies):
    return [enemy for enemy in enemies if enemy_health(enemy) > 0]


def battle(enemy):
    enemies = enemy if isinstance(enemy, list) else [enemy]
    partner = choose_partner()
    enemy_names = ", ".join(enemy["name"] for enemy in enemies)
    say(f"\nBattle begins against {enemy_names}.")
    guarded = False
    while health() > 0 and living_enemies(enemies):
        print("\n--------------------")
        print(f"You: {health()} HP")
        if partner:
            print(f"{partner['name']}: {partner['energy']} energy | Skill: {partner['skill']}")
        for index, foe in enumerate(enemies, start=1):
            print(f"{index}. {foe['name']}: {enemy_health(foe)} HP")
        print("1. Attack")
        print("2. Guard")
        print("3. Eat")
        print("4. Drink")
        print("5. Run")
        print("6. Rally partner")
        choice = input("> ").strip()
        guarded = choice == "2"
        target = random.choice(living_enemies(enemies))
        if choice == "1":
            damage = random.randint(max(1, power() - 2), power() + 4)
            target["energy"] -= damage
            print(f"You dealt {damage} damage to {target['name']}.")
        elif choice == "2":
            player["morale"] += 4
            print("You steady your breathing and raise your guard for the whole party.")
        elif choice == "3":
            eat()
        elif choice == "4":
            drink()
        elif choice == "5":
            escape_score = player["agility"] + (partner["power"] // 2 if partner else 0)
            if random.randint(1, 24) <= escape_score:
                print("Your party escaped!")
                return False
            print("Couldn't escape!")
        elif choice == "6" and partner:
            partner["energy"] = min(100, partner["energy"] + 12)
            player["morale"] += 3
            print(f"You rally {partner['name']}; they prepare {partner['skill']}.")
        else:
            print("You hesitate.")
        clamp()
        if partner and partner["energy"] > 0 and living_enemies(enemies):
            target = random.choice(living_enemies(enemies))
            damage = random.randint(max(1, partner["power"] - 2), partner["power"] + 4)
            if partner["skill"] in ("Expose Weakness", "Static Charge"):
                damage += 2
            target["energy"] -= damage
            partner["energy"] = max(0, partner["energy"] - random.randint(3, 7))
            print(f"{partner['name']} uses {partner['skill']} and deals {damage} damage to {target['name']}.")
        if not living_enemies(enemies):
            print("Enemies defeated!")
            player["morale"] += 8
            clamp()
            return True
        for foe in living_enemies(enemies):
            target_player = not partner or random.randint(1, 2) == 1 or partner["energy"] <= 0
            damage = random.randint(max(1, enemy_power(foe) - 3), enemy_power(foe) + 3)
            if guarded:
                damage = max(1, damage // 2)
            if target_player:
                player["energy"] -= damage
                clamp()
                print(f"{foe['name']} attacks you for {damage} damage.")
            else:
                partner["energy"] = max(0, partner["energy"] - damage)
                print(f"{foe['name']} attacks {partner['name']} for {damage} damage.")
        # Every living participant has now acted once this turn: you, partner, then each enemy.
    print("You were defeated, but the compass burns cold and drags you back from the dark.")
    player["energy"] = 25
    player["morale"] = max(player["morale"], 20)
    player["chaos_taint"] += 1
    return False


def stats():
    print("\n=== PLAYER ===")
    print(f"Power : {power()}")
    print(f"Health: {health()}")
    print(f"Strength : {player['strength']}")
    print(f"Endurance: {player['endurance']}")
    print(f"Vitality : {player['vitality']}")
    print(f"Agility  : {player['agility']}")
    print(f"Energy : {player['energy']}")
    print(f"Morale : {player['morale']}")
    print(f"Hunger : {player['hunger']}")
    print(f"Thirst : {player['thirst']}")
    print(f"Food Supply : {player['food']}")
    print(f"Water Supply: {player['water']}")
    print(f"Inventory: {', '.join(player['inventory'])}")
    print(f"Companions: {', '.join(player['companions']) if player['companions'] else 'None'}")
    if player["memory"]:
        print("People who remember you:")
        for name, memory in sorted(player["memory"].items()):
            print(f"- {name} ({memory['region']}): {memory['meetings']} meeting(s)")


def menu():
    while True:
        choice = ask("Make camp preparations.", [("1", "Continue"), ("2", "View stats"), ("3", "Eat"), ("4", "Drink"), ("5", "Change rations")])
        if choice == "1":
            return
        if choice == "2":
            stats()
        elif choice == "3":
            eat()
        elif choice == "4":
            drink()
        elif choice == "5":
            select_rations()


def select_rations():
    print("Foods:", ", ".join(foods))
    name = ask("Equip which food?")
    if name in foods:
        equip_food(name)
    print("Waters:", ", ".join(waters))
    name = ask("Equip which water?")
    if name in waters:
        equip_water(name)


def rest(hours=6):
    say(f"You rest for {hours} hours.")
    pass_time(hours)
    player["energy"] += 30
    player["morale"] += 12
    clamp()


def travel(region, hours, danger=1):
    say(f"\nYou travel through {region} for {hours} hours.")
    for step in range(hours):
        pass_time(1)
        if step % 3 == 0:
            show_time()
        if player["hunger"] < 35:
            say("Hunger hollows your thoughts.")
            if player["food"] > 0:
                eat()
        if player["thirst"] < 35:
            say("Thirst rasps at your throat.")
            if player["water"] > 0:
                drink()
        if random.randint(1, 10) <= danger:
            handle_event(region)
    menu()


def handle_event(region):
    event = random_event()
    if event == "enemy":
        name = random.choice(region_enemies.get(region, ["Road Ghoul"]))
        level = max(8, power() + random.randint(-2, 3))
        battle(make_enemy(name, level, level, level, level))
    elif event == "food":
        player["food"] += 1
        say("You find usable provisions hidden in a weathered shrine.")
    elif event == "water":
        player["water"] += 1
        say("You refill a canteen from a clean trickle of water.")
    elif event == "traveler":
        player["morale"] += 5
        say("A passing traveler shares rumors, songs, and a warning about black stars.")
    elif event == "omen":
        player["morale"] -= 4
        player["truths"] += 1
        say("The compass points at your own shadow. For a heartbeat, it has nine hands.")
    elif event == "memory":
        player["morale"] += 3
        if player["memory"]:
            name = random.choice(list(player["memory"]))
            say(f"You remember {name}, and the road feels less empty because history now travels with you.")
        else:
            say("A small kindness from home returns to you like a candle in rain.")
    elif event == "kingdom_encounter":
        handle_kingdom_encounter(region)
    clamp()


def reward(mark, stat):
    player["guardian_marks"].append(mark)
    player[stat] += 2
    player["food"] += 2
    player["water"] += 2
    player["resolve"] += 1
    say(f"The Mark of {mark} settles into your spirit. Your {stat} rises.")



def companion_campfire(region):
    say("Night settles around the camp in layers: smoke, cold, stars, and the silence after hard walking.")
    pass_time(1)
    if "Mira" in player["companions"]:
        say("Mira cleans her knife with a scrap of map paper. 'I keep drawing roads we have not earned yet,' she says.")
        say("She marks a little circle for home, then hides it under her thumb before anyone can see her hand shake.")
    if "Kael, the Hooded Traveler" in player["companions"]:
        say("Kael sits just beyond the firelight. Sparks rise through him without touching his cloak.")
        say("When you ask how he knows the old roads, he answers, 'I have been lost longer than most kingdoms have been named.'")
    choice = ask("How do you spend the quiet hour?", [("1", "Share food and stories"), ("2", "Keep watch in silence"), ("3", "Study the ancient compass")])
    if choice == "1":
        player["morale"] += 8
        player["food"] = max(0, player["food"] - 1)
        say("The meal is small, but laughter makes it feel like a feast.")
    elif choice == "2":
        player["energy"] += 5
        player["resolve"] += 1
        say("The others sleep because you do not. Dawn finds you tired but certain.")
    else:
        player["truths"] += 1
        player["morale"] -= 2
        say("The compass needle turns beneath the glass and briefly points at Kael's sleeping heart.")
    clamp()
    pass_time(1)


def optional_discovery(region):
    discoveries = {
        "Stone Kingdom": [
            "You find a side tunnel with fresh air, dry ground, and tool marks on the wall.",
            "Mira marks the tunnel on her map because it can be used as a safe return path.",
            "Behind a loose stone, you find wrapped travel bread and add it to your food supply.",
            "The discovery is simple but useful: the mine is dangerous, and supplies matter here.",
        ],
        "Tide Kingdom": [
            "Rain runs through clean roof channels and into public barrels.",
            "You refill your canteen and check that everyone has enough water for the next road.",
            "A sailor points to the flooded palace and says the water rises whenever the Admiral is angry.",
            "The city teaches you the rule of this chapter: move carefully, keep water close, and watch the tide.",
        ],
        "Ember Kingdom": [
            "Heat rolls through the streets, and your throat dries faster than it did on the open road.",
            "You help carry water jars to families hiding from the fire cult.",
            "A tired guard tells you the cult meets near the palace furnaces after sunset.",
            "This region is about strength, but the first lesson is clear: strength is used to protect people.",
        ],
        "Sky Kingdom": [
            "You cross a high bridge where the wind pushes hard against your shoulders.",
            "Mira ties a safety rope to your pack so one bad step does not end the journey.",
            "Tamsin gives you apples, points to the next tower, and warns you about knife-winged falcons.",
            "The Sky Kingdom tests agility, balance, and honest choices on narrow paths.",
        ],
        "Frost Kingdom": [
            "Snow falls so thickly that the road disappears behind you after only a few steps.",
            "You find a stone shelter, share heat, and decide who needs food before the next march.",
            "Mira writes the names carved in the ice so they are not lost again.",
            "The Frost Kingdom makes the system plain: low energy and low morale can be as dangerous as monsters.",
        ],
        "Storm Kingdom": [
            "Lightning rails hum above the street and light the city in blue flashes.",
            "Professor Venn shows you a machine gate that opens only when the thunder pattern is matched.",
            "Mira spots patrol routes, curfew signs, and locked supply boxes near the palace road.",
            "This place is fast and loud, so agility and careful timing matter before every fight.",
        ],
        "Green Kingdom": [
            "Healthy roots lift stones from the road and point you away from black flowers.",
            "A fox guide offers help only after you tell one true thing without making yourself sound perfect.",
            "You find clean berries, but Mira checks them twice before anyone eats.",
            "The Green Kingdom teaches recovery: nature can heal, but only after the sickness is named.",
        ],
        "Ashvale": [
            "You repair one burned wall, carry water from the well, and pass bread to tired neighbors.",
            "The village cannot give you a Guardian mark, but it gives you food, water, and morale.",
            "Pippin places his clay bird in the window so everyone remembers why you are fighting.",
            "Home is not a quiet chapter. It is the reason the whole journey matters.",
        ],
        "Chaos": [
            "The road bends in wrong directions, so you stop guessing and follow the compass.",
            "Mira finds records showing that the eight Guardians are also eight locks on one prison.",
            "Kael knows too much about the prison songs and will not explain how he learned them.",
            "Chaos is confusing, but the goal stays clear: learn the truth before the final lock opens.",
        ],
        "Light Kingdom": [
            "The road climbs toward dawn, but the air feels quiet instead of safe.",
            "Pilgrims leave simple notes at the shrine: names of people they failed, helped, or miss.",
            "The compass stops pointing to the road and points toward your chest.",
            "The Light Kingdom is the final test of truth, mercy, and resolve.",
        ],
    }
    for text in discoveries.get(region, ["You find an old camp, check your supplies, and keep moving."]):
        say(text)
        pass_time(1)
        if player["hunger"] < 45 and player["food"] > 0:
            eat()
        if player["thirst"] < 45 and player["water"] > 0:
            drink()
    if region in ("Tide Kingdom", "Sky Kingdom", "Green Kingdom"):
        player["morale"] += 4
    if region in ("Frost Kingdom", "Chaos"):
        player["morale"] -= 3
    clamp()


def guardian_conversation(region, guardian):
    talks = {
        "Brunda the Earth Guardian": [
            "Brunda, Guardian of Earth, rises from the stone floor slowly enough for dust to fall from her shoulders.",
            "She says the mine is not cursed. It is breaking because greedy leaders cut supports and called it progress.",
            "She asks whether you came for a blessing or whether you came to help people who are still trapped below.",
            "Her trial is clear: stand firm, carry weight for others, and do not confuse patience with doing nothing.",
        ],
        "Nerys the Water Guardian": [
            "Nerys, Guardian of Water, waits under the flooded palace where the windows glow blue.",
            "She says water can save, drown, clean, or hide. The choice belongs to the person using it.",
            "She asks you to show mercy, but also to stop anyone who keeps hurting the helpless.",
            "Her trial is clear: move with the flood, save who you can, and do not let grief become an excuse.",
        ],
        "Solun the Fire Guardian": [
            "Solun, Guardian of Fire, steps from a furnace and lowers the heat so you can breathe.",
            "He says fire is not only rage. It is also ovens, lamps, warnings, and courage on cold nights.",
            "He asks what your strength is for: burning enemies, protecting families, or making a safer road.",
            "His trial is clear: use power on purpose, and never call cruelty necessary just because it is easy.",
        ],
        "Vaelor the Wind Guardian": [
            "Vaelor, Guardian of Wind, arrives with a gust strong enough to shake every bridge chain.",
            "They say freedom is good, but freedom without care can knock innocent people from the sky.",
            "They ask if you can move quickly while still watching the people behind you.",
            "Their trial is clear: balance speed with duty, and do not run from the cost of your choices.",
        ],
        "Ilyra the Ice Guardian": [
            "Ilyra, Guardian of Ice, sits in a quiet hall where every footstep sounds important.",
            "She says memory protects people from repeating old harm, but memory can also trap the living.",
            "She asks you to carry the past without letting it freeze your heart shut.",
            "Her trial is clear: endure the cold, keep the names, and still choose tomorrow.",
        ],
        "Astrax the Lightning Guardian": [
            "Astrax, Guardian of Lightning, speaks in bright flashes that make the room feel awake.",
            "He says quick power can save a falling child or build a prison before anyone can object.",
            "He asks whether you want power so people fear you or so people can find their way home.",
            "His trial is clear: act fast, but make sure your first answer is not your worst one.",
        ],
        "Eloane the Nature Guardian": [
            "Eloane, Guardian of Nature, speaks through leaves, roots, birds, and the soil under your boots.",
            "She says nature can heal, but it does not heal by pretending sickness is beautiful.",
            "She asks what you will plant after anger has used up every field.",
            "Her trial is clear: name the rot, pull it out, and leave room for new life.",
        ],
        "Seraphine": [
            "Seraphine, Guardian of Light, waits in the last shrine with no crown and no army.",
            "She says light does not make people innocent. It only shows what is true.",
            "She knows Kael from before the hood, before the compass, and before Chaos used his grief.",
            "Her trial is clear: face the truth, even when truth does not make anyone look clean.",
        ],
        "Nerys's Echo": [
            "Nerys's Echo rises from a cracked shell and speaks with a softer voice than the Guardian had.",
            "It says the old war began when each side stopped listening and started calling fear wisdom.",
            "The echo cannot fight for you, but it can show where the truth was hidden.",
        ],
        "Solun's Ember": [
            "Solun's Ember glows above a brazier and spits small sparks when people lie.",
            "It says courage does not mean feeling safe. Courage means helping while afraid.",
            "It asks you to carry that lesson into the next hard choice.",
        ],
        "Brunda's Root": [
            "Brunda's Root taps the cave floor in a slow rhythm like a heartbeat.",
            "It says the first Guardians were ordinary people who held the line after heroes failed.",
            "It reminds you that endurance is not loud, but it can save a world.",
        ],
        "Ilyra's Tear": [
            "Ilyra's Tear freezes in your hand without hurting you.",
            "Inside it, you see that winning the final fight will not erase the work after it.",
            "The vision is not hopeless. It is a warning to survive with care.",
        ],
        "Astrax's Spark": [
            "Astrax's Spark jumps between your fingers like a tiny storm trying to teach a lesson.",
            "It says destiny is only a deadline with a louder name.",
            "It tells you to think, choose, and then move before fear makes the choice for you.",
        ],
        "Eloane's Seed": [
            "Eloane's Seed hums in your pack whenever the road grows quiet.",
            "It shows roots sharing food with weak trees instead of leaving them to die.",
            "It asks you to remember that survival is stronger when it is shared.",
        ],
        "No Guardian": [
            "Ashvale has no Guardian waiting at the end of the street.",
            "Instead, your neighbors bring food, water, bandages, and tired smiles.",
            "They remind you that saving the world only matters because real people live in it.",
        ],
        "The Dawn Oracle": [
            "The Dawn Oracle stands at the gate of light and does not speak in riddles.",
            "It says the last choice will test mercy, resolve, and truth together.",
            "It warns you that a simple answer can still be a hard answer.",
        ],
    }
    for text in talks.get(guardian, [f"{guardian} watches you and waits for your answer."]):
        say(text)
        pass_time(1)
    choice = ask("What do you ask before the trial begins?", [("1", "What happened long ago?"), ("2", "What are you afraid of?"), ("3", "Why does Kael know this?")])
    if choice == "1":
        player["truths"] += 1
        say("You learn that Chaos was locked away by the eight Guardians after the elements nearly destroyed each other.")
    elif choice == "2":
        player["mercy"] += 1
        say("The Guardian says even old powers fear making one wrong choice and being obeyed forever.")
    else:
        player["truths"] += 1
        player["chaos_taint"] += 1
        say("Kael looks away. The Guardian knows his secret, but Kael is not ready to say it aloud.")
    clamp()


def boss_introduction(boss, region):
    speeches = {
        "Lord Malgrit of the Hollow Mine": [
            "Lord Malgrit blocks the mine gate with armed guards behind him.",
            "He used miners as tools and cut corners until the mountain started to fail.",
            "This fight is not only about winning. It is about freeing the people trapped below.",
        ],
        "The Drowned Admiral": [
            "The Drowned Admiral rises from the harbor with a ship bell ringing under the water.",
            "He saved himself by sinking others, and now he calls that leadership.",
            "The battle begins where the flood is strongest, so you brace yourself and watch your footing.",
        ],
        "The Brass Prophet": [
            "The Brass Prophet lifts a burning mask before the palace furnaces.",
            "He says weak people should be burned away so the world can be pure.",
            "Solun's lesson is clear here: fire should protect homes, not decide who deserves to live.",
        ],
        "The Silent Falconer": [
            "The Silent Falconer sends knife-winged birds across the tower bridge.",
            "He never speaks because fear already carries his message for him.",
            "The fight tests agility, timing, and whether you can move without losing your courage.",
        ],
        "Queen Rimeheart": [
            "Queen Rimeheart stands behind frozen mirrors that show people at their worst moments.",
            "She wants a kingdom where nothing changes, because change once hurt her.",
            "Ilyra's trial answers her: memory matters, but life must still move.",
        ],
        "The Clockwork Tyrant": [
            "The Clockwork Tyrant marches out of the palace machine in perfect metal steps.",
            "It turns laws into chains and calls mercy a broken part.",
            "Astrax's power flashes in the machine core, waiting to be freed.",
        ],
        "The Blight Stag": [
            "The Blight Stag steps from the sick forest with black flowers falling from its antlers.",
            "It was once sacred, but the Eclipse taught its wounds to spread.",
            "Eloane's lesson guides you: name the rot, then pull it out.",
        ],
        "The Eclipse Butcher": [
            "The Eclipse Butcher walks into Ashvale wearing voices the village still misses.",
            "It tries to make home feel unsafe so morale will break before the fight starts.",
            "Your neighbors stand behind you, and that is the mark this chapter gives.",
        ],
        "Archivist of Teeth": [
            "The Archivist of Teeth guards the drowned records with stolen mouths on its robe.",
            "It eats witnesses so history becomes easier to control.",
            "Mira raises her notes, and the boss attacks because truth is now in the open.",
        ],
        "The Cinder Regent": [
            "The Cinder Regent waits above the furnaces while refugees are pushed toward the heat.",
            "He sells fear as order and calls every selfish choice necessary.",
            "The chapter's courage becomes simple: protect the people he would spend.",
        ],
        "The Mountain That Hates": [
            "The mountain wakes with a sound like stone learning to breathe.",
            "Old greed left wounds in its deep places, and now those wounds answer as rage.",
            "Endurance matters here because the mountain will not fall quickly or kindly.",
        ],
        "The Future Eater": [
            "The Future Eater sings softly from the snowfield.",
            "It offers to remove pain by removing every future where pain could happen.",
            "You choose a hard tomorrow over an empty one, and the song becomes a battle.",
        ],
        "The Thunderless King": [
            "The Thunderless King waits in a fortress where even your heartbeat sounds too loud.",
            "He stole thunder so rebels could not hear each other gather.",
            "Astrax's Spark jumps in your hand, reminding you that silence is not the same as peace.",
        ],
        "The First Serpent": [
            "The First Serpent waits in the garden beside the first refused apology.",
            "It twists kind wishes into cruel choices and then blames the person who wished.",
            "This battle is about seeing the trick before it turns mercy into harm.",
        ],
        "The Pale Herald": [
            "The Pale Herald lifts a dark trumpet at the last shrine of light.",
            "It says hope has failed and every lamp should go out before disappointment can return.",
            "Seraphine stands with you, and the final light refuses to be quiet.",
        ],
        "The Candleless Monk": [
            "The Candleless Monk blocks the dawn gate with an empty lantern.",
            "He believes hope is cruel because it asks people to try again.",
            "The Dawn Oracle waits beyond him, so this fight opens the way to the final truth.",
        ],
    }
    for text in speeches.get(boss, [f"{boss} comes from {region} and brings the Eclipse with it."]):
        say(text)
        pass_time(1)
    if player["morale"] < 40:
        say("Your hands shake, but your companions stand beside you and remind you why you came.")
    else:
        say("You step forward with enough courage to start, even if you still feel afraid.")
    clamp()


def chapter_aftermath(region, guardian, mark):
    say("The battle's noise leaves slowly, like thunder reluctant to become memory.")
    pass_time(1)
    if guardian != "No Guardian":
        say(f"{guardian} gives no grand blessing at first. Legends, you are learning, need time to breathe after pain.")
        say(f"The Guardian's farewell is quiet: a touch to your brow, a warning to watch Kael, and the Mark of {mark} burning like sunrise beneath your skin.")
    else:
        say("Ashvale does not grant a holy mark. It grants something harder: people who expect you to come back alive.")
    if "Mira" in player["companions"]:
        say("Mira writes the victory down, then crosses out victory and writes survived.")
    if region in ("Stone Kingdom", "Ember Kingdom", "Storm Kingdom"):
        player["food"] += 1
        say("Grateful locals press extra provisions into your pack despite your protests.")
    if region in ("Tide Kingdom", "Frost Kingdom", "Light Kingdom"):
        player["water"] += 1
        say("Someone fills your canteen with water blessed by local custom and practical kindness.")
    clamp()


def guardian_chapter(number, title, region, guardian, mark, stat, boss, scenes):
    say(f"\nChapter {number}: {title}")
    show_time()
    for text in scenes:
        say(text)
        pass_time(1)
        if random.randint(1, 6) == 1:
            handle_event(region)
    optional_discovery(region)
    run_kingdom_sandbox(region, rounds=random.randint(6, 9))
    companion_campfire(region)
    travel(region, random.randint(5, 8), danger=2)
    guardian_conversation(region, guardian)
    choice = ask(f"{guardian} asks what humanity deserves.", [("1", "Mercy, because broken people can mend"), ("2", "Strength, because only survivors can protect others"), ("3", "Truth, even when it ruins legends")])
    if choice == "1":
        player["mercy"] += 1
        player["morale"] += 8
    elif choice == "2":
        player["resolve"] += 1
        player["strength"] += 1
    else:
        player["truths"] += 1
        player["chaos_taint"] += 1
    boss_introduction(boss, region)
    battle(make_enemy(boss, power() + 3, power() + 3, power() + 4, power() + 2))
    chapter_aftermath(region, guardian, mark)
    reward(mark, stat)
    rest(5)


def intro():
    say("====================================")
    say("        ELEMENTAL GUARDIANS")
    say("====================================")
    say("A clear fantasy adventure about saving eight Guardians.")
    say("Type the listed number to choose an action.")
    say("Watch food, water, energy, morale, hunger, and thirst. Travel can give supplies or start battles.")
    say("Mercy, resolve, truth, and chaos taint change the ending.")
    choice = ask("Before the story begins, how do you spend an ordinary Ashvale morning?", [("1", "Help at the bakery"), ("2", "Carry water from the well"), ("3", "Practice with a wooden sword")])
    if choice == "1":
        player["food"] += 2
        player["morale"] += 4
        say("You pack extra bread and feel ready.")
    elif choice == "2":
        player["water"] += 2
        player["endurance"] += 1
        say("You carry heavy buckets and grow tougher.")
    else:
        player["strength"] += 1
        player["resolve"] += 1
        say("Old Fen teaches you basic footwork.")
    clamp()
    show_time()
    stats()
    say("Ashvale is your home. It has a bakery, a well, farms, and neighbors who know you.")
    say("Mara the baker, Pippin, old Fen, and the elder all trust you with small chores.")
    say("The story starts simple: help people, eat breakfast, and stay ready.")
    pass_time(2)


def prologue():
    say("\nPrologue: The Black Sun")
    say("Ashvale starts as a normal village morning.")
    say("Mara gives you bread for the road.")
    player["food"] += 1
    pass_time(1)
    say("Pippin shows you a clay bird he made for his father.")
    say("Travelers warn that the Elemental Guardians are disappearing.")
    pass_time(1)
    say("Then the signs get worse: black milk, nervous crows, and a compass that moves by itself.")
    say("The sun turns black. Monsters attack Ashvale.")
    player["morale"] -= 10
    clamp()
    battle(make_enemy("Eclipse Ravager", 8, 8, 8, 7))
    say("After the fight, people are hurt and homes are burning.")
    say("A hooded traveler named Kael helps rescue the wounded.")
    say("He says the compass chose you because the Guardians need help.")
    say("The compass points toward the next danger instead of north.")
    player["companions"].append("Kael, the Hooded Traveler")
    travel("Ashvale", 6, danger=2)
    say("You find Mira at the ruined bridge.")
    say("She is a courier who records what really happened.")
    say("Together you rescue children from the mill cellar.")
    player["companions"].append("Mira")
    player["inventory"].append("Mira's Map of Living Roads")
    say("Mira studies Kael's compass and does not fully trust him.")
    companion_campfire("Ashvale")


def interlude_truth():
    say("\nChapter 10: The Ninth Door")
    say("You reach Orison, an empty city built around a huge sealed door.")
    optional_discovery("Chaos")
    travel("Chaos", 7, danger=2)
    say("Mira reads the wall records in the archive.")
    say("The eight Guardians are not only protectors. They are locks on a prison.")
    say("Chaos is inside that prison.")
    say("Kael admits the compass wakes each lock when a Guardian is freed.")
    say("He says he thought opening the prison could bring back his lost kingdom.")
    choice = ask("What do you do about Kael?", [("1", "Confront him now"), ("2", "Keep watching him"), ("3", "Ask Mira to take part of the compass")])
    if choice == "1":
        player["truths"] += 2
        say("Kael's shadow attacks when you challenge him.")
        battle(make_enemy("Kael's Shadow", power() + 2, power() + 2, power() + 2, power() + 5))
    elif choice == "2":
        player["chaos_taint"] += 1
        say("You hide your anger so you can learn more.")
    else:
        player["mercy"] += 1
        player["inventory"].append("Stolen Compass Splinter")
        say("Mira steals a compass splinter. It points to Kael and then to your heart.")
    say("Before sleep, Kael says his kingdom died from a plague.")
    say("You still do not know if he is sorry or using you.")
    companion_campfire("Chaos")
    rest(6)


def final_chapters():
    say("\nChapter 18: The Last Guardian of Light")
    say("You travel to the Light Kingdom for the final Guardian.")
    travel("Light Kingdom", 8, danger=2)
    optional_discovery("Light Kingdom")
    say("Seraphine, Guardian of Light, knows Kael's past.")
    guardian_conversation("Light Kingdom", "Seraphine")
    say("Kael says Seraphine let his kingdom die to keep Chaos locked away.")
    say("Seraphine says it is true, and she still carries the guilt.")
    boss_introduction("The Pale Herald", "Light Kingdom")
    battle(make_enemy("The Pale Herald", power() + 5, power() + 4, power() + 5, power() + 4))
    say("Seraphine puts the compass light inside your heart so Kael cannot control it.")
    player["guardian_marks"].append("Light")
    player["vitality"] += 3
    player["mercy"] += 1
    say("Chaos is released, but you now carry every Guardian mark.")
    companion_campfire("Light Kingdom")
    travel("Chaos", 6, danger=3)
    say("\nChapter 19: The Black Eclipse Opens")
    say("Chaos opens the sky like many doors.")
    say("Kael stands under them and wants his dead kingdom back.")
    choice = ask("What do you say to Kael before the final battle?", [("1", "Your grief cannot rule us"), ("2", "You used us, and I will stop you"), ("3", "Help me save what is left of you")])
    if choice == "1":
        player["mercy"] += 1
        say("Kael hears you, but Chaos still holds him.")
    elif choice == "2":
        player["resolve"] += 2
        say("You prepare to end the fight cleanly.")
    else:
        player["mercy"] += 2
        player["chaos_taint"] += 1
        say("Kael reaches back for a moment before Chaos pulls him away.")
    battle(make_enemy("Kael, Vessel of Chaos", power() + 5, power() + 4, power() + 5, power() + 4))
    say("Kael falls, and Chaos breaks free.")
    say("Chaos is the pain and hunger left by every ending.")
    battle(make_enemy("Chaos Unbound", power() + 7, power() + 6, power() + 8, power() + 5))
    ending()


def ending():
    say("\nEnding: The Choice After Chaos")
    if player["mercy"] >= 5 and player["chaos_taint"] <= 3:
        say("You do not destroy Chaos. You bind it and teach the world to face grief safely.")
        say("Kael spends his life repairing the harm he caused.")
        say("Mira writes the true history so no one can hide it again.")
        say("Ending: Dawn Covenant.")
    elif player["resolve"] >= player["mercy"]:
        say("You shatter Chaos and magic fades from the world.")
        say("The Guardians become mortal and the kingdoms rebuild without miracles.")
        say("Mira keeps traveling to protect the truth.")
        say("Ending: Age of Iron.")
    else:
        say("You seal Chaos inside yourself and leave the map behind.")
        say("Travelers later find safe camps that you left for them.")
        say("Mira keeps searching for you.")
        say("Ending: The Wandering Seal.")
    say("The final battle is over. The world now lives with your choices.")
    epilogue()


def epilogue():
    say("\nEpilogue: Roads After Dawn")
    say("Weeks later, Ashvale opens the bakery again.")
    say("Each kingdom rebuilds in a clearer, kinder way.")
    if "Mira" in player["companions"]:
        say("Mira finishes her book and leaves space for survivors to add their stories.")
    if "Kael, the Hooded Traveler" in player["companions"]:
        say("Kael's fate is human and difficult. Some people forgive him, and some do not.")
    say("The compass gives one last click and points to a new road.")
    say("The journey is complete, but the road is still alive.")
    stats()


def campaign():
    chapters = [
        (2, "Earth Trial", "Stone Kingdom", "Brunda the Earth Guardian", "Earth", "endurance", "Lord Malgrit of the Hollow Mine", [
            "You enter the Stone Kingdom with the compass pulling toward the mountains.",
            "Before the climb, you check food, water, energy, and morale because the mine road is long.",
            "Miners explain that supports are breaking and families are trapped below.",
            "You help lift beams into place, which fits the Earth trial and tests endurance.",
            "Mira marks safe tunnels while Kael quietly names paths that should have been forgotten.",
            "At the root-crowned gate, the compass points down to Brunda and the mine's hidden wound.",
        ]),
        (3, "Water Trial", "Tide Kingdom", "Nerys the Water Guardian", "Water", "vitality", "The Drowned Admiral", [
            "Rain begins before the Tide Kingdom walls, and the road turns to shining mud.",
            "You refill water early because this chapter uses floods, canals, and long wet travel.",
            "Ferrymen ask for help moving families out of houses filling with river water.",
            "You choose careful routes over fast ones, keeping morale steady while people are afraid.",
            "Mira learns tide knots from a captain and uses them to mark safe crossings.",
            "When black stairs appear under the harbor, the compass points down to Nerys.",
        ]),
        (4, "Fire Trial", "Ember Kingdom", "Solun the Fire Guardian", "Fire", "strength", "The Brass Prophet", [
            "The Ember Kingdom is bright, loud, and hot enough to make thirst drop quickly.",
            "You ration water before entering Caldera because the desert road punishes carelessness.",
            "Refugees hide in shade while a fire cult promises safety only to the strong.",
            "You carry water jars, move hot metal doors, and use strength to protect instead of threaten.",
            "Kael names an old burned city, and the compass needle shakes in his hand.",
            "Smoke from the palace furnaces forms an arrow toward Solun's shrine.",
        ]),
        (5, "Wind Trial", "Sky Kingdom", "Vaelor the Wind Guardian", "Wind", "agility", "The Silent Falconer", [
            "The Sky Kingdom hangs above the world on bridges, chains, and careful steps.",
            "You tie down loose gear because dropped supplies are gone forever in this region.",
            "Every bridge tests agility, and every lie makes one narrow path tremble.",
            "Tamsin offers a shortcut, but Mira makes you inspect the ropes before trusting it.",
            "Knife-winged falcons circle the highest tower and force you to move between gusts.",
            "The compass points through open air to Vaelor, who is trapped above the clouds.",
        ]),
        (6, "Ice Trial", "Frost Kingdom", "Ilyra the Ice Guardian", "Ice", "endurance", "Queen Rimeheart", [
            "The Frost Kingdom is quiet, white, and dangerous because cold drains energy slowly.",
            "You plan rests before your stats fall too far, and you share food with a lost patrol.",
            "Frozen rivers show old faces under the ice, so Mira writes their names carefully.",
            "Kael hides his grief badly here; even his breath looks heavy.",
            "Queen Rimeheart's palace appears inside a growing snowflake on the road ahead.",
            "The compass leads you to Ilyra, whose trial is about memory without surrender.",
        ]),
        (7, "Lightning Trial", "Storm Kingdom", "Astrax the Lightning Guardian", "Lightning", "agility", "The Clockwork Tyrant", [
            "Lightning rails carry you into a city of copper towers and strict curfews.",
            "The Storm Kingdom rewards speed, but a wrong step can trigger guards or machines.",
            "Professor Venn explains a thunder pattern that opens the next gate.",
            "You count flashes, time your movement, and keep enough energy for a sudden fight.",
            "Mira finds a wanted poster with Kael's face and a date from centuries ago.",
            "The compass points to the palace machine where Astrax's power is being trapped.",
        ]),
        (8, "Nature Trial", "Green Kingdom", "Eloane the Nature Guardian", "Nature", "vitality", "The Blight Stag", [
            "The Green Kingdom looks peaceful until you see black flowers spreading under the trees.",
            "You check berries, refill water from clear streams, and avoid plants that smell sweet and wrong.",
            "Mushroom monks and fox guides argue, but both agree the forest is sick from an old lie.",
            "You follow healthy roots because they lead around poison and toward the source.",
            "Mira leaves a ribbon for Ashvale, and a small green shoot grows beside it.",
            "The compass points to Eloane at the forest heart, where the Blight Stag waits nearby.",
        ]),
        (9, "Home Trial", "Ashvale", "No Guardian", "Home", "morale", "The Eclipse Butcher", [
            "You return to Ashvale expecting rest, but home is still wounded from the first attack.",
            "The village asks for clear tasks: mend a fence, carry water, eat warm food, and sleep if you can.",
            "Helping neighbors raises morale because the system should match the story here.",
            "Pippin's clay bird sits in the bakery window as a small sign that people are still building.",
            "Kael is too quiet at the memorial stones, and Mira notices before you do.",
            "At midnight, the Eclipse Butcher comes home and turns comfort into a battle.",
        ]),
    ]
    for chapter in chapters:
        guardian_chapter(*chapter)
    interlude_truth()
    more = [
        (11, "Memory Trial", "Tide Kingdom", "Nerys's Echo", "Memory", "vitality", "Archivist of Teeth", [
            "You return to the Tide Kingdom because the drowned archive holds missing history.",
            "The dive is slow, so you prepare water routes, food, and enough energy for the return.",
            "Books float through flooded halls and move away from anyone who lies.",
            "Mira copies records showing why Chaos was locked away instead of destroyed.",
            "Kael reads one page about his lost kingdom and folds it with shaking hands.",
            "The Archivist of Teeth attacks because it survives by destroying witnesses.",
        ]),
        (12, "Courage Trial", "Ember Kingdom", "Solun's Ember", "Courage", "strength", "The Cinder Regent", [
            "Back in the Ember Kingdom, refugees hide below balconies where nobles argue about honor.",
            "You use strength to move crates, block guards, and open a safe path through the heat.",
            "A baker's group smuggles families out in flour carts while you draw attention away.",
            "Solun's Ember sparks whenever someone calls cruelty a necessary sacrifice.",
            "Kael saves a child from flame, which proves he can still choose better even if he has lied.",
            "The Cinder Regent waits near the furnaces, turning fear into fuel.",
        ]),
        (13, "Stone Trial", "Stone Kingdom", "Brunda's Root", "Stone", "endurance", "The Mountain That Hates", [
            "The Stone Kingdom calls again when a mountain wakes and closes the road like a fist.",
            "You conserve energy because this chapter is a long climb before the fight begins.",
            "Oren, an old soldier, helps you carry shields, ropes, and food to trapped workers.",
            "Instead of striking the mountain, you listen and answer with the clay bird from Ashvale.",
            "Deep inside, Brunda's Root shows the first oath: guard people, but do not own them.",
            "The mountain's anger becomes a boss because old greed left wounds in the stone.",
        ]),
        (14, "Patience Trial", "Frost Kingdom", "Ilyra's Tear", "Patience", "vitality", "The Future Eater", [
            "In the Frost Kingdom, a choir sings futures out of existence to spare people pain.",
            "The offer sounds kind, but it would remove choice, growth, and every hard tomorrow.",
            "You rest when needed, eat before hunger gets too low, and keep morale from collapsing.",
            "Mira chooses to remember the bridge where fear failed to stop her.",
            "Ilyra's Tear shows that patience means staying present with pain instead of erasing it.",
            "The Future Eater attacks when you choose a difficult future over an empty one.",
        ]),
        (15, "Storm Trial", "Storm Kingdom", "Astrax's Spark", "Storm", "agility", "The Thunderless King", [
            "At the edge of the maps, Tamsin arrives with a stolen airship and no apology.",
            "The storm route is fast, so you watch agility, energy, and supplies between lightning strikes.",
            "Professor Venn ties himself to the mast and shouts useful facts over the wind.",
            "Astrax's Spark teaches the engine to hold steady when fear says to turn back.",
            "Kael admits the place ahead is close to where he first searched for Chaos.",
            "The Thunderless King's fortress waits in silence, stealing the sound of rebellion.",
        ]),
        (16, "Bloom Trial", "Green Kingdom", "Eloane's Seed", "Bloom", "vitality", "The First Serpent", [
            "The garden at the forest center shows scenes Kael removed from every story he told.",
            "You learn he was hurt before he became dangerous, but pain does not excuse betrayal.",
            "Eloane's Seed grows when you choose truth without trying to make yourself look perfect.",
            "The garden gives food and clean water, but only after you stop pretending the rot is gone.",
            "Mira says forgiveness is not the same as trust, and the story lets that be true.",
            "A root door opens to the First Serpent, which twists kind wishes into cruel choices.",
        ]),
        (17, "Dawn Trial", "Light Kingdom", "The Dawn Oracle", "Dawn", "strength", "The Candleless Monk", [
            "The Light Kingdom road climbs toward dawn, and every step feels like a final question.",
            "You check your stats because the last chapters will not be gentle with weak supplies.",
            "Friends you helped send small gifts, songs, or warnings along the road.",
            "The compass stops pointing to places and points to your heart instead.",
            "Kael finally says the name of his lost home: Eronmere.",
            "At the dawn gate, the Candleless Monk tries to end hope before Seraphine can speak.",
        ]),
    ]
    for chapter in more:
        guardian_chapter(*chapter)
    final_chapters()

def main():
    random.seed()
    intro()
    prologue()
    campaign()


if __name__ == "__main__":
    main()
