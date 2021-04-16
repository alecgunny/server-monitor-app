from io import StringIO

from flask import Flask, Response, request
from werkzeug.exceptions import HTTPException

from stillwater.client import ThreadedMultiStreamInferenceClient
from stillwater.client.monitor import ServerStatsMonitor


app = Flask(__name__)
monitor = None


class OngoingExperiment(HTTPException):
    code = 505
    description = "Experiment is ongoing"


class NoExperiment(HTTPException):
    code = 505
    description = "No experiment running"


@app.route("/start")
def start_experiment():
    global monitor
    if monitor is not None:
        raise OngoingExperiment

    ip = request.args.get("ip")
    model_name = request.args.get("model-name")
    model_version = request.args.get("model-version", "1")

    client = ThreadedMultiStreamInferenceClient(
        ip + ":8001", model_name, model_version
    )
    monitor = ServerStatsMonitor(client, StringIO())
    monitor.start()
    return "Started monitoring"


@app.route("/stop")
def stop_experiment():
    global monitor
    if monitor is None:
        raise NoExperiment

    monitor.stop()
    monitor.join(1)
    monitor.close()

    response = Response(
        monitor.output_file.getvalue(),
        content_type="text/csv"
    )
    monitor.output_file.close()

    monitor = None
    return response
