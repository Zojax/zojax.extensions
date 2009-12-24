==================
Content extensions
==================

Система расширений для контента.

  >>> from zope import interface, schema, component
  >>> from zope.app.component.hooks import getSite
  >>> site = getSite()

Каждый `extensions` должен иметь уникальный интерфейс. Для примера
создадим `extension` для `Portal Tabs`:

  >>> class IPortalTabs(interface.Interface):
  ...     
  ...     title = schema.TextLine(
  ...         title = u'Tab title')
  ...     
  ...     enabled = schema.Bool(
  ...         title = u'Enabled',
  ...         default = False)

  >>> class IPortalTabsAware(interface.Interface):
  ...     """ marker interface for aware objects """

  >>> tabs = {}

  >>> class PortalTabsExtension(object):
  ...     interface.implements(IPortalTabs)
  ...     
  ...     def _get_enabled(self):
  ...         return id(self) in tabs
  ...     
  ...     def _set_enabled(self, value):
  ...         key = id(self)
  ...         if value:
  ...             tabs[key] = self
  ...         elif key in tabs:
  ...             del tabs[key]
  ...             
  ...     enabled = property(_get_enabled, _set_enabled)


Теперь нужно зарегестрировать `extension`, для этого нужно
использовать `<zojax:extension />` zcml директиву.

  >>> from zope.configuration import xmlconfig
  >>> import zojax.extensions
  >>> context = xmlconfig.file('meta.zcml', zojax.extensions)

  >>> context = xmlconfig.string('''
  ... <configure xmlns:zojax="http://namespaces.zope.org/zojax" i18n_domain="test">
  ...
  ... <zojax:extension
  ...    name="portaltabs"
  ...    title="Portal tabs"
  ...    description="Portal tabs management."
  ...    for="zojax.extensions.README.IPortalTabsAware"
  ...    schema="zojax.extensions.README.IPortalTabs"
  ...    class="zojax.extensions.README.PortalTabsExtension"
  ...    type="zojax.extensions.interfaces.IPageExtension"
  ...    permission="zope.Public" />
  ...
  ... </configure>''', context)

Теперь нужно создать конент.

  >>> from zope.location import Location
  >>> from zope.annotation.interfaces import IAttributeAnnotatable
  >>> class Content(Location):
  ...     interface.implements(IAttributeAnnotatable)
  ...     def __init__(self, title):
  ...         self.title = title

  >>> content = Content('content 1')

  >>> site['content'] = content

Зарегестрированный `extension` доступен как адаптер к контенту.

  >>> IPortalTabs(content, None) is None
  True

Extension недоступен потому что мы зарегестрировали extension для
IPortalTabeAware обьектов.

  >>> interface.directlyProvides(content, IPortalTabsAware)

  >>> extension = IPortalTabs(content)
  >>> extension.title = u'My tab1'
  >>> extension.enabled = True

Также можно получить доступ к `extension`:

  >>> from zope.component import getAdapter
  >>> from zojax.extensions.interfaces import IExtension

  >>> extension = getAdapter(content, IExtension, 'portaltabs')
  >>> extension.title
  u'My tab1'

Далше мы можем использовать 'tabs' для создания табов.

  >>> tabs
  {...: <zojax.extensions.extensiontype.Extension<portaltabs> ...>}


isAvailable
-----------
Перед созданием адаптера всегда проверяется isAvailable. Есть две
возможности добавить проверку. 1) Добавить `tests` для директивы zojax:extension
2) Переопределить isAvailable метод в классе.

  >>> class IPortalTabs2(IPortalTabs):
  ...     pass

  >>> class PortalTabsExtension2(PortalTabsExtension):
  ...     pass

  >>> def isTabsAware(ext):
  ...     return IPortalTabsAware.providedBy(ext.context)

  >>> context = xmlconfig.string('''
  ... <configure xmlns:zojax="http://namespaces.zope.org/zojax" i18n_domain="test">
  ...
  ... <zojax:extension
  ...    name="portaltabs2"
  ...    title="Portal tabs"
  ...    schema="zojax.extensions.README.IPortalTabs2"
  ...    class="zojax.extensions.README.PortalTabsExtension2"
  ...    tests="zojax.extensions.README.isTabsAware"
  ...    permission="zope.Public" />
  ...
  ... </configure>''', context)

  >>> extension = IPortalTabs2(content)


Skin layer
----------

Можно зарегестрировать extension для layer

  >>> class IPortalTabs3(IPortalTabs):
  ...     pass

  >>> class PortalTabsExtension3(PortalTabsExtension):
  ...     pass

  >>> class ILayer(interface.Interface):
  ...     pass

  >>> context = xmlconfig.string('''
  ... <configure xmlns:zojax="http://namespaces.zope.org/zojax" i18n_domain="test">
  ...
  ... <zojax:extension
  ...    name="portaltabs3"
  ...    title="Portal tabs"
  ...    schema="zojax.extensions.README.IPortalTabs3"
  ...    class="zojax.extensions.README.PortalTabsExtension3"
  ...    layer="zojax.extensions.README.ILayer"
  ...    permission="zope.Public" />
  ...
  ... </configure>''', context)

  >>> extension = IPortalTabs3(content)
  Traceback (most recent call last):
  ...
  TypeError: ('Could not adapt', ...)

  >>> layer = Content('layer')
  >>> interface.directlyProvides(layer, ILayer)

Нужно всегда использовать 'extension' как имя.

  >>> extension1 = component.getMultiAdapter(
  ...     (content, layer), IPortalTabs3, 'extension')

Или

  >>> from zojax.extensions.interfaces import extensionMarker
  >>> extension2 = component.getMultiAdapter(
  ...     (content, layer, extensionMarker), IPortalTabs3)
