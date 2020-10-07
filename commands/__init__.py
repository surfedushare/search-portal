import os
from service.package import PACKAGE as SERVICE_PACKAGE
from harvester.package import PACKAGE as HARVESTER_PACKAGE

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HARVESTER_DIR = os.path.join(ROOT_DIR, "harvester")

REPOSITORY = "017973353230.dkr.ecr.eu-central-1.amazonaws.com"

TARGETS = {
    "service": SERVICE_PACKAGE,
    "harvester": HARVESTER_PACKAGE
}
