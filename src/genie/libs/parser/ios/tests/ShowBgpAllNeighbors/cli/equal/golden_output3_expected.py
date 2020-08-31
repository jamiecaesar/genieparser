expected_output = {
    "list_of_neighbors": ["192.168.165.119"],
    "vrf": {
        "default": {
            "neighbor": {
                "192.168.165.119": {
                    "address_family": {
                        "l2vpn vpls": {
                            "advertise_bit": 0,
                            "bgp_table_version": 403,
                            "current_time": "0x233AE2F9",
                            "dynamic_slow_peer_recovered": "never",
                            "extended_community_attribute_sent": True,
                            "index": 4,
                            "last_detected_dynamic_slow_peer": "never",
                            "last_received_refresh_end_of_rib": "21:35:10",
                            "last_received_refresh_start_of_rib": "21:35:11",
                            "last_sent_refresh_end_of_rib": "04:52:13",
                            "last_sent_refresh_start_of_rib": "04:52:13",
                            "local_policy_denied_prefixes_counters": {
                                "inbound": {
                                    "bestpath_from_this_peer": "n/a",
                                    "originator_loop": 1206,
                                    "total": 1206,
                                },
                                "outbound": {
                                    "bestpath_from_this_peer": 1407,
                                    "originator_loop": "n/a",
                                    "total": 1407,
                                },
                            },
                            "max_nlri": 1,
                            "min_nlri": 0,
                            "neighbor_version": "403/0",
                            "output_queue_size": 0,
                            "prefix_activity_counters": {
                                "received": {
                                    "explicit_withdraw": 0,
                                    "implicit_withdraw": 1005,
                                    "prefixes_total": 1206,
                                    "used_as_bestpath": 201,
                                    "used_as_multipath": 0,
                                },
                                "sent": {
                                    "explicit_withdraw": 0,
                                    "implicit_withdraw": 1608,
                                    "prefixes_total": 1809,
                                    "used_as_bestpath": "n/a",
                                    "used_as_multipath": "n/a",
                                },
                            },
                            "refresh_activity_counters": {
                                "received": {
                                    "refresh_end_of_rib": 6,
                                    "refresh_start_of_rib": 6,
                                },
                                "sent": {
                                    "refresh_end_of_rib": 2,
                                    "refresh_start_of_rib": 2,
                                },
                            },
                            "refresh_epoch": 7,
                            "refresh_in": 1,
                            "refresh_out": 0,
                            "slow_peer_detection": False,
                            "slow_peer_split_update_group_dynamic": False,
                            "suppress_ldp_signaling": True,
                            "update_group_member": 4,
                        },
                        "vpnv4 unicast": {
                            "advertise_bit": 0,
                            "bgp_table_version": 33086714,
                            "community_attribute_sent": True,
                            "dynamic_slow_peer_recovered": "never",
                            "extended_community_attribute_sent": True,
                            "index": 1954,
                            "last_detected_dynamic_slow_peer": "never",
                            "last_received_refresh_end_of_rib": "21:34:52",
                            "last_received_refresh_start_of_rib": "21:35:11",
                            "last_sent_refresh_end_of_rib": "04:51:01",
                            "last_sent_refresh_start_of_rib": "04:52:13",
                            "local_policy_denied_prefixes_counters": {
                                "inbound": {
                                    "af_permit_check": "n/a",
                                    "af_update_check": "n/a",
                                    "bestpath_from_ibgp_peer": "n/a",
                                    "bestpath_from_this_peer": "n/a",
                                    "originator_loop": 151495,
                                    "total": 151495,
                                },
                                "outbound": {
                                    "af_permit_check": 84090,
                                    "af_update_check": 11509,
                                    "bestpath_from_ibgp_peer": 3488082,
                                    "bestpath_from_this_peer": 10473918,
                                    "originator_loop": "n/a",
                                    "total": 14057599,
                                },
                            },
                            "max_nlri": 270,
                            "min_nlri": 0,
                            "neighbor_version": "33086714/0",
                            "output_queue_size": 0,
                            "prefix_activity_counters": {
                                "received": {
                                    "explicit_withdraw": 4059067,
                                    "implicit_withdraw": 10255632,
                                    "prefixes_total": 16316598,
                                    "used_as_bestpath": 2005600,
                                    "used_as_multipath": 0,
                                },
                                "sent": {
                                    "explicit_withdraw": 2045210,
                                    "implicit_withdraw": 81710,
                                    "prefixes_total": 131522,
                                    "used_as_bestpath": "n/a",
                                    "used_as_multipath": "n/a",
                                },
                            },
                            "refresh_activity_counters": {
                                "received": {
                                    "refresh_end_of_rib": 6,
                                    "refresh_start_of_rib": 6,
                                },
                                "sent": {
                                    "refresh_end_of_rib": 4,
                                    "refresh_start_of_rib": 4,
                                },
                            },
                            "refresh_epoch": 7,
                            "refresh_in": 19,
                            "refresh_out": 72,
                            "slow_peer_detection": False,
                            "slow_peer_split_update_group_dynamic": False,
                            "update_group_member": 1954,
                        },
                    },
                    "bgp_event_timer": {
                        "next": {
                            "ackhold": "0x0",
                            "deadwait": "0x0",
                            "giveup": "0x0",
                            "keepalive": "0x0",
                            "linger": "0x0",
                            "pmtuager": "0x0",
                            "processq": "0x0",
                            "retrans": "0x0",
                            "sendwnd": "0x0",
                            "timewait": "0x0",
                        },
                        "starts": {
                            "ackhold": 137871,
                            "deadwait": 0,
                            "giveup": 0,
                            "keepalive": 0,
                            "linger": 0,
                            "pmtuager": 1,
                            "processq": 0,
                            "retrans": 55014,
                            "sendwnd": 8,
                            "timewait": 0,
                        },
                        "wakeups": {
                            "ackhold": 6940,
                            "deadwait": 0,
                            "giveup": 0,
                            "keepalive": 0,
                            "linger": 0,
                            "pmtuager": 1,
                            "processq": 0,
                            "retrans": 14,
                            "sendwnd": 0,
                            "timewait": 0,
                        },
                    },
                    "bgp_neighbor_session": {"sessions": 1},
                    "bgp_negotiated_capabilities": {
                        "enhanced_refresh": "advertised and received",
                        "four_octets_asn": "advertised and received",
                        "graceful_restart": "advertised and received",
                        "graceful_restart_af_advertised_by_peer": [
                            "vpnv4 unicast",
                            "l2vpn vpls",
                        ],
                        "l2vpn_vpls": "advertised and received",
                        "remote_restart_timer": 120,
                        "route_refresh": "advertised and received(new)",
                        "stateful_switchover": "NO for session 1",
                        "vpnv4_unicast": "advertised and received",
                    },
                    "bgp_negotiated_keepalive_timers": {
                        "hold_time": 90,
                        "keepalive_interval": 30,
                        "min_holdtime": 15,
                    },
                    "bgp_neighbor_counters": {
                        "messages": {
                            "in_queue_depth": 0,
                            "out_queue_depth": 0,
                            "received": {
                                "keepalives": 4709,
                                "notifications": 0,
                                "opens": 1,
                                "route_refresh": 0,
                                "total": 127376,
                                "updates": 122642,
                            },
                            "sent": {
                                "keepalives": 5188,
                                "notifications": 0,
                                "opens": 1,
                                "route_refresh": 10,
                                "total": 55036,
                                "updates": 49825,
                            },
                        }
                    },
                    "bgp_session_transport": {
                        "ack_hold": 200,
                        "address_tracking_status": "enabled",
                        "connection": {
                            "dropped": 3,
                            "established": 4,
                            "last_reset": "1d16h",
                            "reset_reason": "Neighbor reset",
                        },
                        "connection_state": "estab",
                        "connection_tableid": 0,
                        "datagram": {
                            "datagram_received": {
                                "out_of_order": 0,
                                "total_data": 322194190,
                                "value": 392625,
                                "with_data": 254123,
                            },
                            "datagram_sent": {
                                "fastretransmit": 1992,
                                "partialack": 1067,
                                "retransmit": 22,
                                "second_congestion": 0,
                                "total_data": 131166632,
                                "value": 434376,
                                "with_data": 102975,
                            },
                        },
                        "delrcvwnd": 741,
                        "ecn_connection": "disabled",
                        "enqueued_packets": {
                            "input_packet": 0,
                            "mis_ordered_packet": 0,
                            "retransmit_packet": 0,
                        },
                        "fast_lock_acquisition_failures": 0,
                        "gr_restart_time": 120,
                        "gr_stalepath_time": 360,
                        "graceful_restart": "enabled",
                        "io_status": 1,
                        "ip_precedence_value": 6,
                        "irs": 3539951191,
                        "iss": 61822047,
                        "krtt": 0,
                        "lock_slow_path": 0,
                        "max_rtt": 1019,
                        "maximum_output_segment_queue_size": 50,
                        "maxrcvwnd": 16384,
                        "min_rtt": 0,
                        "min_time_between_advertisement_runs": 0,
                        "minimum_incoming_ttl": 0,
                        "option_flags": "nagle, path mtu capable",
                        "outgoing_ttl": 255,
                        "packet_fast_path": 0,
                        "packet_fast_processed": 0,
                        "packet_slow_path": 0,
                        "rcv_scale": 0,
                        "rcvnxt": 3862145382,
                        "rcvwnd": 15643,
                        "receive_idletime": 15525,
                        "rib_route_ip": "192.168.165.119",
                        "rtto": 1003,
                        "rtv": 3,
                        "sent_idletime": 15727,
                        "snd_scale": 0,
                        "sndnxt": 190308893,
                        "snduna": 190308893,
                        "sndwnd": 15510,
                        "srtt": 1000,
                        "sso": False,
                        "status_flags": "active open",
                        "tcp_path_mtu_discovery": "enabled",
                        "tcp_semaphore": "0x7FDE7F22E108",
                        "tcp_semaphore_status": "FREE",
                        "transport": {
                            "foreign_host": "192.168.165.119",
                            "foreign_port": "179",
                            "local_host": "10.169.197.254",
                            "local_port": "13427",
                            "mss": 1400,
                        },
                        "unread_input_bytes": 0,
                        "uptime": 144452788,
                    },
                    "bgp_version": 4,
                    "link": "internal",
                    "remote_as": 5918,
                    "router_id": "192.168.165.119",
                    "session_state": "Established",
                    "shutdown": False,
                }
            }
        }
    },
}