import os

import sentry_sdk
import flask
import requests
from sentry_sdk.integrations.flask import FlaskIntegration

sentry_sdk.init(
    dsn="os.environ['SENTRY_DSN']",
    integrations=[FlaskIntegration()],

    # Set traces_sample_rate to 1.0 to capture 100%
    # of transactions for performance monitoring.
    # We recommend adjusting this value in production.
    traces_sample_rate=1.0,

    # By default the SDK will try to use the SENTRY_RELEASE
    # environment variable, or infer a git commit
    # SHA as release, however you may want to set
    # something more human-readable.
    # release="myapp@1.0.0",
)

app = flask.Flask(__name__)


@app.route('/tasks/<task_id>/score/<direction>', methods=['POST'])
def score_task_event(task_id, direction):
    responses = []

    data = flask.request.json
    for commit in data.get('commits', []):
        valid_users = _get_valid_users()
        if commit['author'].get('email') in valid_users or not valid_users:
            responses.append(score_task(task_id, direction))

    return flask.jsonify(responses)


def score_task(task_id, direction):
    habitica_url = 'https://habitica.com/api/v3/tasks/{}/score/{}'.format(task_id, direction)

    headers = {
        'x-api-user': os.environ['HABITICA_API_USER'],
        'x-api-key': os.environ['HABITICA_API_KEY']
    }

    response = requests.post(habitica_url, headers=headers)
    return response.json()


def _get_valid_users():
    valid_users = map(str.strip, filter(
        None, os.environ['VALID_USERS'].split(',')))
    return valid_users


if __name__ == '__main__':
    app.run()
