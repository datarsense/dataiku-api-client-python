class GovernArtifactSearchHandler(object):
    """
    Handler to perform search queries on artifacts.
    Do not create this directly, use :meth:`~dataikuapi.GovernClient.get_artifact_search_handler()`
    """

    def __init__(self, client):
        self.client = client

    def build_request(self, artifact_search_query):
        """
        Create a new artifact search request and return the object that will be used to launch the request

        :param :class:`~dataikuapi.govern.artifact_search_handler.GovernArtifactSearchQuery` artifact_search_query:
        The query that will be addressed during the search.
        :returns The created artifact search request object
        :rtype: :class:`~dataikuapi.govern.artifact_search_handler.GovernArtifactSearchRequest`
        """

        return GovernArtifactSearchRequest(self.client, artifact_search_query)


class GovernArtifactSearchRequest(object):
    """
    A search request object.
    Do not create this directly, use :meth:`~dataikuapi.govern.artifact_search_handler.build_request()` and then run the
    query using :meth:`~dataikuapi.govern.artifact_search_handler.GovernArtifactSearchRequest.perform_search()`
    """

    def __init__(self, client, artifact_search_query):
        self.client = client
        self.search_source, self.query = artifact_search_query.build()
        self.last_artifact_id = None

    def perform_search(self, page_size=20, last_artifact_id=None):
        """
        Run the search request. Use page_size and last_artifact_id to get the paginated results.

        :param int page_size: size of the result page, default value is set to 20.
        :param str last_artifact_id: id of the last artifact. Useful to get the next page of result starting from a
        specific id. If the perform_search is played more than once and that last_artifact_id is not specified, the
        results will be browsed one page after another.
        :returns The result of the search request. This dict contains a key "uiArtifacts" which is the list of the
        results list. The dict contains a key "hasNextPage"  which value is boolean. If this value is set to true, it is
        possible to navigate through the results using the parameters page_size and last_artifact_id.
        :rtype: dict
        """

        if last_artifact_id is not None:
            self.last_artifact_id = last_artifact_id

        body = {
            "searchSource": self.search_source,
            "query": self.query,
            "artifactSearchPagination": {
                "pageSize": page_size,
                "lastArtifactId": self.last_artifact_id
            }
        }

        result = self.client._perform_json("POST", "/artifacts/search", body=body)

        # update local last_artifact_id for next requests
        self.last_artifact_id = result.get("lastArtifactId")

        return result


class GovernArtifactSearchQuery(object):
    """
    A handle to interact with an artifact query. Instantiate and interact with this object to customize the query.
    """

    def __init__(self, artifact_search_source=None, artifact_filters_list=None, artifact_search_sort=None):
        """
        Create a new search query that will be used to perform the search request.

        :param :class:`~dataikuapi.govern.artifact_search_handler.GovernArtifactSearchSource` artifact_search_source:
        (Optional) The search source to restrict the artifact results. For example, use a
         :class:`~dataikuapi.govern.artifact_search_handler.GovernArtifactSearchSourceBlueprints`. to restrict results
        to artifacts that belongs to a specific blueprint,
        :class:`~dataikuapi.govern.artifact_search_handler.GovernArtifactSearchSourceBlueprintVersions`,
        :class:`~dataikuapi.govern.artifact_search_handler.GovernArtifactSearchSourceArtifacts` can also be used to
        change the search source. By default, the search will be executed on all artifacts.
        :param list of `~dataikuapi.govern.artifact_search_handler.GovernArtifactFilter` artifact_filters_list: A list
         of filters to apply on the query.
        :param `~dataikuapi.govern.artifact_search_handler.GovernArtifactSearchSort` artifact_search_sort: The sort
        configuration to apply on the query
        :return: The query object that will be passed to the search object.
        :rtype: :class:`~dataikuapi.govern.artifact_search_handler.GovernArtifactSearchRequest`
        """
        self.artifact_search_source = artifact_search_source if artifact_search_source is not None else GovernArtifactSearchSourceAll()
        self.artifact_filters_list = artifact_filters_list if artifact_filters_list is not None else []
        self.artifact_search_sort = artifact_search_sort

    def set_artifact_search_source(self, artifact_search_source):
        """
        Set a search source for this query

        :param :class:`~dataikuapi.govern.artifact_search_handler.GovernArtifactSearchSource` artifact_search_source:
        (Optional) The search source to restrict the artifact results. For example, use a
        :class:`~dataikuapi.govern.artifact_search_handler.GovernArtifactSearchSourceBlueprints`. to restrict results
        to artifacts that belongs to a specific blueprint,
        :class:`~dataikuapi.govern.artifact_search_handler.GovernArtifactSearchSourceBlueprintVersions`,
        :class:`~dataikuapi.govern.artifact_search_handler.GovernArtifactSearchSourceArtifacts` can also be used to
        change the search source. By default, the search will be executed on all artifacts.
        :return: None
        """
        self.artifact_search_source = artifact_search_source

    def clear_artifact_filters(self):
        """
        Remove the filters set for this query

        :return: None
        """
        self.artifact_filters_list = []

    def add_artifact_filter(self, artifact_filter):
        """
        Add a new artifact filter to the filter list of the query.

        :param `~dataikuapi.govern.artifact_search_handler.GovernArtifactFilter` artifact_filter: A filter to add to the
        filter list.
        :return: None
        """
        self.artifact_filters_list.append(artifact_filter)

    def clear_artifact_search_sort(self):
        """
        Remove the sort configuration of this query.

        :return: None
        """
        self.artifact_search_sort = None

    def set_artifact_search_sort(self, artifact_search_sort):
        """
        Set a new search sort configuration for this request.

        :param `~dataikuapi.govern.artifact_search_handler.GovernArtifactSearchSort` artifact_search_sort: The sort
        configuration to apply on the query
        :return: None
        """
        self.artifact_search_sort = artifact_search_sort

    def build(self):
        query = {"artifactFilters": [artifact_filter.build() for artifact_filter in self.artifact_filters_list]}
        if self.artifact_search_sort is not None:
            query["artifactSearchSort"] = self.artifact_search_sort.build()
        return self.artifact_search_source.build(), query


########################################################
# Search Source
########################################################

class GovernArtifactSearchSource(object):
    """
    An abstract class to embrace the different search source. Do not instantiate this class but its subclasses.
    """

    def __init__(self, search_source_type):
        self.search_source_type = search_source_type

    def build(self):
        raise NotImplementedError("Cannot build an abstract artifact search source")


class GovernArtifactSearchSourceAll(GovernArtifactSearchSource):
    """
    A handle which represent the generic search source.
    """

    def __init__(self):
        super().__init__(search_source_type="all")

    def build(self):
        return {"type": "all"}


class GovernArtifactSearchSourceBlueprints(GovernArtifactSearchSource):
    """
    A handle which represent the blueprints search source. Use this search source to restrict the artifact search to
    some specific blueprints.
    """

    def __init__(self, blueprint_ids=None):
        """
        :param list of str blueprint_ids: (Optional) the list of blueprint ids of which the artifact search will be
        performed.
        """
        super().__init__(search_source_type="blueprints")
        self.blueprint_ids = blueprint_ids if blueprint_ids is not None else []

    def build(self):
        return {"type": self.search_source_type, "blueprintIds": self.blueprint_ids}


class GovernArtifactSearchSourceBlueprintVersions(GovernArtifactSearchSource):
    """
    A handle which represent the artifact search source. Use this search source to restrict the artifact search to
    some specific blueprint versions.
    """

    def __init__(self, blueprint_version_ids=None):
        """
        :param list of dict blueprint_version_ids: (Optional) the list of blueprint ids of which the artifact search will
        be performed. Use :meth:`~dataikuapi.govern.artifact_search_handler.GovernBlueprintVersionIdBuilder.build()` to
        create blueprint version ids from blueprint ids and versions ids.
        """
        super().__init__(search_source_type="blueprintVersions")
        self.blueprint_version_ids = blueprint_version_ids if blueprint_version_ids is not None else []

    def build(self):
        return {"type": self.search_source_type, "blueprintVersionIds": self.blueprint_version_ids}


class GovernArtifactSearchSourceArtifacts(GovernArtifactSearchSource):
    """
    A handle which represent the artifact search source. Use this search source restrict the artifact search to
    some specific artifact.
    """

    def __init__(self, artifact_ids=None):
        """
        :param list of str artifact_ids: (Optional) the list of artifacts ids on which the request will be restricted.
        """
        super().__init__(search_source_type="artifacts")
        self.artifact_ids = artifact_ids if artifact_ids is not None else []

    def build(self):
        return {"type": self.search_source_type, "artifactIds": self.artifact_ids}


########################################################
# Search Sort
########################################################


class GovernArtifactSearchSort(object):
    """
    An abstract class to embrace the different search sort. Do not instantiate this class but its subclasses.
    """

    def __init__(self, artifact_search_sort_type, direction):
        self.artifact_search_sort_type = artifact_search_sort_type
        self.direction = direction

    def build(self):
        raise NotImplementedError("Cannot build an abstract artifact search sort")


class GovernArtifactSearchSortName(GovernArtifactSearchSort):
    """
    A handle which to sort artifacts based on their names.
    """

    def __init__(self, direction="ASC"):
        """
        :param str direction: (Optional) The direction on which the artifacts will be sorted. Can be either "ASC" or
        "DESC"
        """
        super().__init__(artifact_search_sort_type="name", direction=direction)

    def build(self):
        return {"direction": self.direction, "column": {"type": self.artifact_search_sort_type}}


class GovernArtifactSearchSortWorkflow(GovernArtifactSearchSort):
    """
    A handle which to sort artifacts based on their workflow.
    """

    def __init__(self, direction="ASC"):
        """
        :param str direction: (Optional) The direction on which the artifacts will be sorted. Can be either "ASC" or
        "DESC"
        """
        super().__init__(artifact_search_sort_type="workflow", direction=direction)

    def build(self):
        return {"direction": self.direction, "column": {"type": self.artifact_search_sort_type}}


class GovernArtifactSearchSortField(GovernArtifactSearchSort):
    """
    A handle which to sort artifacts based on a list of fields.
    """

    def __init__(self, fields=None, direction="ASC"):
        """
        field of dict {bpid, fielid}

        :param list of dicts fields: (Optional) A list of fields on which the artifacts will be sorted. Use
        :meth:`~dataikuapi.govern.artifact_search_handler.GovernSearchSortFieldBuilder.build()` to create fields based
        on the blueprint id and the field id.
        :param str direction: (Optional) The direction on which the artifacts will be sorted. Can be either "ASC" or
        "DESC"
        """
        super().__init__(artifact_search_sort_type="field", direction=direction)
        self.fields = fields if fields is not None else []

    def build(self):
        return {"direction": self.direction, "column": {"type": self.artifact_search_sort_type, "fields": self.fields}}


########################################################
# Search Filters
########################################################


class GovernArtifactFilter(object):
    """
    An abstract class to represent artifact filters.
    """

    def __init__(self, filter_type):
        self.filter_type = filter_type

    def build(self):
        raise NotImplementedError("Cannot build an abstract artifact filter")


class GovernFieldValueArtifactFilter(GovernArtifactFilter):
    """
    A handle to apply filters on specific fields on a search request.
    """

    def __init__(self, condition_type, condition=None, field_id=None, negate_condition=None, case_sensitive=None):
        """
        :param str condition_type: the condition type of the filter. Has to be chosen from EQUALS, CONTAINS, START_WITH,
        END_WITH.
        :param str condition: (Optional) The value on which the condition will be applied.
        :param str field_id: (Optional) The id of the field on which the condition will be applied. If not specified the
        filter will apply on the name.
        :param boolean negate_condition: (Optional) A boolean to negate the condition. By default, the condition is not
        negated.
        :param str case_sensitive: (Optional) Can be used to activate case-sensitive filtering. By default, filters will
        not be case-sensitive.
        :returns The created filter that will be useful to perform the search.
        """
        super().__init__(filter_type="field")
        self.condition_type = condition_type
        self.condition = condition
        self.field_id = field_id
        self.negate_condition = negate_condition
        self.case_sensitive = case_sensitive

    def build(self):
        field_filter = {"type": self.filter_type, "conditionType": self.condition_type}
        if self.condition is not None:
            field_filter["condition"] = self.condition
        if self.field_id is not None:
            field_filter["fieldId"] = self.field_id
        if self.negate_condition is not None:
            field_filter["negateCondition"] = self.negate_condition
        if self.case_sensitive is not None:
            field_filter["caseSensitive"] = self.case_sensitive
        return field_filter


class GovernArchivedStatusArtifactFilter(GovernArtifactFilter):
    """
    A handle to apply filters on the archived status of artifacts.
    """

    def __init__(self, is_archived):
        """
        :param boolean is_archived: the value for filtering. If is_archived is set to True, all artifacts including
        archived ones will be part of the search result
        """
        super().__init__(filter_type="archived")
        self.is_archived = is_archived

    def build(self):
        return {"type": self.filter_type, "isArchived": self.is_archived}


########################################################
# Builders
########################################################

class GovernBlueprintVersionIdBuilder(object):
    def __init__(self, blueprint_id, version_id):
        self.blueprint_id = blueprint_id
        self.version_id = version_id

    def build(self):
        return {"blueprintId": self.blueprint_id, "versionId": self.version_id}


class GovernSearchSortFieldBuilder(object):
    def __init__(self, blueprint_id, field_id):
        self.blueprint_id = blueprint_id
        self.field_id = field_id

    def build(self):
        return {"blueprintId": self.blueprint_id, "fieldId": self.field_id}