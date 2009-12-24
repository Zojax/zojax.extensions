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
from BTrees.OOBTree import OOBTree

from zope import interface, component
from zope.security.proxy import removeSecurityProxy
from zope.annotation.interfaces import IAnnotatable, IAnnotations

from interfaces import IExtensionDataFactory, IExtensionsDataStorage

_marker = object()

ANNOTATION_KEY = 'zojax.extensions'


class Storage(object):
    component.adapts(IAnnotatable)
    interface.implements(IExtensionsDataStorage)

    def __init__(self, context):
        self.context = context

        annotations = IAnnotations(removeSecurityProxy(context))

        data = annotations.get(ANNOTATION_KEY)

        if data is None:
            data = OOBTree()
            annotations[ANNOTATION_KEY] = data

        self.data = data

    def __getitem__(self, extension):
        name = extension.__name__

        if name not in self.data:
            factory = IExtensionDataFactory(extension, None)
            if factory is None:
                factory = OOBTree

            self.data[name] = factory()

        return self.data[name]
