import os
import sys
import tempfile


def load_dss_mlflow_plugin():
    """ Function to dynamically add entrypoints for MLflow

    MLflow uses entrypoints==0.3 to load entrypoints from plugins at import time.
    This function adds dss-mlflow-plugin entrypoints dynamically by adding them in sys.path
    at call time.
    """
    tempdir = tempfile.mkdtemp()
    plugin_dir = os.path.join(tempdir, "dss-plugin-mlflow.egg-info")
    if not os.path.isdir(plugin_dir):
        os.makedirs(plugin_dir)
    with open(os.path.join(plugin_dir, "entry_points.txt"), "w") as f:
        f.write(
            "[mlflow.request_header_provider]\n"
            "unused=dataikuapi.dss_plugin_mlflow.header_provider:PluginDSSHeaderProvider\n"
            "[mlflow.artifact_repository]\n"
            "dss-managed-folder=dataikuapi.dss_plugin_mlflow.artifact_repository:PluginDSSManagedFolderArtifactRepository\n"
        )
    # Load plugin
    sys.path.insert(0, tempdir)
    return tempdir