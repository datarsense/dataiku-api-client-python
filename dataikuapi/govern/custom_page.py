class GovernCustomPage(object):
    """
    A non-admin handle to interact with a custom page
    Do not create this directly, use :meth:`~dataikuapi.GovernClient.get_custom_page()`
    """

    def __init__(self, client, custom_page_id):
        self.client = client
        self.custom_page_id = custom_page_id

    def get_definition(self):
        """
        Get the definition of the custom page.

        :return: the corresponding custom page definition  object
        :rtype: a :class:`dataikuapi.govern.custom_page.GovernCustomPageDefinition`
        """
        result = self._perform_json("GET", '/custom-page/%s' % self.custom_page_id)

        return GovernCustomPageDefinition(self.client, self.custom_page_id, result)


class GovernCustomPageDefinition(object):
    """
    A non-admin handle to interact with a custom page definition
    Do not create this directly, use :meth:`~dataikuapi.govern.custom_page.GovernCustomPage.get_definition()`
    """

    def __init__(self, client, custom_page_id, definition):
        self.client = client
        self.custom_page_id = custom_page_id
        self.definition = definition

    def get_raw(self):
        """
        Gets the raw content of the custom page.

        :rtype: dict
        """
        return self.definition