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
""" ++extensions++ namespace

$Id$
"""
from zope import interface, component
from zope.location import Location
from zope.security.proxy import removeSecurityProxy
from zope.component import queryAdapter, queryMultiAdapter
from zope.publisher.interfaces import NotFound, IPublishTraverse
from zope.traversing.interfaces import TraversalError, ITraversable

from zojax.extensions.interfaces import IExtensible, IExtension

from interfaces import IExtensionsView, IExtensionPublisher


class ExtensionsNamespace(Location):
    """ a ++extensions++ namespace """
    interface.implements(ITraversable, IPublishTraverse, IExtensionsView)
    component.adapts(IExtensible, interface.Interface)

    __name__ = '++extensions++'

    def __init__(self, context, request=None):
        self.context = context
        self.request = request
        self.__parent__ = context

    def traverse(self, name, ignored):
        if not name:
            return self

        ext = queryAdapter(self.context, IExtension, name)
        if ext is None:
            ext = queryMultiAdapter((self.context, self.request), IExtension, name)

        if ext is not None:
            ext.__parent__ = self
            return ext

        raise TraversalError(name)

    def publishTraverse(self, request, name):
        ext = queryAdapter(self.context, IExtension, name)
        if ext is None:
            ext = queryMultiAdapter((self.context, request), IExtension, name)

        if ext is not None:
            publisher = queryMultiAdapter((ext, self), IExtensionPublisher)
            if publisher is not None:
                return publisher
            else:
                removeSecurityProxy(ext).__parent__ = self
                return ext

        view = queryMultiAdapter((self, request), name=name)
        if view is not None:
            return view

        raise NotFound(self, request, name)

    def browserDefault(self, request):
        return self.context, ('index.html',)
