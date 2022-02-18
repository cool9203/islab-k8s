from pkg import log

#load setting and get logger
setting = log.load_setting("./setting.txt")
logger = log.get_logger(setting=setting, name="worker", logger_name="")

from flask import Flask
from flask_cors import CORS
from waitress import serve
from pkg.api import worker


def main():
    app = Flask(__name__)
    cors = CORS(app)
    app.config['CORS_HEADERS'] = "Content-Type"
    app.config['JSON_AS_ASCII'] = False

    ip = setting.get("IP", "0.0.0.0")
    port = int(setting.get("PORT", 8080))
    develope = setting.get("DEVELOPE", "false")
    debug = setting.get("DEBUG", "true")

    logger.info(f"ip:{ip}")
    logger.info(f"port:{port}")
    logger.info(f"develope:{develope}")
    logger.info(f"debug:{debug}")

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
