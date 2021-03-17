from .discussion import DSSObjectDiscussions

class DSSJupyterNotebook(object):
    """
    A Python/R/Scala notebook on the DSS instance
    """
    def __init__(self, client, project_key, notebook_name):
       self.client = client
       self.project_key = project_key
       self.notebook_name = notebook_name

    def unload(self, session_id=None):
        """
        Stop this Jupyter notebook and release its resources
        """
        sessions = self.get_sessions()
        if sessions is None:
            raise Exception("Notebook isn't running")
        if len(sessions) == 0:
            raise Exception("Notebook isn't running")
        if session_id is None:
            if len(sessions) > 1:
                raise Exception("Several sessions of the notebook are running, choose one")
            else:
                session_id = sessions[0].get('sessionId', None)
        return self.client._perform_json("DELETE",
                                         "/projects/%s/jupyter-notebooks/%s/sessions/%s" % (self.project_key, self.notebook_name, session_id))

    def get_sessions(self):
        """
        Get the list of running sessions of this Jupyter notebook
        """
        sessions = self.client._perform_json("GET",
                                             "/projects/%s/jupyter-notebooks/%s/sessions" % (self.project_key, self.notebook_name))
        return sessions

    def get_content(self):
        """
        Get the content of this Jupyter notebook (metadata, cells, nbformat)
        """
        raw_content = self.client._perform_json("GET", "/projects/%s/jupyter-notebooks/%s" % (self.project_key, self.notebook_name))
        return DSSNotebookContent(self.client, self.project_key, self.notebook_name, raw_content)

    def delete(self):
        """
        Delete this Jupyter notebook and stop all of its active sessions.
        """
        return self.client._perform_json("DELETE",
                                         "/projects/%s/jupyter-notebooks/%s" % (self.project_key, self.notebook_name))

    ########################################################
    # Discussions
    ########################################################
    def get_object_discussions(self):
        """
        Get a handle to manage discussions on the notebook

        :returns: the handle to manage discussions
        :rtype: :class:`dataikuapi.discussion.DSSObjectDiscussions`
        """
        return DSSObjectDiscussions(self.client, self.project_key, "JUPYTER_NOTEBOOK", self.notebook_name)

class DSSNotebookContent(object):
    """
    Content of a Jupyter Notebook. Do not create this directly, use :meth:`DSSJupyterNotebook.get_content`
    """

    """
    A Python/R/Scala notebook on the DSS instance
    """
    def __init__(self, client, project_key, notebook_name, content):
        self.client = client
        self.project_key = project_key
        self.notebook_name = notebook_name
        self.content = content

    def get_raw(self):
        """
        Get the content of this Jupyter notebook (metadata, cells, nbformat)
        :rtype: a dict containing the full content of a notebook
        """
        return self.content

    def get_metadata(self):
        """
        Get the metadata associated to this Jupyter notebook
        :rtype: dict with metadata
        """
        return self.content["metadata"]

    def get_cells(self):
        """
        Get the cells associated to this Jupyter notebook
        :rtype: list of cells
        """
        return self.content["cells"]


    def save(self):
        """
        Save the content of this Jupyter notebook
        """
        return self.client._perform_json("PUT",
                                         "/projects/%s/jupyter-notebooks/%s" % (self.project_key, self.notebook_name),
                                         body=self.content)
