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
""" Extension metaclass

$Id$
"""
import sys
from zope.schema import getFields
from zojax.extensions.extension import Extension, BrowserExtension

_marker = object()


class ExtensionType(type):
    """ Metaclass for extension class

    >>> from zope import interface, schema
    >>> from zojax.extensions import extensiontype

    >>> class IMyExtension(interface.Interface):
    ...   title = schema.TextLine(title = u'Title',
    ...                           default=u'default title')

    >>> class MyExtension(object):
    ...   pass

    >>> ExtensionClass = extensiontype.ExtensionType(
    ...    'myextension', IMyExtension, MyExtension, 'MyExtension', '')

    New class avilable by it's cname in zojax.extensions.extensiontype module

    >>> getattr(extensiontype, 'Extension<myextension>') is ExtensionClass
    True

    Automaticly generate schema fields to ExtensionProperty

    >>> ExtensionClass.title
    <zojax.extensions.extensiontype.ExtensionProperty object at ...>

    We need extension context

    >>> from zope.annotation.interfaces import IAttributeAnnotatable
    >>> class Content(object):
    ...     interface.implements(IAttributeAnnotatable)
    >>> content = Content()

    >>> extension = ExtensionClass(content)
    >>> extension
    <zojax.extensions.extensiontype.Extension<myextension> object at ...>

    >>> isinstance(extension, MyExtension)
    True

    >>> isinstance(extension, extensiontype.Extension)
    True

    Schema

    >>> extension.__schema__
    <InterfaceClass zojax.extensions.README.IMyExtension>

    Access attributes

    >>> extension.title
    u'default title'

    >>> extension.title = u'title'
    >>> extension.title
    u'title'

    We can't change extension schema

    >>> extension.__schema__ = IMyExtension
    Traceback (most recent call last):
    ...
    AttributeError: Can't set __schema__

    We also can use several of base classes and we can use 'layer'

    >>> class MyExtension2(object):
    ...   pass

    >>> class IMyLayer(interface.Interface):
    ...     pass

    >>> ExtensionClass = extensiontype.ExtensionType(
    ...    'myextension', IMyExtension,
    ...    (MyExtension, MyExtension2), 'MyExtension', '', layer=IMyLayer)

    >>> issubclass(ExtensionClass, MyExtension)
    True
    >>> issubclass(ExtensionClass, MyExtension2)
    True
    >>> issubclass(ExtensionClass, extensiontype.BrowserExtension)
    True

    Or without any base classes

    >>> ExtensionClass = extensiontype.ExtensionType(
    ...     'myextension', IMyExtension, title='MyExtension', description='')

    """

    def __new__(cls, name, schema, class_=None, *args, **kw):
        if kw.get('layer', None) is not None:
            base = BrowserExtension
            cname = 'BrowserExtension<%s>'%name
        else:
            base = Extension
            cname = 'Extension<%s>'%name

        if type(class_) is tuple:
            bases = class_ + (base,)
        elif class_ is not None:
            bases = (class_, base)
        else:
            bases = (base,)

        tp = type.__new__(cls, str(cname), bases, {'__name__': name})
        setattr(sys.modules['zojax.extensions.extensiontype'], cname, tp)

        return tp

    def __init__(cls, name, schema, class_=None,
                 title='', description='', tests=(), **kw):
        for f_id in getFields(schema):
            if not hasattr(cls, f_id):
                setattr(cls, f_id, ExtensionProperty(schema[f_id]))

        cls.__title__ = title
        cls.__description__ = description
        cls.__tests__ = tests
        cls.__schema__ = DataProperty(schema)


class DataProperty(object):

    def __init__(self, schema):
        self.schema = schema

    def __get__(self, inst, klass):
        return self.schema

    def __set__(self, inst, value):
        raise AttributeError("Can't set __schema__")


class ExtensionProperty(object):
    """ Special property thats reads and writes values from
    instance's 'data' attribute

    Let's define simple schema field

    >>> from zope import schema, interface

    >>> field = schema.TextLine(
    ...    title = u'Test',
    ...    default = u'default value')
    >>> field.__name__ = 'attr1'

    Now we need content class

    >>> from zojax.extensions.extensiontype import ExtensionProperty
    >>> class Content(object):
    ...
    ...     attr1 = ExtensionProperty(field)

    Lets create class instance and add field values storage

    >>> ob = Content()
    >>> ob.data = {}

    By default we should get field default value

    >>> ob.attr1
    u'default value'

    We can set only valid value

    >>> ob.attr1 = 'value1'
    Traceback (most recent call last):
    ...
    WrongType: ('value1', <type 'unicode'>)

    >>> ob.attr1 = u'value1'
    >>> ob.attr1
    u'value1'

    >>> del ob.attr1
    >>> ob.attr1
    u'default value'

    If storage contains field value we shuld get it

    >>> ob.data['attr1'] = u'value2'
    >>> ob.attr1
    u'value2'

    We can't set value for readonly fields

    >>> field.readonly = True
    >>> ob.attr1 = u'value1'
    Traceback (most recent call last):
    ...
    ValueError: ('attr1', 'field is readonly')

    """

    def __init__(self, field, name=None):
        if name is None:
            name = field.__name__

        self.__field = field
        self.__name = name

    def __get__(self, inst, klass):
        if inst is None:
            return self

        value = inst.data.get(self.__name, _marker)
        if value is _marker:
            return self.__field.default

        return value

    def __set__(self, inst, value):
        field = self.__field.bind(inst)

        field.validate(value)
        if field.readonly and self.__name in inst.data:
            raise ValueError(self.__name, 'field is readonly')

        inst.data[self.__name] = value

    def __delete__(self, inst):
        if self.__name in inst.data:
            del inst.data[self.__name]
