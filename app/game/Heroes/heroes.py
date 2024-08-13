from app import create_app
from app.models import db, Hero, HeroProgress, HeroType, HeroSlots, RarityType


## Create rarity types
def create_rarity_types():
    try:
        common = RarityType(rarity_type_name="Common", rarity_type_description="Common Heroes")
        uncommon = RarityType(rarity_type_name="Uncommon", rarity_type_description="Uncommon Heroes")
        rare = RarityType(rarity_type_name="Rare", rarity_type_description="Rare Heroes")
        epic = RarityType(rarity_type_name="Epic", rarity_type_description="Epic Heroes")
        legendary = RarityType(rarity_type_name="Legendary", rarity_type_description="Legendary Heroes")
        db.session.add(common)
        db.session.add(uncommon)
        db.session.add(rare)
        db.session.add(epic)
        db.session.add(legendary)
        db.session.commit()
        print("Rarity Types Created")
    except Exception as e:
        db.session.rollback()
        print(f"Failed to create rarity types: {e}")

## Create Hero Types
def create_hero_types():
    try:
        warrior = HeroType(hero_type_name="Warrior", hero_type_description="Warrior Heroes")
        mage = HeroType(hero_type_name="Mage", hero_type_description="Mage Heroes")
        rogue = HeroType(hero_type_name="Rogue", hero_type_description="Rogue Heroes")
        db.session.add(warrior)
        db.session.add(mage)
        db.session.add(rogue)
        db.session.commit()
        print("Hero Types Created")
    except Exception as e:
        db.session.rollback()
        print(f"Failed to create hero types: {e}")

## Hero Creator Class
class HeroCreator:
    def __init__(self, hero_name, hero_description, hero_type_id, rarity_type_id):
        self.hero_name = hero_name
        self.hero_description = hero_description
        self.hero_type_id = hero_type_id
        self.rarity_type_id = rarity_type_id
        self.hero = None  # Placeholder for the created hero object

    def create_hero(self):
        try:
            self.hero = Hero(hero_name=self.hero_name, 
                              hero_description=self.hero_description, 
                              hero_type_id=self.hero_type_id, 
                              rarity_type_id=self.rarity_type_id)
            db.session.add(self.hero)
            db.session.commit()
            print("Hero Created")
            return self.hero
        except Exception as e:
            db.session.rollback()
            print(f"Failed to create hero: {e}")

    def set_hero_stats(self, health=0, attack=0, defense=0, speed=0):
        if not self.hero:
            print("Hero must be created before setting stats.")
            return
        try:
            self.hero.base_health = health
            self.hero.base_attack = attack
            self.hero.base_defense = defense
            self.hero.base_speed = speed

            db.session.commit()
        except Exception as e:
            db.session.rollback()
            print(f"Failed to set hero stats: {self.hero_name} {e}")


# Example usage
Warrior = HeroCreator(hero_name="Warrior", hero_description="A strong warrior", hero_type_id=1, rarity_type_id=1)
Mage = HeroCreator(hero_name="Mage", hero_description="A powerful mage", hero_type_id=2, rarity_type_id=2)
Rogue = HeroCreator(hero_name="Rogue", hero_description="A sneaky rogue", hero_type_id=3, rarity_type_id=3)


## Delete Hero Data
def delete_hero_data():
    db.session.query(Hero).delete()
    db.session.query(HeroProgress).delete()
    db.session.query(HeroType).delete()
    db.session.query(HeroSlots).delete()
    db.session.query(RarityType).delete()

## Create Heroes
def create_heroes():
    create_rarity_types()
    create_hero_types()

    Warrior.create_hero()
    Mage.create_hero()
    Rogue.create_hero()







