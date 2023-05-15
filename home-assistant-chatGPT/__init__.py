"""Rest API for Home Assistant."""
import asyncio
from functools import lru_cache
from http import HTTPStatus
import logging
import json

from aiohttp import web
from aiohttp.web_exceptions import HTTPBadRequest
import async_timeout
import voluptuous as vol

from homeassistant.auth.permissions.const import POLICY_READ
from homeassistant.bootstrap import DATA_LOGGING
from homeassistant.components.http import HomeAssistantView

import homeassistant.core as ha
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ServiceNotFound, TemplateError, Unauthorized
from homeassistant.helpers import template
from homeassistant.helpers.json import json_dumps
from homeassistant.helpers.service import async_get_all_descriptions
from homeassistant.helpers.typing import ConfigType
from homeassistant.util.json import json_loads


_LOGGER = logging.getLogger(__name__)

ATTR_BASE_URL = "base_url"
ATTR_EXTERNAL_URL = "external_url"
ATTR_INTERNAL_URL = "internal_url"
ATTR_LOCATION_NAME = "location_name"
ATTR_INSTALLATION_TYPE = "installation_type"
ATTR_REQUIRES_API_PASSWORD = "requires_api_password"
ATTR_UUID = "uuid"
ATTR_VERSION = "version"

DOMAIN = "chat_gpt"
STREAM_PING_PAYLOAD = "ping"
STREAM_PING_INTERVAL = 50  # seconds


async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:
    """Register the API with the HTTP interface."""
    hass.http.register_view(ChatGPTManifest)
    hass.http.register_view(ChatGPTSpec)
    hass.http.register_view(ChatGPTStatesView)
    hass.http.register_view(ChatGPTStateView)

    return True

class ChatGPTManifest(HomeAssistantView):
    """View to handle the Manifest"""

    url = "/.well-known/ai-plugin.json"
    name = "chatGPT:manifest"

    requires_auth = False

    @ha.callback
    def get(self, request):
        """Get manifest."""
        
        hass = request.app["hass"]
        aiPlugin = ''

        fullpath = hass.config.path('custom_components/chat_gpt/ai-plugin.json')

        try:
            with open(fullpath, encoding="utf-8") as plugin:
                aiPlugin = json.load(plugin)
        except:
            _LOGGER.exception(fullpath)
        finally:
            return self.json(aiPlugin)

class ChatGPTSpec(HomeAssistantView):
    """View to handle the API Spec"""

    url = "/api/chatgpt/openapi.json"
    name = "chatGPT:spec"

    requires_auth = False

    @ha.callback
    def get(self, request):
        """Get API Spec."""

        hass = request.app["hass"]
        openApiSpec = ''

        fullpath = hass.config.path('custom_components/chat_gpt/openapi.json')

        try:
            with open(fullpath, encoding="utf-8") as spec_file:
                openApiSpec = json.load(spec_file)
        except:
            _LOGGER.exception(fullpath)
        finally:
            return self.json(openApiSpec)

class ChatGPTStatesView(HomeAssistantView):
    """View to handle States requests."""

    url = "/api/chatgpt/states/{domain}"
    name = "chatGPT:states"

    @ha.callback
    def get(self, request, domain):

        _LOGGER.exception(request)
        """Get current states."""
        user = request["hass_user"]
        entity_perm = user.permissions.check_entity
        states = [
            state
            for state in request.app["hass"].states.async_all(domain)
            if entity_perm(state.entity_id, "read")
        ]
        return self.json(states)

class ChatGPTStateView(HomeAssistantView):
    """View to handle EntityState requests."""

    url = "/api/chatgpt/states/{entity_id}"
    name = "chatGPT:entity-state"

    @ha.callback
    def get(self, request, entity_id):
        """Retrieve state of entity."""
        user = request["hass_user"]
        if not user.permissions.check_entity(entity_id, POLICY_READ):
            raise Unauthorized(entity_id=entity_id)

        if state := request.app["hass"].states.get(entity_id):
            return self.json(state)
        return self.json_message("Entity not found.", HTTPStatus.NOT_FOUND)


# class ChatGPTHistoryPeriodView(HomeAssistantView):
#     """Handle history period requests."""

#     url = "/api/chatgpt/history/period"
#     name = "chatgpt:history:view-period"
#     extra_urls = ["/api/chatgpt/history/period/{datetime}"]

#     async def get(
#         self, request: web.Request, datetime: str | None = None
#     ) -> web.Response:
#         """Return history over a period of time."""
#         datetime_ = None
#         query = request.query

#         if datetime and (datetime_ := dt_util.parse_datetime(datetime)) is None:
#             return self.json_message("Invalid datetime", HTTPStatus.BAD_REQUEST)

#         if not (entity_ids_str := query.get("filter_entity_id")) or not (
#             entity_ids := entity_ids_str.strip().lower().split(",")
#         ):
#             return self.json_message(
#                 "filter_entity_id is missing", HTTPStatus.BAD_REQUEST
#             )

#         hass = request.app["hass"]

#         for entity_id in entity_ids:
#             if not hass.states.get(entity_id) and not valid_entity_id(entity_id):
#                 return self.json_message(
#                     "Invalid filter_entity_id", HTTPStatus.BAD_REQUEST
#                 )

#         now = dt_util.utcnow()
#         if datetime_:
#             start_time = dt_util.as_utc(datetime_)
#         else:
#             start_time = now - _ONE_DAY

#         if start_time > now:
#             return self.json([])

#         if end_time_str := query.get("end_time"):
#             if end_time := dt_util.parse_datetime(end_time_str):
#                 end_time = dt_util.as_utc(end_time)
#             else:
#                 return self.json_message("Invalid end_time", HTTPStatus.BAD_REQUEST)
#         else:
#             end_time = start_time + _ONE_DAY

#         include_start_time_state = "skip_initial_state" not in query
#         significant_changes_only = query.get("significant_changes_only", "1") != "0"

#         minimal_response = "minimal_response" in request.query
#         no_attributes = "no_attributes" in request.query

#         if (
#             not include_start_time_state
#             and entity_ids
#             and not entities_may_have_state_changes_after(
#                 hass, entity_ids, start_time, no_attributes
#             )
#         ):
#             return self.json([])

#         return cast(
#             web.Response,
#             await get_instance(hass).async_add_executor_job(
#                 self._sorted_significant_states_json,
#                 hass,
#                 start_time,
#                 end_time,
#                 entity_ids,
#                 include_start_time_state,
#                 significant_changes_only,
#                 minimal_response,
#                 no_attributes,
#             ),
#         )

#     def _sorted_significant_states_json(
#         self,
#         hass: HomeAssistant,
#         start_time: dt,
#         end_time: dt,
#         entity_ids: list[str],
#         include_start_time_state: bool,
#         significant_changes_only: bool,
#         minimal_response: bool,
#         no_attributes: bool,
#     ) -> web.Response:
#         """Fetch significant stats from the database as json."""
#         with session_scope(hass=hass, read_only=True) as session:
#             return self.json(
#                 list(
#                     history.get_significant_states_with_session(
#                         hass,
#                         session,
#                         start_time,
#                         end_time,
#                         entity_ids,
#                         None,
#                         include_start_time_state,
#                         significant_changes_only,
#                         minimal_response,
#                         no_attributes,
#                     ).values()
#                 )
#             )