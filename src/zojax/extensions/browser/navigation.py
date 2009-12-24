##############################################################################
#
# Copyright (c) 2009 Zope Foundation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""

$Id$
"""
from zope.component import getAdapters, getUtilitiesFor
from zojax.extensions.interfaces import _
from zojax.extensions.interfaces import IExtension
from zojax.extensions.interfaces import IExtensionType
from zojax.extensions.interfaces import IDefaultExtensionType

from interfaces import IExtensionsView


class Navigation(object):

    def listExtensions(self):
        context = self.context.__parent__

        categories = [['', IDefaultExtensionType, []]] + [
            [name, tp, []] for name, tp in getUtilitiesFor(IExtensionType)]
        categories.sort()
        categories[0][0] = _('Extensions')

        for name, extension in getAdapters((context,), IExtension):
            if name and extension.isAvailable():
                for name, category, list in categories:
                    if category.providedBy(extension):
                        list.append((extension.__title__, extension))

        for name, extension in getAdapters((context, self.request), IExtension):
            if name and extension.isAvailable():
                for name, category, list in categories:
                    if category.providedBy(extension):
                        list.append((extension.__title__, extension))

        for name, extension, list in categories:
            list.sort()

        return categories

    def __call__(self, maincontext=None):
        ext = None
        while 1:
            if IExtensionsView.providedBy(maincontext):
                break

            ext = maincontext
            maincontext = getattr(maincontext, '__parent__', None)
            if maincontext is None:
                ext = None
                break

        if ext is not None:
            self.selected = ext.__name__
        else:
            self.selected = None

        return self.index()
