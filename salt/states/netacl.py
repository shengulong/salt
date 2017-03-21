# -*- coding: utf-8 -*-
'''
Network ACL
===========

Manage the firewall configuration on the network device namaged through NAPALM.
The firewall configuration is generated by Capirca_.

.. _Capirca: https://github.com/google/capirca

.. versionadded:: Nitrogen

:codeauthor: Mircea Ulinic <mircea@cloudflare.com>
:maturity:   new
:depends:    capirca, napalm
:platform:   unix

Dependencies
------------

Capirca: ``pip install -e git+git@github.com:google/capirca.git#egg=aclgen``

To be able to load configuration on network devices,
it requires NAPALM_ library to be installed:  ``pip install napalm``.
Please check Installation_ for complete details.

.. _NAPALM: https://napalm.readthedocs.io
.. _Installation: https://napalm.readthedocs.io/en/latest/installation.html
'''
from __future__ import absolute_import

import logging
log = logging.getLogger(__file__)

# Import third party libs
try:
    # pylint: disable=W0611
    import aclgen
    HAS_CAPIRCA = True
    # pylint: enable=W0611
except ImportError:
    HAS_CAPIRCA = False

try:
    # pylint: disable=W0611
    import napalm_base
    # pylint: enable=W0611
    HAS_NAPALM = True
except ImportError:
    HAS_NAPALM = False

import salt.utils.napalm

# ------------------------------------------------------------------------------
# state properties
# ------------------------------------------------------------------------------

__virtualname__ = 'netacl'

# ------------------------------------------------------------------------------
# global variables
# ------------------------------------------------------------------------------

# ------------------------------------------------------------------------------
# property functions
# ------------------------------------------------------------------------------


def __virtual__():
    '''
    This module requires both NAPALM and Capirca.
    '''
    if HAS_CAPIRCA and HAS_NAPALM:
        return __virtualname__
    else:
        return (False, 'The netacl state cannot be loaded: \
                Please install capirca and napalm.')

# ------------------------------------------------------------------------------
# helper functions -- will not be exported
# ------------------------------------------------------------------------------

# ------------------------------------------------------------------------------
# callable functions
# ------------------------------------------------------------------------------


def term(name,
         filter_name,
         term_name,
         filter_options=None,
         pillar_key='acl',
         pillarenv=None,
         saltenv=None,
         merge_pillar=False,
         revision_id=None,
         revision_no=None,
         revision_date=True,
         revision_date_format='%Y/%m/%d',
         test=False,
         commit=True,
         debug=False,
         source_service=None,
         destination_service=None,
         **term_fields):
    '''
    Manage the configuration of a specific policy term.

    filter_name
        The name of the policy filter.

    term_name
        The name of the term.

    filter_options
        Additional filter options. These options are platform-specific.
        See the complete list of options_.

        .. _options: https://github.com/google/capirca/wiki/Policy-format#header-section

    pillar_key: ``acl``
        The key in the pillar containing the default attributes values. Default: ``acl``.

    pillarenv
        Query the master to generate fresh pillar data on the fly,
        specifically from the requested pillar environment.

    saltenv
        Included only for compatibility with
        :conf_minion:`pillarenv_from_saltenv`, and is otherwise ignored.

    merge_pillar: ``False``
        Merge the CLI variables with the pillar. Default: ``False``.

    revision_id
        Add a comment in the term config having the description for the changes applied.

    revision_no
        The revision count.

    revision_date: ``True``
        Boolean flag: display the date when the term configuration was generated. Default: ``True``.

    revision_date_format: ``%Y/%m/%d``
        The date format to be used when generating the perforce data. Default: ``%Y/%m/%d`` (<year>/<month>/<day>).

    test: ``False``
        Dry run? If set as ``True``, will apply the config, discard and return the changes.
        Default: ``False`` and will commit the changes on the device.

    commit: ``True``
        Commit? Default: ``True``.

    debug: ``False``
        Debug mode. Will insert a new key under the output dictionary,
        as ``loaded_config`` contaning the raw configuration loaded on the device.

    source_service
        A special service to choose from. This is a helper so the user is able to
        select a source just using the name, instead of specifying a source_port and protocol.

        As this module is available on Unix platforms only,
        it reads the IANA_ port assignment from /etc/services.

        If the user requires additional shortcuts to be referenced, they can add entries under /etc/services,
        which can be managed using the :mod:`file state <salt.states.file>`.

        .. _IANA: http://www.iana.org/assignments/port-numbers

    destination_service
        A special service to choose from. This is a helper so the user is able to
        select a source just using the name, instead of specifying a destination_port and protocol.
        Allows the same options as ``source_service``.

    **term_fields
        Term attributes.
        To see what fields are supported, please consult the list of supported keywords_.
            Some platforms have few other optional_ keywords.

            .. _keywords: https://github.com/google/capirca/wiki/Policy-format#keywords
            .. _optional: https://github.com/google/capirca/wiki/Policy-format#optionally-supported-keywords

    .. note::
        The following fields are accepted:

        - action
        - address
        - address_exclude
        - comment
        - counter
        - expiration
        - destination_address
        - destination_address_exclude
        - destination_port
        - destination_prefix
        - forwarding_class
        - forwarding_class_except
        - logging
        - log_name
        - loss_priority
        - option
        - policer
        - port
        - precedence
        - principals
        - protocol
        - protocol_except
        - qos
        - pan_application
        - routing_instance
        - source_address
        - source_address_exclude
        - source_port
        - source_prefix
        - verbatim
        - packet_length
        - fragment_offset
        - hop_limit
        - icmp_type
        - ether_type
        - traffic_class_count
        - traffic_type
        - translated
        - dscp_set
        - dscp_match
        - dscp_except
        - next_ip
        - flexible_match_range
        - source_prefix_except
        - destination_prefix_except
        - vpn
        - source_tag
        - destination_tag
        - source_interface
        - destination_interface
        - flattened
        - flattened_addr
        - flattened_saddr
        - flattened_daddr

    .. note::
        The following fields can be also a single value and a list of values:

        - action
        - address
        - address_exclude
        - comment
        - destination_address
        - destination_address_exclude
        - destination_port
        - destination_prefix
        - forwarding_class
        - forwarding_class_except
        - logging
        - option
        - port
        - precedence
        - principals
        - protocol
        - protocol_except
        - pan_application
        - source_address
        - source_address_exclude
        - source_port
        - source_prefix
        - verbatim
        - icmp_type
        - ether_type
        - traffic_type
        - dscp_match
        - dscp_except
        - flexible_match_range
        - source_prefix_except
        - destination_prefix_except
        - source_tag
        - destination_tag
        - source_service
        - destination_service

        Example: ``destination_address`` can be either defined as:

        .. code-block:: yaml

            destination_address: 172.17.17.1/24

        or as a list of destination IP addresses:

        .. code-block:: yaml

            destination_address:
                - 172.17.17.1/24
                - 172.17.19.1/24

        or a list of services to be matched:

        .. code-block:: yaml

            source_service:
                - ntp
                - snmp
                - ldap
                - bgpd

    .. note::
        The port fields ``source_port`` and ``destination_port`` can be used as above to select either
        a single value, either a list of values, but also they can select port ranges. Example:

        .. code-block:: yaml

            source_port:
                - [1000, 2000]
                - [3000, 4000]

        With the configuration above, the user is able to select the 1000-2000 and 3000-4000 source port ranges.

    CLI Example:

    .. code-block:: bash

        salt 'edge01.bjm01' state.sls router.acl

    Output Example:

    .. code-block:: yaml

        edge01.sfo04:
        ----------
                  ID: update_icmp_first_term
            Function: netacl.term
              Result: None
             Comment: Testing mode: Configuration discarded.
             Started: 12:49:09.174179
            Duration: 5751.882 ms
             Changes:
                      ----------
                      diff:
                          [edit firewall]
                          +    family inet {
                          +        /*
                          +         ** $Id: update_icmp_first_term $
                          +         ** $Date: 2017/02/30 $
                          +         **
                          +         */
                          +        filter block-icmp {
                          +            term first-term {
                          +                from {
                          +                    protocol icmp;
                          +                }
                          +                then {
                          +                    reject;
                          +                }
                          +            }
                          +        }
                          +    }

        Summary for edge01.sfo04
        ------------
        Succeeded: 1 (unchanged=1, changed=1)
        Failed:    0
        ------------
        Total states run:     1
        Total run time:   5.752 s

    Pillar example:

    .. code-block:: yaml

        firewall:
          block-icmp:
            first-term:
              protocol:
                - icmp
              action: reject

    State SLS example:

    .. code-block:: yaml

        {%- set filter_name = 'block-icmp' -%}
        {%- set term_name = 'first-term' -%}
        {%- set my_term_cfg = pillar['acl'][filter_name][term_name] -%}

        update_icmp_first_term:
          netacl.term:
            - filter_name: {{ filter_name }}
            - filter_options:
                - not-interface-specific
            - term_name: {{ term_name }}
            - {{ my_term_cfg | json }}

    When passing retrieved pillar data into the state file, it is strongly
    recommended to use the json serializer explicitly (`` | json``),
    instead of relying on the default Python serializer.
    '''
    ret = salt.utils.napalm.default_ret(name)
    test = __opts__['test'] or test
    if not filter_options:
        filter_options = []
    loaded = __salt__['netacl.load_term_config'](filter_name,
                                                 term_name,
                                                 filter_options=filter_options,
                                                 pillar_key=pillar_key,
                                                 pillarenv=pillarenv,
                                                 saltenv=saltenv,
                                                 merge_pillar=merge_pillar,
                                                 revision_id=revision_id if revision_id else name,
                                                 revision_no=revision_no,
                                                 revision_date=revision_date,
                                                 revision_date_format=revision_date_format,
                                                 source_service=source_service,
                                                 destination_service=destination_service,
                                                 test=test,
                                                 commit=commit,
                                                 debug=debug,
                                                 **term_fields)
    return salt.utils.napalm.loaded_ret(ret, loaded, test, debug)


def filter(name,  # pylint: disable=redefined-builtin
           filter_name,
           filter_options=None,
           terms=None,
           pillar_key='acl',
           pillarenv=None,
           saltenv=None,
           merge_pillar=False,
           only_lower_merge=False,
           revision_id=None,
           revision_no=None,
           revision_date=True,
           revision_date_format='%Y/%m/%d',
           test=False,
           commit=True,
           debug=False):
    '''
    Generate and load the configuration of a policy filter.

    filter_name
        The name of the policy filter.

    filter_options
        Additional filter options. These options are platform-specific.
        See the complete list of options_.

        .. _options: https://github.com/google/capirca/wiki/Policy-format#header-section

    terms
        Dictionary of terms for this policy filter.
        If not specified or empty, will try to load the configuration from the pillar,
        unless ``merge_pillar`` is set as ``False``.

    pillar_key: ``acl``
        The key in the pillar containing the default attributes values. Default: ``acl``.

    pillarenv
        Query the master to generate fresh pillar data on the fly,
        specifically from the requested pillar environment.

    saltenv
        Included only for compatibility with
        :conf_minion:`pillarenv_from_saltenv`, and is otherwise ignored.

    merge_pillar: ``False``
        Merge the CLI variables with the pillar. Default: ``False``

    only_lower_merge: ``False``
        Specify if it should merge only the terms fields. Otherwise it will try
        to merge also filters fields. Default: ``False``.
        This option requires ``merge_pillar``, otherwise it is ignored.

    revision_id
        Add a comment in the filter config having the description for the changes applied.

    revision_no
        The revision count.

    revision_date: ``True``
        Boolean flag: display the date when the filter configuration was generated. Default: ``True``.

    revision_date_format: ``%Y/%m/%d``
        The date format to be used when generating the perforce data. Default: ``%Y/%m/%d`` (<year>/<month>/<day>).

    test: ``False``
        Dry run? If set as ``True``, will apply the config, discard and return the changes.
        Default: ``False`` and will commit the changes on the device.

    commit: ``True``
        Commit? Default: ``True``.

    debug: ``False``
        Debug mode. Will insert a new key under the output dictionary,
        as ``loaded_config`` contaning the raw configuration loaded on the device.

    CLI Example:

    .. code-block:: bash

        salt 'edge01.flw01' state.sls router.acl test=True

    Output Example:

    .. code-block:: yaml

        edge01.flw01:
        ----------
                  ID: my-filter
            Function: netacl.filter
              Result: None
             Comment: Testing mode: Configuration discarded.
             Started: 12:24:40.598232
            Duration: 2437.139 ms
             Changes:
                      ----------
                      diff:
                          ---
                          +++
                          @@ -1228,9 +1228,24 @@
                          !
                          +ipv4 access-list my-filter
                          + 10 remark $Id: my-filter_state $
                          + 20 remark $Revision: 5 $
                          + 30 remark my-other-term
                          + 40 permit tcp any range 5678 5680 any
                          +!
                          +!
                      loaded:
                          ! $Id: my-filter_state $
                          ! $Revision: 5 $
                          no ipv6 access-list my-filter
                          ipv6 access-list my-filter
                           remark $Id: my-filter_state $
                           remark $Revision: 5 $
                           remark my-other-term
                           permit tcp any range 5678 5680 any
                          exit

        Summary for edge01.flw01
        ------------
        Succeeded: 1 (unchanged=1, changed=1)
        Failed:    0
        ------------
        Total states run:     1
        Total run time:   2.437 s

    Pillar example:

    .. code-block:: yaml

        acl:
          my-filter:
            options:
              - inet6
            my-term:
              source_port: [1234, 1235]
              protocol:
                - tcp
                - udp
              source_address: 1.2.3.4
              action: reject
            my-other-term:
              source_port:
                - [5678, 5680]
              protocol: tcp
              action: accept

    State SLS Example:

    .. code-block:: yaml

        {% set my_filter_cfg = pillar.get('acl').get('my-filter') -%}
        my-filter_state:
          netacl.filter:
            - filter_name: my-filter
            - terms: {{ my_filter_cfg | json }}
            - revision_date: false
            - revision_no: 5
            - debug: true

    In the example above, as ``inet6`` has been specified in the ``filter_options``,
    the configuration chunk referring to ``my-term`` has been ignored as it referred to
    IPv4 only (from ``source_address`` field).

    When passing retrieved pillar data into the state file, it is strongly
    recommended to use the json serializer explicitly (`` | json``),
    instead of relying on the default Python serializer.
    '''
    ret = salt.utils.napalm.default_ret(name)
    test = __opts__['test'] or test
    if not filter_options:
        filter_options = []
    if not terms:
        terms = {}
    loaded = __salt__['netacl.load_filter_config'](filter_name,
                                                   filter_options=filter_options,
                                                   terms=terms,
                                                   pillar_key=pillar_key,
                                                   pillarenv=pillarenv,
                                                   saltenv=saltenv,
                                                   merge_pillar=merge_pillar,
                                                   only_lower_merge=only_lower_merge,
                                                   revision_id=revision_id if revision_id else name,
                                                   revision_no=revision_no,
                                                   revision_date=revision_date,
                                                   revision_date_format=revision_date_format,
                                                   test=test,
                                                   commit=commit,
                                                   debug=debug)
    return salt.utils.napalm.loaded_ret(ret, loaded, test, debug)


def managed(name,
            filters=None,
            pillar_key='acl',
            pillarenv=None,
            saltenv=None,
            merge_pillar=False,
            only_lower_merge=False,
            revision_id=None,
            revision_no=None,
            revision_date=True,
            revision_date_format='%Y/%m/%d',
            test=False,
            commit=True,
            debug=False):
    '''
    Manage the whole firewall configuration.

    filters
        Dictionary of filters for this policy.
        If not specified or empty, will try to load the configuration from the pillar,
        unless ``merge_pillar`` is set as ``False``.

    pillar_key: ``acl``
        The key in the pillar containing the default attributes values. Default: ``acl``.

    pillarenv
        Query the master to generate fresh pillar data on the fly,
        specifically from the requested pillar environment.

    saltenv
        Included only for compatibility with
        :conf_minion:`pillarenv_from_saltenv`, and is otherwise ignored.

    merge_pillar: ``False``
        Merge the CLI variables with the pillar. Default: ``False``.

    only_lower_merge: ``False``
        Specify if it should merge only the filters and terms fields. Otherwise it will try
        to merge everything at the policy level. Default: ``False``.
        This option requires ``merge_pillar``, otherwise it is ignored.

    test: ``False``
        Dry run? If set as ``True``, will apply the config, discard and return the changes.
        Default: ``False`` and will commit the changes on the device.

    revision_id
        Add a comment in the policy config having the description for the changes applied.

    revision_no
        The revision count.

    revision_date: ``True``
        Boolean flag: display the date when the policy configuration was generated. Default: ``True``.

    revision_date_format: ``%Y/%m/%d``
        The date format to be used when generating the perforce data. Default: ``%Y/%m/%d`` (<year>/<month>/<day>).

    commit: ``True``
        Commit? Default: ``True``.

    debug: ``False``
        Debug mode. Will insert a new key under the output dictionary,
        as ``loaded_config`` contaning the raw configuration loaded on the device.

    CLI Example:

    .. code-block:: bash

        salt 'edge01.bjm01' state.sls router.acl test=True

    Output Example:

    .. code-block:: yaml

        edge01.bjm01:
            ----------
                      ID: netacl_example
                Function: netacl.managed
                  Result: None
                 Comment: Testing mode: Configuration discarded.
                 Started: 12:03:24.807023
                Duration: 5569.453 ms
                 Changes:
                          ----------
                          diff:
                              [edit firewall]
                              +    family inet {
                              +        /*
                              +         ** $Id: netacl_example $
                              +         ** $Date: 2017/07/03 $
                              +         ** $Revision: 2 $
                              +         **
                              +         */
                              +        filter block-icmp {
                              +            interface-specific;
                              +            term first-term {
                              +                from {
                              +                    protocol icmp;
                              +                }
                              +                then {
                              +                    reject;
                              +                }
                              +            }
                              +        }
                              +        /*
                              +         ** $Id: netacl_example $
                              +         ** $Date: 2017/07/03 $
                              +         ** $Revision: 2 $
                              +         **
                              +         */
                              +        filter my-filter {
                              +            interface-specific;
                              +            term my-term {
                              +                from {
                              +                    source-address {
                              +                        1.2.3.4/32;
                              +                    }
                              +                    protocol [ tcp udp ];
                              +                    source-port [ 1234 1235 ];
                              +                }
                              +                then {
                              +                    reject;
                              +                }
                              +            }
                              +            term my-other-term {
                              +                from {
                              +                    protocol tcp;
                              +                    source-port 5678-5680;
                              +                }
                              +                then accept;
                              +            }
                              +        }
                              +    }
                          loaded:
                              firewall {
                                  family inet {
                                      replace:
                                      /*
                                      ** $Id: netacl_example $
                                      ** $Date: 2017/07/03 $
                                      ** $Revision: 2 $
                                      **
                                      */
                                      filter block-icmp {
                                          interface-specific;
                                          term first-term {
                                              from {
                                                  protocol icmp;
                                              }
                                              then {
                                                  reject;
                                              }
                                          }
                                      }
                                  }
                              }
                              firewall {
                                  family inet {
                                      replace:
                                      /*
                                      ** $Id: netacl_example $
                                      ** $Date: 2017/07/03 $
                                      ** $Revision: 2 $
                                      **
                                      */
                                      filter my-filter {
                                          interface-specific;
                                          term my-term {
                                              from {
                                                  source-address {
                                                      1.2.3.4/32;
                                                  }
                                                  protocol [ tcp udp ];
                                                  source-port [ 1234 1235 ];
                                              }
                                              then {
                                                  reject;
                                              }
                                          }
                                          term my-other-term {
                                              from {
                                                  protocol tcp;
                                                  source-port 5678-5680;
                                              }
                                              then accept;
                                          }
                                      }
                                  }
                              }

            Summary for edge01.bjm01
            ------------
            Succeeded: 1 (unchanged=1, changed=1)
            Failed:    0
            ------------
            Total states run:     1
            Total run time:   5.569 s

    The policy configuration has been loaded from the pillar, having the following structure:

    .. code-block:: yaml

        firewall:
          my-filter:
            my-term:
              source_port: [1234, 1235]
              protocol:
                - tcp
                - udp
              source_address: 1.2.3.4
              action: reject
            my-other-term:
              source_port:
                - [5678, 5680]
              protocol: tcp
              action: accept
          block-icmp:
            first-term:
              protocol:
                - icmp
              action: reject

    Example SLS file:

    .. code-block:: yaml

        {%- set fw_filters = pillar.get('firewall', {}) -%}
        netacl_example:
          netacl.managed:
            - filters: {{ fw_filters | json }}
            - revision_no: 2
            - debug: true

    When passing retrieved pillar data into the state file, it is strongly
    recommended to use the json serializer explicitly (`` | json``),
    instead of relying on the default Python serializer.
    '''
    ret = salt.utils.napalm.default_ret(name)
    test = __opts__['test'] or test
    if not filters:
        filters = {}
    loaded = __salt__['netacl.load_policy_config'](filters=filters,
                                                   pillar_key=pillar_key,
                                                   pillarenv=pillarenv,
                                                   saltenv=saltenv,
                                                   merge_pillar=merge_pillar,
                                                   only_lower_merge=only_lower_merge,
                                                   revision_id=revision_id if revision_id else name,
                                                   revision_no=revision_no,
                                                   revision_date=revision_date,
                                                   revision_date_format=revision_date_format,
                                                   test=test,
                                                   commit=commit,
                                                   debug=debug)
    return salt.utils.napalm.loaded_ret(ret, loaded, test, debug)
