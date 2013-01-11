"""
Run a normal OpenERP HTTP process.
"""

import logging
import os
import threading

import openerp.cli.server
import openerp.service.wsgi_server
import openerp.tools.config

import common

_logger = logging.getLogger(__name__)

def run(args):
    os.environ["TZ"] = "UTC"

    if args.addons:
        args.addons = args.addons.split(':')
    else:
        args.addons = []

    config = openerp.tools.config
    config['addons_path'] = ','.join(args.addons)

    openerp.cli.server.check_root_user()
    openerp.netsvc.init_logger()
    #openerp.cli.server.report_configuration()
    openerp.cli.server.configure_babel_localedata_path()
    openerp.cli.server.setup_signal_handlers()

    target = openerp.service.wsgi_server.serve
    if not args.gevent:
        arg = (args.interface, int(args.port), args.threaded)
        threading.Thread(target=target, args=arg).start()
        openerp.cli.server.quit_on_signals()
    else:
        print "The --gevent option is not yet implemented."

def add_parser(subparsers):
    parser = subparsers.add_parser('web',
        description='Run a normal OpenERP HTTP process. By default a '
        'singly-threaded Werkzeug server is used.')
    common.add_addons_argument(parser)
    parser.add_argument('--interface', default='0.0.0.0',
        help='HTTP interface to listen on (default is %(default)s)')
    parser.add_argument('--port', metavar='INT', default=8069,
        help='HTTP port to listen on (default is %(default)s)')
    parser.add_argument('--threaded', action='store_true',
        help='Use a multithreaded Werkzeug server (incompatible with --gevent)')
    parser.add_argument('--gevent', action='store_true',
        help="Use gevent's WSGI server (incompatible with --threaded)")

    parser.set_defaults(run=run)
