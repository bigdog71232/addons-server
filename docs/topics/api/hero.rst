============
Hero Shelves
============

.. note::

    These APIs are not frozen and can change at any time without warning.
    See :ref:`the API versions available<api-versions-list>` for alternatives
    if you need stability.


---------------------
Combined Hero Shelves
---------------------

.. _hero-shelves:

This convienence endpoint serves a single, randomly selected, primary hero shelf,
and a single, randomly selected secondary hero shelf.


.. http:get:: /api/v4/hero/

    :query string lang: Activate translations in the specific language for that query. (See :ref:`translated fields <api-overview-translations>`)
    :>json object primary: A :ref:`primary hero shelf <primary-hero-shelf>`.
    :>json object secondary: A :ref:`secondary hero shelf <secondary-hero-shelf>`.


--------------------
Primary Hero Shelves
--------------------

.. _primary-hero-shelf:

This endpoint returns all enabled primary hero shelves.  As there will only ever be a
small number of shelves this endpoint is not paginated.


.. http:get:: /api/v4/hero/primary/

    :query string lang: Activate translations in the specific language for that query. (See :ref:`translated fields <api-overview-translations>`)
    :query boolean all: return all shelves - both enabled and disabled.  To be used internally to generate .po files containing the strings defined by the content team.
    :>json array results: The array containing the results for this query.
    :>json object results[].gradient: The background colors used for the gradient.
    :>json string results[].gradient.start: The starting color for gradient - typically top or left.
    :>json string results[].gradient.end: The ending color for gradient - typically bottom or right.
    :>json string results[].featured_image: The image used to illustrate the item.
    :>json string|null results[].description: The description for this item, if any. May contain some HTML tags.
    :>json object results[].addon: The :ref:`add-on <addon-detail-object>` for this item if the addon is hosted on AMO. Either this field or ``external`` will be present.  Only a subset of fields are present: ``id``, ``authors``, ``average_daily_users``, ``current_version`` (with only the ``id``, ``compatibility``, ``is_strict_compatibility_enabled`` and ``files`` fields present), ``guid``, ``icon_url``, ``name``, ``ratings``, ``previews``, ``slug``, ``theme_data``, ``type`` and ``url``.
    :>json object results[].external: The :ref:`add-on <addon-detail-object>` for this item if the addon is externally hosted. Either this field or ``addon`` will be present.  Only a subset of fields are present: ``id``, ``guid``, ``homepage``, ``name`` and ``type``.


----------------------
Secondary Hero Shelves
----------------------

.. _secondary-hero-shelf:

This endpoint returns all enabled secondary hero shelves.  As there will only ever be a
small number of shelves - and likely only one - this endpoint is not paginated.


.. http:get:: /api/v4/hero/secondary/

    :query string lang: Activate translations in the specific language for that query. (See :ref:`translated fields <api-overview-translations>`)
    :query boolean all: return all shelves - both enabled and disabled.  To be used internally to generate .po files containing the strings defined by the content team.
    :>json array results: The array containing the results for this query.
    :>json string results[].headline: The headline for this item.
    :>json string results[].description: The description for this item.
    :>json object|null cta: The optional call to action link and text to be displayed with the item.
    :>json string cta.url: The url the call to action would link to.
    :>json string cta.text: The call to action text.
    :>json array modules: The modules for this shelf.  Should always be 3.
    :>json string modules[].icon: The icon used to illustrate the item.
    :>json string modules[].description: The description for this item.
    :>json object|null modules[].cta: The optional call to action link and text to be displayed with the item.
    :>json string modules[].cta.url: The url the call to action would link to.
    :>json string modules[].cta.text: The call to action text.
