import math
from tqdm import tqdm

from django.core.management.base import BaseCommand
from datagrowth.utils import ibatch

from core.logging import HarvestLogger



class HarvesterCommand(BaseCommand):
    """
    This class adds some syntax sugar to make output of all commands similar
    """

    show_progress = True

    def add_arguments(self, parser):
        parser.add_argument('-n', '--no-progress', action="store_true")

    def execute(self, *args, **options):
        self.show_progress = not options.get("no_progress", False)
        super().execute(*args, **options)

    def progress(self, iterator, total=None):
        if not self.show_progress:
            return iterator
        return tqdm(iterator, total=total)


class PipelineCommand(BaseCommand):
    """
    This class adds a logger to make pipeline output of all commands similar
    """

    command_name = None
    batch_size = None
    logger = None

    def add_arguments(self, parser):
        # TODO: remove no-progress flag
        parser.add_argument('-n', '--no-progress', action="store_true")
        parser.add_argument('-d', '--dataset', type=str, required=True)
        parser.add_argument('-b', '--batch-size', type=int, default=32)

    def execute(self, *args, **options):
        self.batch_size = options["batch_size"]
        self.logger = HarvestLogger(options["dataset"], self.command_name, options)
        super().execute(*args, **options)

    def batchify(self, phase, iterator, total):
        batches = int(math.floor(total / self.batch_size))
        rest = total % self.batch_size
        if rest:
            batches += 1
        for batch in ibatch(iterator, batch_size=self.batch_size):
            self.logger.progress(phase, batches)
            yield batch


class OutputCommand(HarvesterCommand):
    pass
