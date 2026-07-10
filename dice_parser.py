import random
import re

class DiceParser:
    def __init__(self):
        self.results = []
    
    def roll_dice(self, count, sides):
        """Бросает count кубиков с sides гранями"""
        return [random.randint(1, sides) for _ in range(count)]
    
    def parse_expression(self, expr):
        """Парсит и вычисляет выражение с кубиками"""
        expr = expr.strip()
        
        # Обработка специальных команд
        if expr == '/d' or expr == '/к':
            return self.parse_dice('/d20')
        
        if expr == '/d%' or expr == '/к%':
            return self.parse_dice('/d100')
        
        # Обработка FATE
        if expr.startswith('/f') or expr.startswith('/fate'):
            return self.parse_fate(expr)
        
        # Обработка бросков с преимуществом/помехой
        if '/dad' in expr or '/dпре' in expr:
            return self.parse_advantage(expr, 'max')
        if '/dis' in expr or '/dпом' in expr:
            return self.parse_advantage(expr, 'min')
        
        # Обработка взрывающихся кубиков
        if '!' in expr:
            return self.parse_exploding(expr)
        
        # Обработка Drop/Keep
        if 'dh' in expr or 'dl' in expr or 'kh' in expr or 'kl' in expr:
            return self.parse_drop_keep(expr)
        
        # Обработка перебросов
        if 'r>' in expr or 'r<' in expr or 'ro>' in expr or 'ro<' in expr:
            return self.parse_reroll(expr)
        
        # Обработка бросков с сопротивлением
        if 'res' in expr or 'спр' in expr:
            return self.parse_resist(expr)
        
        # Обработка обычных дайсов
        return self.parse_dice(expr)
    
    def parse_dice(self, expr):
        """Парсит обычные броски кубиков вида XdY+M"""
        if expr.startswith('/'):
            expr = expr[1:]
        
        parts = re.split(r'([+\-*/])', expr)
        
        dice_part = None
        modifiers = []
        current = ''
        
        for part in parts:
            if part in '+-*/':
                if dice_part is None:
                    dice_part = current.strip()
                else:
                    modifiers.append((part, ''))
                current = ''
            else:
                current += part
        
        if dice_part is None:
            dice_part = current.strip()
        elif current.strip():
            modifiers.append((current.strip(), ''))
        
        if 'd' in dice_part or 'к' in dice_part or 'k' in dice_part:
            dice_part = dice_part.replace('к', 'd').replace('k', 'd')
            
            if dice_part.startswith('d'):
                count = 1
                sides = int(dice_part[1:])
            else:
                parts = dice_part.split('d')
                count = int(parts[0]) if parts[0] else 1
                sides = int(parts[1]) if len(parts) > 1 else 20
        else:
            return int(dice_part) if dice_part else 0
        
        rolls = self.roll_dice(count, sides)
        total = sum(rolls)
        
        for i in range(0, len(modifiers), 2):
            if i+1 < len(modifiers):
                op = modifiers[i]
                val = int(modifiers[i+1]) if modifiers[i+1] else 0
                if op == '+':
                    total += val
                elif op == '-':
                    total -= val
                elif op == '*':
                    total *= val
                elif op == '/':
                    total = total // val if val != 0 else total
        
        result_str = f"{count}d{sides}: {', '.join(map(str, rolls))}"
        if modifiers:
            result_str += f" = {total}"
        else:
            result_str += f" = {total}"
        
        return result_str
    
    def parse_fate(self, expr):
        """Парсит FATE/FUDGE кубики"""
        match = re.search(r'/f(?:ate)?(\d+)?', expr)
        count = int(match.group(1)) if match and match.group(1) else 4
        
        faces = [-1, -1, 0, 0, 1, 1]
        rolls = [random.choice(faces) for _ in range(count)]
        total = sum(rolls)
        
        roll_str = ' '.join(['+' if r == 1 else '-' if r == -1 else '0' for r in rolls])
        return f"Fate {count}d: {roll_str} = {total}"
    
    def parse_advantage(self, expr, mode):
        """Парсит броски с преимуществом/помехой"""
        base_expr = expr.replace('/dad', '').replace('/dпре', '')
        base_expr = base_expr.replace('/dis', '').replace('/dпом', '')
        
        if not base_expr:
            rolls = self.roll_dice(2, 20)
            result = max(rolls) if mode == 'max' else min(rolls)
            roll_str = f"2d20: {', '.join(map(str, rolls))}"
            return f"{roll_str} → {result} ({'преимущество' if mode == 'max' else 'помеха'})"
        
        if 'd' in base_expr or 'к' in base_expr:
            base_expr = base_expr.replace('к', 'd').replace('k', 'd')
            parts = base_expr.split('d')
            count = int(parts[0]) if parts[0] else 1
            sides = int(parts[1]) if len(parts) > 1 else 20
            
            rolls1 = self.roll_dice(count, sides)
            rolls2 = self.roll_dice(count, sides)
            
            total1 = sum(rolls1)
            total2 = sum(rolls2)
            
            result = max(total1, total2) if mode == 'max' else min(total1, total2)
            
            return f"{count}d{sides}: {total1} vs {total2} → {result} ({'преимущество' if mode == 'max' else 'помеха'})"
        
        return "Ошибка в формате команды"
    
    def parse_exploding(self, expr):
        """Парсит взрывающиеся кубики"""
        if expr.endswith('!'):
            base = expr[:-1]
            if base.startswith('/'):
                base = base[1:]
            
            if 'd' in base:
                parts = base.split('d')
                count = int(parts[0]) if parts[0] else 1
                sides = int(parts[1]) if len(parts) > 1 else 20
                
                rolls = []
                total = 0
                
                for _ in range(count):
                    roll = random.randint(1, sides)
                    total += roll
                    rolls.append(roll)
                    
                    while roll == sides:
                        roll = random.randint(1, sides)
                        total += roll
                        rolls.append(f"!{roll}")
                
                return f"{count}d{sides} (взрывной): {', '.join(map(str, rolls))} = {total}"
        
        return "Неизвестный формат взрывающегося броска"
    
    def parse_drop_keep(self, expr):
        """Парсит Drop/Keep броски"""
        match = re.search(r'(\d*)d(\d+)(dh|dl|kh|kl)(\d+)', expr)
        if match:
            count = int(match.group(1)) if match.group(1) else 1
            sides = int(match.group(2))
            operation = match.group(3)
            keep_drop = int(match.group(4))
            
            rolls = self.roll_dice(count, sides)
            sorted_rolls = sorted(rolls)
            
            if operation == 'dh':
                result_rolls = sorted_rolls[:-keep_drop] if keep_drop < len(sorted_rolls) else []
            elif operation == 'dl':
                result_rolls = sorted_rolls[keep_drop:] if keep_drop < len(sorted_rolls) else []
            elif operation == 'kh':
                result_rolls = sorted_rolls[-keep_drop:] if keep_drop <= len(sorted_rolls) else sorted_rolls
            elif operation == 'kl':
                result_rolls = sorted_rolls[:keep_drop] if keep_drop <= len(sorted_rolls) else sorted_rolls
            
            total = sum(result_rolls)
            return f"{count}d{sides}: {', '.join(map(str, rolls))} → {', '.join(map(str, result_rolls))} = {total}"
        
        return "Неизвестный формат Drop/Keep"
    
    def parse_reroll(self, expr):
        """Парсит перебросы"""
        if 'r>' in expr:
            parts = expr.split('r>')
            dice_part = parts[0].replace('/', '')
            threshold = int(parts[1])
            
            if 'd' in dice_part:
                parts = dice_part.split('d')
                count = int(parts[0]) if parts[0] else 1
                sides = int(parts[1]) if len(parts) > 1 else 20
                
                rolls = []
                for _ in range(count):
                    roll = random.randint(1, sides)
                    while roll >= threshold:
                        roll = random.randint(1, sides)
                    rolls.append(roll)
                
                total = sum(rolls)
                return f"{count}d{sides} (переброс ≥{threshold}): {', '.join(map(str, rolls))} = {total}"
        
        if 'r<' in expr:
            parts = expr.split('r<')
            dice_part = parts[0].replace('/', '')
            threshold = int(parts[1])
            
            if 'd' in dice_part:
                parts = dice_part.split('d')
                count = int(parts[0]) if parts[0] else 1
                sides = int(parts[1]) if len(parts) > 1 else 20
                
                rolls = []
                for _ in range(count):
                    roll = random.randint(1, sides)
                    while roll <= threshold:
                        roll = random.randint(1, sides)
                    rolls.append(roll)
                
                total = sum(rolls)
                return f"{count}d{sides} (переброс ≤{threshold}): {', '.join(map(str, rolls))} = {total}"
        
        return "Неизвестный формат переброса"
    
    def parse_resist(self, expr):
        """Парсит броски с сопротивлением"""
        if 'res' in expr:
            base = expr.replace('res', '').replace('/', '')
            if 'd' in base:
                parts = base.split('d')
                count = int(parts[0]) if parts[0] else 1
                sides = int(parts[1]) if len(parts) > 1 else 20
                
                rolls = self.roll_dice(count, sides)
                total = sum(rolls)
                return f"{count}d{sides} (сопротивление): {', '.join(map(str, rolls))} = {total}"
        
        return "Неизвестный формат броска с сопротивлением"