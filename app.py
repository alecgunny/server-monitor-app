from io import StringIO

from flask import Flask, Response, request
from stillwater.client import ThreadedMultiStreamInferenceClient
from stillwater.client.monitor import ServerStatsMonitor


app = Flask(__name__)
monitor = None


@app.route("/start")
def start_experiment():
    global monitor
    if monitor is not None:
        return 400, "Experiment is ongoing"

    url = request.args.get("url")
    model_name = request.args.get("model-name")
    model_version = request.args.get("model-version", "1")

    client = ThreadedMultiStreamInferenceClient(
        url, model_name, model_version
    )
    monitor = ServerStatsMonitor(client, StringIO())
    monitor.start()
    return 200


@app.route("/stop")
def stop_experiment():
    global monitor
    if monitor is None:
        return 400, "No experiment running"

    monitor.stop()
    monitor.join(1)
    response = Response(
        monitor.output_file.getValue(),
        content_type="text/csv"
    )

    monitor = None
    return response
