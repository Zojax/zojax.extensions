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
from zope import interface
from zope.location import Location
from zope.cachedescriptors.property import Lazy

from interfaces import IExtension, IBrowserExtension, IExtensionsDataStorage


class Extension(Location):
    """ base extension """
    interface.implements(IExtension)

    __name__ = u''
    __title__ = u''
    __description__ = u''
    __tests__ = ()

    def __init__(self, context):
        self.context = context
        self.__parent__ = context

    @Lazy
    def data(self):
        return IExtensionsDataStorage(self.context)[self]

    def isAvailable(self):
        for test in self.__tests__:
            if not test(self):
                return False
        return True


class BrowserExtension(Extension):
    interface.implements(IBrowserExtension)

    def __init__(self, context, request=None):
        super(BrowserExtension, self).__init__(context)
        self.request = request
