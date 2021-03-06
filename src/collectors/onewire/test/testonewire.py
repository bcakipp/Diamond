#!/usr/bin/python
# coding=utf-8

###############################################################################

from test import CollectorTestCase
from test import get_collector_config
from test import unittest
from mock import patch

try:
    from cStringIO import StringIO
except ImportError:
    from StringIO import StringIO

from diamond.collector import Collector
from onewire import OneWireCollector

###############################################################################


class TestOneWireCollector(CollectorTestCase):

    def setUp(self):
        config = get_collector_config('OneWireCollector', {
            'owfs': '/mnt/1wire',
            'scan': {'temperature': 't'},
            'id:28.2F702A010000': {'presure': 'p11'}})
        self.collector = OneWireCollector(config, None)

    @patch('os.path.isfile')
    @patch('os.listdir')
    @patch.object(Collector, 'publish')
    def test(self, publish_mock, listdir_mock, isfile_mock):

        open_name = 'onewire.open'
        with patch(open_name, create=True) as open_mock:

            self.mock_data = {
                "28.A76569020000": None,
                "28.A76569020000/temperature": StringIO("22.4375"),
                "28.A76569020000/presure": StringIO("error"),
                "28.2F702A010000": None,
                "28.2F702A010000/presure": StringIO("999"),
                "01.AE5426040000": None,
                "alarm": None,
                "bus.0": None,
                "settings": None, }

            self.mock_root = "/mnt/1wire"

            open_mock.side_effect = self._ret_open_mock
            listdir_mock.side_effect = self._ret_listdir_mock
            isfile_mock.side_effect = self._ret_isfile_mock

            self.collector.collect()

            listdir_mock.assert_called_once_with(self.mock_root)

        metrics = {
            '28_A76569020000.t': 22.4375,
            '28_2F702A010000.p11': 999
        }

        self.setDocExample(self.collector.__class__.__name__, metrics)
        self.assertPublishedMany(publish_mock, metrics)

    def _ret_isfile_mock(self, *args, **kwargs):
        fname = args[0][len(self.mock_root) + 1:]
        return fname in self.mock_data

    def _ret_listdir_mock(self, *args, **kwargs):
        ret = []
        if args[0] == self.mock_root:
            for ls in self.mock_data.keys():
                if '/' not in ls:
                    ret.append(ls)
        return ret

    def _ret_open_mock(self, *args, **kwargs):
        fname = args[0][len(self.mock_root) + 1:]
        if fname in self.mock_data:
            return self.mock_data[fname]
        return None


###############################################################################
if __name__ == "__main__":
    unittest.main()
