class Call:
    """
    A placeholder for the requests response wrapper class.
    The idea would be:
        A requests response object comes back.
        This class wraps it with similar functionality that's found in BeautifulSoup.
        So a response might look like:
            process_names = process.get_all()

            process_names.find('name-or-something').id  # 123456
            or
            process_names.get('name-or-something').id  # 123456

            for process in process_names.find_all('Title', None):
                process.id  # 123456

            process_names.status_code  # 200  From requests
    """

    def __init__(self, response):
        self.response = response
