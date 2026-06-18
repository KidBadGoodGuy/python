
import random
import time
import sys

# -----------------------
# SETTINGS
# -----------------------

FAST_TEXT = False

# -----------------------
# PLAYER
# -----------------------

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

    "equipped_food": None,
    "equipped_water": None,
}

# -----------------------
# TIME
# -----------------------

day = 1
hour = 8

# -----------------------
# ITEMS
# -----------------------

foods = {
    "Bread": {"hunger": 20, "morale": 5},
    "Meat": {"hunger": 35, "energy": 10},
}

waters = {
    "Clean Water": {"thirst": 35},
    "Spring Water": {"thirst": 50, "morale": 5},
}

# -----------------------
# TEXT
# -----------------------

def say(text, speed=0.03):
    if FAST_TEXT:
        print(text)
        return
    for letter in text:
        sys.stdout.write(letter)
        sys.stdout.flush()
        time.sleep(speed)
    print()

# -----------------------
# STATS
# -----------------------

def power():
    return round((player["strength"] + player["endurance"] +
                  player["vitality"] + player["agility"]) / 4)

def health():
    return round((player["energy"] + player["morale"] +
                  player["thirst"] + player["hunger"]) / 4)

def clamp():
    for stat in ("energy", "morale", "thirst", "hunger"):
        player[stat] = max(0, min(100, player[stat]))

# -----------------------
# TIME
# -----------------------

def show_time():
    print(f"Day {day} | {hour:02d}:00")

def pass_time(hours):
    global day, hour
    hour += hours
    while hour >= 24:
        hour -= 24
        day += 1
    hourly_decay()

def hourly_decay():
    player["energy"] -= 1
    player["thirst"] -= 2
    player["hunger"] -= 1
    clamp()

# -----------------------
# FOOD / WATER
# -----------------------

def equip_food(name):
    if name in foods:
        player["equipped_food"] = name

def equip_water(name):
    if name in waters:
        player["equipped_water"] = name

def eat():
    item = player["equipped_food"]
    if not item:
        return
    for stat, value in foods[item].items():
        player[stat] += value
    if player["food"] > 0:
        player["food"] -= 1
    clamp()

def drink():
    item = player["equipped_water"]
    if not item:
        return
    for stat, value in waters[item].items():
        player[stat] += value
    if player["water"] > 0:
        player["water"] -= 1
    clamp()

# -----------------------
# RANDOM EVENTS
# -----------------------

events = [
    "nothing",
    "enemy",
    "food",
    "water",
    "traveler",
]

def random_event():
    return random.choice(events)

# -----------------------
# ENEMY
# -----------------------

def make_enemy(name, strength, endurance, vitality, agility):
    return {
        "name": name,
        "strength": strength,
        "endurance": endurance,
        "vitality": vitality,
        "agility": agility,
        "energy": 100,
        "morale": 100,
        "thirst": 100,
        "hunger": 100,
    }

def enemy_power(enemy):
    return round((enemy["strength"] + enemy["endurance"] +
                  enemy["vitality"] + enemy["agility"]) / 4)

def enemy_health(enemy):
    return round((enemy["energy"] + enemy["morale"] +
                  enemy["thirst"] + enemy["hunger"]) / 4)

# -----------------------
# BATTLE
# -----------------------

def battle(enemy):
    while health() > 0 and enemy_health(enemy) > 0:
        print("\n--------------------")
        print(f"You: {health()} HP")
        print(f'{enemy["name"]}: {enemy_health(enemy)} HP')
        print("1. Attack")
        print("2. Run")

        choice = input("> ")

        if choice == "1":
            damage = random.randint(max(1, power()-2), power()+2)
            enemy["energy"] -= damage
            print(f"You dealt {damage} damage.")

        elif choice == "2":
            if random.randint(1, 20) <= player["agility"]:
                print("You escaped!")
                return False
            else:
                print("Couldn't escape!")

        if enemy_health(enemy) <= 0:
            print("Enemy defeated!")
            return True

        damage = random.randint(max(1, enemy_power(enemy)-2),
                                enemy_power(enemy)+2)
        player["energy"] -= damage
        clamp()
        print(f'{enemy["name"]} dealt {damage} damage.')

    print("You were defeated.")
    return False

# -----------------------
# DISPLAY
# -----------------------

def stats():
    print("\n=== PLAYER ===")
    print(f"Power : {power()}")
    print(f"Health: {health()}")
    print(f"Strength : {player['strength']}")
    print(f"Endurance: {player['endurance']}")
    print(f"Vitality : {player['vitality']}")
    print(f"Agility  : {player['agility']}")
    print()
    print(f"Energy : {player['energy']}")
    print(f"Morale : {player['morale']}")
    print(f"Hunger : {player['hunger']}")
    print(f"Thirst : {player['thirst']}")
    print()
    print(f"Food Supply : {player['food']}")
    print(f"Water Supply: {player['water']}")

# Add your story below by calling these functions.
