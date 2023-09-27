from django.test import TestCase

# Create your tests here.
from django.test import TestCase, RequestFactory
from django.urls import reverse

from .views import download_summary


class DownloadSummaryTestCase(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

    def test_download_summary(self):
        url = reverse('download-summary')
        request = self.factory.get(url)
        response = download_summary(request)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/vnd.ms-excel')
        self.assertEqual(
            response['Content-Disposition'],
            'attachment; filename=robot_summary.xlsx'
        )
