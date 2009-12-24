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
from zope import interface, schema
from zope.app.rotterdam import Rotterdam
from zojax.layoutform.interfaces import ILayoutFormLayer

class ISkin(ILayoutFormLayer, Rotterdam):
    """ skin """


class IExtensionType1(interface.Interface):
    """ Extensions related to extentions1 """


class IExtensionType2(interface.Interface):
    """ Extensions related to extentions2 """


class IExtensionType3(interface.Interface):
    """ Extensions related to extentions3 """


class IExtension1(interface.Interface):

    title = schema.TextLine(
        title = u'Title')

    description = schema.TextLine(
        title = u'Description')


class IExtension2(interface.Interface):

    title = schema.TextLine(
        title = u'Title')

    description = schema.TextLine(
        title = u'Description')


class IExtension3(interface.Interface):

    title = schema.TextLine(
        title = u'Title')

    description = schema.TextLine(
        title = u'Description')
