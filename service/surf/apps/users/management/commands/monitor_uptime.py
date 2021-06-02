import logging
import boto3
import json
from datetime import date, timedelta, datetime, time
from suds.client import Client
from django.core.management.base import BaseCommand


logger = logging.getLogger("service")
SURFRAPPORTAGE_URL = 'https://rapportage.surfnet.nl:9011/interface.php?wsdl'


class Command(BaseCommand):

    def handle(self, *args, **options):
        last_day_of_prev_month = datetime.combine(date.today().replace(day=1) - timedelta(days=1), time.max)
        start_day_of_prev_month = datetime.combine(
            date.today().replace(day=1) - timedelta(days=last_day_of_prev_month.day),
            time.min)
        uptime = self._fetch_uptime(start_day_of_prev_month, last_day_of_prev_month)
        period = f"{start_day_of_prev_month.year}-{start_day_of_prev_month.strftime('%m')}"
        self._send_uptime_to_surfrapportage(uptime, period)

    def _fetch_uptime(self, start_day, end_day):
        session = boto3.Session(region_name='us-east-1')
        cloudwatch = session.client('cloudwatch')
        statistics = cloudwatch.get_metric_statistics(
            Namespace='AWS/Route53',
            MetricName='HealthCheckPercentageHealthy',
            Dimensions=[
                {
                    'Name': 'HealthCheckId',
                    'Value': 'ffae14a5-457d-4397-9f82-f228e2e0c72c'
                }
            ],
            StartTime=start_day,
            EndTime=end_day,
            Period=25920000,
            Statistics=['Average']
        )

        return statistics['Datapoints'][0]['Average']

    def _send_uptime_to_surfrapportage(self, uptime, period):
        username, password = self._retrieve_username_password()
        client = Client(url=SURFRAPPORTAGE_URL, username=username, password=password)
        report = client.factory.create('InsertReportInput')
        report.Period = period
        report.Remark = None
        report.Unit = '%'
        report.IsKPI = True
        report.IsHidden = False
        report.NormValue = 99.5
        report.NormComp = '>='
        report.Type = 'Beschikbaarheid'
        report.Value = uptime
        reply = client.service.er_InsertReport(username, password, report)

        if reply.ReturnCode == 1:
            logger.info('Successfully sent uptime to SURFrapportage')
        else:
            logger.error(f"Failed to send uptime report to SURFrapportage: {reply.ReturnCode}, {reply.ReturnText}")

    def _retrieve_username_password(self):
        session = boto3.Session(region_name='eu-central-1')
        secrets_manager = session.client('secretsmanager')
        secret_value = secrets_manager.get_secret_value(SecretId="surfrapportage")
        secret_payload = json.loads(secret_value["SecretString"])
        return secret_payload['surfrapportage/username'], secret_payload['surfrapportage/password']
