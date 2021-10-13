# Copyright 2021 Tianmian Tech. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
from common.python.common import consts
from common.python.utils.conf_utils import get_env_config

INTRANET_IP = get_env_config(consts.ENV_CONF_KEY_INTRANET_IP)


class GlobalSettingInit:
    """
    Initialize the relevant configuration based on the environment variables
    """

    def __init__(self):
        """
        wefe_board.intranet_base_uri
        wefe_flow.intranet_base_uri
        wefe_gateway.intranet_base_uri
        wefe_serving.intranet_base_uri
        """

