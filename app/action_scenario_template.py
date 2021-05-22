
action_template = '''# Discovery Doc: {discovery_doc_url}
# SERVICE_NAME: [{service_name}]
# VERSION: [{service_version}]
# METHOD_NAME: [{action_name}]

import '//configs/api/policy/mafv2/internal/maf.gcl' as maf
import '//java/com/google/api/policy/mafv2/protos/v2/maf.proto' as proto
import '//production/borg/templates/lambda/formatters.borg' as formatters

Action {action_var_name} = {{
  name = '{action_id}'
  type = 'HTTP'

  inputs = [
{action_inputs}
  ]

  outputs = [
      ### Add output pairs here.
  ]

  http_options = {{
    method = '{http_method}'
    url_path = '{http_url}'
{http_body}
  }}

  cleanup = [
    ### Add necessary cleanup invocations here.
  ]
}}
'''

scenario_template = '''# Discovery Doc: {discovery_doc_url}
# SERVICE_NAME: [{service_name}]
# VERSION: [{service_version}]
# METHOD_ID: [{scenario_name}]

import '//configs/api/policy/mafv2/internal/maf.gcl' as maf
import '//java/com/google/api/policy/mafv2/protos/v2/maf.proto' as proto

TestScenario {scenario_var_name} = @maf.TestScenario {{
  name = '{scenario_id}'
  status = '{scenario_status}'

  setup = [
    @maf.Invocation {{
      action_name = 'builtins.project.create'
      captures = [
        {{ name = 'projectId', value = '${{outputs.projectId}}' }},
      ]
    }},

    ### Add more necessary setup invocations here.
  ]

  api = [
    @maf.Invocation {{
      action_name = '{action_id}'
      arguments = [
{arguments_list}
      ]
    }},
  ]
}}
'''