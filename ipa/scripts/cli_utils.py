# -*- coding: utf-8 -*-

"""Utility methods for ipa cli endpoints."""

# Copyright (c) 2017 SUSE LLC
#
# This file is part of ipa. Ipa provides an api and command line
# utilities for testing images in the Public Cloud.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import os
import sys

import click

from ipa.ipa_controller import collect_results


def echo_log(log_file, no_color):
    try:
        with open(log_file, 'r') as f:
            log_output = ''.join(f.readlines())
    except Exception as error:
        echo_style(
            'Unable to open results log file: %s' % error,
            no_color,
            fg='red'
        )
        sys.exit(1)

    click.echo(log_output)


def echo_results(data, no_color, verbose=False):
    """Print test results in nagios style format."""
    summary = data['summary']
    if 'failed' in summary or 'error' in summary:
        fg = 'red'
        status = 'FAILED'
    else:
        fg = 'green'
        status = 'PASSED'

    results = '{} tests={}|pass={}|fail={}|error={}'.format(
        status,
        str(summary.get('num_tests', 0)),
        str(summary.get('passed', 0)),
        str(summary.get('failed', 0)),
        str(summary.get('error', 0))
    )
    echo_style(results, no_color, fg=fg)

    if verbose:
        echo_verbose_results(data, no_color)


def echo_results_file(results_file, no_color, verbose=False):
    """Print test results in nagios style format."""
    try:
        data = collect_results(results_file)
    except ValueError:
        echo_style(
            'The results file is not the proper json format.',
            no_color,
            fg='red'
        )
        sys.exit(1)
    except KeyError as error:
        echo_style(
            'The results json is missing key: %s' % error,
            no_color,
            fg='red'
        )
        sys.exit(1)
    except Exception as error:
        echo_style(
            'Unable to process results file: %s' % error,
            no_color,
            fg='red'
        )
        sys.exit(1)

    echo_results(data, no_color, verbose)


def echo_style(message, no_color, fg='yellow'):
    if no_color:
        click.echo(message)
    else:
        click.secho(message, fg=fg)


def echo_verbose_results(data, no_color):
    """Print list of tests and result of each test."""
    click.echo()
    click.echo(
        '\n'.join(
            '{}: {}'.format(key, val) for key, val in data['info'].items()
        )
    )
    click.echo()
    for test in data['tests']:
        if test['outcome'] == 'passed':
            fg = 'green'
        else:
            fg = 'red'

        name = test['name'].split(os.sep)[-1].replace('.py', '')
        echo_style(
            '{} {}'.format(name, test['outcome'].upper()),
            no_color,
            fg=fg
        )


def results_history(history_log, no_color):
    """Display a list of ipa test results history."""
    try:
        with open(history_log, 'r') as f:
            history_file = ''.join(f.readlines())
    except Exception as error:
        echo_style(
            'Unable to process results history log.',
            no_color,
            fg='red'
        )
        sys.exit(1)

    click.echo(history_file)