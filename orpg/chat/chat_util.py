# utility function; see Post() in chatwnd.py

import re
import string
from orpg.orpgCore import *
from orpg.tools.orpg_log import logger, debug
from orpg.tools.decorators import debugging

#============================================
# simple_html_repair(string)
#
# Crude html/xml parser/verifier.
# Catches many mistyped and/or malformed
# html tags and prevents them from causing
# issues with the chat display (see chatwnd.py)
# DOES NOT catch misused but properly formated
#    html like <script> or <li> which are known
#    to cause issues with the chat display
#
# Created 04-25-2005 by Snowdog
#=============================================

def simple_html_repair(string):
    "Returns string with extra > symbols to isolate badly formated HTML"
    #walk though string checking positions of < and > tags.
    first_instance = string.find('<')
    if first_instance == -1: return string #no html, bail out.

    #strip string of an instances of ">>" and "<<" recursively
    #while (string.find(">>") != -1):string = string.replace(">>",">")
    while (string.find("<<") != -1):string = string.replace("<<","<")

    last_start = first_instance
    in_tag_flag = 1
    a = first_instance + 1
    while a < len(string):
        if string[a] == '<':
            if in_tag_flag == 1:
                #attempt to figure out best place to put missing >
                #search from last_start to current position
                at_front = 1
                for best_pos in range(last_start,a):
                    if (str(string[best_pos]).isspace())and (at_front == 0):
                        break
                    else:
                        at_front = 0
                        best_pos = best_pos + 1
                a = best_pos
                string = string[:a]+">"+string[a:]
                in_tag_flag = 0
                #jump back up one character to catch the last > and reset the in_tag_flag
                a = a - 1
            else:
                in_tag_flag = 1
                last_start = a

        if string[a] == '>':
            last_start = a #found a closing tag, move start of scan block up.
            in_tag_flag = 0
        if (a >= (len(string)-1))and(in_tag_flag == 1):
            #at end of string and need a closing tag marker
            string = string +">"
        a = a+1

    #strip string of an instances of "<>"
    string = string.replace("<>","")

    #sanity check. Count the < and > characters, if there arn't enough > chars
    #tack them on the end to avoid open-tag conditions
    diff = string.count('<') - string.count('>')
    if diff > 0:
        for d in range(1,diff):
            string = string+">"
    return string

# Depricated! Might as well use the already made component.get('xml')
def strip_unicode(txt):
    for i in xrange(len(txt)):
        if txt[i] not in string.printable:
            try:
                txt = txt.replace(txt[i], '&#' + str(ord(txt[i])) + ';')
            except:
                txt = txt.replace(txt[i], '{?}')
    return txt

#================================================
# strip_script_tags(string)
#
# removes all script tags (start and end)
# 04-26-2005 Snowdog
#================================================

def strip_script_tags(string):
    #kill the <script> issue
    p = re.compile( '<(\s*)(/*)[Ss][Cc][Rr][Ii][Pp][Tt](.*?)>')
    string =  p.sub( "<!-- script tag removed //-->", string)
    return string

#================================================
# strip_li_tags(string)
#
# removes all li tags (start and end)
# 05-13-2005
#================================================

def strip_li_tags(string):
    #kill the <li> issue
    string = re.sub( r'<(\s*)[Ll][Ii](.*?)>', r'<b><font color="#000000" size=+1>*</font></b>    ', string)
    string = re.sub( r'<(/*)[Ll][Ii](.*?)>', r'<br />', string)
    return string

#================================================
# strip_body_tags(string)
#
# removes all body tags (start and end) from messages
# should not break the setting of custom background colors
#   through legitimate means such as the OpenRPG settings.
# 07-27-2005 by mDuo13
#================================================

def strip_body_tags(string):
    bodytag_regex = re.compile(r"""<\/?body.*?>""", re.I)
    string = re.sub(bodytag_regex, "", string)
    return string

#================================================
# strip_misalignment_tags(string)
#
# removes the alignment aspect of <p> tags, since
# simply closing one doesn't actually fix the text
# alignment. (I'm assuming this is a bug in wxWindows'
# html parser.)
# However, closing <center> tags does
# return the text to its normal alignment, so this
# algorithm simply closes them, allowing them to be
# used legitimately without causing much annoyance.
# 07-27-2005 mDuo13
#================================================

def strip_misalignment_tags(string):
    alignment_regex = re.compile(r"""<p([^>]*?)align\s*=\s*('.*?'|".*?"|[^\s>]*)(.*?)>""", re.I)
    string = re.sub(alignment_regex, "<p\\1\\3>", string)

    center_regex = re.compile(r"""<center.*?>""", re.I)
    endcenter_regex = re.compile(r"""</center.*?>""", re.I)
    num_centertags = center_regex.findall(string)
    num_endcentertags = endcenter_regex.findall(string)
    if num_centertags > num_endcentertags:
        missing_tags = len(num_centertags) - len(num_endcentertags)
        string = string + missing_tags*"</center>"#yes, you can do this.
    return string

#================================================
# strip_img_tags(string)
#
# removes all img tags (start and end)
# 05-13-2005
# redone 07-11-2005 by mDuo13
#================================================

def strip_img_tags(string):
    #This is a Settings definable feature, Allowing users to enable or disable image display to fix the client crash due to large img posted to chat.
    #p = re.sub( r'<(\s*)(/*)[Ii][Mm][Gg][ ][Ss][Rr][Cc][=](.*?)>', r'<!-- img tag removed //--> <a href=\3>\3</a>', string)

    #this regex is substantially more powerful than the one above
    img_tag_regex = re.compile(r"""<img.*?src\s*?=\s*('.*?'|".*?"|[^\s>]*).*?>""", re.I)
    #this is what replaces the regex match. the \\1 refers to the URL from the previous string
    img_repl_str = "<a href=\\1>[img]</a>"

    #replaces all instances of images in the string with links
    p = re.sub(img_tag_regex, img_repl_str, string)
    return p
