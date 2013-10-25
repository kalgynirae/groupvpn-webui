from flask import Flask
from wtforms import Form, BooleanField, IntegerField, TextField, validators

class ConfigurationForm(Form):
    group_name = TextField("Group name")
    xmpp_host = TextField("XMPP host")
    ip_base = TextField("IP base", [validators.IPAddress()])
    ip_netmask = TextField("IP netmask", [validators.IPAddress()])
    machine_count = IntegerField("Number of machines",
                                 [validators.NumberRange(min=0)])
    end_to_end_security = BooleanField("End-to-end security")

app = Flask(__name__)
@app.route('/', methods=['GET', 'POST'])
def configurate():
    form = ConfigurationForm(request.form)
    if request.method == 'POST' and form.validate():
        return render_template('success.html', form=form)
    return render_template('configuration.html', form=form)
