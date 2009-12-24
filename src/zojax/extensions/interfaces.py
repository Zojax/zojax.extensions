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
from zope import schema, interface
from zope.location.interfaces import ILocation
from zope.i18nmessageid import MessageFactory

_ = MessageFactory('zojax.extensions')


class IExtensible(interface.Interface):
    """ marker interface for object that support extensions """


class IExtensionType(interface.interfaces.IInterface):
    """ extensions category """


class IExtension(ILocation):
    """ extension """

    __name__ = interface.Attribute(u'Extension name')
    __title__ = interface.Attribute(u'Extension title')
    __description__ = interface.Attribute(u'Extension description')
    __tests__ = interface.Attribute(u'Availabilty tests')
    __schema__ = interface.Attribute(u'Schema')

    context = interface.Attribute('Extension context')

    def isAvailable():
        """ check if this extension available in context """


class IBrowserExtension(IExtension):
    """ browser extension """

    request = interface.Attribute('Request')


class IExtensionDataFactory(interface.Interface):
    """ data factory """

    def __call__():
        """ create data object """


class IExtensionsDataStorage(interface.Interface):
    """ data storage for extensions """

    data = interface.Attribute('Data')

    def __getitem__(extension):
        """ get named data """


class ExtensionMarker(object):
    """ extension marker """

extensionMarker = ExtensionMarker()


class IDefaultExtensionType(interface.Interface):
    """ Extensions """


class IPageExtension(interface.Interface):
    _("""Extensions related to page structure.""")


class IPortalExtension(interface.Interface):
    _("""Extension related to base portal functionality.""")
