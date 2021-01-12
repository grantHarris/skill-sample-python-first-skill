import requests

from fiql_parser import Constraint
from fiql_parser import Expression
from fiql_parser import Operator


class BookingApi:

    def __init__(self, url):
        """
        Example usage

        api = BookingApi('https://digcore-booking-srvc-prod.events.lllapi.com')
        print(api.get(city='edmonton', start_date='2020-01-05T08:00:00', category='yoga'))
        """
        self.url = url

    def get(self, city=None, start_date=None, category=None):
        """
        Get the next 10 bookings which satsify the above params

        All params are optional and AND'ed together.

        :param city: City where the booking is located
        :param start_date: Start date of first booking
        :param category: Category to search. ie Yoga.

        :returns tuple: Returns a tuple with a list of the first 10 (maximum) bookings that satisfy
        the above filters. No bookings will return an empty list. Second is the total number of bookings
        if we paginated through the whole result set (beyond the 10)
        """

        def _build_fiql(city=None, start_date=None, category=None):
            expression = Expression()

            expression.add_element(Constraint('status.id', '==', 'published'))
            expression.add_element(Operator(';'))

            if start_date:
                expression.add_element(Constraint('local_start_date_time', '=ge=', start_date))
                expression.add_element(Operator(';'))

            if city:
                expression.add_element(Constraint('location.city', '==', city))
                expression.add_element(Operator(';'))

            if category:
                expression.add_element(Constraint('category.name', '==', category))

            return str(expression).replace(';', '%3B')

        def _format_row(row):
            attributes = row['attributes']
            return {
                'id': row['id'],
                'description': attributes['description'],
                'name': attributes['name'],
                'openings': attributes['openings'],
                'local_start_date_time': attributes['local_start_date_time']
            }

        params = f'page_size=10&page_number=1&sort=start_date_time&filter={_build_fiql(city, start_date, category)}'
        response = requests.get(f'{self.url}/v1/bookings', params=params)

        data = response.json()
        rows = [_format_row(row) for row in data['data']]
        return rows, data['meta']['total']
