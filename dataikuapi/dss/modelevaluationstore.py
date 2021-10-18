import json
from io import BytesIO

from dataikuapi.dss.metrics import ComputedMetrics
from .discussion import DSSObjectDiscussions
from .future import DSSFuture

try:
    basestring
except NameError:
    basestring = str


class DSSModelEvaluationStore(object):
    """
    A handle to interact with a model evaluation store on the DSS instance.

    Do not create this directly, use :meth:`dataikuapi.dss.DSSProject.get_model_evaluation_store`
    """
    def __init__(self, client, project_key, mes_id):
        self.client = client
        self.project = client.get_project(project_key)
        self.project_key = project_key
        self.mes_id = mes_id

    @property
    def id(self):
        return self.mes_id

    def get_settings(self):
        """
        Returns the settings of this model evaluation store.

        :rtype: DSSModelEvaluationStoreSettings
        """
        data = self.client._perform_json(
            "GET", "/projects/%s/modelevaluationstores/%s" % (self.project_key, self.mes_id))
        return DSSModelEvaluationStoreSettings(self, data)


    ########################################################
    # Misc
    ########################################################

    def get_zone(self):
        """
        Gets the flow zone of this model evaluation store

        :rtype: :class:`dataikuapi.dss.flow.DSSFlowZone`
        """
        return self.project.get_flow().get_zone_of_object(self)

    def move_to_zone(self, zone):
        """
        Moves this object to a flow zone

        :param object zone: a :class:`dataikuapi.dss.flow.DSSFlowZone` where to move the object
        """
        if isinstance(zone, basestring):
           zone = self.project.get_flow().get_zone(zone)
        zone.add_item(self)

    def share_to_zone(self, zone):
        """
        Share this object to a flow zone

        :param object zone: a :class:`dataikuapi.dss.flow.DSSFlowZone` where to share the object
        """
        if isinstance(zone, basestring):
            zone = self.project.get_flow().get_zone(zone)
        zone.add_shared(self)

    def unshare_from_zone(self, zone):
        """
        Unshare this object from a flow zone

        :param object zone: a :class:`dataikuapi.dss.flow.DSSFlowZone` from where to unshare the object
        """
        if isinstance(zone, basestring):
            zone = self.project.get_flow().get_zone(zone)
        zone.remove_shared(self)

    def get_usages(self):
        """
        Get the recipes referencing this model evaluation store

        Returns:
            a list of usages
        """
        return self.client._perform_json("GET", "/projects/%s/modelevaluationstores/%s/usages" % (self.project_key, self.mes_id))

    def get_object_discussions(self):
        """
        Get a handle to manage discussions on the model evaluation store

        :returns: the handle to manage discussions
        :rtype: :class:`dataikuapi.discussion.DSSObjectDiscussions`
        """
        return DSSObjectDiscussions(self.client, self.project_key, "MODEL_EVALUATION_STORE", self.mes_id)

    ########################################################
    # Deletion
    ########################################################

    def delete(self):
        """
        Delete the model evaluation store

        """
        return self.client._perform_empty("DELETE", "/projects/%s/modelevaluationstores/%s" % (self.project_key, self.mes_id))


    ########################################################
    # Model evaluations
    ########################################################

    def list_model_evaluations(self):
        """
        List the model evaluations in this model evaluation store. The list is sorted
        by ME creation date.

        :returns: The list of the model evaluations
        :rtype: list of :class:`dataikuapi.dss.modelevaluationstore.DSSModelEvaluation`
        """
        items = self.client._perform_json("GET", "/projects/%s/modelevaluationstores/%s/evaluations/" % (self.project_key, self.mes_id))
        return [DSSModelEvaluation(self, item["ref"]["evaluationId"]) for item in items]

    def get_model_evaluation(self, evaluation_id):
        """
        Get a handle to interact with a specific model evaluation
       
        :param string evaluation_id: the id of the desired model evaluation
        
        :returns: A :class:`dataikuapi.dss.modelevaluationstore.DSSModelEvaluation` model evaluation handle
        """
        return DSSModelEvaluation(self, evaluation_id)

    def get_latest_model_evaluation(self):
        """
        Get a handle to interact with the latest model evaluation computed


        :returns: A :class:`dataikuapi.dss.modelevaluationstore.DSSModelEvaluation` model evaluation handle
            if the store is not empty, else None
        """

        latest_evaluation_id = self.client._perform_text(
            "GET", "/projects/%s/modelevaluationstores/%s/latestEvaluationId" % (self.project_key, self.mes_id))
        if not latest_evaluation_id:
            return None
        return DSSModelEvaluation(self, latest_evaluation_id)

    def delete_model_evaluations(self, evaluations):
        """
        Remove model evaluations from this store
        """
        obj = []
        for evaluation in evaluations:
            if isinstance(evaluation, DSSModelEvaluation):
                obj.append(evaluation.evaluation_id)
            elif isinstance(evaluation, dict):
                obj.append(evaluation['evaluation_id'])
            else:
                obj.append(evaluation)
        self.client._perform_json(
                "DELETE", "/projects/%s/modelevaluationstores/%s/evaluations/" % (self.project_key, self.mes_id), body=obj)

    def build(self, job_type="NON_RECURSIVE_FORCED_BUILD", wait=True, no_fail=False):
        """
        Starts a new job to build this model evaluation store and wait for it to complete.
        Raises if the job failed.

        .. code-block:: python

            job = mes.build()
            print("Job %s done" % job.id)

        :param job_type: The job type. One of RECURSIVE_BUILD, NON_RECURSIVE_FORCED_BUILD or RECURSIVE_FORCED_BUILD
        :param wait: wait for the build to finish before returning
        :param no_fail: if True, does not raise if the job failed. Valid only when wait is True
        :return: the :class:`dataikuapi.dss.job.DSSJob` job handle corresponding to the built job
        :rtype: :class:`dataikuapi.dss.job.DSSJob`
        """
        jd = self.project.new_job(job_type)
        jd.with_output(self.mes_id, object_type="MODEL_EVALUATION_STORE")
        if wait:
            return jd.start_and_wait(no_fail)
        else:
            return jd.start(allowFail=not no_fail)


    ########################################################
    # Metrics
    ########################################################

    def get_last_metric_values(self):
        """
        Get the metrics of the latest model evaluation built

        Returns:
            a list of metric objects and their value
        """
        return ComputedMetrics(self.client._perform_json(
            "GET", "/projects/%s/modelevaluationstores/%s/metrics/last" % (self.project_key, self.mes_id)))

    def get_metric_history(self, metric):
        """
        Get the history of the values of the metric on this model evaluation store

        Returns:
            an object containing the values of the metric, cast to the appropriate type (double, boolean,...)
        """
        return self.client._perform_json(
            "GET", "/projects/%s/modelevaluationstores/%s/metrics/history" % (self.project_key, self.mes_id),
            params={'metricLookup': metric if isinstance(metric, str)or isinstance(metric, unicode)
                                           else json.dumps(metric)})

    def compute_metrics(self, metric_ids=None, probes=None):
        """
        Compute metrics on this model evaluation store. If the metrics are not specified, the metrics
        setup on the model evaluation store are used.
        """
        url = "/projects/%s/modelevaluationstores/%s/actions" % (self.project_key, self.mes_id)
        if metric_ids is not None:
            return self.client._perform_json(
                "POST" , "%s/computeMetricsFromIds" % url,
                body={"metricIds" : metric_ids})
        elif probes is not None:
            return self.client._perform_json(
                "POST" , "%s/computeMetrics" % url,
                body=probes)
        else:
            return self.client._perform_json(
                "POST" , "%s/computeMetrics" % url)


class DSSModelEvaluationStoreSettings:
    """
    A handle on the settings of a model evaluation store

    Do not create this class directly, instead use :meth:`dataikuapi.dss.DSSModelEvaluationStore.get_settings`
    """

    def __init__(self, model_evaluation_store, settings):
        self.model_evaluation_store = model_evaluation_store
        self.settings = settings

    def get_raw(self):
        return self.settings

    def save(self):
        self.model_evaluation_store.client._perform_empty(
                "PUT", "/projects/%s/modelevaluationstores/%s" % (self.model_evaluation_store.project_key, self.model_evaluation_store.mes_id),
                body=self.settings)


class DSSModelEvaluation:
    """
    A handle on a model evaluation

    Do not create this class directly, instead use :meth:`dataikuapi.dss.DSSModelEvaluationStore.get_model_evaluation`
    """

    def __init__(self, model_evaluation_store, evaluation_id):
        self.model_evaluation_store = model_evaluation_store
        self.client = model_evaluation_store.client
        # unpack some fields
        self.evaluation_id = evaluation_id
        self.project_key = model_evaluation_store.project_key
        self.mes_id = model_evaluation_store.mes_id

    def get_full_info(self):
        """
        Retrieve the model evaluation with its performance data

        :return: the model evaluation full info, as a :class:`dataikuapi.dss.DSSModelEvaluationInfo`
        """
        data = self.client._perform_json(
            "GET", "/projects/%s/modelevaluationstores/%s/evaluations/%s" % (self.project_key, self.mes_id, self.evaluation_id))
        return DSSModelEvaluationFullInfo(self, data)

    def get_full_id(self):
        return "ME-{}-{}-{}".format(self.project_key, self.mes_id, self.evaluation_id)

    def delete(self):
        """
        Remove this model evaluation
        """
        obj = [self.evaluation_id]
        self.client._perform_json(
                "DELETE", "/projects/%s/modelevaluationstores/%s/evaluations/" % (self.project_key, self.mes_id), body=obj)

    @property
    def full_id(self):
        return "ME-%s-%s-%s"%(self.project_key, self.mes_id, self.evaluation_id)

    def compute_data_drift(self, reference=None, data_drift_params=None, wait=True):
        """
        Compute data drift against a reference model or model evaluation. The reference is determined automatically unless specified.

        :param reference: saved model version (full ID or DSSTrainedPredictionModelDetails)
                or model evaluation (full ID or DSSModelEvaluation) to use as reference (optional)
        :type reference: Union[str, DSSModelEvaluation, DSSTrainedPredictionModelDetails]
        :param data_drift_params: data drift computation settings as a :class:`dataikuapi.dss.modelevaluationstore.DataDriftParams` (optional)
        :type data_drift_params: DataDriftParams
        :param wait: data drift computation settings (optional)
        :returns: a :class:`dataikuapi.dss.modelevaluationstore.DataDriftResult` containing data drift analysis results if `wait` is `True`, or a :class:`~dataikuapi.dss.future.DSSFuture` handle otherwise
        """

        if hasattr(reference, 'full_id'):
            reference = reference.full_id

        if data_drift_params:
            data_drift_params = data_drift_params.data

        future_response = self.client._perform_json(
            "POST", "/projects/%s/modelevaluationstores/%s/evaluations/%s/computeDataDrift" % (self.project_key, self.mes_id, self.evaluation_id),
            body={
                "referenceId": reference,
                "dataDriftParams": data_drift_params
            })
        future = DSSFuture(self.client, future_response.get('jobId', None), future_response, result_wrapper=DataDriftResult)
        return future.wait_for_result() if wait else future

    def get_metrics(self):
        """
        Get the metrics for this model evaluation. Metrics must be understood here as Metrics in DSS Metrics & Checks

        :return: the metrics, as a JSON object
        """
        return self.client._perform_json(
            "GET", "/projects/%s/modelevaluationstores/%s/evaluations/%s/metrics" % (self.project_key, self.mes_id, self.evaluation_id))

    def get_sample_df(self):
        """
        Get the sample of the evaluation dataset on which the evaluation was performed

        :return:
            the sample content, as a :class:`pandas.DataFrame`
        """
        buf = BytesIO()
        with self.client._perform_raw(
                "GET",
                "/projects/%s/modelevaluationstores/%s/evaluations/%s/sample" % (self.project_key, self.mes_id, self.evaluation_id)
        ).raw as f:
            buf.write(f.read())
        schema_txt = self.client._perform_raw(
            "GET",
            "/projects/%s/modelevaluationstores/%s/evaluations/%s/schema" % (self.project_key, self.mes_id, self.evaluation_id)
        ).text
        schema = json.loads(schema_txt)
        import pandas as pd
        return pd.read_csv(BytesIO(buf.getvalue()), compression='gzip', sep='\t', header=None, names=[c["name"] for c in schema["columns"]])


class DSSModelEvaluationFullInfo:
    """
    A handle on the full information on a model evaluation.

    Includes information such as the full id of the evaluated model, the evaluation params,
    the performance and drift metrics, if any, etc.

    Do not create this class directly, instead use :meth:`dataikuapi.dss.DSSModelEvaluation.get_full_info`
    """
    def __init__(self, model_evaluation, full_info):
        self.model_evaluation = model_evaluation
        self.full_info = full_info
        self.metrics = self.full_info["metrics"]  # type: dict
        """The performance and data drift metric, if any."""
        self.evaluation_parameters = self.full_info["evaluation"]["metricParams"]  # type: dict
        """Information on the evaluation parameters, most noticeably the evaluation metric (evaluationMetric field of the returned dict)."""
        self.creation_date = self.full_info["evaluation"]["created"]  # type: int
        """The date and time of the creation of the model evaluation, as an epoch."""
        self.full_id = self.full_info["evaluation"]["ref"]["fullId"]  # type: str
        self.model_full_id = self.full_info["evaluation"]["modelRef"]["fullId"]  # type: str
        self.model_type = self.full_info["evaluation"]["modelType"]  # type: str
        self.model_parameters = self.full_info["evaluation"]["modelParams"]
        self.prediction_type = self.full_info["evaluation"]["predictionType"]  # type: str
        self.prediction_variable = self.full_info["evaluation"]["predictionVariable"]  # type: str
        self.target_variable = self.full_info["evaluation"]["targetVariable"]  # type: str
        self.user_meta = self.full_info["evaluation"]["userMeta"]  # type: dict
        """The user-accessible metadata (name, labels)
        Returns the original object, not a copy. Changes to the returned object are persisted to DSS by calling :meth:`save_user_meta`."""

    def get_raw(self):
        return self.full_info

    def save_user_meta(self):
        return self.model_evaluation.client._perform_text(
                "PUT", "/projects/%s/modelevaluationstores/%s/evaluations/%s/user-meta" %
                       (self.model_evaluation.project_key, self.model_evaluation.mes_id, self.model_evaluation.evaluation_id), body=self.user_meta)


class DataDriftParams(object):
    """
    Object that represents parameters for data drift computation.
    Do not create this object directly, use :meth:`dataikuapi.dss.modelevaluationstore.DataDriftParams.from_params` instead.
    """
    def __init__(self, data):
        self.data = data

    def __repr__(self):
        return u"{}({})".format(self.__class__.__name__, self.data)

    @staticmethod
    def from_params(columns, nb_bins=10, compute_histograms=True, confidence_level=0.95):
        """
        Creates parameters for data drift computation from columns, number of bins, compute histograms and confidence level

        :param dict columns: A dict representing the per column settings.
        You should use a :class:`~dataikuapi.dss.modelevaluationstore.PerColumnDriftParamBuilder` to build it.
        :param int nb_bins: (optional) Nb. bins in histograms (apply to all columns) - default: 10
        :param bool compute_histograms: (optional) Enable/disable histograms - default: True
        :param float confidence_level: (optional) Used to compute confidence interval on drift's model accuracy - default: 0.95

        :rtype: :class:`dataikuapi.dss.modelevaluationstore.DataDriftParams`
        """
        return DataDriftParams({
            "columns": columns,
            "nbBins": nb_bins,
            "computeHistograms": compute_histograms,
            "confidenceLevel": confidence_level
        })


class PerColumnDriftParamBuilder(object):
    """
    Builder for a map of per column drift params settings.
    Used as a helper before computing data drift to build columns param expected in dataikuapi.dss.modelevaluationstore.DataDriftParams.from_params.
    """
    def __init__(self):
        self.columns = {}

    def build(self):
        """Returns the built dict for per column drift params settings"""
        return self.columns

    def with_column_drift_param(self, name, handling="AUTO", enabled=False):
        """
        Sets the drift params settings for given column name.

        :param: string name: The name of the column
        :param: string handling: (optional) The column type, should be either NUMERICAL, CATEGORICAL or AUTO (default: AUTO)
        :param: bool name: (optional) If the column should be enabled (default: False)
        """
        self.columns[name] = {
            "handling": handling,
            "enabled": enabled
        }
        return self


class DataDriftResult(object):
    """
    A handle on the data drift result of a model evaluation.

    Do not create this class directly, instead use :meth:`dataikuapi.dss.DSSModelEvaluation.compute_data_drift`
    """
    def __init__(self, data):
        self.data = data
        self.drift_model_result = DriftModelResult(self.data["driftModelResult"])
        """Drift analysis based on drift modeling."""
        self.univariate_drift_result = UnivariateDriftResult(self.data["univariateDriftResult"])
        """Per-column drift analysis based on comparison of distributions."""
        self.per_column_settings = list(map(ColumnSettings, self.data["perColumnSettings"]))
        """Information about column handling that has been used (errors, types, etc)."""
        self.reference_sample_size = self.data["referenceSampleSize"]  # type: int
        self.current_sample_size = self.data["currentSampleSize"]  # type: int

    def get_raw(self):
        """
        Get the raw data drift result.

        :return: the raw data drift result
        :rtype: dict
        """
        return self.data


class DriftModelResult(object):
    """
    A handle on the drift model result.

    Do not create this class directly, instead use :meth:`dataikuapi.dss.modelevaluationstore.DataDriftResult.get_drift_model_result`
    """
    def __init__(self, data):
        self.data = data
        self.reference_sample_size = self.data["referenceSampleSize"]  # type: int
        """Number of rows coming from reference model evaluation in the drift model trainset."""
        self.current_sample_size = self.data["currentSampleSize"]  # type: int
        """Number of rows coming from current model evaluation in the drift model trainset."""
        self.drift_model_accuracy = DriftModelAccuracy(self.data["driftModelAccuracy"])
        self.feature_drift_importance = DriftVersusImportanceChart(self.data["driftVersusImportance"])

    def get_raw(self):
        """
        Get the raw drift model result.

        :return: the raw drift model result
        :rtype: dict
        """
        return self.data


class UnivariateDriftResult(object):
    """
    A handle on the univariate data drift.

    Do not create this class directly, instead use :meth:`dataikuapi.dss.modelevaluationstore.DataDriftResult.get_univariate_drift_result`
    """
    def __init__(self, data):
        self.data = data
        self.per_column_drift_data = self.data["columns"]  # type: dict
        """Drift data per column, as a dict of column name -> drift data."""

    def get_raw(self):
        """
        Get the raw univariate data drift.

        :return: the raw univariate data drift
        :rtype: dict
        """
        return self.data


class ColumnSettings(object):
    """
    A handle on column handling information.

    Do not create this class directly, instead use :meth:`dataikuapi.dss.modelevaluationstore.DataDriftResult.get_per_column_settings`
    """
    def __init__(self, data):
        self.data = data
        self.name = self.data["name"]  # type: str
        self.actual_column_handling = self.data["actualHandling"]  # type: str
        """The actual column handling (either forced via drift params or inferred from model evaluation preprocessings).
        It can be any of NUMERICAL, CATEGORICAL, or IGNORED."""
        self.default_column_handling = self.data["defaultHandling"]  # type: str
        """The default column handling (based on model evaluation preprocessing only).
        It can be any of NUMERICAL, CATEGORICAL, or IGNORED."""
        self.error_message = self.data.get("errorMessage", None)

    def get_raw(self):
        """
        Get the raw column handling information.

        :return: the raw column handling information
        :rtype: dict
        """
        return self.data


class DriftModelAccuracy(object):
    """
    A handle on the drift model accuracy.

    Do not create this class directly, instead use :meth:`dataikuapi.dss.modelevaluationstore.DriftModelResult.get_drift_model_accuracy`
    """
    def __init__(self, data):
        self.data = data
        self.value = self.data["value"]  # type: float
        self.lower_confidence_interval = self.data["lower"]  # type: float
        self.upper_confidence_interval = self.data["upper"]  # type: float
        self.pvalue = self.data["pvalue"]  # type: float

    def get_raw(self):
        """
        Get the raw drift model accuracy data.

        :return: the drift model accuracy data
        :rtype: dict
        """
        return self.data


class DriftVersusImportanceChart(object):
    """
    A handle on the feature drift importance chart data.

    Do not create this class directly, instead use :meth:`dataikuapi.dss.modelevaluationstore.DriftModelResult.get_feature_drift_importance`
    """
    def __init__(self, data):
        self.data = data
        self.column_names = self.data["columns"]  # type: list
        self.column_drift_scores = self.data["columnDriftScores"]  # type: list
        self.column_original_scores = self.data["columnImportanceScores"]  # type: list

    def get_raw(self):
        """
        Get the raw feature drift importance chart data.

        :return: the feature drift importance chart data
        :rtype: dict
        """
        return self.data
