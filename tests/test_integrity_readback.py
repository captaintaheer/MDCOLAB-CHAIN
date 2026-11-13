"""Tests for the ledger read-back integrity check in automate_layers.collect_ledger_metrics.

A stub `peer` executable stands in for the Fabric peer CLI, so no Fabric network or Docker is
needed. The stub accepts every CreateAsset invoke immediately and makes an asset readable only
after a configurable number of ReadAsset queries, which reproduces an invoke that has been
accepted by the orderer but is not yet committed (throughput mode, no --waitForEvent).

Run: python -m unittest tests/test_integrity_readback.py -v
"""
import io, contextlib, os, stat, sys, tempfile, textwrap, unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
import automate_layers as al  # noqa: E402

STUB = textwrap.dedent('''\
    #!/usr/bin/env python3
    import fcntl, json, os, sys
    here = os.path.dirname(os.path.abspath(__file__))
    state = os.path.join(here, 'state.json')
    lock = open(os.path.join(here, 'state.lock'), 'w')
    fcntl.flock(lock, fcntl.LOCK_EX)  # invokes run concurrently in throughput mode
    s = json.load(open(state)) if os.path.exists(state) else {'assets': {}, 'queries': 0}
    args = sys.argv[1:]
    call = json.loads(args[args.index('-c') + 1])
    if args[1] == 'invoke':
        aid, value = call['Args'][0], call['Args'][1]
        s['assets'][aid] = value
        json.dump(s, open(state, 'w'))
        sys.exit(0)
    aid = call['Args'][0]
    s['queries'] += 1
    json.dump(s, open(state, 'w'))
    if aid not in s['assets'] or s['queries'] <= int(os.environ.get('STUB_COMMIT_AFTER_QUERIES', '0')):
        sys.stderr.write('Error: endorsement failure during query. response: status:500 message:"the asset %s does not exist"\\n' % aid)
        sys.exit(1)
    value = s['assets'][aid]
    if os.environ.get('STUB_TAMPER') == '1':
        value = '0' * len(value)
    print(json.dumps({'ID': aid, 'Color': value, 'Size': 0, 'Owner': 'system', 'AppraisedValue': 0}))
''')

DIGEST = 'ab' * 32


class ReadBackIntegrityTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        base = self.tmp.name
        tn = os.path.join(base, 'layer-3', 'fabric-samples', 'test-network')
        bindir = os.path.join(base, 'layer-3', 'fabric-samples', 'bin')
        os.makedirs(tn); os.makedirs(bindir); os.makedirs(os.path.join(base, 'layer-2', 'output'))
        with open(os.path.join(base, 'layer-2', 'output', 'result_hash.txt'), 'w') as f:
            f.write(DIGEST + '\n')
        peer = os.path.join(bindir, 'peer')
        with open(peer, 'w') as f:
            f.write(STUB)
        os.chmod(peer, os.stat(peer).st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
        self.base = base
        self._env = {k: os.environ.get(k) for k in ('STUB_COMMIT_AFTER_QUERIES', 'STUB_TAMPER', 'READBACK_TIMEOUT_S')}

    def tearDown(self):
        for k, v in self._env.items():
            if v is None:
                os.environ.pop(k, None)
            else:
                os.environ[k] = v
        self.tmp.cleanup()

    def run_ledger(self, **env):
        os.environ.update(env)
        with contextlib.redirect_stdout(io.StringIO()):
            return al.collect_ledger_metrics(self.base, tx_count=4, mode='throughput', disable_peer_stats=True,
                                             fast=True, concurrency=4)

    def test_pending_commit_single_query_fails(self):
        # One query only (no waiting), as in the previous implementation: the asset is not yet visible.
        m = self.run_ledger(STUB_COMMIT_AFTER_QUERIES='3', READBACK_TIMEOUT_S='0')
        self.assertEqual(m['tx_success_rate'], 1.0)
        self.assertFalse(m['integrity_ok'])
        self.assertTrue(m['integrity_reason'].startswith('query_failed'))
        self.assertEqual(m['query_latency'], 0.0)

    def test_pending_commit_polling_matches(self):
        m = self.run_ledger(STUB_COMMIT_AFTER_QUERIES='3', READBACK_TIMEOUT_S='15')
        self.assertEqual(m['tx_success_rate'], 1.0)
        self.assertTrue(m['integrity_ok'])
        self.assertEqual(m['integrity_reason'], 'digest_match')
        self.assertGreater(m['query_latency'], 0.0)

    def test_tampered_value_is_detected(self):
        m = self.run_ledger(STUB_COMMIT_AFTER_QUERIES='0', STUB_TAMPER='1', READBACK_TIMEOUT_S='15')
        self.assertFalse(m['integrity_ok'])
        self.assertEqual(m['integrity_reason'], 'digest_mismatch')


if __name__ == '__main__':
    unittest.main()
