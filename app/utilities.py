import json
import os
from Bio import SeqIO

base_urls = {
    'kipoi-py3-keras2': os.environ['KERAS2_URL'],
    'kipoi-py3-keras1.2': os.environ['KERAS1_URL'],
}

environments = list(base_urls.keys())
headers = {'Content-Type': 'application/json', 'Accept': 'application/json'}


def get_errors(request):
    if not request.form:
        return {'type': 'error', 'message': 'Not a valid request'}

    if 'models' not in request.form:
        return {'type': 'error', 'message': 'No models selected'}

    selected_models = eval(request.form['models'])
    if selected_models is None or len(selected_models) == 0:
        return {'type': 'error', 'message': 'No models selected'}

    return None


def read_models(models_form_data):
    selected_models = eval(models_form_data)

    models = {'kipoi-py3-keras2': [], 'kipoi-py3-keras1.2': []}

    for selected_model in selected_models:
        model_name = selected_model.split('@@@')[0]
        model_environment = selected_model.split('@@@')[1]

        models[model_environment].append(model_name)

    return models


def read_sequences(request):
    sequences = None

    if 'sequences' in request.form:
        sequences = json.loads(request.form['sequences'])

    if 'file' in request.files:
        file = request.files['file']
        base_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'files')
        full_path = os.path.join(base_path, request.form['filename'])
        file.save(full_path)
        fasta_sequences = SeqIO.parse(open(full_path), 'fasta')

        sequences = []
        for fasta in fasta_sequences:
            sequences.append({
                'id': fasta.id,
                'seq': str(fasta.seq)
            })
        os.remove(full_path)

    if sequences is None or len(sequences) == 0:
        return None, {'type': 'error', 'message': 'No sequences sent'}

    return sequences, None


def check_errors(response):
    if 'type' in response and response['type'] == 'error':
        return response

    return None


def get_model_list_url(environment):
    return f'{base_urls[environment]}/metadata/model_list/{environment}'


def get_predictions_url(environment):
    return f'{base_urls[environment]}/get_predictions'


def no_models_selected(selected_models, environment):
    return len(selected_models[environment]) == 0
