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
""" zojax:extension directive

$Id$
"""
from zope import interface
from zope.schema import getFields, TextLine, Bool
from zope.interface.common.mapping import IEnumerableMapping

from zope.component import getUtility
from zope.component.zcml import adapter
from zope.component.interface import provideInterface

from zope.schema.interfaces import IField

from zope.security import checkPermission
from zope.security.zcml import Permission
from zope.security.checker import Checker, CheckerPublic, ProxyFactory

from zope.configuration import fields
from zope.configuration.exceptions import ConfigurationError

from zope.app.security.protectclass import protectName, protectSetAttribute

from extensiontype import ExtensionType
from extension import Extension, BrowserExtension
from interfaces import IExtensionsDataStorage, ExtensionMarker
from interfaces import IExtension, IBrowserExtension, IDefaultExtensionType


class IExtensionDirective(interface.Interface):

    for_ = fields.GlobalInterface(
        title = u'Specifications to be adapted',
        description = u'This should be a interface or classe',
        required = False)

    name = TextLine(
        title = u'Name',
        description = u'Name of the extension used to access the settings.',
        required = True)

    schema = fields.GlobalInterface(
        title = u'Extension schema',
        description = u'This attribute specifies the schema of the extension',
        required = True)

    title = fields.MessageID(
        title = u'Title',
        description = u'Title of the extension for UIs.',
        required = True)

    description = fields.MessageID(
        title = u'Description',
        description = u'Description of the extension for UIs.',
        default = u'',
        required = False)

    class_ = fields.GlobalObject(
        title = u'Class',
        description = u'Custom extension class',
        required = False)

    layer = fields.GlobalObject(
        title = u'The layer the extension should be found in',
        required=False)

    permission = Permission(
        title = u'Permission',
        description = u'Default access permission.',
        required = False)

    tests = fields.Tokens(
        title = u'Tests',
        description = u'Extension availability tests.',
        value_type = fields.GlobalObject(),
        required = False)

    type = fields.GlobalInterface(
        title = u'Type',
        description = u'Extention type.',
        required = False)


class ExtensionDirective(object):

    def __init__(self, _context, name, schema, title,
                 for_ = interface.Interface,
                 description = u'', class_=None, layer = None,
                 permission = 'zojax.ManageExtension',
                 tests=(), type=IDefaultExtensionType):

        for test in tests:
            if not callable(test):
                raise ConfigurationError('Test should be callable.')

        # permission checker
        if permission == 'zope.Public':
            tests = tuple(tests)
        else:
            tests = (PermissionChecker(permission),) + tuple(tests)

        # generate class
        ExtensionClass = ExtensionType(
            name, schema, class_,
            title, description, tests=tests, layer=layer)

        interface.classImplements(ExtensionClass, schema)

        # register adater
        if layer:
            factory = ExtensionClass
            adapter(_context, (factory,), IExtension,
                    (for_, layer), name=name)
            adapter(_context, (factory,), schema,
                    (for_, layer), name='extension')
            adapter(_context, (Wrapper(factory),),
                    schema, (for_, layer, ExtensionMarker))
        else:
            factory = ExtensionClass
            adapter(_context, (factory,), schema, (for_,))
            adapter(_context, (factory,), IExtension, (for_,), name=name)

        # extension type
        if type is not None:
            interface.classImplements(ExtensionClass, type)

        # save data for subdirectives
        self._class = ExtensionClass
        self._context = _context
        self._permission = permission

        # set default security rules
        self.require(_context, permission,
                     interface=(schema,), set_schema=(schema,))

        # allow access to IExtension interface
        if layer:
            self.require(_context, CheckerPublic, interface=(IBrowserExtension,))
        else:
            self.require(_context, CheckerPublic, interface=(IExtension,))

    def require(self, _context,
                permission=None, attributes=None, interface=None,
                like_class=None, set_attributes=None, set_schema=None):
        """Require a permission to access a specific aspect"""
        if not (interface or attributes or set_attributes or set_schema):
            raise ConfigurationError("Nothing required")

        if not permission:
            raise ConfigurationError("No permission specified")

        if interface:
            for i in interface:
                if i:
                    self.__protectByInterface(i, permission)

        if attributes:
            self.__protectNames(attributes, permission)

        if set_attributes:
            self.__protectSetAttributes(set_attributes, permission)

        if set_schema:
            for s in set_schema:
                self.__protectSetSchema(s, permission)

    def allow(self, _context, attributes=None, interface=None):
        """Like require, but with permission_id zope.Public"""
        return self.require(_context, CheckerPublic, attributes, interface)

    def __protectByInterface(self, interface, permission_id):
        "Set a permission on names in an interface."
        for n, d in interface.namesAndDescriptions(1):
            self.__protectName(n, permission_id)

        self._context.action(
            discriminator = None,
            callable = provideInterface,
            args = (interface.__module__+'.'+interface.getName(), interface))

    def __protectName(self, name, permission_id):
        "Set a permission on a particular name."
        self._context.action(
            discriminator = ('zojax:extensions:protectName',
                             self._class, name, object()),
            callable = protectName,
            args = (self._class, name, permission_id))

    def __protectNames(self, names, permission_id):
        "Set a permission on a bunch of names."
        for name in names:
            self.__protectName(name, permission_id)

    def __protectSetAttributes(self, names, permission_id):
        "Set a permission on a bunch of names."
        for name in names:
            self._context.action(
                discriminator = ('zojax:extensions:protectSetAttribute',
                                 self._class, name, object()),
                callable = protectSetAttribute,
                args = (self._class, name, permission_id))

    def __protectSetSchema(self, schema, permission_id):
        "Set a permission on a bunch of names."
        _context = self._context

        for name in schema:
            field = schema[name]
            if IField.providedBy(field) and not field.readonly:
                _context.action(
                    discriminator = ('zojax:extensions:protectSetAttribute',
                                     self._class, name, object()),
                    callable = protectSetAttribute,
                    args = (self._class, name, permission_id))

        _context.action(
            discriminator = None,
            callable = provideInterface,
            args = (schema.__module__+'.'+schema.getName(), schema))


class PermissionChecker(object):

    def __init__(self, permission):
        self.permission = permission

    def __call__(self, extension):
        return checkPermission(self.permission, extension)


class Wrapper(object):

    def __init__(self, klass):
        self.klass = klass

    def __call__(self, context, request, marker):
        return self.klass(context, request)
