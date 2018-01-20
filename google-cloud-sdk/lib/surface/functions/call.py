# Copyright 2015 Google Inc. All Rights Reserved.
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

"""Triggers execution of a Google Cloud Function."""
import json

from googlecloudsdk.api_lib.functions import util
from googlecloudsdk.calliope import base
from googlecloudsdk.calliope import exceptions
from googlecloudsdk.command_lib.functions import flags
from googlecloudsdk.core import properties
from googlecloudsdk.core import resources


class Call(base.Command):
  """Trigger execution of a Google Cloud Function."""

  @staticmethod
  def Args(parser):
    """Register flags for this command."""
    flags.AddRegionFlag(
        parser,
        help_text='The region of the function to execute.',
    )
    parser.add_argument(
        'name',
        help='Name of the function to execute.',
        type=util.ValidateFunctionNameOrRaise)
    parser.add_argument(
        '--data',
        help='JSON string with data that will be passed to the function.')

  @util.CatchHTTPErrorRaiseHTTPException
  def Run(self, args):
    """This is what gets called when the user runs this command.

    Args:
      args: an argparse namespace. All the arguments that were provided to this
        command invocation.

    Returns:
      Function call results (error or result with execution id)
    """
    if args.data:
      try:
        json.loads(args.data)
      except ValueError as e:
        raise exceptions.InvalidArgumentException(
            '--data', 'Is not a valid JSON: ' + e.message)
    client = util.GetApiClientInstance()
    function_ref = resources.REGISTRY.Parse(
        args.name,
        params={
            'projectsId': properties.VALUES.core.project.GetOrFail,
            'locationsId': properties.VALUES.functions.region.GetOrFail,
        },
        collection='cloudfunctions.projects.locations.functions')
    # Do not retry calling function - most likely user want to know that the
    # call failed and debug.
    client.projects_locations_functions.client.num_retries = 0
    messages = client.MESSAGES_MODULE
    return client.projects_locations_functions.Call(
        messages.CloudfunctionsProjectsLocationsFunctionsCallRequest(
            name=function_ref.RelativeName(),
            callFunctionRequest=messages.CallFunctionRequest(data=args.data)))

Call.detailed_help = {
    'brief': 'Trigger execution of a Google Cloud Function.',
    'EXAMPLES': """\
        To call a function giving it hello world in message field of its event
        argument (depending on your environment you might need to escape
        characters in --data flag value differently):

        $ {{command}} helloWorld --data '{"message":"Hello World!"}'

     """
}
