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
    os.mkdir(plugin_dir)
    with open(os.path.join(plugin_dir, "entry_points.txt"), "w") as f:
        f.write(
            "[mlflow.request_header_provider]\n"
            "unused=dataikuapi.dss_plugin_mlflow.header_provider:PluginHeaderProvider\n"
        )
    sys.path.insert(0, tempdir)
