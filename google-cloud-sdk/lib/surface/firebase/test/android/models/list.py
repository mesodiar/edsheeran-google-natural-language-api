# Copyright 2017 Google Inc. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""The 'gcloud firebase test android models list' command."""
import re

from googlecloudsdk.api_lib.firebase.test import util
from googlecloudsdk.calliope import base
from googlecloudsdk.core import log


class List(base.ListCommand):
  """List all Android models available for testing."""

  @staticmethod
  def Args(parser):
    """Method called by Calliope to register flags for this command.

    Args:
      parser: An argparse parser used to add arguments that follow this
          command in the CLI. Positional arguments are allowed.
    """
    parser.display_info.AddFormat("""
        table[box](
          id:label=MODEL_ID,
          manufacturer:label=MAKE,
          name:label=MODEL_NAME,
          form.color(blue=VIRTUAL,yellow=PHYSICAL):label=FORM,
          format("{0:4} x {1}", screenY, screenX):label=RESOLUTION,
          supportedVersionIds.list(undefined="none"):label=OS_VERSION_IDS,
          tags.join(sep=", ").color(green=default,red=deprecated,yellow=preview)
        )
    """)

  def Run(self, args):
    """Run the 'gcloud firebase test android models list' command.

    Args:
      args: an argparse namespace. All the arguments that were provided to this
        command invocation (i.e. group and command arguments combined).

    Returns:
      The list of device models we want to have printed later. Obsolete models
      with no currently supported OS versions are filtered out.
    """
    catalog = util.GetAndroidCatalog(self.context)
    filtered_models = [
        model for model in catalog.models if model.supportedVersionIds
    ]
    self._epilog = self._warn_on_deprecated_tag(filtered_models)

    return filtered_models

  def Epilog(self, resources_were_displayed=True):
    super(List, self).Epilog(resources_were_displayed)

    if self._epilog:
      log.warn(self._epilog)

  @staticmethod
  def _warn_on_deprecated_tag(models):
    for model in models:
      for tag in model.tags:
        if re.match('deprecated', tag):
          return (
              'Some devices are deprecated. Learn more at https://firebase.'
              'google.com/docs/test-lab/available-testing-devices#deprecated')
    return None
