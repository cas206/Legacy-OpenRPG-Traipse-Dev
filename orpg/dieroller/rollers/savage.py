# (at your option) any later version.
# # This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 675 Mass Ave, Cambridge, MA 02139, USA.
# --
#
# File: savage.py
# Authors: Rich Finder
#        : Alexandre Major
# Maintainer:
# Version: 0.2
#
# Description: Savage Worlds die roller
# Permission was granted by Pinnacle to reprint the result descriptions from their tables on Apr 20, 2006 by Simon Lucas
#

__version__ = "$Id: savage.py,v Traipse 'Ornery-Orc' prof.ebral Exp $"

import string
from random import *

from std import std
from orpg.dieroller.base import *

# Savage, as in Savage Worlds
class sw(std):
    #def __init__(self,source=[], wnd=1, loc="rnd", chmod=0):
    def __init__(self,source=[],fmod=0):
        std.__init__(self,source)

# these methods return new die objects for specific options

    def fright(self,fearmod=0):
        return fright(self,fearmod=0)

    def kob(self,wnd,loc):
        return kob(self,wnd=1,loc="rnd")

    def ooc(self):
        return ooc(self)

    def ract(self,chmod=0):
        return ract(self,chmod=0)

    def vcrit(self):
        return vcrit(self)

    def fortune(self):
        return fortune(self)

    def freak(self):
        return freak(self)

    def swdhelps(self):
        return swdhelps(self)

die_rollers.register(sw)

class fright(std):
    #-----------------The Fright Table
    #  Rolls on the Fright - which is a 1d20 roll modified by the fear level of a monster.  This function automatically generates
    #  The appropriate random number and then adds the fear modifier to the rol and displays the result of the roll with the effect
    #  of that roll.
    #  Usage:  [fright()]
    #          [fright(6)] - if the fear modifier of the monster was 6
    #-----------------
    def __init__(self,fmod=0):
        global fear
        std.__init__(self)
        fear=fmod

    #def sum(self):

    def __str__(self):
        global fear
        iroll = randint(1,20)
        froll = iroll + fear
        if froll >= 1 and froll <=4:
            fresult = "Adrenaline Rush"
            fdescription = "The hero's \"fight\" response takes over.  He adds +2 to all Trait and damage rolls on his next action."
        elif froll >= 5 and froll <=8:
            fresult = "Shaken"
            fdescription = "The character is Shaken."
        elif froll >=9 and froll <=12:
            fresult = "Pankicked"
            fdescription = "The character immediately moves his full Pace plus running die away from the danger and is Shaken."
        elif froll >=13 and froll <=16:
            fresult = "Minor Phobia"
            fdescription = "The character gains a Minor Phobia Hindrance somehow associated with the trauma."
        elif froll >=17 and froll <=18:
            fresult = "Major Phobia"
            fdescription = "The character gains a Major Phobia Hindrance."
        elif froll >=19 and froll <= 20:
            fresult = "The Mark of Fear"
            fdescription = "The hero is Shaken and also suffers some cosmetic, physical alteration -- a white streak forms in the hero's hair, his eyes twitch constantly, or some other minor physical alteration.  This reduces his Charisma by 1."
        else:
            fresult = "Heart Attack"
            fdescription = "The hero is so overwhelmed with fear that his heart stutters.  He becomes Incapacitated and must make a Vigor roll at -2.  If Successful, he's Shaken and can't attempt to recover for 1d4 rounds.  If he fails, he dies in 2d6 rounds.  A Healing roll at -4 saves the victim's life, but he remains Incapacitated."
        myStr = "[" + str(iroll) + "+"+str(fear)+"="+str(froll)+"] ==> " + fresult +":  "+ fdescription
        return myStr

class kob(std):
    #-------------------The Knockout Blow Table
    #  This table used when a character has sustained more than 3 wounds.  The number wounds taken that sends a character to the
    #  Knockout Blow Table is what gets sent with the kob command - not the total number of wounds the character currently has.
    #  For example - a character has 2 wounds and is hit takes 2 more wounds, this will result in a total of 4 wounds, but the
    #  number that gets sent to the kob roll is 2, because that is the number of wounds sustained that sent the character to the kob
    #  table.
    #
    #  It is also important to note that if a called shot to particular area was made, that information should be sent with the "roll"
    #  as well, because the KOB Table may need to determine some dramatic effects for permanent injuries, etc.  If a hit location was sent
    #  the function will use that information.
    #  Valid Hit Locations are:  h (head), g (guts), la (left arm), ra (right arm), rl (right leg), ll (left leg), c (crotch)
    #  Usage = [kob(3)] - If 3 wounds were received that sent the player to the Knockout Blow Table - no called shot
    #          [kob(3,"h") - If 3 wounds were received that sent the player to the Knockout Blow Table with a called shot to the head
    #---------------------
    global wound, loca
    def __init__(self, wnd, loc="rnd"):
        global wound, loca
        std.__init__(self, wnd)
        #Need to check to make sure that wnd is a number
        if (int(wnd)):
            wound = wnd
            loca = loc
        else:
            mystr = "You need to supply a number for the wound."
            return mystr

    def __str__(self):
        global wound, loca
        itbl = "no"
        if wound == 1:
            wtype = "Battered and Bruised"
            wdescription = "If your hero was previously Incapacitated, this result has no further effect. Otherwise, your hero's had the wind knocked out of him. Make a Spirit roll at the beginning of each round. If the roll is successful, he becomes Shaken and can return to the fight."
        elif wound == 2:  #Need to roll on the Injury table as well
            wtype = "Incapacitated"
            wdescription = "Your hero is beaten badly enough to take him out of this fight. He's Incapacitated and must roll on the Injury Table."
            itbl = "yes"
        elif wound == 3:
            wtype = "Bleeding Out"
            wdescription = "Your hero is bleeding out and Incapacitated. Roll on the Injury Table and make a Vigor roll at the start of each combat round. A failure means the hero has lost too much blood and becomes mortally Wounded (see below; begin rolling for the Mortal Wound in the next round). With a success, he keeps bleeding and must roll again next round. With a raise, or a successful Healing roll, he stops bleeding and is Incapacitated."
            itbl = "yes"
        elif wound < 1:
            wtype = "No Wounds?"
            wdescription = "The Number of wounds specified was less than one...why are you consulting this chart?"
        else:
            wtype = "Mortal Wound"
            wdescription = "Your hero has suffered a life-threatening wound and will not recover without aid. He is Incapacitated and must roll on the Injury Table. He must also make a Vigor roll at the start of each round. If the roll is failed, he passes on. A Healing roll stabilizes the victim but leaves him Incapacitated."
            itbl = "yes"

        if itbl == "yes":
            #Determine if a Hit location was specified already
            if loca.lower() == "h":
                iroll = 11
            elif loca.lower() == "g":
                iroll = 5
            elif loca.lower() == "ra":
                iroll = 3
                aroll = 2
            elif loca.lower() == "la":
                iroll = 3
                aroll = 1
            elif loca.lower() == "rl":
                iroll = 10
                lroll = 2
            elif loca.lower() == "ll":
                iroll = 10
                lroll = 1
            elif loca.lower() == "c":
                iroll = 2
            else:  #none of the above were provided...wo will need to determine randomly
                iroll = randint(2,12)
            #resolve the injury table stuff...
            if iroll == 2:
                iloc = "Unmentionables"
                idescription = "The hero suffers an embarrassing and painful wound to the groin."
            elif iroll == 3 or iroll == 4:
                if loca != "ra" and loca != "la":  #  If a hit location was not specified (or not recognized) already, determine randomly
                    aroll = randint(1,2)
                if aroll == 1:
                    warm = "Left"
                else:
                    warm = "Right"
                iloc = warm + " Arm"
                idescription = "The arm is rendered useless."
            elif iroll >= 5 and iroll <= 9:  #will need to make another random roll
                iloc = "Guts"
                idescription = "Your hero catches one somewhere between the crotch and the chin."
                groll = randint(1,6)
                if groll == 1 or groll == 2:
                    #idescription += " <b>Broken (" + str(groll) + ")</b> His Agility is reduced by a die type (min dr)."
                    idescription += " <b>Broken (" + str(groll) + ")</b> His Agility is reduced by a die type (min d4)."
                elif groll == 3 or groll == 4:
                    idescription += " <b>Battered (" + str(groll) + ")</b> His Vigor is reduced by a die type (min d4)."
                else:
                    idescription += " <b>Busted (" + str(groll) + ")</b> His Strength is reduced by a die type (min d4)."
            elif iroll == 10:
                if loca != "ll" and loca != "rl":  #  If a hit location was not specified (or not recognized) already, determine randomly
                    lroll = randint(1,2)
                if lroll == 1:
                    wleg = "Left"
                else:
                    wleg = "Right"
                iloc = wleg + " Leg"
                idescription = "The character's leg is crushed, broken, or mangled. His Pace is reduced by 1."
            else:  #Will need to make another random roll for this one.
                iloc = "Head"
                idescription = "Your hero has suffered a grievous injury to his head."
                hroll = randint(1,6)  #determine how the head is impacted by the wound
                if hroll == 1 or hroll ==2:
                    idescription += "<b>Hideous Scar (" + str(hroll) + ")</b>Your hero now has the Ugly Hindrance."
                elif hroll == 3 or hroll == 4:
                    idescription += "<b>Blinded (" + str(hroll) + ")</b> One or both of your hero's eyes was damaged. He gains the Bad Eyes Hindrance."
                else:
                    idescription += "<b>Brain Damage (" + str(hroll) + ")</b> Your hero suffers massive trauma to the head. His Smarts is reduced one die type (min d4)."
            idescription += " Make a Vigor roll applying any wound modifiers. If the Vigor roll is failed, the injury is permanent regardless of healing. If the roll is successful, the effect goes away when all wounds are healed."
            if iroll == 2:
                idescription +=" If the injury is permanent, reproduction is out of the question without miracle surgery or magic."
            if loca != "h" and loca != "g" and loca != "c" and loca != "rl" and loca != "ll" and loca != "ra" and loca != "la":
                idescription +="<br><br><b>***If the attack that caused the Injury was directed at a specific body part, use that location instead of rolling randomly.***</b>"
            myStr = "[" + wtype + "] ==>" + wdescription + "<br><br><b>Injury Table Result ("+ str(iroll) +"): </b> [" + iloc + "] ==> " + idescription
        else:
            myStr = "[" + wtype + "] ==>" + wdescription
        return myStr

class ract(std):
    #----------------------The Reaction Table
    #  This is used to randomly determine the general mood of NPCs toward the player characters.  This simulates a 2d6 roll
    #  and displays the reaction.  This roll can be modified by the Charisma of the player(s).
    #  Usage:  [ract()] - No Charisma modifier
    #          [ract(2)] - A +2 Charisma modifier
    #          [ract(-2)] - A -2 Charisma modifier
    #----------------------
    global charisma
    def __init__(self,chmod=0):
        global charisma
        std.__init__(self)
        charisma = chmod

    def __str__(self):
        global charisma
        r1roll = randint(2,12)
        rroll = r1roll + charisma
        if rroll == 2:
            reaction = "Hostile"
            rdescription = "The NPC is openly hostile and does his best to stand in the hero's way. He won't help without an overwhelming reward or payment of some kind."
        elif rroll >=3 and rroll <=4:
            reaction = "Unfriendly"
            rdescription = "The NPC is openly hostile and does his best to stand in the hero's way. He won't help without an overwhelming reward or payment of some kind."
        elif rroll >=5 and rroll <=9:
            reaction = "Neutral"
            rdescription = "The NPC has no particular attitude, and will help for little reward if the task at hand is very easy. If the task is difficult, he'll require substantial payment of some kind."
        elif rroll >=10 and rroll <=11:
            reaction = "Friendly"
            rdescription = "The NPC will go out of his way for the hero. He'll likely do easy tasks for free (or very little), and is willing to do more dangerous tasks for fair pay or other favors."
        else:
            reaction = "Helpful"
            rdescription = "The NPC is anxious to help the hero, and will probably do so for little or no pay depending on the nature of the task."
        #myStr = "[" + reaction + "(" + str(r1roll) + "+Charisma Mods("+str(charisma)+")="+str(rroll)+")] ==> " + rdescription
        myStr = "["+str(r1roll)+"+"+str(charisma)+"(charisma modifier)="+str(rroll)+"] ==> "+reaction+":  "+rdescription
        return myStr

class ooc(std):
    #--------------------The Out of Control Vehicle Table
    #  This table is used when a vehicle is injured during combat and must determine what happens to the vehicle.  This is a 2d6
    #  roll and displays the results of the roll.  This will also display altitude information for flying vehicles.
    #  Usage:  [ooc()]
    #--------------------
    def __init__(self):
        std.__init__(self)

    def __str__(self):
        ooroll = randint(2,12)
        oodescripton = "Something"
        if ooroll == 2:
            ooeffect = "Roll Over"
            rroll = randint(1,6)
            oodescription = "The vehicle performs a Slip and rolls over "+ str(rroll)+ " time"
            if rroll < 2:
                oodescription +="s"
            oodescription += " in that direction. Roll collision damage for the vehicle and everyone inside. Any exterior-mounted weapons or accessories are ruined."
        elif ooroll == 3 or ooroll == 4:
            ooeffect = "Spin"
            sroll = randint(1,6)
            froll = randint(1,12)
            oodescription = "Move the vehicle "+str(sroll)+"\" in the direction of the maneuver, or "+str(sroll)+"\" away from a damaging blow. At the end of the Spin,the vehicle is facing is "+str(froll)+" o'clock."
        elif ooroll >= 5 and ooroll <= 9:
            ooeffect = "Skid"
            sroll = randint(1,4)
            oodescription = "Move the vehicle "+str(sroll)+"\" left or right (in the direction of a failed maneuver, or away from a damaging attack)."
        elif ooroll == 10 or ooroll == 11:
            ooeffect = "Slip"
            sroll = randint(1,6)
            oodescription = "Move the vehicle "+str(sroll)+"\" left or right (in the direction of a failed maneuver, or away from a damaging attack)."
        else:
            ooeffect = "Flip"
            froll = randint(1,4)
            oodescription = "The vehicle flips end over end "+str(froll)+" times. Move it forward that many increments of its own length. Roll collision damage for the vehicle, its passengers, and anything it hits. "
            shroll = randint(1,2)
            if shroll == 1:
                oodescription += "<br><br><b>Note:</b> If the vehicle is slow and/or heavy (such as a tank) it Slips instead: "
                sroll = randint(1,6)
                oodescription += "Move the vehicle "+str(sroll)+"\" left or right (in the direction of a failed maneuver, or away from a damaging attack)."
            else:
                oodescription += "<br><br><b>Note (GM's discretion):</b> If the vehicle is slow and/or heavy (such as a tank) it Skids instead: "
                sroll = randint(1,4)
                oodescription += "Move the vehicle "+str(sroll)+"\" left or right (in the direction of a failed maneuver, or away from a damaging attack)."

        oodescription += "<br><br>For flying vehicles conducting combat in the air, the vehicle"
        altchange = randint(2,12)
        if altchange == 2:
            dwn = randint(2,20)
            oodescription += " loses "+str(dwn)+"\" of altitude."
        elif altchange == 3 or altchange == 4:
            dwn = randint(1,10)
            oodescription += " loses "+str(dwn)+"\" of altitude."
        elif altchange >= 5 and altchange <= 9:
            oodescription += " has no change in altitude."
        else:
            altup = randint(1,10)
            oodescription += " gains "+str(altup)+"\" of altitude."
        myStr = "[" + ooeffect + "(" + str(ooroll) + ")] ==> " + oodescription
        return myStr

class vcrit(std):
    #----------------The Critical Hit Vehicle Table
    #  This table generates a 2d6 roll to determine the Critical Hit results every time a vehicle takes a wound.  There are no
    #  modifiers to this roll
    #  Usage [vcrit()]
    #----------------
    def __init__(self):
        std.__init__(self)

    def __str__(self):
        chitroll = randint(2,12)
        if chitroll == 2:
            cheffect = "Scratch and Dent"
            chdescription = "The attack merely scratches the paint. There's no permanent damage."
        elif chitroll == 3:
            cheffect = "Engine"
            chdescription = "The engine is hit. Oil leaks, pistons misfire, etc. Acceleration is halved (round down). This does not affect deceleration, however."
        elif chitroll == 4:
            cheffect = "Locomotion"
            chdescription = "The wheels, tracks, or whatever have been hit. Halve the vehicle's Top Speed immediately. If the vehicle is pulled by animals, the shot hits one of them instead."
        elif chitroll == 5:  #Need to make an additional roll to see what direction the vehicle can turn...
            cheffect = "Controls"
            troll = randint(1,2)
            if troll == 1:
                aturn = "left"
            else:
                aturn = "right"
            chdescription = "The control system is hit. Until a Repair roll is made, the vehicle can only perform turns to the "+str(aturn)+". This may prohibit certain maneuvers as well."
        elif chitroll >= 6 and chitroll <=8:
            cheffect = "Chassis"
            chdescription = "The vehicle suffers a hit in the body with no special effects."
        elif chitroll == 9 or chitroll == 10:
            cheffect = "Crew"
            chdescription = "A random crew member is hit. The damage from the attack is rerolled. If the character is inside the vehicle, subtract the vehicle's Armor from the damage. Damage caused by an explosion affects all passengers in the vehicle."
        elif chitroll == 11:
            cheffect = "Weapon"
            chdescription = "A random weapon on the side of the vehicle that was hit is destroyed and may no longer be used. If there is no weapon, this is a Chassis hit instead (The vehicle suffers a hit in the body with no special effects)."
        else:
            cheffect = "Wrecked"
            chdescription = "The vehicle is wrecked and automatically goes Out of Control.<br><br><b>[Out of Control]</b> ==>"+str(ooc())
        myStr = "["+cheffect+" ("+str(chitroll)+")] ==> "+chdescription
        return myStr

    def ooc(self):
        return vcritooc(self)

class swdhelps(std):
    #Display help information for this die roller - it will list all the available commands, and how to use them
    def __init__(self):
        std.__init__(self)

    def __str__(self):
        myStr = "<table border='1' valign='top'>\
        <tr>\
            <td colspan='3'>This chart will show you the various commands you can use and what is required, etc.  The <i><b>italicized text</b></i> are optional variables.  Any text that is not italicized and is within parentheses is required.  About the only roll that has a required element is the Knockout Blow roll (kob).</td>\
        </tr>\
        <tr>\
            <td align='center'><b>Die Command</b></td><td align='center' width='55%'><b>Description</b></td><td align='center'width='30%'><b>Example</b></td>\
        </tr>\
        <tr>\
            <td><b>[fright(<i>monster's fear modifier</i>)]</b></td><td>Rolls on the <b>Fright Table</b>.  This command generates a number between 1 and 20 and displays the corresponding entry from the Fright Table.</td><td>[fright()]<br>[fright(6)]</td>\
        </tr>\
        <tr>\
            <td><b>[kob(#ofWounds,<i>hitLocation</i>)]</b></td><td>Rolls on the <b>Knockout Blow Table</b> as well as the <b>Injury Table</b> if necessary.  The number of wounds must be specified, however, the location only needs to be specified if a particular body part was targeted.  If a hit location was targeted, then the following codes should be used:<br>\
                <ul>\
                    <li>h = head</li>\
                    <li>g = guts/other vital areas</li>\
                    <li>c = crotch/groin</li>\
                    <li>la = left arm</li>\
                    <li>ra = right arm</li>\
                    <li>ll = left leg</li>\
                    <li>rl = right leg</li>\
                </ul><br>If no hit location is specified, the hit location will be determined when the roll on the Injury Table is necessary.  When specifiying a hit locations, the code must be entered within double quotes.</td><td><b>3 wounds, no called shot</b><br>[kob(3)]<br><b>2 wounds to the head</b><br>[kob(2,\"h\")]</td>\
        </tr>\
        <tr>\
            <td><b>[ract(<i>Charisma Mods</i>)]</b></td><td>Rolls on the <b>Reaction Table</b>.  Will generate the initial reaction to the PCs.  If the Charisma modifiers are supplied, they will be taken into account as well.  Remember that this table is generally only consulted when the reaction of the NPC is comlpetely unknown to the GM.</td><td><b>Reaction no Charisma Mods</b><br>[ract()]<br><b>Reaction with +2 Charisma Mods</b><br>[ract(2)]</td>\
        </tr>\
        <tr>\
            <td><b>[vcrit()]</b></td><td>Rolls on the <b>Critical Hit Table</b> for vehicles.  If a roll on the Out of Control Chart is necessary, it will automatically roll on that table as well.</td><td>[vcrit()]</td>\
        </tr>\
        <tr>\
            <td><b>[ooc()]</b></td><td>Rolls on the <b>Out of Controll Table</b> for vehicles.  This roll will automatically determine any directions/movement rolls as well.</td><td>[ooc()]</td>\
        </tr>\
        <tr>\
            <td><b>[fortune()]</b></td><td>Rolls on the <b>Fortune Table</b> for the Showdown Skirmish rules.  This roll will automatically roll on the <b>Freak Event Table</b> if necessary</td><td>[fortune()]</td>\
        </tr>\
        <tr>\
            <td><b>[freak()]</b></td><td>Rolls on the <b>Freak Event Table</b>.</td><td>[freak()]</td>\
        </tr>\
        <tr>\
            <td><b>[swdhelps()]</b></td><td>Displays this help list.</td><td>[swdhelps()]</td>\
        </tr>\
        </table>"
        return myStr

class fortune(std):
    def __init___(self):
        std.__init__(self)

    def __str__(self):
        forroll = randint(2,12)
        if forroll == 2 or forroll == 12: #Need to roll on Freak Event Table
            fortune = "Freak Event!"
            fdescription = "Roll on the Freak Event Table.<br><br><b>[Freak Event Table]</b> ==> "+str(freak())
        elif forroll == 3:
            fortune = "Twist of Fate"
            fdescription = "Take a benny from your opponent. If he does not have one, he must immediately remove any one Extra from play."
        elif forroll == 4:
            fortune = "The Quick and the Dead"
            fdescription = "Swap one of your opponent's cards for any one of yours."
        elif forroll == 5:
            fortune = "Rally"
            fdescription = "Pick any one unit on the board with Shaken figures. All those figures recover automatically."
        elif forroll >= 6 and forroll <= 8:
            fortune = "Hand of Fate"
            fdescription = "Gain one extra benny."
        elif forroll == 9:
            fortune = "Close Call"
            fdescription = "Any one of your opponent's units stumbles, becomes confused, or is otherwise disrupted. All its members suffer -2 to their trait rolls this round."
        elif forroll == 10:
            fortune = "Teamwork"
            fdescription = "Pick any one other unit within 12\" of this one. Discard its Action Card. It acts on the Joker along with this unit, and gains the usual bonuses as well."
        else:
            fortune = "Out of Ammo"
            fdescription = "Pick any one enemy unit. It's out of ammo or Power Points (your choice). If this result cannot be applied, you gain a benny instead."
        myStr = "["+fortune+" ("+str(forroll)+")] ==>"+fdescription
        return myStr

    def freak(self):
        return fortunefreak(self)

class freak(std):
    def __init__(self):
        std.__init__(self)

    def __str__(self):
        feroll = randint(1,10)
        if feroll == 1:
            fevent = "Storm"
            fedescription = "A sudden storm rolls in. Rain begins to pour and visibility is limited to 12\". All attack rolls are at -1, and black powder weapons don't work at all. The round after this event, all streams become impassable, even at fords. Only bridges remain."
        elif feroll == 2:
            fevent = "Fire!"
            fedescription = "Fire breaks out on the board! Roll randomly among each occupied building, patch of trees, or other flammable terrain type. If none of these are occupied, roll randomly among all flammable terrain pieces. The entire building or forest catches fire this round and causes 2d6 damage to everything within. The fire continues for the rest of the game--unless a storm comes, which quenches it immediately.<br><br>At the beginning of each turn thereafter, roll 1d6 for each flammable structure within 4\" (adjacent buildings, another patch of forest, etc.). On a 4-6, that structure catches fire as well. Check to see if these new fires spread in the following rounds."
        elif feroll == 3:
            fevent = "Blood Ties"
            fedescription = "One of the Wild Cards on the other side is related or has some other special bond with one of your heroes (a Wild Card of your choice). For the rest of the battle, these two won't attack each other directly unless there are no other targets on the board."
        elif feroll == 4:
            fevent = "Death of a Hero"
            inspireroll = randint(1,2)
            if inspireroll == 1:
                fedescription ="The next time one of your Wild Cards dies, his noble sacrifice triggers new resolve in his companions.  When your next Wild Card is Incapacitated the rest of your force is inspired by his legacy and adds +1 to all their rolls until another of your Wild Cards is killed."
            else:
                fedescription = "The next time one of your Wild Cards dies, his noble sacrifice triggers bone-chilling dread in his companions. When your next Wild Card is Incapacitated the rest of your force is filled with dread. They subtract -1 from all their rolls for the rest of the game until an <i>enemy</i> Wild Card is slain."
        elif feroll == 5:
            fevent = "Fickle Fate"
            fedescription = "Fate favors the underdog. The side with the fewest bennies draws until it has the same number as their foe. Place these in the common pool."
        elif feroll == 6:
            fevent = "Back from the Dead"
            fedescription = "One of your dead was just knocked unconscious. He returns in the spot where he fell. If this is a Wild Card, he returns with but a single wound."
        elif feroll == 7:
            fevent = "Bitter Cold/Heat"
            fedescription = "The weather heats up or cools down, depending on your environment. All troops become tired or bogged down and reduce their running rolls by half for the rest of the game."
        elif feroll == 8:
            fevent = "Battle Tested"
            fedescription = "Any one of your units improves any one skill or attribute a die type immediately."
        elif feroll == 9:
            fevent = "The Fog"
            fedescription = "Dense fog, mist, or smoke rolls drifts over the battlefield. Place two connected Large Burst Templates at the center of one randomly determined board edge. The fog drifts 2d6\" each round in a random direction (roll a d12 and read it like a clock facing). The fog \"bounces\" if it hits an edge in a random direction (so that it never leaves the field)."
        else:
            fevent = "Reinforcements"
            fedescription = "A group of your most common currently-fielded troop type arrives on the field of battle! Place these troops in your deployment area. They act on the Joker this round and are dealt in normally hereafter."
        myStr = "["+fevent+"("+str(feroll)+")] ==> "+fedescription
        return myStr

class rdm(std):  #If I get the time and the inspiration - I may try to incorporate a Random Table roller...  I need to think about this one.
    def __init__(self):
        std.__init__(self)

    def __str__(self):
        return myStr
