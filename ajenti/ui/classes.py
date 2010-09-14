import random
import base64
from lxml import etree 

class Element(etree.ElementBase):
    """ Generate XML element

    @tag - element name
    *args - any number of dictionaries {'attribute':'value'}
    **kwargs - any number of keyword arguments attribute="value"
    """
    def __init__(self, tag, *args, **kwargs):
        etree.ElementBase.__init__(self)
        self.tag = tag
        self.set('id', str(random.randint(1,9000*9000)))
        for k in args:
            self.append(k)
        for k in kwargs:
            self[k] = kwargs[k]
    
    def appendChild(self, el):
        print 'Remove that f#cking appendChild()!'
        self.append(el)
        
    def append(self, el):
        if el is not None:
            etree.ElementBase.append(self, el)
        
    def __setitem__(self, idx, val):
        self.set(idx, unicode(str(val)))
        
    def __getitem__(self, idx):
        return self.get(idx)
    
        
class UI(object):

    """ Automatically generate XML tags by calling name

    >>> m = UI.Meta(encoding="ru")
    >>> m.toxml()
    '<meta encoding="ru"/>'
    >>>
    """
    class __metaclass__(type):
        def __getattr__(cls, name):
            return lambda *args, **kw: Element(name.lower(), *args, **kw)

    @staticmethod
    def gen(name, *args, **kwargs):
        """ Generate XML tags by name, if name will violate Pyhton syntax

        >>> xi = UI.gen('xml:include', href="some.xml")
        >>> xi.toxml()
        '<xml:include href="some.xml"/>'
        >>>
        """
        return Element(name.lower(), *args, **kwargs)

    @staticmethod
    def CustomHTMLj(*args, **kwargs):
        class CustomHTML(Element):
            def __init__(self, *args, **kwargs):
                Element.__init__(self, 'customhtml', **kwargs)
                for e in args:
                    self['html'] = base64.b64encode(str(e))

        return CustomHTML(*args, **kwargs)

    @staticmethod
    def Text(text):
        return Element('span', {'py:content':"'%s'"%text, 'py:strip':""})

    @staticmethod
    def ProgressBar(*args, **kwargs):
        class ProgressBar(Element):
            def __init__(self, value=0, max=1, width=1):
                Element.__init__(self, 'progressbar', **kwargs)
                self['right'] = width - int(value*width/max)
                self['left'] = int(value*width/max)
                
        return ProgressBar(*args, **kwargs)

    @staticmethod
    def LayoutTable(*args, **kwargs):
        class LayoutTable(Element):
            def __init__(self, *args, **kwargs):
                Element.__init__(self, 'layouttable', **kwargs)
                for e in args:
                    if isinstance(e, Element):
                        if e.tag == 'layouttablerow':
                            self.append(e)
                        else:
                            self.append(UI.LayoutTableRow(e))

        return LayoutTable(*args, **kwargs)

    @staticmethod
    def LayoutTableRow(*args, **kwargs):
        class LayoutTableRow(Element):
            def __init__(self, *args):
                Element.__init__(self, 'layouttablerow', **kwargs)
                for e in args:
                    if e.tag == 'layouttablecell':
                        self.append(e)
                    else:
                        c = UI.LayoutTableCell(e)
                        c['spacing'] = self['spacing']
                        self.append(c)

        return LayoutTableRow(*args, **kwargs)

    @staticmethod
    def DataTable(*args, **kwargs):
        class DataTable(Element):
            def __init__(self, *args, **kwargs):
                Element.__init__(self, 'datatable', **kwargs)
                for e in args:
                    if isinstance(e, Element):
                        if e.tag == 'datatablecell':
                            self.append(e)
                        else:
                            self.append(UI.DataTableCell(e))
                for e in args:
                    self.append(e)

        return DataTable(*args, **kwargs)

    @staticmethod
    def DataTableRow(*args, **kwargs):
        class DataTableRow(Element):
            def __init__(self, *args, **kwargs):
                Element.__init__(self, 'datatablerow', **kwargs)
                for e in args:
                    if isinstance(e, Element):
                        if e.tag == 'datatablecell':
                            self.append(e)
                        else:
                            self.append(UI.DataTableCell(e))

        return DataTableRow(*args, **kwargs)

    @staticmethod
    def TreeContainer(*args, **kwargs):
        class TreeContainer(Element):
            def __init__(self, *args):
                print self.__class__
                Element.__init__(self, 'treecontainer', **kwargs)
                for e in args:
                    if isinstance(e, Element):
                        if e.tag == 'treecontainer':
                            self.append(e)
                        elif e.tag == 'treecontainernode':
                            self.append(e)
                        else:
                            self.append(UI.TreeContainerNode(e))

        return TreeContainer(*args)

    @staticmethod
    def TabControl(*args, **kwargs):
        class TabControl(Element):
            vnt = None
            vnb = None
            tc = 0

            def __init__(self, *args, **kwargs):
                print self
                Element.__init__(self, 'tabcontrol', **kwargs)
                self.vnt = UI.TabHeaderNode(id=self['id'])
                self.vnb = UI.VContainer()
                self.append(self.vnt)
                self.append(self.vnb)

            def add(self, name, content):
                self.vnt.append(UI.TabHeader(text=name, pid=self['id'], id=str(self.tc)))
                self.vnb.append(UI.TabBody(content, pid=self['id'], id=str(self.tc)))
                self.tc += 1

        return TabControl(*args, **kwargs)


class TreeManager(object):
    """ Processes treenode click events and stores the nodes'
    collapsed/expanded states.
    You should keep the TreeManager inside the session,
    call node_click() on each 'click' event, and apply() to the tree
    object before rendering it.
    """
    states = None

    def __init__(self):
        self.reset()

    def reset(self):
        self.states = []

    def node_click(self, id):
        if id in self.states:
            self.states.remove(id)
        else:
            self.states.append(id)
        
    def apply(self, tree):
        try:
            tree['expanded'] = tree['id'] in self.states

            for n in tree.getchildren():
                if n.tag == 'treecontainer':
                    self.apply(n)
        except:
            pass
