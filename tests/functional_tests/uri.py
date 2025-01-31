#!/usr/bin/env python3
#encoding=utf-8

# Copyright (c) 2019-2024, The Monero Project
# 
# All rights reserved.
# 
# Redistribution and use in source and binary forms, with or without modification, are
# permitted provided that the following conditions are met:
# 
# 1. Redistributions of source code must retain the above copyright notice, this list of
#    conditions and the following disclaimer.
# 
# 2. Redistributions in binary form must reproduce the above copyright notice, this list
#    of conditions and the following disclaimer in the documentation and/or other
#    materials provided with the distribution.
# 
# 3. Neither the name of the copyright holder nor the names of its contributors may be
#    used to endorse or promote products derived from this software without specific
#    prior written permission.
# 
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY
# EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF
# MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL
# THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
# SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
# PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT,
# STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF
# THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

"""Test URI RPC
"""

try:
  from urllib import quote as urllib_quote
except:
  from urllib.parse import quote as urllib_quote

from framework.wallet import Wallet

class URITest():
    def run_test(self):
      self.create()
      self.test_monero_uri()
      self.test_multi_uri()  
    
    def create(self):
        print('Creating wallet')
        wallet = Wallet()
        # close the wallet if any, will throw if none is loaded
        try: wallet.close_wallet()
        except: pass
        seed = 'velvet lymph giddy number token physics poetry unquoted nibs useful sabotage limits benches lifestyle eden nitrogen anvil fewest avoid batch vials washing fences goat unquoted'
        res = wallet.restore_deterministic_wallet(seed = seed)
        assert res.address == '42ey1afDFnn4886T7196doS9GPMzexD9gXpsZJDwVjeRVdFCSoHnv7KPbBeGpzJBzHRCAs9UxqeoyFQMYbqSWYTfJJQAWDm'
        assert res.seed == seed

    def test_monero_uri(self):
        print('Testing monero: URI')
        wallet = Wallet()

        utf8string = [u'えんしゅう', u'あまやかす']
        quoted_utf8string = [urllib_quote(x.encode('utf8')) for x in utf8string]

        ok = False
        try: res = wallet.make_uri(payments=[{}])  # no address
        except: ok = True
        assert ok
        
        ok = False
        try: res = wallet.make_uri(payments=[{'address': 'kjshdkj'}])  # invalid address
        except: ok = True
        assert ok

        # single payment tests
        for address in [
            '42ey1afDFnn4886T7196doS9GPMzexD9gXpsZJDwVjeRVdFCSoHnv7KPbBeGpzJBzHRCAs9UxqeoyFQMYbqSWYTfJJQAWDm',
            '4BxSHvcgTwu25WooY4BVmgdcKwZu5EksVZSZkDd6ooxSVVqQ4ubxXkhLF6hEqtw96i9cf3cVfLw8UWe95bdDKfRQeYtPwLm1Jiw7AKt2LY',
            '8AsN91rznfkBGTY8psSNkJBg9SZgxxGGRUhGwRptBhgr5XSQ1XzmA9m8QAnoxydecSh5aLJXdrgXwTDMMZ1AuXsN1EX5Mtm'
        ]:
            # basic address
            res = wallet.make_uri(payments=[{'address': address}])
            assert res.uri == 'monero:' + address
            parsed = wallet.parse_uri(res.uri)
            assert len(parsed.uri['payments']) == 1
            assert parsed.uri['payments'][0]['address'] == address
            assert parsed.uri['payments'][0]['amount'] == 0
            assert parsed.uri['payment_id'] == ''
            assert parsed.uri['tx_description'] == ''

            # with amount
            res = wallet.make_uri(payments=[{
                'address': address,
                'amount': 11000000000
            }])
            assert 'tx_amount=0.011' in res.uri or 'tx_amount=0.011000000000' in res.uri
            parsed = wallet.parse_uri(res.uri)
            assert parsed.uri['payments'][0]['amount'] == 11000000000
        
        address = '42ey1afDFnn4886T7196doS9GPMzexD9gXpsZJDwVjeRVdFCSoHnv7KPbBeGpzJBzHRCAs9UxqeoyFQMYbqSWYTfJJQAWDm'

        # test desc
        res = wallet.make_uri(
            payments=[{'address': address}],
            tx_description=utf8string[0]
        )
        assert 'tx_description=' + quoted_utf8string[0] in res.uri
        parsed = wallet.parse_uri(res.uri)
        assert parsed.uri['tx_description'] == utf8string[0]

        # test recipient name in payment entry
        res = wallet.make_uri(payments=[{
            'address': address,
            'recipient_name': utf8string[0]
        }])
        assert 'recipient_name=' + quoted_utf8string[0] in res.uri
        parsed = wallet.parse_uri(res.uri)
        assert parsed.uri['payments'][0]['recipient_name'] == utf8string[0]

        # combined parameters
        res = wallet.make_uri(
            payments=[{
                'address': address,
                'amount': 1000000000000,
                'recipient_name': utf8string[0]
            }],
            tx_description=utf8string[1]
        )
        parsed = wallet.parse_uri(res.uri)
        assert parsed.uri['payments'][0]['amount'] == 1000000000000
        assert parsed.uri['payments'][0]['recipient_name'] == utf8string[0]
        assert parsed.uri['tx_description'] == utf8string[1]

        # test payment ID rejection
        ok = False
        try: 
            wallet.make_uri(
                payments=[{'address': address}],
                payment_id='1' * 64
            )
        except: ok = True
        assert ok

        # notes: spaces must be encoded as %20
        # external payment ids are not supported anymore
        # test URI parsing from docs
        res = wallet.parse_uri('monero:46BeWrHpwXmHDpDEUmZBWZfoQpdc6HaERCNmx1pEYL2rAcuwufPN9rXHHtyUA4QVy66qeFQkn6sfK8aHYjA3jk3o1Bv16em?tx_amount=239.39014&tx_description=donation')
        assert len(res.uri['payments']) == 1
        assert res.uri['payments'][0]['address'] == '46BeWrHpwXmHDpDEUmZBWZfoQpdc6HaERCNmx1pEYL2rAcuwufPN9rXHHtyUA4QVy66qeFQkn6sfK8aHYjA3jk3o1Bv16em'
        assert res.uri['payments'][0]['amount'] == 239390140000000
        assert res.uri['tx_description'] == 'donation'


        # test malformed/invalid URIs
        for uri in [
            '',
            ':',
            'monero',
            'notmonero:42ey1afDFnn4886T7196doS9GPMzexD9gXpsZJDwVjeRVdFCSoHnv7KPbBeGpzJBzHRCAs9UxqeoyFQMYbqSWYTfJJQAWDm',
            'MONERO:42ey1afDFnn4886T7196doS9GPMzexD9gXpsZJDwVjeRVdFCSoHnv7KPbBeGpzJBzHRCAs9UxqeoyFQMYbqSWYTfJJQAWDm',
            'MONERO::42ey1afDFnn4886T7196doS9GPMzexD9gXpsZJDwVjeRVdFCSoHnv7KPbBeGpzJBzHRCAs9UxqeoyFQMYbqSWYTfJJQAWDm',
            'monero:',
            'monero:badaddress',
            'monero:tx_amount=10',
            'monero:?tx_amount=10',
            'monero:42ey1afDFnn4886T7196doS9GPMzexD9gXpsZJDwVjeRVdFCSoHnv7KPbBeGpzJBzHRCAs9UxqeoyFQMYbqSWYTfJJQAWDm?tx_amount=-1',
            'monero:42ey1afDFnn4886T7196doS9GPMzexD9gXpsZJDwVjeRVdFCSoHnv7KPbBeGpzJBzHRCAs9UxqeoyFQMYbqSWYTfJJQAWDm?tx_amount=1e12',
            'monero:42ey1afDFnn4886T7196doS9GPMzexD9gXpsZJDwVjeRVdFCSoHnv7KPbBeGpzJBzHRCAs9UxqeoyFQMYbqSWYTfJJQAWDm?tx_amount=+12',
            'monero:42ey1afDFnn4886T7196doS9GPMzexD9gXpsZJDwVjeRVdFCSoHnv7KPbBeGpzJBzHRCAs9UxqeoyFQMYbqSWYTfJJQAWDm?tx_amount=1+2',
            'monero:42ey1afDFnn4886T7196doS9GPMzexD9gXpsZJDwVjeRVdFCSoHnv7KPbBeGpzJBzHRCAs9UxqeoyFQMYbqSWYTfJJQAWDm?tx_amount=A',
            'monero:42ey1afDFnn4886T7196doS9GPMzexD9gXpsZJDwVjeRVdFCSoHnv7KPbBeGpzJBzHRCAs9UxqeoyFQMYbqSWYTfJJQAWDm?tx_amount=0x2',
            'monero:42ey1afDFnn4886T7196doS9GPMzexD9gXpsZJDwVjeRVdFCSoHnv7KPbBeGpzJBzHRCAs9UxqeoyFQMYbqSWYTfJJQAWDm?tx_amount=222222222222222222222',
            'monero:42ey1afDFnn4886T7196doS9GPMzexD9gXpsZJDwVjeRVdFCSoHnv7KPbBeGpzJBzHRCAs9UxqeoyFQMYbqSWYTfJJQAWDn?tx_amount=10',
            'monero:42ey1afDFnn4886T7196doS9GPMzexD9gXpsZJDwVjeRVdFCSoHnv7KPbBeGpzJBzHRCAs9UxqeoyFQMYbqSWYTfJJQAWDm&',
            'monero:42ey1afDFnn4886T7196doS9GPMzexD9gXpsZJDwVjeRVdFCSoHnv7KPbBeGpzJBzHRCAs9UxqeoyFQMYbqSWYTfJJQAWDm&tx_amount',
            'monero:42ey1afDFnn4886T7196doS9GPMzexD9gXpsZJDwVjeRVdFCSoHnv7KPbBeGpzJBzHRCAs9UxqeoyFQMYbqSWYTfJJQAWDm&tx_amount=',
            'monero:42ey1afDFnn4886T7196doS9GPMzexD9gXpsZJDwVjeRVdFCSoHnv7KPbBeGpzJBzHRCAs9UxqeoyFQMYbqSWYTfJJQAWDm&tx_amount=10=',
            'monero:42ey1afDFnn4886T7196doS9GPMzexD9gXpsZJDwVjeRVdFCSoHnv7KPbBeGpzJBzHRCAs9UxqeoyFQMYbqSWYTfJJQAWDm&tx_amount=10=&',
            'monero:42ey1afDFnn4886T7196doS9GPMzexD9gXpsZJDwVjeRVdFCSoHnv7KPbBeGpzJBzHRCAs9UxqeoyFQMYbqSWYTfJJQAWDm&tx_amount=10=&foo=bar',
            'monero:42ey1afDFnn4886T7196doS9GPMzexD9gXpsZJDwVjeRVdFCSoHnv7KPbBeGpzJBzHRCAs9UxqeoyFQMYbqSWYTfJJQAWDm?tx_amount=10&tx_amount=20',
            'monero:42ey1afDFnn4886T7196doS9GPMzexD9gXpsZJDwVjeRVdFCSoHnv7KPbBeGpzJBzHRCAs9UxqeoyFQMYbqSWYTfJJQAWDm?tx_payment_id=1111111111111111',
            'monero:4BxSHvcgTwu25WooY4BVmgdcKwZu5EksVZSZkDd6ooxSVVqQ4ubxXkhLF6hEqtw96i9cf3cVfLw8UWe95bdDKfRQeYtPwLm1Jiw7AKt2LY?tx_payment_id=' + '1' * 64,
            'monero:9ujeXrjzf7bfeK3KZdCqnYaMwZVFuXemPU8Ubw335rj2FN1CdMiWNyFV3ksEfMFvRp9L9qum5UxkP5rN9aLcPxbH1au4WAB',
            'monero:5K8mwfjumVseCcQEjNbf59Um6R9NfVUNkHTLhhPCmNvgDLVS88YW5tScnm83rw9mfgYtchtDDTW5jEfMhygi27j1QYphX38hg6m4VMtN29',
            'monero:7A1Hr63MfgUa8pkWxueD5xBqhQczkusYiCMYMnJGcGmuQxa7aDBxN1G7iCuLCNB3VPeb2TW7U9FdxB27xKkWKfJ8VhUZthF',
        ]:
            ok = False
            try: res = wallet.parse_uri(uri)
            except: ok = True
            assert ok, f"Failed to reject invalid URI: {uri}"

        # unknown parameter tests for single URI: unknown parameters but otherwise valid
        print('Testing unknown parameters in single-URI')
        test_cases = [
            ('monero:' + address + '?tx_amount=239.39014&foo=bar', ['foo=bar']),
            ('monero:' + address + '?tx_amount=239.39014&foo=bar&baz=quux', ['foo=bar', 'baz=quux']),
            ('monero:' + address + '?tx_amount=239.39014&%20=%20', ['%20=%20']),
            ('monero:' + address + '?tx_amount=239.39014&unknown=' + quoted_utf8string[0], 
             [u'unknown=' + quoted_utf8string[0]])
        ]
        
        for uri, expected_unknown in test_cases:
            res = wallet.parse_uri(uri)
            assert len(res.uri['payments']) == 1, "Should have single payment"
            assert res.uri['payments'][0]['address'] == address
            assert res.uri['payments'][0]['amount'] == 239390140000000
            assert res.unknown_parameters == expected_unknown, \
                f"Unexpected unknown params: {res.unknown_parameters}"

def test_multi_uri(self):
        print('Testing multi-recipient URIs')
        wallet = Wallet()
        address1 = '42ey1afDFnn4886T7196doS9GPMzexD9gXpsZJDwVjeRVdFCSoHnv7KPbBeGpzJBzHRCAs9UxqeoyFQMYbqSWYTfJJQAWDm'
        address2 = '4BxSHvcgTwu25WooY4BVmgdcKwZu5EksVZSZkDd6ooxSVVqQ4ubxXkhLF6hEqtw96i9cf3cVfLw8UWe95bdDKfRQeYtPwLm1Jiw7AKt2LY'
        utf8string = [u'えんしゅう', u'あまやかす']
        quoted_utf8string = [urllib_quote(x.encode('utf8')) for x in utf8string]

        # multi-URI unknown parameter tests
        print('Testing unknown parameters in multi-URI')
        multi_uri_cases = [
            (
                f'monero:{address1};{address2}?tx_amount=0.5;0.2&foo=bar',
                {'addresses': [address1, address2], 'amounts': [500000000000, 200000000000]},
                ['foo=bar']
            ),
            (
                f'monero:{address1};{address2}?tx_amount=1.0;0&recipient_name=Alice;&unknown_param=123',
                {'addresses': [address1, address2], 'amounts': [1000000000000, 0], 'names': ['Alice', '']},
                ['unknown_param=123']
            ),
            (
                f'monero:{address1};{address2}?tx_description=Test&unknown1=val1&unknown2=val2',
                {'addresses': [address1, address2], 'description': 'Test'},
                ['unknown1=val1', 'unknown2=val2']
            ),
            (
                f'monero:{address1};{address2}?recipient_name=Name1;Name2&tx_amount=0.1;0.2&special=%40%24%5E',
                {'addresses': [address1, address2], 'amounts': [100000000000, 200000000000], 'names': ['Name1', 'Name2']},
                ['special=%40%24%5E']
            )
        ]

        for uri, expected, expected_unknown in multi_uri_cases:
            res = wallet.parse_uri(uri)
            
            # verify payment count
            assert len(res.uri['payments']) == len(expected['addresses']), \
                f"Expected {len(expected['addresses'])} payments, got {len(res.uri['payments'])}"
            
            # check addresses and amounts
            for i, payment in enumerate(res.uri['payments']):
                assert payment['address'] == expected['addresses'][i], \
                    f"Address mismatch at position {i}"
                
                if 'amounts' in expected:
                    assert payment['amount'] == expected['amounts'][i], \
                        f"Amount mismatch at position {i}"
                
                if 'names' in expected:
                    assert payment['recipient_name'] == expected['names'][i], \
                        f"Name mismatch at position {i}"
            
            # check desc
            if 'description' in expected:
                assert res.uri['tx_description'] == expected['description'], \
                    "Description mismatch"
            
            # verify unknown parameters
            assert res.unknown_parameters == expected_unknown, \
                f"Unknown params mismatch. Expected {expected_unknown}, got {res.unknown_parameters}"

        # test mixed parameter positions
        res = wallet.parse_uri(
            f'monero:{address1};{address2}?unknown_first=123&tx_amount=0.1;0.2&unknown_last=456'
        )
        assert res.unknown_parameters == ['unknown_first=123', 'unknown_last=456']
        assert len(res.uri['payments']) == 2
        assert res.uri['payments'][0]['amount'] == 100000000000
        assert res.uri['payments'][1]['amount'] == 200000000000

        # test special characters in unknown params
        special_uri = f'monero:{address1};{address2}?weird_param={quoted_utf8string[0]}&tx_amount=1;2'
        res = wallet.parse_uri(special_uri)
        assert res.unknown_parameters == [u'weird_param=' + quoted_utf8string[0]]
        assert res.uri['payments'][0]['amount'] == 1000000000000
        assert res.uri['payments'][1]['amount'] == 2000000000000

        # test multiple unknown params with same key
        res = wallet.parse_uri(f'monero:{address1}?tx_amount=1&flag=1&flag=2')
        assert res.unknown_parameters == ['flag=1', 'flag=2']
        assert res.uri['payments'][0]['amount'] == 1000000000000


if __name__ == '__main__':
    URITest().run_test()
