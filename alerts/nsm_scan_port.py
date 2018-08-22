#!/usr/bin/env python

# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
# Copyright (c) 2018 Mozilla Corporation

from lib.alerttask import AlertTask
from query_models import SearchQuery, TermMatch, QueryStringMatch, PhraseMatch, ExistsMatch


class NSMScanPort(AlertTask):
    def __init__(self):
        AlertTask.__init__(self)
        self._config = self.parse_json_alert_config('nsm_scan_port.json')

    def main(self):
        search_query = SearchQuery(minutes=1)
        search_query.add_must([
            TermMatch('category', 'bro'),
            TermMatch('details.source', 'notice'),
            PhraseMatch('details.note', 'Scan::Port_Scan'),
            QueryStringMatch('details.sourceipaddress: {}'.format(self._config['sourcemustmatch']))
        ])
        search_query.add_must_not([
            QueryStringMatch('details.sourceipaddress: {}'.format(self._config['sourcemustnotmatch']))
        ])

        self.filtersManual(search_query)
        self.searchEventsAggregated('details.sourceipaddress', samplesLimit=10)
        self.walkAggregations(threshold=1)


    def onAggregation(self, aggreg):
        category = 'nsm'
        severity = 'WARNING'
        tags = ['nsm', "bro", 'portscan']

        indicators = 'unknown'
        #port = 'unknown'
        # Maybe iterate through it?
        x = aggreg['events'][0]['_source']
        if 'details' in x:
            if 'indicators' in x['details']:
                indicators = x['details']['sourceipaddress']
        #    if 'p' in x['details']:
        #        port = x['details']['p']

        summary = 'Port scan from {}'.format(indicators)

        return self.createAlertDict(summary, category, tags, aggreg['events'], severity)

