from models import HeroProgress


class BattleSystem:
    
    def __init__(self, p1heroes, p2heroes):
        # Player 1 Heroes
        self.p1heroes = p1heroes
        
        # Player 2 Heroes
        self.p2heroes = p2heroes
        
        self.game_status = 0  # 0: ongoing, 1: player 1 wins, 2: player 2 wins
    
    def attack(self, attacker, defender):
        damage = attacker.attack - defender.defense
        if damage > 0:
            defender.health -= damage
        if defender.health <= 0:
            defender.health = 0
            self.check_win_conditions()
    
    def check_win_conditions(self):
        p1_alive = any(hero.health > 0 for hero in self.p1heroes)
        p2_alive = any(hero.health > 0 for hero in self.p2heroes)
        
        if not p1_alive:
            self.game_status = 2  # Player 2 wins
        elif not p2_alive:
            self.game_status = 1  # Player 1 wins
    
    def heal(self, hero):
        hero.health += hero.heal_power
        if hero.health > hero.max_health:
            hero.health = hero.max_health
    
    def special_ability(self, hero, target):
        # Implement special ability logic here
        pass
    
    
    
    
        