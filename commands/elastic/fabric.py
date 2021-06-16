from invoke import Exit
from fabric import task
import signal

from commands.elastic.utils import get_es_client


@task(name="connect_elastic")
def connect_elastic_cluster(conn):
    """
    Forwards a port to the Elastic Search cluster. Useful to inspect harvests and the logs.
    """
    if conn.host != conn.config.aws.bastion:
        raise Exit(f"Did not expect the host {conn.host} while the bastion is {conn.config.aws.bastion}")

    print("Elastic Search available with SSH encryption at: https://localhost:9222/ "
          "and/or Kibana at https://localhost:9222/_plugin/kibana")
    with conn.forward_local(local_port=9222, remote_host=conn.config.elastic_search.host, remote_port=443):
        signal.pause()


@task
def push_indices_template(conn):
    """
    Creates or updates index templates to create indices with correct settings
    """
    if conn.host != conn.config.aws.bastion:
        raise Exit(f"Did not expect the host {conn.host} while the bastion is {conn.config.aws.bastion}")

    with conn.forward_local(local_port=9222, remote_host=conn.config.elastic_search.host, remote_port=443):
        client = get_es_client(conn)
        client.indices.put_template("basic-settings", body={
            "index_patterns": [
                "harvest-logs*", "document-logs*", "service-logs*", "search-results*", "harvest-results*"
            ],
            "settings": {
                "number_of_shards": 1,
                "number_of_replicas": 0
            }
        })
