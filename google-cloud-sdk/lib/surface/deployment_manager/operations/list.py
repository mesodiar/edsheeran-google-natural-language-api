# Copyright 2014 Google Inc. All Rights Reserved.
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

"""operations list command."""
from apitools.base.py import list_pager

from googlecloudsdk.api_lib.deployment_manager import dm_api_util
from googlecloudsdk.api_lib.deployment_manager import dm_base
from googlecloudsdk.calliope import base
from googlecloudsdk.command_lib.deployment_manager import flags


@dm_base.UseDmApi(dm_base.DmApiVersion.V2)
class List(base.ListCommand, dm_base.DmCommand):
  """List operations in a project.

  Prints a table with summary information on all operations in the project.
  """

  detailed_help = {
      'EXAMPLES': """\
          To print out a list of operations with some summary information about each, run:

            $ {command}

          To print only the name of each operation, run:

            $ {command} --simple-list
          """,
  }

  @staticmethod
  def Args(parser):
    """Args is called by calliope to gather arguments for this command.

    Args:
      parser: An argparse parser that you can use to add arguments that go
          on the command line after this command. Positional arguments are
          allowed.
    """
    dm_api_util.SIMPLE_LIST_FLAG.AddToParser(parser)
    parser.display_info.AddFormat(flags.OPERATION_FORMAT)

  def Run(self, args):
    """Run 'operations list'.

    Args:
      args: argparse.Namespace, The arguments that this command was invoked
          with.

    Returns:
      The list of operations for this project.

    Raises:
      HttpException: An http error response was received while executing api
          request.
    """
    request = self.messages.DeploymentmanagerOperationsListRequest(
        project=dm_base.GetProject(),
    )
    return dm_api_util.YieldWithHttpExceptions(list_pager.YieldFromList(
        self.client.operations, request, field='operations',
        limit=args.limit, batch_size=args.page_size))
