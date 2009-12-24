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
""" zojax extensions tests

$Id$
"""
import os.path
import unittest, doctest
from zope import interface, component
from zope.app.testing import setup
from zope.app.component import hooks
from zope.app.testing.functional import ZCMLLayer, FunctionalDocFileSuite
from zope.annotation.attribute import AttributeAnnotations

from zojax.extensions import storage

zojaxExtensionsLayout = ZCMLLayer(
    os.path.join(os.path.split(__file__)[0], 'ftesting.zcml'),
    __name__, 'zojaxExtensionsLayout', allow_teardown=True)


def setUp(test):
    setup.placefulSetUp(True)
    component.provideAdapter(storage.Storage)
    component.provideAdapter(AttributeAnnotations)

    hooks.setHooks()
    setup.setUpTraversal()
    setup.setUpSiteManagerLookup()
    setup.setUpTestAsModule(test, 'zojax.extensions.README')


def test_suite():
    tests = FunctionalDocFileSuite(
        "testbrowser.txt",
        optionflags=doctest.ELLIPSIS|doctest.NORMALIZE_WHITESPACE)
    tests.layer = zojaxExtensionsLayout

    return unittest.TestSuite((
        tests,
        doctest.DocFileSuite(
            '../README.ru',
            setUp=setUp,
            optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS),
        doctest.DocTestSuite(
            'zojax.extensions.extensiontype',
            setUp=setUp,
            optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS),
        ))
