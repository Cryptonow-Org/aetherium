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
        print('Testing monero: URI - single')
        wallet = Wallet()

        utf8string = [u'えんしゅう', u'あまやかす']
        quoted_utf8string = [urllib_quote(x.encode('utf8')) for x in utf8string]

        ok = False
        try: res = wallet.make_uri()
        except: ok = True
        assert ok
        ok = False
        try: res = wallet.make_uri(address = '')
        except: ok = True
        assert ok
        ok = False
        try: res = wallet.make_uri(address = 'kjshdkj')
        except: ok = True
        assert ok

        for address in [
            '42ey1afDFnn4886T7196doS9GPMzexD9gXpsZJDwVjeRVdFCSoHnv7KPbBeGpzJBzHRCAs9UxqeoyFQMYbqSWYTfJJQAWDm',
            '4BxSHvcgTwu25WooY4BVmgdcKwZu5EksVZSZkDd6ooxSVVqQ4ubxXkhLF6hEqtw96i9cf3cVfLw8UWe95bdDKfRQeYtPwLm1Jiw7AKt2LY',
            '8AsN91rznfkBGTY8psSNkJBg9SZgxxGGRUhGwRptBhgr5XSQ1XzmA9m8QAnoxydecSh5aLJXdrgXwTDMMZ1AuXsN1EX5Mtm'
        ]:
            res = wallet.make_uri(address = address)
            assert res.uri == 'monero:' + address
            res = wallet.parse_uri(res.uri)
            assert res.uri.payments[0].address == address
            assert res.uri.payments[0].amount == 0
            assert res.uri.payments[0].recipient_name == ''
            assert res.uri.payment_id == ''
            assert res.uri.tx_description == ''
            
            assert not 'unknown_parameters' in res or len(res.unknown_parameters) == 0
            res = wallet.make_uri(address = address, amount = 11000000000)
            assert res.uri == 'monero:' + address + '?tx_amount=0.011' or res.uri == 'monero:' + address + '?tx_amount=0.011000000000'
            res = wallet.parse_uri(res.uri)
            assert res.uri.payments[0].address == address
            assert res.uri.payments[0].amount == 11000000000
            assert res.uri.payments[0].recipient_name == ''
            assert res.uri.payment_id == ''
            assert res.uri.tx_description == ''
            assert not 'unknown_parameters' in res or len(res.unknown_parameters) == 0

        address = '42ey1afDFnn4886T7196doS9GPMzexD9gXpsZJDwVjeRVdFCSoHnv7KPbBeGpzJBzHRCAs9UxqeoyFQMYbqSWYTfJJQAWDm'

        res = wallet.make_uri(address = address, tx_description = utf8string[0])
        assert res.uri == 'monero:' + address + '?tx_description=' + quoted_utf8string[0]
        res = wallet.parse_uri(res.uri)
        assert res.uri.payments[0].address == address
        assert res.uri.payments[0].amount == 0
        assert res.uri.payments[0].recipient_name == ''
        assert res.uri.payment_id == ''
        assert res.uri.tx_description == utf8string[0]
        assert not 'unknown_parameters' in res or len(res.unknown_parameters) == 0

        res = wallet.make_uri(address = address, recipient_name = utf8string[0])
        assert res.uri == 'monero:' + address + '?recipient_name=' + quoted_utf8string[0]
        res = wallet.parse_uri(res.uri)
        assert res.uri.payments[0].address == address
        assert res.uri.payments[0].amount == 0
        assert res.uri.payments[0].recipient_name == utf8string[0]
        assert res.uri.payment_id == ''
        assert res.uri.tx_description == ''
        assert not 'unknown_parameters' in res or len(res.unknown_parameters) == 0

        res = wallet.make_uri(address = address, recipient_name = utf8string[0], tx_description = utf8string[1])
        assert res.uri == 'monero:' + address + '?recipient_name=' + quoted_utf8string[0] + '&tx_description=' + quoted_utf8string[1]
        res = wallet.parse_uri(res.uri)
        assert res.uri.payments[0].address == address
        assert res.uri.payments[0].amount == 0
        assert res.uri.payments[0].recipient_name == utf8string[0]
        assert res.uri.payment_id == ''
        assert res.uri.tx_description == utf8string[1]
        assert not 'unknown_parameters' in res or len(res.unknown_parameters) == 0

        res = wallet.make_uri(address = address, recipient_name = utf8string[0], tx_description = utf8string[1], amount = 1000000000000)
        assert res.uri == 'monero:' + address + '?tx_amount=1.000000000000&recipient_name=' + quoted_utf8string[0] + '&tx_description=' + quoted_utf8string[1]
        res = wallet.parse_uri(res.uri)
        assert res.uri.payments[0].address == address
        assert res.uri.payments[0].amount == 1000000000000
        assert res.uri.payments[0].recipient_name == utf8string[0]
        assert res.uri.payment_id == ''
        assert res.uri.tx_description == utf8string[1]
        assert not 'unknown_parameters' in res or len(res.unknown_parameters) == 0

        # standalone payment ids are supported but not recommended
        res = wallet.make_uri(address = address, recipient_name = utf8string[0], tx_description = utf8string[1], amount = 1000000000000, payment_id = '1' * 64)
        assert res.uri == 'monero:' + address + '?tx_amount=1.000000000000&recipient_name=' + quoted_utf8string[0] + '&tx_description=' + quoted_utf8string[1] + '&tx_payment_id=' + '1' * 64
        
        # in case of standalone payment id removal
        # ok = False
        # try:
        #     res = wallet.make_uri(address = address, recipient_name = utf8string[0], tx_description = utf8string[1], amount = 1000000000000, payment_id = '1' * 64)
        # except:
        #     ok = True
        # assert ok

        # spaces must be encoded as %20
        res = wallet.make_uri(address = address, tx_description = ' ' + utf8string[1] + ' ' + utf8string[0] + ' ', amount = 1000000000000)
        assert res.uri == 'monero:' + address + '?tx_amount=1.000000000000&tx_description=%20' + quoted_utf8string[1] + '%20' + quoted_utf8string[0] + '%20'
        res = wallet.parse_uri(res.uri)
        assert res.uri.payments[0].address == address
        assert res.uri.payments[0].amount == 1000000000000
        assert res.uri.payments[0].recipient_name == ''
        assert res.uri.payment_id == ''
        assert res.uri.tx_description == ' ' + utf8string[1] + ' ' + utf8string[0] + ' '
        assert not 'unknown_parameters' in res or len(res.unknown_parameters) == 0

        # the example from the docs
        res = wallet.parse_uri('monero:46BeWrHpwXmHDpDEUmZBWZfoQpdc6HaERCNmx1pEYL2rAcuwufPN9rXHHtyUA4QVy66qeFQkn6sfK8aHYjA3jk3o1Bv16em?tx_amount=239.39014&tx_description=donation')
        assert res.uri.payments[0].address == '46BeWrHpwXmHDpDEUmZBWZfoQpdc6HaERCNmx1pEYL2rAcuwufPN9rXHHtyUA4QVy66qeFQkn6sfK8aHYjA3jk3o1Bv16em'
        assert res.uri.payments[0].amount == 239390140000000
        assert res.uri.payments[0].recipient_name == ''
        assert res.uri.tx_description == 'donation'
        
        assert res.uri.payment_id == ''
        assert not 'unknown_parameters' in res or len(res.unknown_parameters) == 0

        # malformed/invalid
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
            # Standalone payment ids are still supported, in case of complete functionality removal: uncomment this.
            # 'monero:42ey1afDFnn4886T7196doS9GPMzexD9gXpsZJDwVjeRVdFCSoHnv7KPbBeGpzJBzHRCAs9UxqeoyFQMYbqSWYTfJJQAWDm?tx_payment_id=1111111111111111',
            # 'monero:4BxSHvcgTwu25WooY4BVmgdcKwZu5EksVZSZkDd6ooxSVVqQ4ubxXkhLF6hEqtw96i9cf3cVfLw8UWe95bdDKfRQeYtPwLm1Jiw7AKt2LY?tx_payment_id=' + '1' * 64,
            'monero:9ujeXrjzf7bfeK3KZdCqnYaMwZVFuXemPU8Ubw335rj2FN1CdMiWNyFV3ksEfMFvRp9L9qum5UxkP5rN9aLcPxbH1au4WAB',
            'monero:5K8mwfjumVseCcQEjNbf59Um6R9NfVUNkHTLhhPCmNvgDLVS88YW5tScnm83rw9mfgYtchtDDTW5jEfMhygi27j1QYphX38hg6m4VMtN29',
            'monero:7A1Hr63MfgUa8pkWxueD5xBqhQczkusYiCMYMnJGcGmuQxa7aDBxN1G7iCuLCNB3VPeb2TW7U9FdxB27xKkWKfJ8VhUZthF',
        ]:
            ok = False
            try: res = wallet.parse_uri(uri)
            except: ok = True
            assert ok, res

        # unknown parameters but otherwise valid
        res = wallet.parse_uri('monero:' + address + '?tx_amount=239.39014&foo=bar')
        assert res.uri.payments[0].address == address
        assert res.uri.payments[0].amount == 239390140000000
        assert res.unknown_parameters == ['foo=bar'], res
        res = wallet.parse_uri('monero:' + address + '?tx_amount=239.39014&foo=bar&baz=quux')
        assert res.uri.payments[0].address == address
        assert res.uri.payments[0].amount == 239390140000000
        assert res.unknown_parameters == ['foo=bar', 'baz=quux'], res
        res = wallet.parse_uri('monero:' + address + '?tx_amount=239.39014&%20=%20')
        assert res.uri.payments[0].address == address
        assert res.uri.payments[0].amount == 239390140000000
        assert res.unknown_parameters == ['%20=%20'], res
        res = wallet.parse_uri('monero:' + address + '?tx_amount=239.39014&unknown=' + quoted_utf8string[0])
        assert res.uri.payments[0].address == address
        assert res.uri.payments[0].amount == 239390140000000
        assert res.unknown_parameters == [u'unknown=' + quoted_utf8string[0]], res
        
    
    def test_multi_uri(self):
        print('Testing multi-recipient monero: URI')
        wallet = Wallet()
        addr1 = '42ey1afDFnn4886T7196doS9GPMzexD9gXpsZJDwVjeRVdFCSoHnv7KPbBeGpzJBzHRCAs9UxqeoyFQMYbqSWYTfJJQAWDm'
        addr2 = '4BxSHvcgTwu25WooY4BVmgdcKwZu5EksVZSZkDd6ooxSVVqQ4ubxXkhLF6hEqtw96i9cf3cVfLw8UWe95bdDKfRQeYtPwLm1Jiw7AKt2LY'
        addr3 = '8AsN91rznfkBGTY8psSNkJBg9SZgxxGGRUhGwRptBhgr5XSQ1XzmA9m8QAnoxydecSh5aLJXdrgXwTDMMZ1AuXsN1EX5Mtm'
        utf8string = [u'えんしゅう', u'あまやかす']
        quoted_utf8string = [urllib_quote(x.encode('utf8')) for x in utf8string]

        # build multi-recipient URI with two payments.
        payments = [
            {'address': addr1, 'amount': 500000000000, 'recipient_name': utf8string[0]},
            {'address': addr2, 'amount': 200000000000, 'recipient_name': utf8string[1]}
        ]
        res = wallet.make_uri(payments=payments, payment_id='', tx_description='multi test')
        # expect URI like:
        # monero:addr1;addr2?tx_amount=0.5;0.2&recipient_name=<url_encoded_name1>;<url_encoded_name2>&tx_description=multi%20test
        parsed = wallet.parse_uri(res.uri)
        # verify that both payments are present.
        assert len(parsed.uri.payments) == 2, "Expected 2 payments in multi-recipient URI"
        assert parsed.uri.payments[0].address == addr1
        assert parsed.uri.payments[0].amount == 500000000000
        assert parsed.uri.payments[0].recipient_name == utf8string[0]
        assert parsed.uri.payments[1].address == addr2
        assert parsed.uri.payments[1].amount == 200000000000
        assert parsed.uri.payments[1].recipient_name == utf8string[1]
        # check tx_description at the top level.
        assert parsed.uri.tx_description == 'multi test'
        assert parsed.uri.payment_id == ''

        # build multi-recipient URI with three payments.
        payments = [
            {'address': addr1, 'amount': 1000000000000, 'recipient_name': utf8string[0]},
            {'address': addr2, 'amount': 500000000000,  'recipient_name': utf8string[1]},
            {'address': addr3, 'amount': 250000000000,  'recipient_name': ''}
        ]
        res = wallet.make_uri(payments=payments, payment_id='', tx_description='three pay')
        parsed = wallet.parse_uri(res.uri)
        assert len(parsed.uri.payments) == 3, "Expected 3 payments in multi-recipient URI"
        assert parsed.uri.payments[0].address == addr1
        assert parsed.uri.payments[0].amount == 1000000000000
        assert parsed.uri.payments[0].recipient_name == utf8string[0]
        assert parsed.uri.payments[1].address == addr2
        assert parsed.uri.payments[1].amount == 500000000000
        assert parsed.uri.payments[1].recipient_name == utf8string[1]
        assert parsed.uri.payments[2].address == addr3
        assert parsed.uri.payments[2].amount == 250000000000
        assert parsed.uri.payments[2].recipient_name == ''
        assert parsed.uri.tx_description == 'three pay'
        
        payments = [
            {'address': addr1, 'amount': 500000000000, 'recipient_name': 'Alice'},
            {'address': addr2, 'amount': 0, 'recipient_name': 'Bob'}
        ]
        # manually build a URI with mismatched amounts (remove Bob's amount).
        # we simulate this by concatenating amounts incorrectly.
        # (this step assumes you have control over the output URI; in practice, the server would reject it. For testing, we assume the RPC returns an error.)
        uri_bad = 'monero:' + addr1 + ';' + addr2 + '?tx_amount=0.5&recipient_name=Alice;Bob'
        ok = False
        try:
            wallet.parse_uri(uri_bad)
        except Exception:
            ok = True
        assert ok, "Expected rejection for mismatched payment counts"

        # case: trailing semicolon in addresses or parameters should be handled gracefully
        uri_trailing = 'monero:' + addr1 + ';' + addr2 + ';' + '?tx_amount=0.5;0.2&recipient_name=Alice;Bob'
        # depending on the implementation, a trailing empty value might be dropped.
        parsed = wallet.parse_uri(uri_trailing)
        assert len(parsed.uri.payments) == 2, "Trailing delimiter should not add empty payment"

        # case: special characters in recipient names and descriptions
        special_name = "A&B=Test?"
        special_desc = "Desc with spaces & symbols!"
        payments = [
            {'address': addr1, 'amount': 750000000000, 'recipient_name': special_name},
            {'address': addr2, 'amount': 250000000000, 'recipient_name': special_name}
        ]
        
        # the RPC should URL-encode these parameters.
        res = wallet.make_uri(payments=payments, tx_description=special_desc)
        parsed = wallet.parse_uri(res.uri)
        # check that the decoded values match the original.
        for pay in parsed.uri.payments:
            assert pay.recipient_name == special_name, "Special characters in recipient name mismatch"
        assert parsed.uri.tx_description == special_desc, "Special characters in description mismatch"
        
        # build a well-formed multi-recipient URI and tack on unknown parameters.
        payments = [
            {'address': addr1, 'amount': 239390140000000, 'recipient_name': ''}
        ]
        uri_with_unknown = 'monero:' + addr1 + '?tx_amount=239.39014&foo=bar&baz=quux'
        parsed = wallet.parse_uri(uri_with_unknown)
        assert parsed.uri.payments[0].address == addr1
        assert parsed.uri.payments[0].amount == 239390140000000
        # unknown parameters should be collected in the unknown_parameters list.
        assert parsed.unknown_parameters == ['foo=bar', 'baz=quux'], "Unknown parameters mismatch"

if __name__ == '__main__':
    URITest().run_test()