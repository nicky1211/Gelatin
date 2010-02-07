# Copyright (C) 2010 Samuel Abels.
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2, as
# published by the Free Software Foundation.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
import urllib
from Builder import Builder
from lxml    import etree

class Xml(Builder):
    def __init__(self):
        self.etree   = etree.Element('xml')
        self.current = [self.etree]
        self.stack   = []

    def serialize(self):
        return etree.tostring(self.etree, pretty_print = True)

    def dump(self):
        print self.serialize()

    def _splittag(self, path):
        tag, attribs = Builder._splittag(self, path)
        theattribs   = []
        for key, value in attribs:
            value = urllib.quote(value.replace(r'\"', '"'))
            theattribs.append((key, value))
        return tag, theattribs

    def _tag2xpath(self, tag, attribs):
        tag = tag.replace(' ', '-')
        if not attribs:
            return tag
        attribs = ['@' + k + '="' + v + '"' for k, v in attribs]
        return './' + tag + '[' + ' and '.join(attribs) + ']'

    def add(self, path, data = None):
        node = self.current[-1]
        for item in self._splitpath(path):
            tag, attribs = self._splittag(item)
            xpath        = self._tag2xpath(tag, attribs)
            next_node    = node.xpath(xpath)
            if next_node:
                node = next_node[0]
            else:
                node = etree.SubElement(node, tag, **dict(attribs))
        if data:
            node.text  = node.text is not None and node.text or ''
            node.text += data
        return node

    def enter(self, path):
        #print "ENTER", path
        node = self.add(path)
        self.stack.append(self.current[-1])
        self.current.append(node)
        return node

    def leave(self):
        #print "LEAVE"
        node = self.stack.pop()
        while self.current[-1] != node:
            self.current.pop()
