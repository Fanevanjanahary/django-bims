import requests
from django.core.management import BaseCommand
from datetime import datetime
from django.core.management import call_command


class Command(BaseCommand):
    """
    Import all odonata data
    """

    def add_arguments(self, parser):
        parser.add_argument(
            '-token',
            '--token',
            dest='token',
            default='',
            help='Api token for the request'
        )
        parser.add_argument(
            '-tr',
            '--total-records',
            dest='total_records',
            default='',
            help='Total records of the data'
        )
        parser.add_argument(
            '-l',
            '--limit',
            dest='limit',
            default='10',
            help='Limit count'
        )
        parser.add_argument(
            '-s',
            '--start-index',
            dest='start_index',
            default='0',
            help='Start index'
        )

    def handle(self, *args, **options):
        api_token = options.get('token', '')
        if not api_token:
            print('Missing API TOKEN')
            return

        total_records = options.get('total_records', '')

        if not total_records:
            print('Getting total records...')
            url = f'https://api.birdmap.africa/vmus/v2/dwc/OdonataMAP/{api_token}/all/json/0'
            response = requests.get(url)
            total_records = (
                response.json()['data']['result'][0]['Number_of_records']
            )

        if isinstance(total_records, str):
            total_records = int(total_records)

        limit = int(options.get('limit', '10'))
        start_index = int(options.get('start_index', '0'))

        with open('import_all_odonata_log.txt', 'w') as the_file:
            the_file.write('')

        while start_index < total_records:
            if start_index + limit > total_records:
                limit = total_records - start_index
            log_text = (
                f"Fetching {start_index},{limit} of {total_records} - "
                f"{datetime.today()}\n"
            )
            print(log_text)
            call_command('import_odonata_data',
                         start_index=start_index,
                         limit=limit,
                         token=api_token)
            start_index += limit
