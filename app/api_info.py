"""The class that saves all the information about an API.
"""

import re

# import constants
from app import utils
from app import action_scenario_template


ARGUMENTS_MAPPINGS = {
    'project': {
        'displayed_name': ['projectsid', 'projectid', 'project'],
        'argument_value': '${captures.projectId}',
    },
    'folder': {
        'displayed_name': ['foldersid'],
        'argument_value': '56993760227',
    },
    'organization': {
        'displayed_name': ['organizationsid'],
        'argument_value': '161175821343',
    },
    'location': {
        'displayed_name': ['locationsid', 'location'],
        'argument_value': '${globals.regions[0]}',
    },
    'region': {
        'displayed_name': [],
        'argument_value': '${globals.regions[0]}',
    },
    'zone': {
        'displayed_name': [],
        'argument_value': '${globals.zones[0]}',
    },
}

FALLBACK_ARGUMENT_VALUE = '${fn.randomId(globals.testId)}'


class ApiInfo:
  """API Info Class that saves all the information about an API.
  """

  def __init__(self):
    # Service Info
    self.discovery_doc_url = None
    self.service_name = None
    self.version = None
    self.base_url = None

    # Local Info
    self.config_dir = ''

    # API Info
    self.name = None
    self.http_method = None
    self.method_url = None
    self.path_params = []
    self.query_params = []
    self.status = 'NORMAL'

  def populate_from_method_doc(self, method_doc):
    self.populate_name(method_doc)
    self.populate_http_method(method_doc)
    self.populate_url_and_path_params(method_doc)
    self.populate_query_params(method_doc)

  def populate_name(self, method_doc):
    self.name = method_doc.get('id')

  def populate_http_method(self, method_doc):
    self.http_method = method_doc.get('httpMethod')

  def populate_url_and_path_params(self, method_doc):
    raw_path = method_doc.get('flatPath') or method_doc.get('path')
    parameter_pattern = re.compile(r'\{(.*?)\}')
    for match in re.finditer(parameter_pattern, raw_path):
      self.path_params.append(match.group(1))
    self.method_url = raw_path

  def populate_query_params(self, method_doc):
    for param_name, param in method_doc.get('parameters', {}).items():
      if (not param.get('required', False) or
          param.get('location', '').lower() not in ['query']):
        continue
      self.query_params.append(param_name)

  def action_id_to_camel(self, action_id):
    words = action_id.split('.')
    new_words = [words[0]]
    for i in range(1, len(words)):
      if words[i]:
        new_word = words[i][0].upper() + words[i][1:]
        new_words.append(new_word)
    return ''.join(new_words)

  def generate_action_inputs(self):
    action_inputs = self.path_params + self.query_params
    action_inputs = [
        '    {{ name = \'{}\' }},'.format(action_input)
        for action_input in action_inputs]

    action_inputs_str = '\n'.join(action_inputs)
    return action_inputs_str

  def generate_full_url(self):
    """Generate the full URL from baseUrl, path params and query params."""
    path_url = self.method_url
    for parameter in self.path_params:
      raw_parameter = '{{{0}}}'.format(parameter)
      maf_input = '${{inputs.{0}}}'.format(parameter)
      path_url = path_url.replace(raw_parameter, maf_input)

    if self.query_params:
      query_tokens = [
          '{0}=${{inputs.{0}}}'.format(query) for query in self.query_params]
      query_str = '&'.join(query_tokens)
      return '{0}{1}?{2}'.format(self.base_url, path_url, query_str)
    else:
      return '{0}{1}'.format(self.base_url, path_url)

  def generate_action_scenario_name(self):
    return '{0}.{1}.{2}'.format(self.service_name, self.version, self.name)

  def generate_action(self):
    """Generate action content string from template."""
    action_template = action_scenario_template.action_template
    action_content = action_template.format(
        discovery_doc_url=self.discovery_doc_url,
        service_name=self.service_name,
        service_version=self.version,
        action_name=self.name,

        action_var_name=self.action_id_to_camel(self.name),
        action_id=self.generate_action_scenario_name(),
        http_method=self.http_method,
        http_url=self.generate_full_url(),
        http_body='' if self.http_method in ['GET', 'DELETE'] else
        '    body = formatters.JSON.format({})',
        action_inputs=self.generate_action_inputs())
    return action_content

  def get_scenario_argument_value(self, action_input):
    for argument_mapping in ARGUMENTS_MAPPINGS.values():
      if action_input.lower() in argument_mapping['displayed_name']:
        return argument_mapping['argument_value']
    return FALLBACK_ARGUMENT_VALUE

  def generate_scenario_arguments(self):
    action_inputs = self.path_params + self.query_params
    scenario_arguments = []
    for action_input in action_inputs:
      action_input_value = self.get_scenario_argument_value(action_input)
      scenario_arguments.append(
          '        {{ name = \'{0}\', value = \'{1}\' }},'.format(
              action_input, action_input_value))
    scenario_arguments_str = '\n'.join(scenario_arguments)
    return scenario_arguments_str

  def generate_scenario(self):
    """Generate scenario content string from template."""
    scenario_template = action_scenario_template.scenario_template
    scenario_content = scenario_template.format(
        discovery_doc_url=self.discovery_doc_url,
        service_name=self.service_name,
        service_version=self.version,
        scenario_name=self.name,
        scenario_status=self.status,

        config_dir=self.config_dir,
        scenario_var_name=self.action_id_to_camel(self.name),
        scenario_id=self.generate_action_scenario_name(),
        action_id=self.generate_action_scenario_name(),
        arguments_list=self.generate_scenario_arguments())
    return scenario_content

