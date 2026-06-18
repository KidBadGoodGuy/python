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
}

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

events = ["nothing", "enemy", "food", "water", "traveler", "omen", "memory"]

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


def battle(enemy):
    say(f"\n{enemy['name']} enters the battle.")
    while health() > 0 and enemy_health(enemy) > 0:
        print("\n--------------------")
        print(f"You: {health()} HP")
        print(f"{enemy['name']}: {enemy_health(enemy)} HP")
        print("1. Attack")
        print("2. Guard")
        print("3. Eat")
        print("4. Drink")
        print("5. Run")
        choice = input("> ").strip()
        if choice == "1":
            damage = random.randint(max(1, power() - 2), power() + 4)
            enemy["energy"] -= damage
            print(f"You dealt {damage} damage.")
        elif choice == "2":
            player["morale"] += 3
            print("You steady your breathing and raise your guard.")
        elif choice == "3":
            eat()
        elif choice == "4":
            drink()
        elif choice == "5":
            if random.randint(1, 20) <= player["agility"]:
                print("You escaped!")
                return False
            print("Couldn't escape!")
        else:
            print("You hesitate.")
        clamp()
        if enemy_health(enemy) <= 0:
            print("Enemy defeated!")
            player["morale"] += 6
            clamp()
            return True
        damage = random.randint(max(1, enemy_power(enemy) - 3), enemy_power(enemy) + 3)
        if choice == "2":
            damage = max(1, damage // 2)
        player["energy"] -= damage
        clamp()
        print(f"{enemy['name']} dealt {damage} damage.")
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
        say("A small kindness from home returns to you like a candle in rain.")
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
            "You find a quarry chapel where miners carved prayers into every stone they removed from the mountain.",
            "A retired Guardian soldier named Oren shows you a shield split by a creature he swears had no face.",
            "Behind a false wall, Mira uncovers a tax ledger that is really a map of tunnels older than the crown.",
            "Pippin appears with dusty knees and asks whether heroes get scared underground. Kael says, 'Only the honest ones.'",
        ],
        "Tide Kingdom": [
            "A floating market rocks gently in the rain. Merchants sell salt charms, stormglass, and letters rescued from shipwrecks.",
            "You meet Luma the wandering musician, who plays a fiddle strung with silver fishbone and refuses payment except rumors.",
            "In a drowned schoolhouse, chalk words still glow: water remembers the shape of every promise.",
            "Mira finds a sealed bottle addressed to someone who died before the Black Eclipse. She carries it anyway.",
        ],
        "Ember Kingdom": [
            "Caldera's children race ember-kites above alleys warm enough to bake bread on the walls.",
            "A glassmaker explains that fire is not anger. 'Anger destroys. Fire transforms. Learn the difference or burn with fools.'",
            "You explore an ash garden where statues of criminals weep molten gold when lied to.",
            "Kael refuses a cup of cinnamon tea because the steam forms a crown before vanishing.",
        ],
        "Sky Kingdom": [
            "Cloud-herders guide woolly thunderheads into pens while bells keep the lightning calm.",
            "Tamsin, the rival adventurer, drops from a rope ladder, steals one apple, then gives you three better ones.",
            "A ruined tower hangs upside down under a bridge. Its library can only be read by people brave enough to look down.",
            "The compass needle spins whenever Kael looks at the open sky, as if the horizon remembers chasing him.",
        ],
        "Frost Kingdom": [
            "You cross a battlefield preserved in blue ice. The soldiers' shadows are still fighting after their bodies have forgiven each other.",
            "An old woman named Sava sells mittens, soup, and blunt prophecies. She says Mira will outlive a song and hate it.",
            "In a mirror cave, you see yourself wearing a crown of black antlers. The image smiles first.",
            "Kael breaks the mirror with his bare hand and bleeds darkness that freezes before it hits the ground.",
        ],
        "Storm Kingdom": [
            "Copper rain ticks on rooftops like thousands of tiny clocks disagreeing about tomorrow.",
            "Professor Venn, a lost historian with lightning-burned eyebrows, insists the Guardians were chosen by failure, not virtue.",
            "You solve a street puzzle by stepping only when thunder answers the brass bells.",
            "A wanted poster curls around Kael's boot. The ink is fresh. The date is three centuries old.",
        ],
        "Green Kingdom": [
            "Mushroom monks debate whether patience is a kind of courage or just fear wearing moss.",
            "A fox diplomat offers safe passage if you can tell one true story without making yourself the hero.",
            "In a hidden grove, every tree has a door, and behind each door is a room someone lost in childhood.",
            "Mira leaves a ribbon for Ashvale on a branch. By morning the tree grows pears.",
        ],
        "Ashvale": [
            "Your old lane is smaller than memory and larger than grief.",
            "The village elder gives you your mother's mended satchel and pretends not to cry when you recognize the stitchwork.",
            "Children paint Guardian symbols on broken fences because bright colors make monsters hesitate, according to Pippin.",
            "Kael stands before the memorial stones and whispers a name no one in Ashvale should know.",
        ],
        "Chaos": [
            "The road folds back on itself until your footprints meet you coming the other way.",
            "A campfire burns without wood. In its smoke, ancient heroes argue about whether saving the world ever saved them.",
            "You find a monument to the Ninth Element. Someone has scratched out the word monster and written loneliness.",
            "Mira asks Kael who taught him the prison songs. He says, 'My jailer. My friend. My victim.'",
        ],
        "Light Kingdom": [
            "Pilgrims polish shattered halos and hang them from doorways so dawn knows where to enter.",
            "A blind librarian reads sunlight by touch and says every ray has a different accent.",
            "You discover a nursery where children once practiced forgiving enemies by naming stars after them.",
            "Kael kneels at the threshold and cannot cross until Mira takes his hand. He looks more ashamed than grateful.",
        ],
    }
    for text in discoveries.get(region, ["You find an old campsite and learn nothing except that someone before you was also hungry, tired, and afraid."]):
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
            "Brunda rises from the cavern floor like a mountain remembering it can stand.",
            "Her voice is gravel over roots. 'I held cities on my back while kings argued over whose banners deserved wind.'",
            "She admits she is tired of being mistaken for patience. Stone can wait, she says, but it can also fall.",
            "When you mention Pippin's clay bird, her enormous hands close gently around the little token.",
            "'Then the small ones still build,' Brunda says. 'Good. I can stand one more time.'",
        ],
        "Nerys the Water Guardian": [
            "Nerys appears beneath the flooded palace, hair drifting around her like black kelp in moonlight.",
            "'Water keeps no shape,' she says, 'yet mortals demand that grief remain tidy.'",
            "She remembers carrying plague ships away from harbors and being cursed by the families who never knew she saved them.",
            "Mira asks whether mercy can drown. Nerys answers, 'Only when it refuses to move.'",
            "The Guardian touches your canteen, and for a moment you taste rain from every childhood in the world.",
        ],
        "Solun the Fire Guardian": [
            "Solun steps from a furnace that has burned since the first winter, his beard a river of sparks.",
            "He laughs like a roof collapsing and calls you little ember, but his eyes are full of old funerals.",
            "'They begged me for weapons, then blamed me when weapons behaved like weapons.'",
            "Kael says fire is easiest to corrupt. Solun replies, 'No. Fire is honest. People lie about what they want burned.'",
            "He kneels so you can see the crack in his chest where the Eclipse has been drinking heat.",
        ],
        "Vaelor the Wind Guardian": [
            "Vaelor arrives as a hawk, a storm, a laughing old woman, and finally a tall figure with cloud-white braids.",
            "'Names are cages with pretty doors,' Vaelor says, delighted when Mira writes that down angrily.",
            "The Guardian confesses that freedom without responsibility becomes merely another kind of storm damage.",
            "Tamsin challenges Vaelor to a race around the tower and loses so spectacularly that even Kael smiles.",
            "Before speaking of Chaos, Vaelor makes everyone stand silently and listen to the wind carry prayers from below.",
        ],
        "Ilyra the Ice Guardian": [
            "Ilyra sits on a throne of frozen tears, young and ancient, with snowflakes caught in her lashes like unsent letters.",
            "She says ice is memory given mercy: it preserves until the living are strong enough to thaw.",
            "Her fear is not death but becoming a museum for pain nobody intends to heal.",
            "You tell her about Ashvale's bakery being rebuilt first. Her smile is small enough to miss and bright enough to matter.",
            "'Then warmth still negotiates with ruin,' she whispers. 'I will listen.'",
        ],
        "Astrax the Lightning Guardian": [
            "Astrax descends through the copper storm as a figure made of sudden decisions.",
            "Every word arrives before his mouth moves. 'Think faster,' he says. 'The future is impatient.'",
            "Professor Venn bows and calls him the patron of inventors, fools, and anyone who has shouted 'hold this' before disaster.",
            "Astrax fears stillness. He once paused for one breath, and an empire used that breath to build chains.",
            "He asks whether you want power to strike enemies or light windows for strangers.",
        ],
        "Eloane the Nature Guardian": [
            "Eloane is not one shape. She is antlers, petals, soil, grandmother hands, wolf eyes, and a voice like rain in leaves.",
            "'Nature is not kind,' she says, 'but it is generous with second chances.'",
            "The forest around her is sick because it has been forced to grow around a lie buried in its roots.",
            "A fox diplomat bows to her. Mushroom monks stop arguing. Even Kael lowers his hood.",
            "Eloane asks what you will plant when vengeance has used up all the fields.",
        ],
        "Seraphine": [
            "Seraphine waits in a hall where dawn has been folded into banners and stored against despair.",
            "She looks almost human until she opens her eyes and every candle remembers why it was made.",
            "'Light reveals,' she says. 'It does not excuse. It does not flatter. It simply refuses to let wounds hide forever.'",
            "She knew Kael before the hood, before the bargain, before grief taught him to call prisons doors.",
            "When she speaks his true name, he drops to one knee as if struck by a bell.",
        ],
        "Nerys's Echo": [
            "The echo of Nerys pours from a cracked shell and speaks with the voices of drowned librarians.",
            "It remembers the first war against Chaos as a debate that became a battlefield only after everyone stopped listening.",
            "The echo cannot fight beside you, but it can tell you where truth was hidden from kings.",
        ],
        "Solun's Ember": [
            "Solun's ember hovers above a brazier, sulking like a tiny sun denied proper drama.",
            "It tells you courage is not fearlessness. Courage is fear forced to carry water and keep walking.",
        ],
        "Brunda's Root": [
            "Brunda's root coils through the hollow mountain and taps ancient rhythms against your boots.",
            "It says the first Guardians were ordinary people who chose to hold the line after legends ran away.",
        ],
        "Ilyra's Tear": [
            "Ilyra's tear freezes in your palm without hurting you.",
            "Inside it, you see a future where you win and still have to live afterward.",
        ],
        "Astrax's Spark": [
            "Astrax's spark jumps between your fingers and spells rude advice in blue fire.",
            "It insists destiny is just a deadline with better public relations.",
        ],
        "Eloane's Seed": [
            "Eloane's seed hums under the soil of your pack.",
            "It shows you roots sharing food with trees too proud to ask for help.",
        ],
        "No Guardian": [
            "There is no Guardian waiting in Ashvale, only people with soot on their faces and bread in their hands.",
            "The village elder says, 'Do not insult us by calling survival small.'",
            "For once, the legend is not ancient. It is a dozen neighbors raising a roof before rain.",
        ],
    }
    for text in talks.get(guardian, [f"{guardian} studies you with eyes full of storms the history books forgot."]):
        say(text)
        pass_time(1)
    choice = ask("What do you ask before the trial begins?", [("1", "Ask about the old wars"), ("2", "Ask what the Guardian fears"), ("3", "Ask why Kael knows so much")])
    if choice == "1":
        player["truths"] += 1
        say("The answer comes slowly: Chaos was born when every element tried to become the only element, and the silence between them learned hunger.")
    elif choice == "2":
        player["mercy"] += 1
        say("The Guardian does not hide the answer. Immortals fear being obeyed long after they are wrong.")
    else:
        player["truths"] += 1
        player["chaos_taint"] += 1
        say("Kael's hand tightens around his sleeve. The Guardian looks away first, which frightens you more than any confession.")
    clamp()


def boss_introduction(boss, region):
    speeches = {
        "Lord Malgrit of the Hollow Mine": ["Lord Malgrit arrives in armor made from stolen headstones.", "He claims the mountain owes him obedience because he has buried enough workers inside it."],
        "The Drowned Admiral": ["A ship's bell tolls underwater, and the Drowned Admiral marches from the flood with barnacles for medals.", "'I kept my fleet alive by sinking everyone else first,' he says."],
        "The Brass Prophet": ["The Brass Prophet's mask opens like a furnace door.", "He preaches that only fire can purify a world too sentimental to save itself."],
        "The Silent Falconer": ["A hooded figure releases birds made of knives and never speaks.", "Vaelor says silence can be a mercy, but this silence is a leash."],
        "Queen Rimeheart": ["Queen Rimeheart enters with a procession of frozen mirrors, each one showing a subject who disappointed her.", "She wants a kingdom where nobody changes because change stole everyone she loved."],
        "The Clockwork Tyrant": ["Gears rise through the plaza, assembling a king from lawbooks, swords, and unpaid debts.", "The Clockwork Tyrant declares mercy an inefficient machine part."],
        "The Blight Stag": ["The Blight Stag steps from the trees, antlers dripping black flowers.", "It was once a sacred beast until Eclipse spores taught it that rot could also bloom."],
        "The Eclipse Butcher": ["The Eclipse Butcher wears an apron stitched from village flags.", "It remembers every home it ruined and speaks in the voices of people who begged it to stop."],
        "Archivist of Teeth": ["The Archivist of Teeth smiles with stolen mouths arranged along its sleeves.", "It collects truths by eating the witnesses."],
        "The Cinder Regent": ["The Cinder Regent applauds from a balcony while refugees are dragged below to feed the furnaces.", "He says hope burns longer when taxed properly."],
        "The Mountain That Hates": ["The whole mountain inhales, and every tunnel becomes a throat.", "It hates because miners carved greed into its bones and called the wounds progress."],
        "The Future Eater": ["The Future Eater unfolds from a hymn, all empty eyes and lullaby teeth.", "It offers painless oblivion with the tenderness of a nurse smothering a patient."],
        "The Thunderless King": ["The Thunderless King rides a dead lightning bolt into view.", "He stole thunder so no rebellion could ever hear itself begin."],
        "The First Serpent": ["The First Serpent coils around the garden's oldest tree, wearing Kael's face and then your own.", "It says every betrayal begins as a wish to spare someone pain."],
        "The Pale Herald": ["The Pale Herald carries a trumpet made from dawnbone.", "It announces that light has failed and all lamps should surrender their flames."],
    }
    for text in speeches.get(boss, [f"{boss} emerges from {region}, carrying the Black Eclipse like a wound that learned to walk."]):
        say(text)
        pass_time(1)
    if player["morale"] < 40:
        say("Your hands tremble before the battle. Mira notices and stands closer without saying anything.")
    else:
        say("You step forward before fear can finish making its argument.")
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
    say("A fantasy journey of roads, choices, hunger, courage, and old powers waking beneath a peaceful world.")
    say("You will choose actions by typing the listed number, watch your food and water, rest when the road becomes cruel, and listen when companions speak.")
    say("Battles use Attack, Guard, Eat, Drink, and Run. Travel may bring strangers, supplies, omens, memories, or danger.")
    say("Most importantly, your mercy, resolve, truths, and wounds will follow you all the way to the ending.")
    choice = ask("Before the story begins, how do you spend an ordinary Ashvale morning?", [("1", "Help at the bakery"), ("2", "Carry water from the well"), ("3", "Practice with a wooden sword")])
    if choice == "1":
        player["food"] += 2
        player["morale"] += 4
        say("You learn that warm bread can end arguments faster than wise speeches.")
    elif choice == "2":
        player["water"] += 2
        player["endurance"] += 1
        say("The well rope burns your palms, but every full bucket feels like a small promise kept.")
    else:
        player["strength"] += 1
        player["resolve"] += 1
        say("Old Fen teaches you that a hero who forgets footwork becomes a dramatic bruise.")
    clamp()
    show_time()
    stats()
    say("Ashvale is not a legend yet. It is home: pear trees, mended shutters, muddy boots by doorways, and people who know your name before you knock.")
    say("Mara the baker, Pippin with his clay animals, old Fen, the village elder, and half the children in the lane pull you into chores, jokes, and small duties.")
    say("For a while, the world asks nothing grander of you than kindness, patience, and whether you remembered to eat breakfast.")
    pass_time(2)


def prologue():
    say("\nPrologue: The Black Sun Rumors")
    say("Ashvale wakes to ordinary miracles: pear blossoms on the road, kettle steam in windows, and old Fen arguing with his goat about politics.")
    say("You begin at the bakery because your mother always said history could wait until after breakfast.")
    say("Mara the baker slips you an extra heel of bread. 'For the road you keep pretending you won't take,' she says.")
    player["food"] += 1
    pass_time(1)
    say("At the well, Pippin shows you a clay bird he made for his father in the north quarry.")
    say("'If monsters come,' he declares, 'I'll throw it at them. Artistic and tactical.'")
    pass_time(1)
    say("Travelers arriving for market bring old rumors instead of fresh jokes: Elemental Guardians seen weeping in shrines, rivers running uphill for one hour, lightning striking the same empty grave nine times.")
    say("The elder dismisses the stories in public, then asks you in private whether your mother's red scarf has ever felt warm when no fire was near.")
    say("At dusk, you overhear Mara telling Fen that the Guardians were not only protectors. They were witnesses, judges, and perhaps jailers of something older than kingdoms.")
    say("Nobody gives a speech about history. You collect it in fragments: a miner's prayer to Earth, a sailor's charm to Water, a cracked festival mask for Fire, a lullaby asking Wind to carry children safely home.")
    pass_time(2)
    say("Then the peaceful fragments stop fitting together.")
    say("Milk sours black in clean pails. Crows land facing west. The ancient compass in your keepsake box ticks though it has no gears.")
    say("The village bell rings noon once, twice, and then keeps ringing though no hand pulls the rope.")
    say("The sun goes black. Pear blossoms lift from the ground and fly upward as if the sky has started inhaling.")
    player["morale"] -= 10
    clamp()
    battle(make_enemy("Eclipse Ravager", 8, 8, 8, 7))
    say("When the creature falls, the street is not victorious. It is full of people calling names that do not answer.")
    say("A hooded traveler steps through smoke and falling ash. He knows exactly where the wounded are trapped before anyone tells him.")
    say("He pulls you from burning wheat. His voice is kind, but the shadows obey him too quickly.")
    say("'The Guardians are vanishing,' he says. 'If the compass chose you, the world has already run out of safer plans.'")
    say("He gives you an ancient compass. Its needle points not north, but toward whatever the world is most afraid to lose.")
    player["companions"].append("Kael, the Hooded Traveler")
    travel("Ashvale", 6, danger=2)
    say("You find Mira at the ruined bridge, pinning a monster's sleeve to the planks with one knife while writing with the other hand.")
    say("'Courier,' she says, not looking up. 'Historian if we survive. Liar if we don't.'")
    say("Together you rescue three children from the mill cellar, then sit in the dust while they argue over who screamed bravest.")
    player["companions"].append("Mira")
    player["inventory"].append("Mira's Map of Living Roads")
    say("Mira studies Kael's compass by firelight and frowns. 'This script is older than the Guardian churches. Why did he have it wrapped like a funeral relic?'")
    companion_campfire("Ashvale")


def interlude_truth():
    say("\nChapter 10: The Ninth Door")
    say("Orison appears at dusk where no map agrees it should be: an abandoned city built around a door too large for any wall.")
    say("Its streets are paved with white tiles, each tile engraved with a name. Some are kings. Some are children. Some are scratched away.")
    optional_discovery("Chaos")
    travel("Chaos", 7, danger=2)
    say("In the central archive, bells ring under the streets though every tower has fallen.")
    say("Professor Venn returns, breathless and delighted, dragging three satchels of forbidden rubbings behind him.")
    say("'Good news,' he pants. 'The world is older, sadder, and more illegally engineered than we thought.'")
    say("Mira deciphers a wall of guardian names. There are not eight circles around the world. There are eight locks around one prison.")
    say("The first Guardians were chosen after the Elemental War, when fire tried to rule water, water tried to drown earth, and light tried to erase shadow entirely.")
    say("Chaos was born from everything the elements rejected: contradiction, grief, hunger, change, endings, beginnings no one asked for.")
    say("Kael smiles sadly and admits the compass awakens each lock when a Guardian is freed.")
    say("'I thought I was saving them,' he says, and Mira's voice goes flat. 'No. You thought we were useful.'")
    choice = ask("Do you confront Kael or pretend trust until you learn more?", [("1", "Confront him"), ("2", "Pretend trust"), ("3", "Ask Mira to steal the compass at night")])
    if choice == "1":
        player["truths"] += 2
        say("Kael removes his hood. For the first time, he looks less mysterious than exhausted.")
        say("His shadow remains hooded after he does not.")
        battle(make_enemy("Kael's Shadow", power() + 2, power() + 2, power() + 2, power() + 5))
    elif choice == "2":
        player["chaos_taint"] += 1
        say("You swallow anger. Kael calls that wisdom. Mira waits until he leaves and calls it dangerous.")
        say("She does not abandon you. That makes the silence worse.")
    else:
        player["mercy"] += 1
        player["inventory"].append("Stolen Compass Splinter")
        say("Mira returns pale. 'It whispered your name in my mother's voice,' she says.")
        say("The splinter points toward the Light Kingdom, then toward Kael, then toward your heart.")
    say("Before sleep, Kael tells you his kingdom died in a plague the Guardians could have stopped if they had broken the prison.")
    say("You do not know whether it is confession, manipulation, or both. The worst truths often are.")
    companion_campfire("Chaos")
    rest(6)


def final_chapters():
    say("\nChapter 18: The Last Guardian of Light")
    say("The road to the Light Kingdom begins at midnight and climbs toward dawn without ever passing morning.")
    travel("Light Kingdom", 8, danger=2)
    optional_discovery("Light Kingdom")
    say("The Light Kingdom is not bright. It is a library of dawns, each sunrise stored in crystal for a day when hope runs out.")
    say("Seraphine, Guardian of Light, kneels among broken suns. She knew Kael as a prince before Chaos wore his grief like a mask.")
    guardian_conversation("Light Kingdom", "Seraphine")
    say("Kael cannot meet her eyes. 'You left us to die,' he says.")
    say("Seraphine answers without defending herself. 'Yes. I chose the prison over your kingdom. I have carried every name since.'")
    say("For the first time, Kael's anger has nowhere theatrical to stand. It becomes a man crying in a ruined hall.")
    boss_introduction("The Pale Herald", "Light Kingdom")
    battle(make_enemy("The Pale Herald", power() + 5, power() + 4, power() + 5, power() + 4))
    say("Seraphine sacrifices her immortal flame to seal the compass inside your heart instead of Kael's hand.")
    say("It hurts like swallowing a sunrise. It heals like hearing your name spoken by someone who waited for you.")
    player["guardian_marks"].append("Light")
    player["vitality"] += 3
    player["mercy"] += 1
    say("Chaos is released anyway, but now it must face someone who has walked the whole wounded world.")
    companion_campfire("Light Kingdom")
    travel("Chaos", 6, danger=3)
    say("\nChapter 19: The Black Eclipse Opens")
    say("The sky fills with doors. Behind each one is a version of the world where someone made a different choice and called it peace.")
    say("Kael stands beneath them, no hood left, no mystery left, only grief with a weapon.")
    say("'I only wanted my dead kingdom back,' he says. Chaos answers with every voice you have lost.")
    choice = ask("What do you say to Kael before the final battle?", [("1", "Your grief is real, but it cannot rule us"), ("2", "You used us, and I will end this"), ("3", "Help me save what is left of you")])
    if choice == "1":
        player["mercy"] += 1
        say("Kael flinches as if mercy is harder to endure than hatred.")
    elif choice == "2":
        player["resolve"] += 2
        say("He nods once. 'Then strike cleanly. I am tired of doors.'")
    else:
        player["mercy"] += 2
        player["chaos_taint"] += 1
        say("For one breath, Kael reaches back. Chaos drags him forward by the wound in his shadow.")
    battle(make_enemy("Kael, Vessel of Chaos", power() + 5, power() + 4, power() + 5, power() + 4))
    say("Kael falls. Mira catches him because she is furious, not because she has forgiven him.")
    say("The Ninth Element crawls free: not fire, not storm, but the hunger beneath all endings.")
    say("Chaos speaks in your voice first. Then your mother's. Then Pippin's. Then no voice at all, which is worst.")
    battle(make_enemy("Chaos Unbound", power() + 7, power() + 6, power() + 8, power() + 5))
    ending()


def ending():
    say("\nEnding: The Choice After Chaos")
    if player["mercy"] >= 5 and player["chaos_taint"] <= 3:
        say("You refuse to destroy Chaos. You name it grief, bind it with every Guardian mark, and teach the world to mourn without becoming monstrous.")
        say("Kael spends the rest of his life rebuilding roads to villages he hurt, never asking anyone to call it redemption.")
        say("Mira publishes the true history with every ugly part left in. The first copy is chained in Ashvale's bakery so anyone can argue with it over breakfast.")
        say("Ending: Dawn Covenant. The Guardians return as mortal guides, and every kingdom lights one lamp for Ashvale.")
    elif player["resolve"] >= player["mercy"]:
        say("You drive the Guardian marks into the eclipse and shatter Chaos at the cost of magic itself.")
        say("The Guardians fade smiling, terrified, relieved. Seraphine is the last light to go, and she thanks you for letting the world grow up.")
        say("Mira keeps traveling because history is heavier without miracles and someone must make sure kings do not edit it again.")
        say("Ending: Age of Iron. The world survives without miracles, and your name becomes the first law of every rebuilt kingdom.")
    else:
        say("The compass splinter opens in your chest. You imprison Chaos within yourself and walk beyond the map before anyone can stop you.")
        say("Years later, travelers find impossible campsites where clean water waits beside warm bread and a note saying keep going.")
        say("Mira never stops searching. Kael, if he lives, walks behind her at a respectful distance, carrying the books.")
        say("Ending: The Wandering Seal. On moonless nights, Mira still hears your footsteps guarding the roads between worlds.")
    say("The final battle is over, but victory is not the same as peace. The world waits to learn what your choices have made of it.")
    epilogue()


def epilogue():
    say("\nEpilogue: Roads After Dawn")
    say("Weeks pass before the sky trusts itself to be blue for a full day.")
    say("You return first to Ashvale, where the bakery opens before the council hall because everyone agrees civilization should smell like bread.")
    say("The Stone Kingdom carves public oaths into bridges. The Tide Kingdom builds schools above the floodline and below it. Caldera turns old war furnaces into communal ovens.")
    say("Sky bridges are repaired with safer lies removed. Frost memorials are thawed carefully, one name at a time. Storm inventors put lightning in streetlamps instead of prisons. Green roots lift black flowers from buried secrets.")
    if "Mira" in player["companions"]:
        say("Mira finishes her book and refuses every royal editor. Its last chapter is blank so survivors can write in the margins.")
    if "Kael, the Hooded Traveler" in player["companions"]:
        say("Kael's fate remains difficult and human: some doors open for him, some close, and none of them erase what he did.")
    say("You revisit shrines, markets, campsites, and battlefields. People remember your choices differently, but they remember that you chose.")
    say("On the last night, the ancient compass gives one soft click and points past every known kingdom toward a star that should not be moving.")
    say("The journey is complete. The road, however, is still alive.")
    stats()


def campaign():
    chapters = [
        (
            2,
            "The Root-Crowned Gate",
            "Stone Kingdom",
            "Brunda the Earth Guardian",
            "Earth",
            "endurance",
            "Lord Malgrit of the Hollow Mine",
            [
                "The Stone Kingdom begins where the road stops pretending to be flat.",
                "Terraced villages cling to cliffs while miners sing to keep tunnels from collapsing.",
                "At Graniteford, an elder named Dama measures strangers by how they treat mules, children, and borrowed tools.",
                "A child named Pippin asks you to carry a clay bird to his father below the mountain.",
                "Kael knows the miners' mourning song. When Dama asks who taught him, he says the dead are generous teachers.",
                "The Stone Council hides a prophecy inside tax records because tyrants never read them.",
                "Mira spends an afternoon pretending to be an accountant and emerges with three maps, two warrants, and a headache.",
                "The quarry gates open after you help shore up a cracked support beam with your own aching shoulders.",
            ],
        ),
        (
            3,
            "The Kingdom Under Rain",
            "Tide Kingdom",
            "Nerys the Water Guardian",
            "Water",
            "vitality",
            "The Drowned Admiral",
            [
                "Rain begins three miles before the Tide Kingdom and never quite ends.",
                "Canal lanterns drift like patient stars across streets of blue stone.",
                "You help ferrymen rescue families from houses that have begun dreaming they are ships.",
                "Captain Sella, who has one wooden leg and no patience for prophecy, teaches you which ropes can be trusted wet.",
                "Mira teaches you to read tide-knots while Kael refuses to board any boat with mirrors.",
                "A shrine to Nerys is filled with bowls of tears, each labeled with the name of someone forgiven too late.",
                "Luma the musician returns and plays a song that makes the rain fall upward for exactly seven notes.",
                "At low tide, black stairs appear beneath the harbor and every bell in the city rings from underwater.",
            ],
        ),
        (
            4,
            "Embers That Remember",
            "Ember Kingdom",
            "Solun the Fire Guardian",
            "Fire",
            "strength",
            "The Brass Prophet",
            [
                "The desert city of Caldera is built inside the rib cage of an ancient dragon.",
                "Its people greet dawn by lighting lanterns from yesterday's ashes and naming one mistake they will not repeat.",
                "A baker feeds refugees with ovens powered by volcanic tears.",
                "You help carry water through streets so hot the shadows look thirsty.",
                "In the Trial of Coals, you must walk slowly and speak one regret aloud.",
                "Kael names a city you have never heard of. The coals turn blue beneath his feet.",
                "A brass-robed cult preaches that the Eclipse is a forge and the weak are only ore.",
                "Mira buys a heat-cracked lens from a child inventor and discovers it reveals invisible chains around the palace.",
            ],
        ),
        (
            5,
            "Roads in the Sky",
            "Sky Kingdom",
            "Vaelor the Wind Guardian",
            "Wind",
            "agility",
            "The Silent Falconer",
            [
                "The Sky Kingdom hangs above the world on chains of prayer, old engineering, and stubbornness.",
                "Bridges of woven cloud connect towers where children keep pet thunderheads.",
                "A sky-smuggler named Tamsin offers shortcuts, lies, and excellent apples.",
                "You cross a bridge that vanishes whenever anyone lies, which makes negotiations with Tamsin athletic.",
                "The wind carries your mother's lullaby, though she never climbed higher than Ashvale's mill.",
                "Kael grows quieter with every mile of open air, as though he once fell and never quite stopped falling.",
                "At the feather market, people trade secrets by tying them to birds and hoping they return kinder.",
                "A flock of knife-winged falcons circles the highest tower without casting shadows.",
            ],
        ),
        (
            6,
            "The Mirror Snow",
            "Frost Kingdom",
            "Ilyra the Ice Guardian",
            "Ice",
            "endurance",
            "Queen Rimeheart",
            [
                "The Frost Kingdom does not welcome visitors; it tests whether they can listen to silence without filling it.",
                "Snowfields reflect possible futures, including one where you never left home.",
                "You share heat with an old soldier who once hunted Guardians and now plants blue flags for the lost.",
                "Sava the mitten-seller charges one story per bowl of soup and rejects any story with a lazy ending.",
                "Kael weeps frost when no one is meant to see.",
                "A frozen river shows faces under the ice, not trapped, but waiting for descendants to remember their names.",
                "Mira records names until her ink freezes. Then she scratches them into the page with a needle.",
                "Queen Rimeheart's palace appears inside a snowflake that grows larger the closer you walk toward it.",
            ],
        ),
        (
            7,
            "The City of Copper Rain",
            "Storm Kingdom",
            "Astrax the Lightning Guardian",
            "Lightning",
            "agility",
            "The Clockwork Tyrant",
            [
                "Lightning rails scream between copper towers and libraries that argue with their readers.",
                "Children here learn arithmetic by counting seconds between flash and thunder.",
                "You solve a conductor's puzzle by matching thunder intervals to old nursery rhymes.",
                "Professor Venn joins you for three streets, gets lost twice, and accidentally proves a forbidden theorem.",
                "Mira finds a wanted poster showing Kael's face from three hundred years ago.",
                "Kael claims it is a common face. Nobody believes him, including a nearby statue that rolls its eyes.",
                "The city council has been replaced by brass automata that vote unanimously for curfews, taxes, and silence.",
                "A dead lightning bolt is chained beneath the palace, and it whispers whenever someone says freedom.",
            ],
        ),
        (
            8,
            "The Forest That Speaks Last",
            "Green Kingdom",
            "Eloane the Nature Guardian",
            "Nature",
            "vitality",
            "The Blight Stag",
            [
                "The Green Kingdom begins with a sign that reads: wipe your boots, apologize to the moss, and do not flatter the foxes.",
                "Trees here remember names better than people do, and every leaf turns to listen.",
                "You negotiate between mushroom monks, fox diplomats, and a village swallowed by protective vines.",
                "A grove shows you Ashvale regrowing around a black throne.",
                "Kael touches one tree and the bark recoils as though burned by winter.",
                "Mira befriends a tiny sprout growing from an old helmet and names it General Salad.",
                "The forest's sickness spreads in beautiful patterns, black flowers blooming exactly where old lies were buried.",
                "At dusk, antlers appear between the trees, carrying candles that burn with green flame.",
            ],
        ),
        (
            9,
            "The Feast of Small Victories",
            "Ashvale",
            "No Guardian",
            "Home",
            "morale",
            "The Eclipse Butcher",
            [
                "You return home to bury the dead and find survivors rebuilding the bakery first.",
                "Pippin's clay bird sits in a window beside Mira's map and a bowl of pears.",
                "The village elder gives you three tasks: mend a fence, eat something warm, and stop apologizing for surviving.",
                "For one night, nobody asks you to save the world; they only ask you to dance.",
                "Kael dances like someone remembering court lessons from a kingdom no history book admits existed.",
                "Mira laughs so hard she has to sit down, then cries because laughing did not feel impossible anymore.",
                "At midnight, the memorial stones turn toward the road as if watching something approach.",
                "The Eclipse Butcher comes home wearing the voices of the dead.",
            ],
        ),
    ]
    for chapter in chapters:
        guardian_chapter(*chapter)
    interlude_truth()
    more = [
        (
            11,
            "The Sunken Archive",
            "Tide Kingdom",
            "Nerys's Echo",
            "Memory",
            "vitality",
            "Archivist of Teeth",
            [
                "You dive through a drowned palace where books swim away from liars.",
                "Captain Sella ties a rope around your waist and says if history bites, bite back.",
                "The archive reveals Chaos once offered immortality to every kingdom and was refused by children first.",
                "Mira records everything, even the parts that make her hands shake.",
                "Kael reads a page about his plague-kingdom and folds it so carefully you hear the paper hurt.",
                "A school of silver fish arranges itself into the face of Nerys and points toward a sealed vault.",
            ],
        ),
        (
            12,
            "The Parliament of Ash",
            "Ember Kingdom",
            "Solun's Ember",
            "Courage",
            "strength",
            "The Cinder Regent",
            [
                "Fire nobles duel with poetry while refugees sleep beneath gold balconies.",
                "You expose a regent selling eclipse glass to monsters.",
                "A baker's coalition smuggles families out inside flour carts and asks you to distract the palace guard.",
                "Kael saves a child from flame and looks almost human again.",
                "Solun's ember spits sparks whenever anyone says necessary sacrifice too comfortably.",
                "The parliament chamber is a furnace designed to make honest witnesses sweat and liars glow.",
            ],
        ),
        (
            13,
            "Hollow Mountain",
            "Stone Kingdom",
            "Brunda's Root",
            "Stone",
            "endurance",
            "The Mountain That Hates",
            [
                "A mountain opens like a mouth and demands the name of whoever broke the first promise.",
                "Oren the retired soldier returns with a shield, a limp, and an argument against dying dramatically.",
                "You answer by placing Pippin's clay bird on its tongue.",
                "The mountain lets you pass, embarrassed by tenderness.",
                "Deep below, the first Guardian oath is carved into bedrock: hold, but do not clutch; guard, but do not own.",
                "Kael reads the oath and turns away before anyone can see whether he understands it.",
            ],
        ),
        (
            14,
            "The Choir of No Tomorrow",
            "Frost Kingdom",
            "Ilyra's Tear",
            "Patience",
            "vitality",
            "The Future Eater",
            [
                "A choir sings futures out of existence to spare people pain.",
                "Sava returns with soup so spicy it makes three prophecies reconsider themselves.",
                "You must choose one painful memory to keep forever.",
                "The kept memory becomes armor.",
                "Mira chooses the bridge where you met because she says fear should remember it failed.",
                "Kael refuses to choose. The choir chooses for him, and every note sounds like a plague bell.",
            ],
        ),
        (
            15,
            "Storm at the Edge of Maps",
            "Storm Kingdom",
            "Astrax's Spark",
            "Storm",
            "agility",
            "The Thunderless King",
            [
                "The last map edge flaps like torn cloth above an endless sea of clouds.",
                "Tamsin returns with a stolen airship and absolutely no apology.",
                "Together you steer through living lightning toward the place Kael fears most.",
                "Professor Venn straps himself to the mast and shouts footnotes into the storm.",
                "Astrax's spark teaches the engine to be brave, which mostly sounds like illegal acceleration.",
                "The Thunderless King's fortress waits in a quiet so complete your heartbeat feels rebellious.",
            ],
        ),
        (
            16,
            "Garden of the First Lie",
            "Green Kingdom",
            "Eloane's Seed",
            "Bloom",
            "vitality",
            "The First Serpent",
            [
                "In a garden older than language, flowers bloom into scenes Kael edited out of history.",
                "He was not the first villain of Chaos. He was its first survivor.",
                "You can hate him less without trusting him more.",
                "The fox diplomat returns and admits this is the most inconvenient moral nuance it has ever witnessed.",
                "Eloane's seed cracks open and grows a door made from intertwined roots.",
                "Behind the door, the First Serpent waits beside the first apology ever refused.",
            ],
        ),
        (
            17,
            "Before the Last Dawn",
            "Light Kingdom",
            "The Dawn Oracle",
            "Dawn",
            "strength",
            "The Candleless Monk",
            [
                "Pilgrims climb a road paved with broken halos and leave letters for tomorrow.",
                "Mira asks what you will do if saving the world requires forgiving the person who ruined yours.",
                "The compass stops pointing outward. It points at your heart.",
                "Luma plays one last road song, and every recurring friend you helped sends a verse along the wind.",
                "Pippin's clay bird, somehow still whole, grows warm in your pack.",
                "At the gate of dawn, Kael finally says the name of his lost kingdom: Eronmere.",
            ],
        ),
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
