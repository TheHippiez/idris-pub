from zope.interface import Interface, Attribute

class IBlobStoreBackend(Interface):

    repository = Attribute('repository config')

    def blob_exists(self, blob_key):
        "Determine if a blob exists in the filesystem"
        pass

    def upload_url(self, blob_key):
        "Create an upload url that can be used to POST bytes"
        pass

    def receive_blob(self, request, blob):
        """Optionally do something with the upload request

        The local backend (which is not suitable for production)
        will receive the POST request with the full body here,
        The NGINX backend works similar, but only receives a
        header with file information.
        In case of the GCS blobstore, this method will not be called.

        Note that some backends can add the checksum to the blob object here
        this way, an additional call to blob_checksum is not needed later on.
        """
        pass

    def blob_checksum(self, blobkey):
        """Optionally return md5 checksum for blobkey,
        only called when receive_blob() has not returned a checksum
        """
        pass

    def serve_blob(self, request, response, blob):
        "Modify the response to servce bytes from blob_key"
        pass

    def local_path(self, blob):
        """Returns a local path to the blob.
        This means the blob has to be downloaded to the server
        for some backends"""
        pass


class IBlobTransform(Interface):
    name = Attribute('The name of the transform')
    supported_formats = Attribute('''
    list of mimetypes to which this transform can be applied.
    Wildcards are allowed (image/*)''')
    returns_bytes = Attribute('Boolean indicating transform returns binary data')
    returns_text = Attribute('Boolean indicating transform returns textual data')
    returns_obj = Attribute('Boolean indicating transform returns object data')

    def execute(self, blob_path):
        "run the transform returning the bytes/text or dict result"
        pass


class IDataLookupService(Interface):
    id = Attribute('The id of the lookup')
    name = Attribute('The name of the lookup')
    supported_kind = Attribute('Which kind of data the lookup returns')
    query_param_name = Attribute('The name of the param used for querying')

    def __init__(self, settings):
        "intialize the service with settings frm the registry"
        pass

    def query(self, query):
        """run the data lookup returning metadata as a dict,
        or None if not found"""
        pass


class ICourseRoyaltyCalculator(Interface):
    royalty_agency = Attribute('Registry Agency')
    tariff_long_cost_per_page_dutch = Attribute(
        """Ammount of euros (decimal)
        'Inbreuken, uitgever onbekend (vrijwaringsfonds)'""")
    tariff_long_cost_per_page_foreign = Attribute(
        """Ammount of euros (decimal)
        'Inbreuken, uitgever onbekend (vrijwaringsfonds)'""")
    tariff_short_max_article_words = Attribute(
        'Maximum number of words to stay within short article tariff')
    tariff_short_max_chapter_words = Attribute(
        'Maximum number of words to stay within short chapter tariff')
    tariff_short_max_chapter_from_total_work_percentage = Attribute(
        '''Maximum percentage of pages from book that can be used
        to stay within short tariff''')
    tariff_middle_max_from_total_work_percentage = Attribute(
        '''Maximum percentage of pages from total work that can be used
        to stay within middle tariff''')
    tariff_middle_max_pages = Attribute(
        'Maximum number of pages to stay within middle tariff')


    def calculate(self, materials):
        """run the calculation on materials data as returned from the
        toc_items_royalty method of the course resource

        returns a list with the following info on each material:

        - id (learning material id)
        - cost (in cents)
        - cost_message (description of the cost calculation)
        - tarif (short/middle/long/excempt/unknown/none)
        - tarif_message (description of the tarif choice)
        - warning (incomplete data error)
        - warning_message (description of the warning)
        """
        pass
