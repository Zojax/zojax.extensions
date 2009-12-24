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
""" Use configlet as content container

$Id$
"""
from zope import interface, component, event
from zope.proxy import removeAllProxies
from zope.proxy import ProxyBase, getProxiedObject, non_overridable
from zope.proxy.decorator import DecoratorSpecificationDescriptor
from zope.security.decorator import DecoratedSecurityCheckerDescriptor
from zope.location.interfaces import ILocation
from zope.location.location import ClassAndInstanceDescr
from zope.app.container.btree import BTreeContainer
from zope.app.container.sample import SampleContainer
from zope.app.container.contained import uncontained
from zope.annotation.interfaces import IAttributeAnnotatable
from zope.app.catalog.interfaces import INoAutoReindex

from zojax.content.type.order import Reordable
from zojax.content.type.interfaces import IOrder, IItem, IContentContainer

from extension import Extension
from interfaces import IExtensionDataFactory


class ContentContainerExtension(SampleContainer, Extension):
    interface.implements(IItem, IContentContainer, INoAutoReindex)

    def __init__(self, tests=()):
        Extension.__init__(self, tests)

    @property
    def title(self):
        return self.__title__

    @property
    def description(self):
        return self.__description__

    @property
    def _SampleContainer__data(self):
        return self.data

    def get(self, key, default=None):
        item = super(ContentContainerExtension, self).get(key, default)

        if item is default:
            return item

        return ItemLocationProxy(removeAllProxies(item), self)

    def __iter__(self):
        return iter(self.data)

    def __getitem__(self, key):
        item = super(ContentContainerExtension, self).__getitem__(key)

        return ItemLocationProxy(removeAllProxies(item), self)

    def __delitem__(self, key):
        uncontained(self[key], self, key)
        del self.data[key]


class ConfigletContainerOrder(Reordable):
    @component.adapter(ContentContainerExtension)

    def __init__(self, context):
        context = removeAllProxies(context)
        super(ConfigletContainerOrder, self).__init__(context.data)

        self.context = context


class ExtensionData(BTreeContainer):
    interface.implements(IAttributeAnnotatable)


class ExtensionDataFactory(object):
    component.adapts(ContentContainerExtension)
    interface.implements(IExtensionDataFactory)

    def __init__(self, ext):
        self.extension = ext

    def __call__(self):
        data = ExtensionData()
        data.__parent__ = removeAllProxies(self.extension.context)
        return data


class ItemLocationProxy(ProxyBase):
    interface.implements(ILocation)

    __slots__ = '__parent__'
    __safe_for_unpickling__ = True

    def __new__(self, ob, container=None):
        return ProxyBase.__new__(self, ob)

    def __init__(self, ob, container=None):
        ProxyBase.__init__(self, ob)
        self.__parent__ = container

    @non_overridable
    def __reduce__(self, proto=None):
        raise TypeError("Not picklable")

    __doc__ = ClassAndInstanceDescr(
        lambda inst: getProxiedObject(inst).__doc__,
        lambda cls, __doc__ = __doc__: __doc__,
        )

    __reduce_ex__ = __reduce__
    __providedBy__ = DecoratorSpecificationDescriptor()
    __Security_checker__ = DecoratedSecurityCheckerDescriptor()
