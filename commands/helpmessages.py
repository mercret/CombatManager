from commands.commands import commands,shortcuts,usage

helpform='Usage: {} {}\nShortcut: {}\n{}'
helpmessages=['Moves to next entity in the queue',
              'Heals entity with index n hp points',
              'Damages entity with index n hp points',
              'Removes entity with index n from queue, by setting it to inactive',
              'Restore entity with index n to queue, by setting it to active',
              'Delays entity with index n up or down',
              'Displays help about command',
              'Stop the program']
#[helpform.format(commands[x],usage[x],shortcuts[x],helpmessages[x]) for x in range(0,len(commands))]
helpdict=dict(zip(commands,[helpform.format(commands[x],usage[x],shortcuts[x],helpmessages[x]) for x in range(0,len(commands))]))
helpdict.update(dict(zip(shortcuts,[helpform.format(commands[x],usage[x],shortcuts[x],helpmessages[x]) for x in range(0,len(commands))])))
