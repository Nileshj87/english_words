import socket
from flask import Flask, request, render_template
from wtforms import Form, validators, SearchField
from word_details import WordDetail
import os
# import concurrent_log_handler
import logging.config

script_dictionary = os.path.dirname(os.path.abspath(__file__))
config_folder = os.path.normpath(os.path.join(script_dictionary, 'config'))

log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

# log1 = logging.getLogger('engineio.server')
# log1.setLevel(logging.ERROR)
#
# log2 = logging.getLogger('socketio.server')
# log2.setLevel(logging.ERROR)

log_config_path = os.path.normpath(os.path.join(config_folder, 'logs.conf'))
logging.config.fileConfig(log_config_path, disable_existing_loggers=False)

logger = logging.getLogger("MAIN")


class FormField(Form):
    name = SearchField('Enter Word:', validators=[validators.data_required()])


app = Flask(__name__)
@app.route("/", methods=['GET', 'POST'])
def home_page():
    logger.info("Home Page START")
    form = FormField(request.form)
    string_x = None
    if request.method == 'POST':
        word = request.form['name'].title()
        print(word)
        wd = WordDetail(word)
        string_x = wd.call_methods()
        logger.info("Home Page END")
        return render_template('index.html', form=form, data=[string_x], word_name = word)
    logger.info("Home Page END")
    return render_template('index.html', form=form)


if __name__ == "__main__":
    # app.run('192.168.0.100', debug=True, threaded=True)
    ip_address = socket.gethostbyname(socket.gethostname())
    port = 5000
    print("Application is running on {}:{}".format(ip_address, port))
    logger.info("Application is running on {}:{}".format(socket.gethostbyname(socket.gethostname())), port)
    app.run(ip_address, port=port, threaded=True)


