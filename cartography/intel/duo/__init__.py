import logging

import duo_client
import neo4j

from cartography.config import Config
from cartography.intel.duo.api_host import sync_duo_api_host
from cartography.intel.duo.endpoints import sync_duo_endpoints
from cartography.intel.duo.groups import sync_duo_groups
from cartography.intel.duo.users import sync_duo_users
from cartography.util import timeit


logger = logging.getLogger(__name__)


@timeit
def get_client(config: Config) -> duo_client.Admin:
    '''
    Return a duo Admin client with the creds in the config object
    '''
    return duo_client.Admin(
        ikey=config.duo_api_key,
        skey=config.duo_api_secret,
        host=config.duo_api_hostname,
    )


@timeit
def start_duo_ingestion(neo4j_session: neo4j.Session, config: Config) -> None:
    '''
    If this module is configured, perform ingestion of duo data. Otherwise warn and exit
    :param neo4j_session: Neo4J session for database interface
    :param config: A cartography.config object
    :return: None
    '''
    if not all([
        config.duo_api_key,
        config.duo_api_secret,
        config.duo_api_hostname,
    ]):
        logger.info(
            'Duo import is not configured - skipping this module. '
            'See docs to configure.',
        )
        return

    client = get_client(config)
    common_job_parameters = {
        "UPDATE_TAG": config.update_tag,
        "DUO_API_HOSTNAME": config.duo_api_hostname,
    }

    sync_duo_api_host(
        neo4j_session,
        common_job_parameters,
    )
    sync_duo_endpoints(
        client,
        neo4j_session,
        common_job_parameters,
    )
    sync_duo_groups(
        client,
        neo4j_session,
        common_job_parameters,
    )
    sync_duo_users(
        client,
        neo4j_session,
        common_job_parameters,
    )
