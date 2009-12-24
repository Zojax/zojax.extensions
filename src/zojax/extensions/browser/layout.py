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
from zojax.extensions.interfaces import _
from zojax.extensions.browser.interfaces import IExtensionsView


class Layout(object):

    def update(self):
        self.title = getattr(self.context, 'title', _('No title'))
        self.title = getattr(self.context, 'description', u'')

        ext = None
        context = self.maincontext
        while 1:
            if IExtensionsView.providedBy(context):
                break
            ext = context
            context = getattr(context, '__parent__', None)

        if IExtensionsView.providedBy(self.maincontext):
            self.extensionsView = True
        else:
            self.extensionsView = False

        self.extension = ext
        super(Layout, self).update()
