from widgets.combatmanager import CombatManager

def start():
    cm=CombatManager()
    cm.attributes('-zoomed',True)
    cm.mainloop()