# Minecraft-markup-language
mcMarkup.py is a simple python script to generate a cube of command blocks from a file of commands

### Usage ###
put a file named `input.mcm` in the same folder as `mcMarkup.py`. Run the script, and you're done.
That's all there is, your list of commands will be placed in the world on a clock that is fired every tick.
Aditional syntax can be used:

#### if statements ####
use `#if @e[selector]` and `#endif` on a line to make all the commands in between those lines conditional.
All the commands in between the two lines will get `execute @e[selector]` in front of them, thus creating an if condition.
There's no elses though, inverting a minecraft selector pretty much impossible without creating an extra scoreboard objective.

#### variables ####
use `#var name value` to declare a new variable, then use `$name` in a command to replace it with `value`

#### functions ####
use `#func name` to declare a new function, all functions must be declared at the end of the text file, after all the commands that should be put in the one tick clock.
use `$name` to run the function, the way this works is the function will not actually be put inside the clock, this way the commands in the function aren't fired every tick. `$name` will be replaced with a setblock command that fires a chain of commands. So there will be a one tick delay.