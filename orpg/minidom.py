"""\
minidom.py -- a lightweight DOM implementation based on SAX.

parse( "foo.xml" )

parseString( "<foo><bar/></foo>" )

Todo:
=====
 * convenience methods for getting elements and text.
 * more testing
 * bring some of the writer and linearizer code into conformance with this
        interface
 * SAX 2 namespaces
"""

from orpg import pulldom
import string
from StringIO import StringIO
import types

class Node:
    ELEMENT_NODE                = 1
    ATTRIBUTE_NODE              = 2
    TEXT_NODE                   = 3
    CDATA_SECTION_NODE          = 4
    ENTITY_REFERENCE_NODE       = 5
    ENTITY_NODE                 = 6
    PROCESSING_INSTRUCTION_NODE = 7
    COMMENT_NODE                = 8
    DOCUMENT_NODE               = 9
    DOCUMENT_TYPE_NODE          = 10
    DOCUMENT_FRAGMENT_NODE      = 11
    NOTATION_NODE               = 12
    allnodes = {}
    _debug = 0
    _makeParentNodes = 1
    debug = None

    def __init__(self):
        self.childNodes = []
        self.ownerDocument = None
        if Node._debug:
            index = repr(id(self)) + repr(self.__class__)
            Node.allnodes[index] = repr(self.__dict__)
            if Node.debug is None: Node.debug = StringIO()
                #open( "debug4.out", "w" )
            Node.debug.write("create %s\n" % index)

    def __getattr__(self, key):
        if key[0:2] == "__": raise AttributeError
        # getattr should never call getattr!
        if self.__dict__.has_key("inGetAttr"):
            del self.inGetAttr
            raise AttributeError, key
        prefix, attrname = key[:5], key[5:]
        if prefix == "_get_":
            self.inGetAttr = 1
            if hasattr(self, attrname):
                del self.inGetAttr
                return (lambda self=self, attrname=attrname:
                                getattr(self, attrname))
            else:
                del self.inGetAttr
                raise AttributeError, key
        else:
            self.inGetAttr = 1
            try: func = getattr(self, "_get_" + key)
            except AttributeError: raise AttributeError, key
            del self.inGetAttr
            return func()

    def __nonzero__(self):
        return 1

    def toxml(self,pretty=0):
        writer = StringIO()
        self.writexml(writer,pretty)
        return str(writer.getvalue())

    def hasChildNodes(self):
        if self.childNodes: return 1
        else: return 0

    def getChildren(self):
        return self.childNodes

    def _get_firstChild(self):
        if self.hasChildNodes(): return self.childNodes[0]
        else: return None

    def _get_lastChild(self):
        return self.childNodes[-1]

    def insertBefore(self, newChild, refChild):
        if refChild == None: return self.appendChild(newChild)
        index = self.childNodes.index(refChild)
        self.childNodes.insert(index, newChild)
        if self._makeParentNodes:
            newChild.parentNode = self
            newChild.ownerDocument = self.ownerDocument
        return newChild

    def appendChild(self, node):
        if self.childNodes:
            last = self.lastChild
            node.previousSibling = last
            last.nextSibling = node
        else: node.previousSibling = None
        node.nextSibling = None
        node.ownerDocument = self.ownerDocument
        node.parentNode = self
        self.childNodes.append(node)
        return node

    def replaceChild(self, newChild, oldChild):
        index = self.childNodes.index(oldChild)
        self.childNodes[index] = newChild
        newChild.ownerDocument = self.ownerDocument
        return oldChild

    def removeChild(self, oldChild):
        index = self.childNodes.index(oldChild)
        del self.childNodes[index]
        return oldChild

    def cloneNode(self, deep=0):
        newNode = Node()
        if deep: self.deep_clone(newNode)
        return newNode

    def deep_clone(self, newNode):
        for child in self.childNodes:
            new_child = child.cloneNode(1)
            newNode.appendChild(new_child)

    def normalize(self):
        """Join adjacent Text nodes and delete empty Text nodes
        in the full depth of the sub-tree underneath this Node.
        """
        i = 0
        while i < len(self.childNodes):
            cn = self.childNodes[i]
            if cn.nodeType == Node.TEXT_NODE:
                i = i + 1
                # join adjacent Text nodes
                while i < len(self.childNodes) and self.childNodes[i].nodeType == Node.TEXT_NODE:
                    cn.nodeValue = cn.data = cn.data + self.childNodes[i].data
                    del self.childNodes[i]
                # delete empty nodes
                if cn.nodeValue.strip() == "":
                    i = i - 1
                    del self.childNodes[i]
                continue
            elif cn.nodeType == Node.ELEMENT_NODE: cn.normalize()
            i = i + 1

    def unlink(self):
        self.parentNode = None
        while self.childNodes:
            self.childNodes[-1].unlink()
            del self.childNodes[-1] # probably not most efficient!
        self.childNodes = None
        self.previousSibling = None
        self.nextSibling = None
        if self.attributes:
            for attr in self._attrs.values(): self.removeAttributeNode(attr)
            assert not len(self._attrs)
            assert not len(self._attrsNS)
        if Node._debug:
            index = repr(id(self)) + repr(self.__class__)
            self.debug.write("Deleting: %s\n" % index)
            del Node.allnodes[index]

def _write_data(writer, data):
    "Writes datachars to writer."
    data = string.replace(data, "&", "&amp;")
    data = string.replace(data, "<", "&lt;")
    data = string.replace(data, "\"", "&quot;")
    data = string.replace(data, ">", "&gt;")
    writer.write(data)

def _getElementsByTagNameHelper(parent, name, rc):
    for node in parent.childNodes:
        if node.nodeType == Node.ELEMENT_NODE and \
            (name == "*" or node.tagName == name):
            rc.append(node)
        _getElementsByTagNameHelper(node, name, rc)
    return rc

def _getElementsByTagNameNSHelper(parent, nsURI, localName, rc):
    for node in parent.childNodes:
        if node.nodeType == Node.ELEMENT_NODE:
            if ((localName == "*" or node.tagName == localName) and
                (nsURI == "*" or node.namespaceURI == nsURI)):
                rc.append(node)
            _getElementsByTagNameNSHelper(node, name, rc)

class Attr(Node):
    nodeType = Node.ATTRIBUTE_NODE

    def __init__(self, qName, namespaceURI="", localName=None, prefix=None):
        # skip setattr for performance
        self.__dict__["localName"] = localName or qName
        self.__dict__["nodeName"] = self.__dict__["name"] = qName
        self.__dict__["namespaceURI"] = namespaceURI
        self.__dict__["prefix"] = prefix
        self.attributes = None
        Node.__init__(self)
        # nodeValue and value are set elsewhere

    def __setattr__(self, name, value):
        if name in ("value", "nodeValue"): self.__dict__["value"] = self.__dict__["nodeValue"] = value
        else: self.__dict__[name] = value

    def cloneNode(self, deep=0):
        newNode = Attr(self.__dict__["name"],self.__dict__["namespaceURI"],
                        self.__dict__["localName"],self.__dict__["prefix"])
        newNode.__dict__["value"] = newNode.__dict__["nodeValue"] = self.value
        if deep: self.deep_clone(newNode)
        return newNode

class AttributeList:
    """the attribute list is a transient interface to the underlying
    dictionaries.  mutations here will change the underlying element's
    dictionary"""
    def __init__(self, attrs, attrsNS):
        self._attrs = attrs
        self._attrsNS = attrsNS
        self.length = len(self._attrs.keys())

    def copy(self):
        clone = AttributeList(self._attrs.copy(),self._attrsNS.copy())
        return clone

    def item(self, index):
        try: return self[self.keys()[index]]
        except IndexError: return None

    def items(self):
        return map(lambda node: (node.tagName, node.value),
                   self._attrs.values())

    def itemsNS(self):
        return map(lambda node: ((node.URI, node.localName), node.value),
                   self._attrs.values())

    def keys(self):
        return self._attrs.keys()

    def keysNS(self):
        return self._attrsNS.keys()

    def values(self):
        return self._attrs.values()

    def __len__(self):
        return self.length

    def __cmp__(self, other):
        if self._attrs is getattr(other, "_attrs", None): return 0
        else: return cmp(id(self), id(other))

    #FIXME: is it appropriate to return .value?
    def __getitem__(self, attname_or_tuple):
        if type(attname_or_tuple) is types.TupleType: return self._attrsNS[attname_or_tuple]
        else: return self._attrs[attname_or_tuple]

    # same as set
    def __setitem__(self, attname, value):
        if type(value) is types.StringType:
            node = Attr(attname)
            node.value=value
        else:
            assert isinstance(value, Attr) or type(value) is types.StringType
            node = value
        old = self._attrs.get(attname, None)
        if old: old.unlink()
        self._attrs[node.name] = node
        self._attrsNS[(node.namespaceURI, node.localName)] = node

    def __delitem__(self, attname_or_tuple):
        node = self[attname_or_tuple]
        node.unlink()
        del self._attrs[node.name]
        del self._attrsNS[(node.namespaceURI, node.localName)]

class Element(Node):
    nodeType = Node.ELEMENT_NODE

    def __init__(self, tagName, namespaceURI="", prefix="",
                 localName=None):
        Node.__init__(self)
        self.tagName = self.nodeName = tagName
        self.localName = localName or tagName
        self.prefix = prefix
        self.namespaceURI = namespaceURI
        self.nodeValue = None
        self._attrs={}  # attributes are double-indexed:
        self._attrsNS={}#    tagName -> Attribute
                #    URI,localName -> Attribute
                # in the future: consider lazy generation of attribute objects
                #                this is too tricky for now because of headaches
                #                with namespaces.

    def cloneNode(self, deep=0):
        newNode = Element(self.tagName,self.namespaceURI,self.prefix,self.localName )
        keys = self._attrs.keys()
        for k in keys:
            attr = self._attrs[k].cloneNode(1)
            newNode.setAttributeNode(attr)
        if deep: self.deep_clone(newNode)
        return newNode

    def _get_tagName(self):
        return str(self.tagName)

    def getAttributeKeys(self):
        result = []
        if self._attrs: return self._attrs.keys()
        else: return None

    def getAttribute(self, attname):
        if self.hasAttribute(attname): return str(self._attrs[attname].value)
        else: return ""

    def getAttributeNS(self, namespaceURI, localName):
        return self._attrsNS[(namespaceURI, localName)].value

    def setAttribute(self, attname, value):
        attr = Attr(attname)
        # for performance
        attr.__dict__["value"] = attr.__dict__["nodeValue"] = value
        self.setAttributeNode(attr)

    def setAttributeNS(self, namespaceURI, qualifiedName, value):
        prefix, localname = _nssplit(qualifiedName)
        # for performance
        attr = Attr(qualifiedName, namespaceURI, localname, prefix)
        attr.__dict__["value"] = attr.__dict__["nodeValue"] = value
        self.setAttributeNode(attr)
        # FIXME: return original node if something changed.

    def getAttributeNode(self, attrname):
        return self._attrs.get(attrname)

    def getAttributeNodeNS(self, namespaceURI, localName):
        return self._attrsNS[(namespaceURI, localName)]

    def setAttributeNode(self, attr):
        old = self._attrs.get(attr.name, None)
        if old: old.unlink()
        self._attrs[attr.name] = attr
        self._attrsNS[(attr.namespaceURI, attr.localName)] = attr
        # FIXME: return old value if something changed

    def removeAttribute(self, name):
        attr = self._attrs[name]
        self.removeAttributeNode(attr)

    def removeAttributeNS(self, namespaceURI, localName):
        attr = self._attrsNS[(namespaceURI, localName)]
        self.removeAttributeNode(attr)

    def removeAttributeNode(self, node):
        node.unlink()
        del self._attrs[node.name]
        del self._attrsNS[(node.namespaceURI, node.localName)]

    def hasAttribute(self, name):
        return self._attrs.has_key(name)

    def hasAttributeNS(self, namespaceURI, localName):
        return self._attrsNS.has_key((namespaceURI, localName))

    def getElementsByTagName(self, name):
        return _getElementsByTagNameHelper(self, name, [])

    def getElementsByTagNameNS(self, namespaceURI, localName):
        _getElementsByTagNameNSHelper(self, namespaceURI, localName, [])

    def __repr__(self):
        return "<DOM Element: %s at %s>" % (self.tagName, id(self))

    # undocumented
    def writexml(self, writer, tabs=0):
        tab_str = ""
        if tabs:
            tab_str = "\n" + ("  "*(tabs-1))
            tabs += 1
        writer.write(tab_str + "<" + self.tagName)
        a_names = self._get_attributes().keys()
        a_names.sort()

        for a_name in a_names:
            writer.write(" %s=\"" % a_name)
            _write_data(writer, self._get_attributes()[a_name].value)
            writer.write("\"")
        if self.childNodes:
            writer.write(">")
            for node in self.childNodes:
                node.writexml(writer,tabs)
            if self.childNodes[0].nodeType == Node.TEXT_NODE:
                tab_str = ""
            writer.write(tab_str + "</%s>" % self.tagName)
        else: writer.write("/>")

    def _get_attributes(self):
        return AttributeList(self._attrs, self._attrsNS)

class Comment(Node):
    nodeType = Node.COMMENT_NODE

    def __init__(self, data):
        Node.__init__(self)
        self.data = self.nodeValue = data
        self.nodeName = "#comment"
        self.attributes = None

    def writexml(self, writer, tabs=0):
        writer.write("<!--%s-->" % self.data)

    def cloneNode(self, deep=0):
        newNode = Comment(self.data)
        if deep: self.deep_clone(newNode)
        return newNode

class ProcessingInstruction(Node):
    nodeType = Node.PROCESSING_INSTRUCTION_NODE

    def __init__(self, target, data):
        Node.__init__(self)
        self.target = self.nodeName = target
        self.data = self.nodeValue = data
        self.attributes = None

    def writexml(self, writer, tabs=0):
        writer.write("<?%s %s?>" % (self.target, self.data))

    def cloneNode(self, deep=0):
        newNode = ProcessingInstruction(self.target, self.data)
        if deep: self.deep_clone(newNode)
        return newNode

class Text(Node):
    nodeType = Node.TEXT_NODE
    nodeName = "#text"

    def __init__(self, data):
        Node.__init__(self)
        self.data = self.nodeValue = data
        self.attributes = None

    def __repr__(self):
        if len(self.data) > 10: dotdotdot = "..."
        else: dotdotdot = ""
        return "<DOM Text node \"%s%s\">" % (self.data[0:10], dotdotdot)

    def writexml(self, writer, tabs=0):
        _write_data(writer, self.data)

    def _get_nodeValue(self):
        return str(self.nodeValue)

    def _set_nodeValue(self,data):
        self.data = self.nodeValue = data

    def cloneNode(self, deep=0):
        newNode = Text(self.data)
        if deep: self.deep_clone(newNode)
        return newNode

def _nssplit(qualifiedName):
    fields = string.split(qualifiedName,':', 1)
    if len(fields) == 2: return fields
    elif len(fields) == 1: return ('', fields[0])

class Document(Node):
    nodeType = Node.DOCUMENT_NODE
    documentElement = None

    def __init__(self):
        Node.__init__(self)
        self.attributes = None
        self.nodeName = "#document"
        self.nodeValue = None
        self.ownerDocument = self

    def appendChild(self, node):
        if node.nodeType == Node.ELEMENT_NODE:
            if self.documentElement: raise TypeError, "Two document elements disallowed"
            else: self.documentElement = node
        Node.appendChild(self, node)
        return node
    createElement = Element
    createTextNode = Text
    createComment = Comment
    createProcessingInstruction = ProcessingInstruction
    createAttribute = Attr

    def createElementNS(self, namespaceURI, qualifiedName):
        prefix,localName = _nssplit(qualifiedName)
        return Element(qualifiedName, namespaceURI, prefix, localName)

    def createAttributeNS(self, namespaceURI, qualifiedName):
        prefix,localName = _nssplit(qualifiedName)
        return Attr(qualifiedName, namespaceURI, localName, prefix)

    def getElementsByTagNameNS(self, namespaceURI, localName):
        _getElementsByTagNameNSHelper(self, namespaceURI, localName)

    def unlink(self):
        self.documentElement = None
        Node.unlink(self)

    def getElementsByTagName(self, name):
        rc = []
        _getElementsByTagNameHelper(self, name, rc)
        return rc

    def writexml(self, writer):
        for node in self.childNodes: node.writexml(writer)

def _doparse(func, args, kwargs):
    events = apply(func, args, kwargs)
    toktype, rootNode = events.getEvent()
    events.expandNode(rootNode)
    return rootNode

def parse(*args, **kwargs):
    "Parse a file into a DOM by filename or file object"
    return _doparse(pulldom.parse, args, kwargs)

def parseString(*args, **kwargs):
    "Parse a file into a DOM from a string"
    return _doparse(pulldom.parseString, args, kwargs)
