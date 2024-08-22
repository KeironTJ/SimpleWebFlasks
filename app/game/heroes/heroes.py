from app import create_app
from app.models import db, Hero, HeroType, RarityType, HeroSlotGroups


## Create rarity types
def sync_rarity_types():
    rarity_types = [
        {"name": "Common", "description": "Common Heroes"},
        {"name": "Uncommon", "description": "Uncommon Heroes"},
        {"name": "Rare", "description": "Rare Heroes"},
        {"name": "Epic", "description": "Epic Heroes"},
        {"name": "Legendary", "description": "Legendary Heroes"}
    ]

    existing_rarities = {r.rarity_type_name: r for r in RarityType.query.all()}
    for rarity in rarity_types:
        if rarity["name"] in existing_rarities:
            existing_rarities[rarity["name"]].rarity_type_description = rarity["description"]
            del existing_rarities[rarity["name"]]

        else:
            new_rarity = RarityType(rarity_type_name=rarity["name"], rarity_type_description=rarity["description"])
            db.session.add(new_rarity)

    for rarity in existing_rarities.values():
        db.session.delete(rarity)

    db.session.commit()
    print("Rarity Types Synchronized")

def sync_slot_groups():
    slot_groups = [
        {"name": "Main", "size": 4}
    ]
    existing_groups = {g.name: g for g in HeroSlotGroups.query.all()}
    for group in slot_groups:
        if group["name"] in existing_groups:
            existing_groups[group["name"]].size = group["size"]
            del existing_groups[group["name"]]
        else:
            new_group = HeroSlotGroups(name=group["name"], size=group["size"])
            db.session.add(new_group)
    for group in existing_groups.values():
        db.session.delete(group)
    db.session.commit()
    print("Slot Groups Synchronized")

def sync_hero_types():
    hero_types = [
        {"name": "Neutral", "description": "Generic Heroes"},
        {"name": "Warrior", "description": "Specialist heroes designed for attacking"},
        {"name": "Mage", "description": "Specialist heroes designed for defending"},
        {"name": "Rogue", "description": "Specialist heroes designed for speed"}
    ]
    existing_types = {t.hero_type_name: t for t in HeroType.query.all()}
    for hero_type in hero_types:
        if hero_type["name"] in existing_types:
            existing_types[hero_type["name"]].hero_type_description = hero_type["description"]
            del existing_types[hero_type["name"]]
        else:
            new_type = HeroType(hero_type_name=hero_type["name"], hero_type_description=hero_type["description"])
            db.session.add(new_type)
    for hero_type in existing_types.values():
        db.session.delete(hero_type)
    db.session.commit()
    print("Hero Types Synchronized")

class HeroCreator:
    def __init__(self, hero_name, hero_description, hero_type_id, rarity_type_id):
        self.hero_name = hero_name
        self.hero_description = hero_description
        self.hero_type_id = hero_type_id
        self.rarity_type_id = rarity_type_id
        self.hero = None

    def create_or_update_hero(self):
        existing_hero = Hero.query.filter_by(hero_name=self.hero_name).first()
        if existing_hero:
            existing_hero.hero_description = self.hero_description
            existing_hero.hero_type_id = self.hero_type_id
            existing_hero.rarity_type_id = self.rarity_type_id
            self.hero = existing_hero
            print(f"Hero {self.hero_name} Updated")
        else:
            self.hero = Hero(hero_name=self.hero_name, 
                             hero_description=self.hero_description, 
                             hero_type_id=self.hero_type_id, 
                             rarity_type_id=self.rarity_type_id)
            db.session.add(self.hero)
            print(f"Hero {self.hero_name} Created")
        db.session.commit()
        return self.hero

    def set_hero_stats(self, health=0, attack=0, defense=0, speed=0):
        if not self.hero:
            print("Hero must be created before setting stats.")
            return
        self.hero.health = health
        self.hero.attack = attack
        self.hero.defense = defense
        self.hero.speed = speed
        db.session.commit()
        print(f"Stats set for Hero {self.hero_name}")

def sync_heroes():
    heroes = [
        {"name": "Bill", "description": "The perfect definition of being in the wrong place at the wrong time.", "type_id": 1, "rarity_id": 1, 
         "stats": {"health": 3, "attack": 3, "defense": 3, "speed": 3}},

        {"name": "Serenity", "description": "Aspires to become something bigger", "type_id": 3, "rarity_id": 1, 
         "stats": {"health": 2, "attack": 2, "defense": 4, "speed": 4}},

        {"name": "Akk The Barbarian", "description": "About as frightening as a chocolate knife", "type_id": 2, "rarity_id": 1, 
         "stats": {"health": 4, "attack": 4, "defense": 2, "speed": 2}},

        {"name": "The Apprentice", "description": "New to magic", "type_id": 3, "rarity_id": 1, 
         "stats": {"health": 2, "attack": 4, "defense": 4, "speed": 2}}

    ]

    existing_heroes = {h.hero_name: h for h in Hero.query.all()}

    for hero_data in heroes:
        if hero_data["name"] in existing_heroes:
            hero = existing_heroes[hero_data["name"]]
            hero.hero_description = hero_data["description"]
            hero.hero_type_id = hero_data["type_id"]
            hero.rarity_type_id = hero_data["rarity_id"]
            hero.health = hero_data["stats"]["health"]
            hero.attack = hero_data["stats"]["attack"]
            hero.defense = hero_data["stats"]["defense"]
            hero.speed = hero_data["stats"]["speed"]
            del existing_heroes[hero_data["name"]]
            print(f"Hero {hero_data['name']} Updated")

        else:
            new_hero = Hero(hero_name=hero_data["name"], 
                            hero_description=hero_data["description"], 
                            hero_type_id=hero_data["type_id"], 
                            rarity_type_id=hero_data["rarity_id"],
                            health=hero_data["stats"]["health"],
                            attack=hero_data["stats"]["attack"],
                            defense=hero_data["stats"]["defense"],
                            speed=hero_data["stats"]["speed"])
            db.session.add(new_hero)
            print(f"Hero {hero_data['name']} Created")

    for hero in existing_heroes.values():
        db.session.delete(hero)
        print(f"Hero {hero.hero_name} Deleted")
        
    db.session.commit()
    print("Heroes Synchronized")


def update_heroes():
    sync_rarity_types()
    sync_hero_types()
    sync_slot_groups()
    sync_heroes()