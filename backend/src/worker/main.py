from pkg import log
import os

logger = log.get_logger(log_file_name="worker", logger_name="", log_level=os.environ.get("LOG_LEVEL", "INFO"))

from flask import Flask
from flask_cors import CORS
from waitress import serve
from pkg.api import worker


def main():
    app = Flask(__name__)
    cors = CORS(app)
    app.config['CORS_HEADERS'] = "Content-Type"
    app.config['JSON_AS_ASCII'] = False

    ip = os.environ.get("LISTEN_IP", "0.0.0.0")
    port = int(os.environ.get("LISTEN_PORT", 8080))
    develope = os.environ.get("DEVELOPE", "false")
    debug = os.environ.get("DEBUG", "true")
    log_level = os.environ.get("LOG_LEVEL", "INFO")

    logger.info(f"LISTEN_IP:{ip}")
    logger.info(f"LISTEN_PORT:{port}")
    logger.info(f"develope:{develope}")
    logger.info(f"debug:{debug}")
    logger.info(f"log_level:{log_level}")

    #dynamic load api
    try:
        worker.add_url_rule(app)
    except Exception as e:
        logger.error(e)

    #open flask server
    if (develope.lower() == "true"):
        if (debug.lower() == "false"):
            app.run(host=ip, port=port, debug=False)
        else:
            app.run(host=ip, port=port, debug=True)
    elif (develope.lower() == "false"):
        serve(app, host=ip, port=port)
    else:
        logging.critical("api server not create.")


if (__name__ == "__main__"):
    main()
