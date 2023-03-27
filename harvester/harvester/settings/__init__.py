# We're adding the environments directory outside of the project directory to the path
# That way we can load the environments and re-use them in different contexts
# Like maintenance tasks and harvesting tasks.
# These environments get loaded through the invoke library.
import sys
import os
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.join(BASE_DIR, "..", "..", "environments"))
from project import PROJECT

# We could specify the settings file with DJANGO_SETTINGS_MODULE environment variable,
# but that wouldn't load other environment variables that load through the invoke library.
# To minimize the amount of environment variables we load settings dynamically in this file based on PROJECT.
# This bypasses the DJANGO_SETTINGS_MODULE environment variable.
if PROJECT == "edusources":
    from .edusources_nl import *
else:
    from .publinova_nl import *
