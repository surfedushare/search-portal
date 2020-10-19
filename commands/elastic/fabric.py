from invoke import Exit
from fabric import task
import signal


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
