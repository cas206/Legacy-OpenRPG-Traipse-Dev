from orpg.orpgCore import component
import re
from orpg.tools.orpg_log import logger
from wx import TextEntryDialog, ID_OK

class InterParse():

    def __init__(self):
        pass

    def Post(self, s, send=False, myself=False):
        s = self.Normalize(s)
        component.get('chat').set_colors()
        component.get('chat').Post(s, send, myself)

    def Normalize(self, s):
        for plugin_fname in component.get('chat').activeplugins.keys():
            plugin = component.get('chat').activeplugins[plugin_fname]
            try: s = plugin.pre_parse(s)
            except Exception, e:
                if str(e) != "'module' object has no attribute 'post_msg'":
                    logger.general(traceback.format_exc())
                    logger.general("EXCEPTION: " + str(e))
        if component.get('chat').parsed == 0:
            s = self.Node(s)
            s = self.Dice(s)
            s = self.Filter(s)
            component.get('chat').parsed = 1
        return s
    
    def Filter(self, s):
        s = component.get('chat').GetFilteredText(s)
        return s

    def Node(self, s):
        """Parses player input for embedded nodes rolls"""
        cur_loc = 0
        #[a-zA-Z0-9 _\-\.]
        reg = re.compile("(!@(.*?)@!)")
        matches = reg.findall(s)
        for i in xrange(0,len(matches)):
            newstr = self.Node(self.resolve_nodes(matches[i][1]))
            s = s.replace(matches[i][0], newstr, 1)
        return s

    def Dice(self, s):
        """Parses player input for embedded dice rolls"""
        reg = re.compile("\[([^]]*?)\]")
        matches = reg.findall(s)
        for i in xrange(0,len(matches)):
            newstr = self.Unknown(matches[i])
            qmode = 0
            newstr1 = newstr
            if newstr[0].lower() == 'q':
                newstr = newstr[1:]
                qmode = 1
            if newstr[0].lower() == '#':
                newstr = newstr[1:]
                qmode = 2
            try: newstr = component.get('DiceManager').proccessRoll(newstr)
            except: pass
            if qmode == 1:
                s = s.replace("[" + matches[i] + "]", 
                            "<!-- Official Roll [" + newstr1 + "] => " + newstr + "-->" + newstr, 1)
            elif qmode == 2:
                s = s.replace("[" + matches[i] + "]", newstr[len(newstr)-2:-1], 1)
            else: s = s.replace("[" + matches[i] + "]", 
                            "[" + newstr1 + "<!-- Official Roll -->] => " + newstr, 1)
        return s

    def Unknown(self, s):
	# Uses a tuple. Usage: ?Label}dY. If no Label is assigned then use ?}DY
        newstr = "0"
        reg = re.compile("(\?\{*)([a-zA-Z ]*)(\}*)")
        matches = reg.findall(s)
        for i in xrange(0,len(matches)):
            lb = "Replace '?' with: "
            if len(matches[i][0]):
                lb = matches[i][1] + "?: "
            dlg = TextEntryDialog(self, lb, "Missing Value?")
            dlg.SetValue('')
            if matches[i][0] != '':
                dlg.SetTitle("Enter Value for " + matches[i][1])
            if dlg.ShowModal() == ID_OK: newstr = dlg.GetValue()
            if newstr == '': newstr = '0'
            s = s.replace(matches[i][0], newstr, 1).replace(matches[i][1], '', 1).replace(matches[i][2], '', 1)
            dlg.Destroy()
        return s

    def NodeMap(self, s, node):
        """Parses player input for embedded nodes rolls"""
        cur_loc = 0
        reg = re.compile("(!!(.*?)!!)")
        matches = reg.findall(s)
        for i in xrange(0,len(matches)):
            tree_map = node.get('map')
            tree_map = tree_map + '::' + matches[i][1]
            newstr = '!@'+ tree_map +'@!'
            s = s.replace(matches[i][0], newstr, 1)
            s = self.Node(s)
            s = self.NodeParent(s, tree_map)
        return s

    def NodeParent(self, s, tree_map):
        """Parses player input for embedded nodes rolls"""
        cur_loc = 0
        reg = re.compile("(!#(.*?)#!)")
        matches = reg.findall(s)
        for i in xrange(0,len(matches)):
            ## Build the new tree_map
            new_map = tree_map.split('::')
            del new_map[len(new_map)-1]
            parent_map = matches[i][1].split('::')
            ## Backwards Reference the Parent Children
            child_node = self.get_node('::'.join(new_map))
            newstr = self.get_root(child_node, tree_map, new_map, parent_map)
            s = s.replace(matches[i][0], newstr, 1)
            s = self.Node(s)
        return s

    def get_root(self, child_node, tree_map, new_map, parent_map):
        if child_node == 'Invalid Reference!': return child_node
        roots = child_node.getchildren(); tr = tree_map.split('::')
        newstr = ''
        for root in roots:
            try: t = new_map.index(root.get('name'))
            except: t = 1
            if parent_map[0] == root.get('name'):
                newstr = '!@' + '::'.join(new_map[:len(tr)-t]) + '::' + '::'.join(parent_map) + '@!'
        if newstr != '': return newstr
        else:
            del new_map[len(new_map)-1]
            child_node = self.get_node('::'.join(new_map))
            newstr = self.get_root(child_node, tree_map, new_map, parent_map)
            return newstr

    def get_node(self, s):
        return_node = 'Invalid Reference!'
        value = ""
        path = s.split('::')
        depth = len(path)
        try: node = component.get('tree').tree_map[path[0]]['node']
        except Exception, e: return return_node
        return_node = self.resolve_get_loop(node, path, 1, depth)
        return return_node

    def resolve_get_loop(self, node, path, step, depth):
        if step == depth: return node
        else:
            child_list = node.findall('nodehandler')
            for child in child_list:
                if step == depth: break
                if child.get('name') == path[step]:
                    node = self.resolve_get_loop(child, path, step+1, depth)
            return node

    def resolve_nodes(self, s):
        self.passed = False
        string = 'Invalid Reference!'
        value = ""
        path = s.split('::')
        depth = len(path)
        try: node = component.get('tree').tree_map[path[0]]['node']
        except Exception, e: return string
        if node.get('class') in ('dnd35char_handler', 
                                "SWd20char_handler", 
                                "d20char_handler", 
                                "dnd3echar_handler"): string = self.resolve_cust_loop(node, path, 1, depth)
        elif node.get('class') == 'rpg_grid_handler': self.resolve_grid(node, path, 1, depth)
        else: string = self.resolve_loop(node, path, 1, depth)
        return string

    def resolve_loop(self, node, path, step, depth):
        if step == depth: return self.resolution(node)
        else:
            child_list = node.findall('nodehandler')
            for child in child_list:
                if step == depth: break
                if child.get('name') == path[step]:
                    node = child
                    step += 1
                    if node.get('class') in ('dnd35char_handler', 
                                            "SWd20char_handler", 
                                            "d20char_handler", 
                                            "dnd3echar_handler"): 
                        string = self.resolve_cust_loop(node, path, step, depth)
                    elif node.get('class') == 'rpg_grid_handler': 
                        string = self.resolve_grid(node, path, step, depth)
                    else: string = self.resolve_loop(node, path, step, depth)
            return string

    def resolution(self, node):
        if self.passed == False:
            self.passed = True
            if node.get('class') == 'textctrl_handler': 
                s = str(node.find('text').text)
            else: s = 'Nodehandler for '+ node.get('class') + ' not done!' or 'Invalid Reference!'
        else:
            s = ''
        s = self.NodeMap(s, node)
        s = self.NodeParent(s, node.get('map'))
        return s

    def resolve_grid(self, node, path, step, depth):
        if step == depth:
            return 'Invalid Grid Reference!'
        cell = tuple(path[step].strip('(').strip(')').split(','))
        grid = node.find('grid')
        rows = grid.findall('row')
        col = rows[int(self.Dice(cell[0]))-1].findall('cell')
        try: s = self.NodeMap(col[int(self.Dice(cell[1]))-1].text, node) or 'No Cell Data'
        except: s = 'Invalid Grid Reference!'
        return s

    def resolve_cust_loop(self, node, path, step, depth):
        s = 'Invalid Reference!'
        node_class = node.get('class')
        ## Code needs clean up. Either choose .lower() or .title(), then reset the path list's content ##
        if step == depth: self.resolution(node)
        ##Build Abilities dictionary##
        if node_class not in ('d20char_handler', "SWd20char_handler"): ab = node.find('character').find('abilities')
        else: ab = node.find('abilities')
        ab_list = ab.findall('stat'); pc_stats = {}

        for ability in ab_list:
            pc_stats[ability.get('name')] = ( 
                    str(ability.get('base')), 
                    str((int(ability.get('base'))-10)/2) )
            pc_stats[ability.get('abbr')] = ( 
                    str(ability.get('base')), 
                    str((int(ability.get('base'))-10)/2) )

        if node_class not in ('d20char_handler', "SWd20char_handler"): ab = node.find('character').find('saves')
        else: ab = node.find('saves')
        ab_list = ab.findall('save')
        for save in ab_list:
            pc_stats[save.get('name')] = (str(save.get('base')), str(int(save.get('magmod')) + int(save.get('miscmod')) + int(pc_stats[save.get('stat')][1]) ) )
            if save.get('name') == 'Fortitude': abbr = 'Fort'
            if save.get('name') == 'Reflex': abbr = 'Ref'
            if save.get('name') == 'Will': abbr = 'Will'
            pc_stats[abbr] = ( str(save.get('base')), str(int(save.get('magmod')) + int(save.get('miscmod')) + int(pc_stats[save.get('stat')][1]) ) )

        if path[step].lower() == 'skill':
            if node_class not in ('d20char_handler', "SWd20char_handler"): node = node.find('snf')
            node = node.find('skills')
            child_list = node.findall('skill')
            for child in child_list:
                if path[step+1].lower() == child.get('name').lower():
                    if step+2 == depth: s = child.get('rank')
                    elif path[step+2].lower() == 'check':
                        s = '<b>Skill Check:</b> ' + child.get('name') + ' [1d20+'+str( int(child.get('rank')) + int(pc_stats[child.get('stat')][1]) )+']'
            return s

        if path[step].lower() == 'feat':
            if node_class not in ('d20char_handler', "SWd20char_handler"): node = node.find('snf')
            node = node.find('feats')
            child_list = node.findall('feat')
            for child in child_list:
                if path[step+1].lower() == child.get('name').lower():
                    if step+2 == depth: s = '<b>'+child.get('name')+'</b>'+': '+child.get('desc')
            return s
        if path[step].lower() == 'cast':
            if node_class not in ('d20char_handler', "SWd20char_handler"): node = node.find('snp')
            node = node.find('spells')
            child_list = node.findall('spell')
            for child in child_list:
                if path[step+1].lower() == child.get('name').lower():
                    if step+2 == depth: s = '<b>'+child.get('name')+'</b>'+': '+child.get('desc')
            return s
        if path[step].lower() == 'attack':
            if node_class not in ('d20char_handler', "SWd20char_handler"): node = node.find('combat')
            if path[step+1].lower() == 'melee' or path[step+1].lower() == 'm':
                bonus_text = '(Melee)'
                bonus = node.find('attacks')
                bonus = bonus.find('melee')
                bonus = bonus.attrib; d = int(pc_stats['Str'][1])
            elif path[step+1].lower() == 'ranged' or path[step+1].lower() == 'r':
                bonus_text = '(Ranged)'
                bonus = node.find('attacks')
                bonus = bonus.find('ranged')
                bonus = bonus.attrib; d = int(pc_stats['Dex'][1])
            for b in bonus:
                d += int(bonus[b])
            bonus = str(d)
            if path[step+2] == None: s= bonus
            else:
                weapons = node.find('attacks')
                weapons = weapons.findall('weapon')
                for child in weapons:
                    if path[step+2].lower() == child.get('name').lower():
                        s = '<b>Attack: '+bonus_text+'</b> '+child.get('name')+' [1d20+'+bonus+'] ' + 'Damage: ['+child.get('damage')+']'
            return s
        elif pc_stats.has_key(path[step].title()):
            if step+1 == depth: s = pc_stats[path[step].title()][0] + ' +('+pc_stats[path[step].title()][1]+')'
            elif path[step+1].title() == 'Mod': s = pc_stats[path[step].title()][1]
            elif path[step+1].title() == 'Check': s = '<b>'+path[step].title()+' Check:</b> [1d20+'+str(pc_stats[path[step].title()][1])+']'
            return s
        return s

Parse = InterParse()
