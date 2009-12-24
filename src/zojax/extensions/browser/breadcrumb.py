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
""" custom IBreadcrumb implementation for IConfiglet

$Id$
"""
from zope import interface, component
from zope.traversing.browser import absoluteURL
from z3c.breadcrumb.interfaces import IBreadcrumb
from z3c.breadcrumb.browser import GenericBreadcrumb

from zojax.extensions.interfaces import _, IExtension
from zojax.extensions.browser.interfaces import IExtensionsView


class ExtensionBreadcrumb(GenericBreadcrumb):
    component.adapts(IExtension, interface.Interface)

    @property
    def name(self):
        return self.context.__title__ or self.context.__name__

    @property
    def url(self):
        return '%s/'%absoluteURL(self.context, self.request)


class ExtensionsNamespaceBreadcrumb(GenericBreadcrumb):
    component.adapts(IExtensionsView, interface.Interface)

    name = _('Extensions')

    @property
    def url(self):
        return '%s/'%absoluteURL(self.context, self.request)
