"""
File containing the routes.
"""

from flask import Blueprint, jsonify, request
from app.cache import cache
from .utilities import *
import requests

bp = Blueprint('routes', __name__)


@bp.route('/metadata/model_list')
@cache.cached(timeout=3600)
def get_model_list():
    all_models = []

    for environment in environments:
        try:
            environment_response = requests.get(get_model_list_url(environment))
            environment_response.raise_for_status()
        except requests.exceptions.ConnectionError:
            continue
        except requests.exceptions.HTTPError as error:
            return jsonify({'type': 'error', 'message': error.args[0]})

        if environment_response.status_code == 200:
            environment_models = environment_response.json()
            error = check_errors(environment_models)

            if error is not None:
                return jsonify(error)

            all_models += environment_models

    return jsonify(all_models)


@bp.route('/metadata/samples')
def get_sample_sequences():
    response = {}

    base_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'samples')

    with open(os.path.join(base_path, 'example.fasta'), 'r') as fasta:
        response['fasta_data'] = fasta.read()

    with open(os.path.join(base_path, 'example.vcf'), 'r') as vcf:
        response['vcf_data'] = vcf.read()

    with open(os.path.join(base_path, 'example.bed'), 'r') as bed:
        response['bed_data'] = bed.read()

    return jsonify(response)


@bp.route('/get_predictions', methods=['POST'])
def get_predictions():
    errors = get_errors(request)
    if errors is not None:
        return jsonify(errors)

    selected_models = read_models(request.form['models'])
    sequences, error = read_sequences(request)

    if error is not None:
        return jsonify(error)

    predictions = []

    for environment in environments:

        if no_models_selected(selected_models, environment):
            continue

        data = {'models': selected_models[environment], 'sequences': sequences}

        try:
            environment_response = requests.post(get_predictions_url(environment), json=data, headers=headers)
            environment_response.raise_for_status()
        except requests.exceptions.ConnectionError:
            return jsonify({'type': 'error', 'message': 'Cannot connect to the servers at the moment.'})
        except requests.exceptions.HTTPError as error:
            return jsonify({'type': 'error', 'message': error.args[0]})

        if environment_response.status_code == 200:
            environment_predictions = environment_response.json()

            errors = check_errors(environment_predictions)
            if errors is not None:
                return jsonify(errors)

            predictions += environment_predictions

    return jsonify(predictions)
