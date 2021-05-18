"""This file contains the class that parses discovery doc.

And generates actions and scenarios.
"""

import json
import os

from app.api_info import ApiInfo

import requests


class DiscoveryDocParser:
  """The class that parses discovery doc and generates actions and scenarios."""

  def __init__(self):
    # Discover Doc Info
    self.discovery_doc_url = None
    self.service_name = None
    self.version = None
    self.base_url = None
    self.discovery_doc = None

    # Result
    self.result = {}

  def get_toc(self, dis_doc_url):
    self.read_discovery_doc(dis_doc_url)
    self.result = {}
    self.result['discovery_doc_url'] = self.discovery_doc_url
    self.result['service_name'] = self.service_name
    self.result['version'] = self.version
    self.result['base_url'] = self.base_url
    self.result['api_count'] = 0
    self.result['toc'] = {}
    self.parse_discovery_doc()
    return self.result

  def read_discovery_doc(self, dis_doc_url):
    """Reads discovery doc and populates necessary fields."""
    http_response = requests.get(dis_doc_url)
    discovery_doc = json.loads(http_response.text)

    self.discovery_doc_url = dis_doc_url
    self.service_name = discovery_doc.get('name', '')
    self.version = discovery_doc.get('version', '')
    self.base_url = discovery_doc.get('baseUrl', '')
    self.discovery_doc = discovery_doc

  def parse_discovery_doc(self):
    self.parse_discovery_doc_dict(self.discovery_doc, [])

  def generate_actions_and_scenarios(self, method_dict):
    self.result['api_count'] += 1
    api_info = ApiInfo()
    api_info.discovery_doc_url = self.discovery_doc_url
    api_info.service_name = self.service_name
    api_info.version = self.version
    api_info.base_url = self.base_url
    api_info.populate_from_method_doc(method_dict)
    return api_info

  def parse_discovery_doc_dict(self, resource_dict, resource_path):
    """Parse the methods under the current path, and recursively traverse next resources."""
    print(resource_path)
    flattened_resource_path = ' -> '.join(resource_path)
    self.result['toc'][flattened_resource_path] = []
    if 'methods' in resource_dict:
      methods = resource_dict['methods']
      for _, method_dict in methods.items():
        api_info = self.generate_actions_and_scenarios(method_dict)
        self.result['toc'][flattened_resource_path].append({
                'api_name': api_info.name,
                'definition': json.dumps(method_dict),
                'action': api_info.generate_action(),
                'scenario': api_info.generate_scenario()
            })

    if 'resources' in resource_dict:
      next_resources = resource_dict['resources']
      for next_resource_name, next_resource_dict in next_resources.items():
        resource_path.append(next_resource_name)
        self.parse_discovery_doc_dict(next_resource_dict, resource_path)
        resource_path.pop()

  def __str__(self):
    rstr = 'service name: [{}]\n'.format(self.service_name)
    rstr += 'version: [{}]\n'.format(self.version)
    rstr += 'base_url: [{}]\n'.format(self.base_url)
    rstr += 'discovery_doc_url: [{}]\n'.format(self.discovery_doc_url)

    return rstr
