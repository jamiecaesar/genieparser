''' showversion.py

Example parser class

'''
import xmltodict
import re
from ats import tcl
from ats.tcl.keyedlist import KeyedList
from metaparser import MetaParser
from metaparser.util.schemaengine import Schema, Any, Optional, Or, And, Default, Use

def regexp(expression):
    def match(value):
        if re.match(expression,value):
            return value
        else:
            raise TypeError("Value '%s' doesnt match regex '%s'"
                              %(value,expression))
    return match

class ShowOspfSchema(MetaParser):

    schema = {'process_id':
                {Any():
                    {'vrf':
                        {Any():
                            {'id': str,
                             Optional('nsr'): str,
                             Optional('nsf'): str,
                             Optional('ospf_rtr_type'): str,
                             Optional('num_of_areas'): str,
                             Optional('num_of_normal_areas'): str,
                             Optional('num_of_stub_areas'): str,
                             Optional('num_of_nssa_areas'): str,
                             Optional('area'):
                                 {regexp('(.*)'):
                                     {'interfaces_in_this_area': Or(str, KeyedList({})),
                                      'active_interfaces': Or(str, KeyedList({}))},
                                 },
                             }
                         },
                     }
                 },
            }


class ShowOspf(ShowOspfSchema, MetaParser):
    """ parser class - implements detail parsing mechanisms for cli, xml, and
    yang output.
    """
    #*************************
    # schema - class variable
    #
    # Purpose is to make sure the parser always return the output
    # (nested dict) that has the same data structure across all supported
    # parsing mechanisms (cli(), yang(), xml()).


    def cli(self):
        ''' parsing mechanism: cli

        Function cli() defines the cli type output parsing mechanism which
        typically contains 3 steps: executing, transforming, returning
        '''
        cmd = 'show ospf'.format()
        out = self.device.execute(cmd)
        ospf_dict = {}
        entry = None
        for line in out.splitlines():
            line = line.rstrip()
            p1 = re.compile(r'\s*Routing +Process +\"ospf +(?P<process_id>[0-9]+)\" +with +ID +(?P<router_id>[0-9\.]+)$')
            m = p1.match(line)
            if m:
                pid = m.groupdict()['process_id']
                rid = m.groupdict()['router_id']
                vrf = 'default'
                if 'process_id' not in ospf_dict:
                    ospf_dict['process_id'] = {}
                ospf_dict['process_id'][pid] = {}
                if 'vrf' not in ospf_dict['process_id'][pid]:
                    ospf_dict['process_id'][pid]['vrf'] = {}
                if vrf not in ospf_dict['process_id'][pid]['vrf']:
                    ospf_dict['process_id'][pid]['vrf'][vrf] = {}
                ospf_dict['process_id'][pid]['vrf'][vrf]['id'] = rid
                ospf_dict['process_id'][pid]['vrf'][vrf]['nsf'] = 'disabled'
                continue

            p2 = re.compile(r'\s*NSR \(Non\-stop routing\) is (?P<nsr>[a-zA-Z]+)$')
            m = p2.match(line)
            if m:
                ospf_dict['process_id'][pid]['vrf'][vrf]['nsr'] = m.groupdict()['nsr']
                continue

            p3 = re.compile(r'\s*It is an (?P<ospf_rtr_type>.*)$')
            m = p3.match(line)
            if m:
                ospf_dict['process_id'][pid]['vrf'][vrf]['ospf_rtr_type'] = m.groupdict()['ospf_rtr_type']
                continue

            p4 = re.compile(r'\s*Number +of +areas +in +this +router +is (?P<num_of_areas>[0-9]+). '
                         r'(?P<num_of_normal_area>[0-9]+) normal (?P<num_of_stub_area>[0-9]+) '
                         r'stub (?P<num_of_nssa_area>[0-9]+) nssa')
            m = p4.match(line)
            if m:
                ospf_dict['process_id'][pid]['vrf'][vrf]['num_of_areas'] = m.groupdict()['num_of_areas']
                ospf_dict['process_id'][pid]['vrf'][vrf]['num_of_normal_areas'] = m.groupdict()['num_of_normal_area']
                ospf_dict['process_id'][pid]['vrf'][vrf]['num_of_stub_areas'] = m.groupdict()['num_of_stub_area']
                ospf_dict['process_id'][pid]['vrf'][vrf]['num_of_nssa_areas'] = m.groupdict()['num_of_nssa_area']
                continue
            p5 = re.compile(r'\s*Non\-Stop +Forwarding +(?P<nsf>[a-zA-Z]+)$')
            m = p5.match(line)
            if m:
                ospf_dict['process_id'][pid]['vrf'][vrf]['nsf'] = m.groupdict()['nsf']
                continue

            p6 = re.compile(r'^\s+Area +(?P<area>.*)$')
            m = p6.match(line)
            if m:
                area = m.groupdict()['area']
                if 'area' not in ospf_dict['process_id'][pid]['vrf'][vrf]:
                    ospf_dict['process_id'][pid]['vrf'][vrf]['area'] = {}
                if area not in ospf_dict['process_id'][pid]['vrf'][vrf]['area']:
                    ospf_dict['process_id'][pid]['vrf'][vrf]['area'][area] = {}
                continue

            p7 = re.compile(r'\s+Number +of +interfaces +in +this +area +is +(?P<interfaces_in_this_area>\d+)$')
            m = p7.match(line)
            if m:
                ospf_dict['process_id'][pid]['vrf'][vrf]['area'][area]['interfaces_in_this_area'] = m.groupdict()['interfaces_in_this_area']
                ospf_dict['process_id'][pid]['vrf'][vrf]['area'][area]['active_interfaces'] = m.groupdict()['interfaces_in_this_area']
                continue

        return ospf_dict

    def xml(self):
        ''' parsing mechanism: xml

        Function xml() defines the xml type output parsing mechanism which
        typically contains 3 steps: executing, transforming, returning
        '''
        output =  tcl.q.caas.abstract(device=self.device.handle,
                                      exec='show ospf')
        result = tcl.cast_any(output[1])

        return result

    def yang(self):
        ''' parsing mechanism: yang

        Function yang() defines the yang type output parsing mechanism which
        typically contains 3 steps: executing, transforming, returning
        '''

        ret = {}
        cmd = '''<native><router><ospf/></router></native>'''
        output = self.device.get(('subtree', cmd))

        for data in output.data:
            for native in data:
                for ospf in native:
                    process_id = None
                    nsr = None
                    vrf = 'default'
                    ref = None
                    router_id = None
                    id_value = 0
                    default_cost = None
                    process_id = None
                    areas = {}
                    for value in ospf:
                        # Remove the namespace
                        text = value.tag[value.tag.find('}')+1:]
                        if text == 'id':
                            process_id = value.text
                            continue
                        if text == 'nsr':
                            nsr = value.text
                            continue
                        if text == 'vrf':
                            vrf = value.text
                            continue
                        if text == 'auto-cost':
                            for auto in value:
                                text = auto.tag[auto.tag.find('}')+1:]
                                if text == 'reference-bandwidth':
                                    ref = auto.text
                            continue
                        if text == 'router-id':
                            router_id = value.text
                            continue

                        # Can have multiple area in one ospf
                        if text == 'area':
                            id_value = 0
                            default_cost = None
                            for area in value:
                                text = area.tag[area.tag.find('}')+1:]
                                if text == 'id':
                                    id_value = area.text
                                if text == 'default-cost':
                                    default_cost = area.text
                            areas[id_value] = {}
                            areas[id_value]['default_cost'] = default_cost


                    # Let's build it now
                    if 'process_id' not in ret:
                        ret['process_id'] = {}
                    ret['process_id'][process_id] = {}
                    ret['process_id'][process_id]['vrf'] = {}
                    ret['process_id'][process_id]['vrf'][vrf] = {}
                    if router_id is not None:
                        ret['process_id'][process_id]['vrf'][vrf]['id'] = router_id
                    if areas != {}:
                        ret['process_id'][process_id]['vrf'][vrf]['area'] = areas
                    if ref is not None:
                        ret['process_id'][process_id]['vrf'][vrf]['reference_bandwidth'] = ref
                    if nsr is not None:
                        ret['process_id'][process_id]['vrf'][vrf]['nsr'] = nsr

        return ret

class ShowOspfVrfAll(ShowOspfSchema, MetaParser):
    """ parser class - implements detail parsing mechanisms for cli, xml, and
    yang output.
    """
    #*************************
    # schema - class variable
    #
    # Purpose is to make sure the parser always return the output
    # (nested dict) that has the same data structure across all supported
    # parsing mechanisms (cli(), yang(), xml()).


    def cli(self):
        ''' parsing mechanism: cli

        Function cli() defines the cli type output parsing mechanism which
        typically contains 3 steps: executing, transforming, returning
        '''
        cmd = 'show ospf vrf all'.format()
        out = self.device.execute(cmd)
        ospf_dict = {}
        entry = None
        for line in out.splitlines():
            line = line.rstrip()

            p1 = re.compile(r'^\s*VRF +(?P<vrf>.*) +in +Routing +Process +\"ospf '
                            r'+(?P<process_id>[0-9]+)\" +with +ID +(?P<router_id>[0-9\.]+)$')
            m = p1.match(line)
            if m:
                if 'process_id' not in ospf_dict:
                    ospf_dict['process_id'] = {}
                pid = m.groupdict()['process_id']
                ospf_dict['process_id'][pid] = {}
                rid = m.groupdict()['router_id']
                vrf = m.groupdict()['vrf']
                if 'vrf' not in ospf_dict['process_id'][pid]:
                    ospf_dict['process_id'][pid]['vrf'] = {}
                if vrf not in ospf_dict['process_id'][pid]['vrf']:
                    ospf_dict['process_id'][pid]['vrf'][vrf] = {}
                ospf_dict['process_id'][pid]['vrf'][vrf]['id'] = rid
                ospf_dict['process_id'][pid]['vrf'][vrf]['nsf'] = 'disabled'
                continue

            p2 = re.compile(r'^\s*NSR \(Non-stop routing\) is (?P<nsr>[a-zA-Z]+)$')
            m = p2.match(line)
            if m:
                ospf_dict['process_id'][pid]['vrf'][vrf]['nsr'] = m.groupdict()['nsr']
                continue

            p3 = re.compile(r'^\s*It is an (?P<ospf_rtr_type>.*)$')
            m = p3.match(line)
            if m:
                ospf_dict['process_id'][pid]['vrf'][vrf]['ospf_rtr_type'] = m.groupdict()['ospf_rtr_type']
                continue

            p4 = re.compile(r'^\s*Number +of +areas +in +this +router +is (?P<num_of_areas>[0-9]+). '
                         r'(?P<num_of_normal_area>[0-9]+) normal (?P<num_of_stub_area>[0-9]+) '
                         r'stub (?P<num_of_nssa_area>[0-9]+) nssa')
            m = p4.match(line)
            if m:
                ospf_dict['process_id'][pid]['vrf'][vrf]['num_of_areas'] = m.groupdict()['num_of_areas']
                ospf_dict['process_id'][pid]['vrf'][vrf]['num_of_normal_areas'] = m.groupdict()['num_of_normal_area']
                ospf_dict['process_id'][pid]['vrf'][vrf]['num_of_stub_areas'] = m.groupdict()['num_of_stub_area']
                ospf_dict['process_id'][pid]['vrf'][vrf]['num_of_nssa_areas'] = m.groupdict()['num_of_nssa_area']
                continue

            p5 = re.compile(r'^\s*Non\-Stop +Forwarding +(?P<nsf>[a-zA-Z]+)$')
            m = p5.match(line)
            if m:
                ospf_dict['process_id'][pid]['vrf'][vrf]['nsf'] = m.groupdict()['nsf']
                continue

            p6 = re.compile(r'^\s+Area +(?P<area>.*)$')
            m = p6.match(line)
            if m:
                area = m.groupdict()['area']
                if 'area' not in ospf_dict['process_id'][pid]['vrf'][vrf]:
                    ospf_dict['process_id'][pid]['vrf'][vrf]['area'] = {}
                if area not in ospf_dict['process_id'][pid]['vrf'][vrf]['area']:
                    ospf_dict['process_id'][pid]['vrf'][vrf]['area'][area] = {}
                continue

            p7 = re.compile(r'^\s+Number +of +interfaces +in +this +area +is +(?P<interfaces_in_this_area>\d+)$')
            m = p7.match(line)
            if m:
                ospf_dict['process_id'][pid]['vrf'][vrf]['area'][area]['interfaces_in_this_area'] = m.groupdict()['interfaces_in_this_area']
                ospf_dict['process_id'][pid]['vrf'][vrf]['area'][area]['active_interfaces'] = m.groupdict()['interfaces_in_this_area']
                continue
        return ospf_dict

    def xml(self):
        ''' parsing mechanism: xml

        Function xml() defines the xml type output parsing mechanism which
        typically contains 3 steps: executing, transforming, returning
        '''
        output =  tcl.q.caas.abstract(device=self.device.handle,
                                      exec='show ospf vrf all | xml')
        result = tcl.cast_any(output[1])

        return result

class ShowOspfNeighborDetailSchema(MetaParser):
    schema = {Optional('intf_list'): list,
              'intf':
                {Any():
                     {'neighbor': str,
                      'interface_address': str,
                      'process_id': str,
                      'vrf': str,
                      'area': str,
                      'state': str,
                      'state_changes': str,
                      Optional('uptime'): str,
					  Optional('neigh_priority'): str,
                      'dr': str,
                      'bdr':str}
                },
            }

class ShowOspfNeighborDetail(ShowOspfNeighborDetailSchema, MetaParser):
    """ parser class - implements detail parsing mechanisms for cli, xml, and
    yang output.
    """
    #*************************
    # schema - class variable
    #
    # Purpose is to make sure the parser always return the output
    # (nested dict) that has the same data structure across all supported
    # parsing mechanisms (cli(), yang(), xml()).


    def cli(self):
        ''' parsing mechanism: cli

        Function cli() defines the cli type output parsing mechanism which
        typically contains 3 steps: executing, transforming, returning
        '''
        cmd = 'show ospf neighbor detail'.format()
        out = self.device.execute(cmd)
        intf_list = []
        ospf_neigh_dict = {}
        entry = None
        for line in out.splitlines():
            line = line.rstrip()
            p1 = re.compile(r'^\s*Neighbors\s+for\s+OSPF\s+(?P<process_id>\S+)$')
            m = p1.match(line)
            if m:
                process_id = m.groupdict()['process_id']
                vrf = 'default'

            p2 = re.compile(r'^\s*Neighbor\s+(?P<neighbor>\S+),\s*interface\s+address\s+(?P<interface_address>\S+)')
            m = p2.match(line)
            if m:
                neighbor = m.groupdict()['neighbor']
                interface_address = m.groupdict()['interface_address']

            p3 = re.compile(r'^\s*In\s+the\s+area\s+(?P<area>\S+)\s+via\s+interface\s+(?P<interface>\S+)')
            m = p3.match(line)
            if m:
                interface = m.groupdict()['interface']

                if 'intf' not in ospf_neigh_dict:
                    ospf_neigh_dict['intf'] = {}
                intf_list.append(interface)
                ospf_neigh_dict['intf'][interface] = {}
                ospf_neigh_dict['intf'][interface]['area'] = m.groupdict()['area']
                ospf_neigh_dict['intf'][interface]['interface_address'] = interface_address
                ospf_neigh_dict['intf'][interface]['neighbor'] = neighbor
                ospf_neigh_dict['intf'][interface]['process_id'] = process_id
                ospf_neigh_dict['intf'][interface]['vrf'] = vrf
                continue

            p4 = re.compile(r'^ *Neighbor +priority +is +(?P<neigh_priority>[0-9]+), '
                            r'State +is +(?P<state>[a-zA-Z]+), '
                            r'+(?P<state_changes>\d+) +state +changes$')
            m = p4.match(line)
            if m:
                ospf_neigh_dict['intf'][interface]['neigh_priority'] = m.groupdict()['neigh_priority']
                ospf_neigh_dict['intf'][interface]['state'] = m.groupdict()['state']
                ospf_neigh_dict['intf'][interface]['state_changes'] = m.groupdict()['state_changes']
                continue

            p5 = re.compile(r'^\s*DR\s+is\s+(?P<dr>\S+)\s+BDR\s+is\s+(?P<bdr>\S+)')
            m = p5.match(line)
            if m:
                ospf_neigh_dict['intf'][interface]['dr'] = m.groupdict()['dr']
                ospf_neigh_dict['intf'][interface]['bdr'] = m.groupdict()['bdr']
                continue

            p6 = re.compile(r'^\s*Neighbor\s+is\s+up\s+for\s+(?P<uptime>\S+)')
            m = p6.match(line)
            if m:
                ospf_neigh_dict['intf'][interface]['uptime'] = m.groupdict()['uptime']
                continue
        if intf_list:
            ospf_neigh_dict['intf_list'] = intf_list

        return ospf_neigh_dict

    def xml(self):
        ''' parsing mechanism: xml

        Function xml() defines the xml type output parsing mechanism which
        typically contains 3 steps: executing, transforming, returning
        '''
        output =  tcl.q.caas.abstract(device=self.device.handle,
                                      exec='show ospf neighbor detail | xml')
        result = tcl.cast_any(output[1])

        return result

class ShowOspfNeighborDetailVrfAll(ShowOspfNeighborDetailSchema, MetaParser):
    """ parser class - implements detail parsing mechanisms for cli, xml, and
    yang output.
    """
    #*************************
    # schema - class variable
    #
    # Purpose is to make sure the parser always return the output
    # (nested dict) that has the same data structure across all supported
    # parsing mechanisms (cli(), yang(), xml()).
    def cli(self):
        cmd = 'show ospf vrf all neighbor detail'.format()
        out = self.device.execute(cmd)
        intf_list = []
        ospf_neigh_dict = {}
        entry = None
        for line in out.splitlines():
            line = line.rstrip()
            p1 = re.compile(r'^\s*Neighbors\s+for\s+OSPF\s+(?P<process_id>\S+),\s*VRF\s+(?P<vrf>\S+)$')
            m = p1.match(line)
            if m:
                process_id = m.groupdict()['process_id']
                vrf = m.groupdict()['vrf']

            p2 = re.compile(r'^\s*Neighbor\s+(?P<neighbor>\S+),\s*interface\s+address\s+(?P<interface_address>\S+)')
            m = p2.match(line)
            if m:
                neighbor = m.groupdict()['neighbor']
                interface_address = m.groupdict()['interface_address']

            p3 = re.compile(r'^\s*In\s+the\s+area\s+(?P<area>\S+)\s+via\s+interface\s+(?P<interface>\S+)')
            m = p3.match(line)
            if m:
                interface = m.groupdict()['interface']
                if 'intf' not in ospf_neigh_dict:
                    ospf_neigh_dict['intf'] = {}
                intf_list.append(interface)
                ospf_neigh_dict['intf'][interface] = {}
                ospf_neigh_dict['intf'][interface]['area'] = m.groupdict()['area']
                ospf_neigh_dict['intf'][interface]['interface_address'] = interface_address
                ospf_neigh_dict['intf'][interface]['neighbor'] = neighbor
                ospf_neigh_dict['intf'][interface]['process_id'] = process_id
                ospf_neigh_dict['intf'][interface]['vrf'] = vrf
                continue

            p4 = re.compile(r'^ *Neighbor +priority +is +(?P<neigh_priority>[0-9]+), '
                            r'State +is +(?P<state>[a-zA-Z]+), '
                            r'+(?P<state_changes>\d+) +state +changes$')
            m = p4.match(line)
            if m:
                ospf_neigh_dict['intf'][interface]['neigh_priority'] = m.groupdict()['neigh_priority']
                ospf_neigh_dict['intf'][interface]['state'] = m.groupdict()['state']
                ospf_neigh_dict['intf'][interface]['state_changes'] = m.groupdict()['state_changes']
                continue

            p5 = re.compile(r'^\s*DR\s+is\s+(?P<dr>\S+)\s+BDR\s+is\s+(?P<bdr>\S+)')
            m = p5.match(line)
            if m:
                ospf_neigh_dict['intf'][interface]['dr'] = m.groupdict()['dr']
                ospf_neigh_dict['intf'][interface]['bdr'] = m.groupdict()['bdr']
                continue

            p6 = re.compile(r'^\s*Neighbor\s+is\s+up\s+for\s+(?P<uptime>\S+)')
            m = p6.match(line)
            if m:
                ospf_neigh_dict['intf'][interface]['uptime'] = m.groupdict()['uptime']
                continue

        if intf_list:
            ospf_neigh_dict['intf_list'] = intf_list

        return ospf_neigh_dict

    def xml(self):
        ''' parsing mechanism: xml

        Function xml() defines the xml type output parsing mechanism which
        typically contains 3 steps: executing, transforming, returning
        '''
        output =  tcl.q.caas.abstract(device=self.device.handle,
                                      exec='show ospf vrf all neighbor detail | xml')
        result = tcl.cast_any(output[1])

        return result

class ShowOspfInterfaceSchema(MetaParser):
    schema = {Optional('intfs_all'): list,
              Optional('intfs_up'): list,
              Optional('intfs_down'): list,
              'intf':
                {Any():
                     {'ip_address': str,
                      'process_id': str,
                      'vrf': str,
                      'area': str,
                      'network_type': str,
                      'cost': str,
                      Optional('rid'): str,
					  Optional('priority'): str,
					  Optional('mtu'): str,
					  Optional('t_delay'): str,
					  Optional('state'): str,
					  Optional('intf_state'): str,
					  Optional('max_pkt_size'): str,
                      Optional('designated_router_id'): str,
                      Optional('designated_router_address'): str,
                      Optional('backup_designated_router_id'): str,
                      Optional('backup_designated_router_address'): str,
                      Optional('hello_timer'): str,
                      Optional('dead_timer'): str,
                      Optional('wait_timer'): str,
                      Optional('retransmit_timer'): str,
                      Optional('neighbor'): str,
					  Optional('nsf_state'): str}
                },
            }



class ShowOspfInterface(ShowOspfInterfaceSchema,MetaParser):
    """ parser class - implements detail parsing mechanisms for cli, xml, and
    yang output.
    """
    #*************************
    # schema - class variable
    #
    # Purpose is to make sure the parser always return the output
    # (nested dict) that has the same data structure across all supported
    # parsing mechanisms (cli(), yang(), xml()).


    def cli(self):
        ''' parsing mechanism: cli

        Function cli() defines the cli type output parsing mechanism which
        typically contains 3 steps: executing, transforming, returning
        '''
        cmd = 'show ospf interface'.format()
        out = self.device.execute(cmd)
        intfs_all = []
        intfs_up = []
        intfs_down = []
        ospf_intf_dict = {}
        entry = None
        for line in out.splitlines():
            line = line.rstrip()

            p1 = re.compile(r'\s*Interfaces\s+for\s+OSPF\s+(?P<process_id>[^,]+)$')
            m = p1.match(line)
            if m:
                process_id = m.groupdict()['process_id']
                vrf = 'default'

            p2 = re.compile(r'^\s*(?P<intf>\S+)\s+is\s+(?P<admin_state>up|down),\s*line\s+protocol\s+is\s+(?P<prot_state>up|down)$')
            m = p2.match(line)
            if m:
                intf = m.groupdict()['intf']
                if 'intf' not in ospf_intf_dict:
                    ospf_intf_dict['intf'] = {}

                ospf_intf_dict['intf'][intf] = {}
                ospf_intf_dict['intf'][intf]['process_id'] = process_id
                ospf_intf_dict['intf'][intf]['vrf'] = vrf
                admin_state = m.groupdict()['admin_state']
                proto_state = m.groupdict()['prot_state']
                intfs_all.append(intf)
                if admin_state == 'up' and proto_state == 'up':
                    ospf_intf_dict['intf'][intf]['intf_state'] = 'up'
                    intfs_up.append(intf)
                else:
                    ospf_intf_dict['intf'][intf]['intf_state'] = 'down'
                    intfs_down.append(intf)
                continue

            p3 = re.compile(r'^\s*Internet +Address +(?P<ip_address>[0-9\.]+)/(?P<mask>[0-9]+), +Area +(?P<area>[0-9]+)')
            m = p3.match(line)
            if m:
                addr = m.groupdict()['ip_address']
                ospf_intf_dict['intf'][intf]['ip_address'] = addr
                area = m.groupdict()['area']
                ospf_intf_dict['intf'][intf]['area'] = area
                continue

            p4 = re.compile(r'^\s*Process\s+ID\s+(?P<pid>[^,]+),\s*Router\s+ID\s+(?P<rid>[^,]+),'
                            r'\s*Network\s+Type\s+(?P<ntype>[^,]+),\s*Cost:\s+(?P<cost>\S+)')
            m = p4.match(line)
            if m:
                pid = m.groupdict()['pid']
                ospf_intf_dict['intf'][intf]['process_id'] = pid
                rid = m.groupdict()['rid']
                ospf_intf_dict['intf'][intf]['rid'] = rid
                ntype = m.groupdict()['ntype']
                ospf_intf_dict['intf'][intf]['network_type'] = ntype
                cost = m.groupdict()['cost']
                ospf_intf_dict['intf'][intf]['cost'] = cost
                continue

            p5 = re.compile(r'^\s*Transmit\s+Delay\s+is\s+(?P<tdelay>[^,]+),'
                            r'\s*State\s+(?P<ospf_state>[^,]+),\s*Priority\s+(?P<pri>[^,]+),'
                            r'\s*MTU\s+(?P<mtu>[^,]+),\s*MaxPktSz\s+(?P<max_pkt_size>[^,]+)')
            m = p5.match(line)
            if m:
                tdelay = m.groupdict()['tdelay']
                ospf_intf_dict['intf'][intf]['t_delay'] = tdelay
                ospf_state = m.groupdict()['ospf_state']
                ospf_intf_dict['intf'][intf]['state'] = ospf_state
                pri = m.groupdict()['pri']
                ospf_intf_dict['intf'][intf]['priority'] = pri
                mtu = m.groupdict()['mtu']
                ospf_intf_dict['intf'][intf]['mtu'] = mtu
                max_pkt_size = m.groupdict()['max_pkt_size']
                ospf_intf_dict['intf'][intf]['max_pkt_size'] = max_pkt_size
                continue

            p6 = re.compile(r'\s*Designated\s+Router\s+\(ID\)\s*(?P<designated_router_id>[^,]+),'
                            r'\s*Interface\s+address (?P<designated_router_address>\S+)')
            m = p6.match(line)
            if m:
                designated_router_id = m.groupdict()['designated_router_id']
                ospf_intf_dict['intf'][intf]['designated_router_id'] = designated_router_id
                designated_router_address = m.groupdict()['designated_router_address']
                ospf_intf_dict['intf'][intf]['designated_router_address'] = designated_router_address
                continue

            p7 = re.compile(r'\s*Backup\s+Designated\s+router\s+\(ID\)\s*(?P<backup_designated_router_id>[^,]+),'
                            r'\s*Interface\s+address (?P<backup_designated_router_address>\S+)')
            m = p7.match(line)
            if m:
                backup_designated_router_id = m.groupdict()['backup_designated_router_id']
                ospf_intf_dict['intf'][intf]['backup_designated_router_id'] = backup_designated_router_id
                backup_designated_router_address = m.groupdict()['backup_designated_router_address']
                ospf_intf_dict['intf'][intf]['backup_designated_router_address'] = backup_designated_router_address
                continue

            p8 = re.compile(r'\s+Adjacent\s+with\s+neighbor\s+(?P<neighbor>\S+)')
            m = p8.match(line)
            if m:
                neighbor = m.groupdict()['neighbor']
                ospf_intf_dict['intf'][intf]['neighbor'] = neighbor
                continue

            p9 = re.compile(r'^\s*Timer +intervals +configured, +Hello +(?P<hello_timer>[0-9]+), '
                            r'+Dead +(?P<dead_timer>[0-9]+), '
                            r'+Wait +(?P<wait_timer>[0-9]+), '
                            r'+Retransmit +(?P<retransmit_timer>[0-9]+)')
            m = p9.match(line)
            if m:
                hello_timer = m.groupdict()['hello_timer']
                ospf_intf_dict['intf'][intf]['hello_timer'] = hello_timer
                dead_timer = m.groupdict()['dead_timer']
                ospf_intf_dict['intf'][intf]['dead_timer'] = dead_timer
                wait_timer = m.groupdict()['wait_timer']
                ospf_intf_dict['intf'][intf]['wait_timer'] = wait_timer
                retransmit_timer = m.groupdict()['retransmit_timer']
                ospf_intf_dict['intf'][intf]['retransmit_timer'] = retransmit_timer
                continue

        if intfs_all:
            ospf_intf_dict['intfs_all'] = intfs_all
        if intfs_down:
            ospf_intf_dict['intfs_up'] = intfs_up
        if intfs_up:
            ospf_intf_dict['intfs_down'] = intfs_down

        return ospf_intf_dict

    def xml(self):
        ''' parsing mechanism: xml

        Function xml() defines the xml type output parsing mechanism which
        typically contains 3 steps: executing, transforming, returning
        '''
        output =  tcl.q.caas.abstract(device=self.device.handle,
                                      exec='show ospf interface')
        result = tcl.cast_any(output[1])

        return result
		
class ShowOspfInterfaceVrfAll(ShowOspfInterfaceSchema,MetaParser):
    """ parser class - implements detail parsing mechanisms for cli, xml, and
    yang output.
    """
    #*************************
    # schema - class variable
    #
    # Purpose is to make sure the parser always return the output
    # (nested dict) that has the same data structure across all supported
    # parsing mechanisms (cli(), yang(), xml()).


    def cli(self):
        ''' parsing mechanism: cli

        Function cli() defines the cli type output parsing mechanism which
        typically contains 3 steps: executing, transforming, returning
        '''
        cmd = 'show ospf vrf all interface'.format()
        out = self.device.execute(cmd)
        intfs_all = []
        intfs_up = []
        intfs_down = []
        ospf_intf_dict = {}
        entry = None
        for line in out.splitlines():
            line = line.rstrip()

            p1 = re.compile(r'^\s*Interfaces\s+for\s+OSPF\s+(?P<process_id>[^,]+),\s*VRF\s+(?P<vrf>\S+)$')
            m = p1.match(line)
            if m:
                process_id = m.groupdict()['process_id']
                vrf = m.groupdict()['vrf']

            p2 = re.compile(r'^\s*(?P<intf>\S+)\s+is\s+(?P<admin_state>up|down),\s*line\s+protocol\s+is\s+(?P<prot_state>up|down)$')
            m = p2.match(line)

            if m:
                intf = m.groupdict()['intf']
                if 'intf' not in ospf_intf_dict:
                    ospf_intf_dict['intf'] = {}

                ospf_intf_dict['intf'][intf] = {}
                ospf_intf_dict['intf'][intf]['process_id'] = process_id
                ospf_intf_dict['intf'][intf]['vrf'] = vrf
                admin_state = m.groupdict()['admin_state']
                proto_state = m.groupdict()['prot_state']
                intfs_all.append(intf)
                if admin_state == 'up' and proto_state == 'up':
                    ospf_intf_dict['intf'][intf]['intf_state'] = 'up'
                    intfs_up.append(intf)
                else:
                    ospf_intf_dict['intf'][intf]['intf_state'] = 'down'
                    intfs_down.append(intf)
                continue

            p3 = re.compile(r'^\s*Internet +Address +(?P<ip_address>[0-9\.]+)/(?P<mask>[0-9]+), +Area +(?P<area>[0-9]+)')
            m = p3.match(line)
            if m:
                addr = m.groupdict()['ip_address']
                ospf_intf_dict['intf'][intf]['ip_address'] = addr
                area = m.groupdict()['area']
                ospf_intf_dict['intf'][intf]['area'] = area
                continue

            p4 = re.compile(r'^\s*Process\s+ID\s+(?P<pid>[^,]+),\s*VRF\s+(?P<vrf>[^,]+),\s*Router\s+ID\s+(?P<rid>[^,]+),'
                            r'\s*Network\s+Type\s+(?P<ntype>[^,]+),\s*Cost:\s+(?P<cost>\S+)')
            m = p4.match(line)
            if m:
                pid = m.groupdict()['pid']
                ospf_intf_dict['intf'][intf]['process_id'] = pid
                rid = m.groupdict()['rid']
                ospf_intf_dict['intf'][intf]['rid'] = rid
                ntype = m.groupdict()['ntype']
                ospf_intf_dict['intf'][intf]['network_type'] = ntype
                cost = m.groupdict()['cost']
                ospf_intf_dict['intf'][intf]['cost'] = cost
                continue

            p5 = re.compile(r'^\s*Transmit\s+Delay\s+is\s+(?P<tdelay>[^,]+),'
                            r'\s*State\s+(?P<ospf_state>[^,]+),\s*Priority\s+(?P<pri>[^,]+),'
                            r'\s*MTU\s+(?P<mtu>[^,]+),\s*MaxPktSz\s+(?P<max_pkt_size>[^,]+)')
            m = p5.match(line)
            if m:
                tdelay = m.groupdict()['tdelay']
                ospf_intf_dict['intf'][intf]['t_delay'] = tdelay
                ospf_state = m.groupdict()['ospf_state']
                ospf_intf_dict['intf'][intf]['state'] = ospf_state
                pri = m.groupdict()['pri']
                ospf_intf_dict['intf'][intf]['priority'] = pri
                mtu = m.groupdict()['mtu']
                ospf_intf_dict['intf'][intf]['mtu'] = mtu
                max_pkt_size = m.groupdict()['max_pkt_size']
                ospf_intf_dict['intf'][intf]['max_pkt_size'] = max_pkt_size
                continue

            p6 = re.compile(r'\s*Designated\s+Router\s+\(ID\)\s*(?P<designated_router_id>[^,]+),'
                            r'\s*Interface\s+address (?P<designated_router_address>\S+)')
            m = p6.match(line)
            if m:
                designated_router_id = m.groupdict()['designated_router_id']
                ospf_intf_dict['intf'][intf]['designated_router_id'] = designated_router_id
                designated_router_address = m.groupdict()['designated_router_address']
                ospf_intf_dict['intf'][intf]['designated_router_address'] = designated_router_address
                continue

            p7 = re.compile(r'\s*Backup\s+Designated\s+router\s+\(ID\)\s*(?P<backup_designated_router_id>[^,]+),'
                            r'\s*Interface\s+address (?P<backup_designated_router_address>\S+)')
            m = p7.match(line)
            if m:
                backup_designated_router_id = m.groupdict()['backup_designated_router_id']
                ospf_intf_dict['intf'][intf]['backup_designated_router_id'] = backup_designated_router_id
                backup_designated_router_address = m.groupdict()['backup_designated_router_address']
                ospf_intf_dict['intf'][intf]['backup_designated_router_address'] = backup_designated_router_address
                continue

            p8 = re.compile(r'\s*Adjacent\s+with\s+neighbor\s+(?P<neighbor>\S+)')
            m = p8.match(line)
            if m:
                neighbor = m.groupdict()['neighbor']
                ospf_intf_dict['intf'][intf]['neighbor'] = neighbor
                continue

            p9 = re.compile(r'^\s*Timer +intervals +configured, +Hello +(?P<hello_timer>[0-9]+), '
                            r'+Dead +(?P<dead_timer>[0-9]+), '
                            r'+Wait +(?P<wait_timer>[0-9]+), '
                            r'+Retransmit +(?P<retransmit_timer>[0-9]+)')
            m = p9.match(line)
            if m:
                if 'intf' not in ospf_intf_dict:
                    ospf_intf_dict['intf'] = {}

                hello_timer = m.groupdict()['hello_timer']
                ospf_intf_dict['intf'][intf]['hello_timer'] = hello_timer
                dead_timer = m.groupdict()['dead_timer']
                ospf_intf_dict['intf'][intf]['dead_timer'] = dead_timer
                wait_timer = m.groupdict()['wait_timer']
                ospf_intf_dict['intf'][intf]['wait_timer'] = wait_timer
                retransmit_timer = m.groupdict()['retransmit_timer']
                ospf_intf_dict['intf'][intf]['retransmit_timer'] = retransmit_timer
                continue

        if intfs_all:
            ospf_intf_dict['intfs_all'] = intfs_all
        if intfs_down:
            ospf_intf_dict['intfs_up'] = intfs_up
        if intfs_up:
            ospf_intf_dict['intfs_down'] = intfs_down
        return ospf_intf_dict

    def xml(self):
        ''' parsing mechanism: xml

        Function xml() defines the xml type output parsing mechanism which
        typically contains 3 steps: executing, transforming, returning
        '''
        output =  tcl.q.caas.abstract(device=self.device.handle,
                                      exec='show ospf vrf all interface | xml')
        result = tcl.cast_any(output[1])

        return result

class ShowOspfDatabaseSchema(MetaParser):

    schema = {'process_id':
                  {Any():
                       {Optional('vrf'):
                            {Any():
                                {Optional('router_id'): str,
                                 Optional('area'):
                                    {regexp('.*'):
                                        {Any():
                                            {Optional('ls_id'):
                                                {Any():
                                                    {Optional('advrouter'):
                                                        {Any():
                                                            {'age': str,
                                                             'seq': str,
                                                             'cksum': str,
                                                             Optional('lnkcnt'): str},
                                                        }
                                                    },
                                                },
                                            },
                                        },
                                    },
                                },
                            },
                        }
                   }
              }

class ShowOspfDatabase(ShowOspfDatabaseSchema, MetaParser):
    """ parser class - implements detail parsing mechanisms for cli, xml, and
    yang output.
    """
    #*************************
    # schema - class variable
    #
    # Purpose is to make sure the parser always return the output
    # (nested dict) that has the same data structure across all supported
    # parsing mechanisms (cli(), yang(), xml()).


    def cli(self):
        ''' parsing mechanism: cli

        Function cli() defines the cli type output parsing mechanism which
        typically contains 3 steps: executing, transforming, returning
        '''
        cmd = 'show ospf database'.format()
        out = self.device.execute(cmd)
        ospf_db_dict = {}
        lsa_type = {}
        vrf = 'default'
        for line in out.splitlines():
            line = line.rstrip()
            p1 = re.compile(r'^\s*(?P<key>[a-zA-Z0-9]+) +Router +with +ID '
                            r'\((?P<router_id>[0-9\.]+)\) '
                            r'\(Process ID (?P<process_id>[0-9]+)\)')
            m = p1.match(line)
            if m:
                router_id = m.groupdict()['router_id']
                process_id = m.groupdict()['process_id']
                if 'process_id' not in ospf_db_dict:
                    ospf_db_dict['process_id'] = {}
                if process_id not in ospf_db_dict['process_id']:
                    ospf_db_dict['process_id'][process_id] = {}
                if 'vrf' not in ospf_db_dict['process_id'][process_id]:
                    ospf_db_dict['process_id'][process_id]['vrf'] = {}
                if vrf not in ospf_db_dict['process_id'][process_id]['vrf']:
                    ospf_db_dict['process_id'][process_id]['vrf'][vrf] = {}
                ospf_db_dict['process_id'][process_id]['vrf'][vrf]['router_id'] = router_id
                continue

            p2 = re.compile(r'^\s*Router +Link +States +\(Area +(?P<area>[0-9]+)\)')
            m = p2.match(line)
            if m:
                area = m.groupdict()['area']
                if 'area' not in ospf_db_dict['process_id'][process_id]['vrf'][vrf]:
                    ospf_db_dict['process_id'][process_id]['vrf'][vrf]['area'] = {}
                if area not in ospf_db_dict['process_id'][process_id]['vrf'][vrf]['area']:
                    ospf_db_dict['process_id'][process_id]['vrf'][vrf]['area'][area] = {}
                if 'router_link' not in ospf_db_dict['process_id'][process_id]['vrf'][vrf]['area'][area]:
                    ospf_db_dict['process_id'][process_id]['vrf'][vrf]['area'][area]['router_link'] = {}
                lsa_type = ospf_db_dict['process_id'][process_id]['vrf'][vrf]['area'][area]['router_link']
                continue

            p3 = re.compile(r'^\s*Net +Link +States +\(Area +(?P<area>[0-9]+)\)')
            m = p3.match(line)
            if m:
                area = m.groupdict()['area']
                if 'area' not in ospf_db_dict['process_id'][process_id]['vrf'][vrf]:
                    ospf_db_dict['process_id'][process_id]['vrf'][vrf]['area'] = {}
                if area not in ospf_db_dict['process_id'][process_id]['vrf'][vrf]['area']:
                    ospf_db_dict['process_id'][process_id]['vrf'][vrf]['area'][area] = {}
                if 'network_link' not in ospf_db_dict['process_id'][process_id]['vrf'][vrf]['area'][area]:
                    ospf_db_dict['process_id'][process_id]['vrf'][vrf]['area'][area]['network_link'] = {}
                lsa_type = ospf_db_dict['process_id'][process_id]['vrf'][vrf]['area'][area]['network_link']
                continue

            p4 = re.compile(r'^\s*Summary +Network +Link +States +\(Area +(?P<area>[0-9]+)\)')
            m = p4.match(line)
            if m:
                area = m.groupdict()['area']
                if 'area' not in ospf_db_dict['process_id'][process_id]['vrf'][vrf]:
                    ospf_db_dict['process_id'][process_id]['vrf'][vrf]['area'] = {}
                if area not in ospf_db_dict['process_id'][process_id]['vrf'][vrf]['area']:
                    ospf_db_dict['process_id'][process_id]['vrf'][vrf]['area'][area] = {}
                if 'summary_network_link' not in ospf_db_dict['process_id'][process_id]['vrf'][vrf]['area'][area]:
                    ospf_db_dict['process_id'][process_id]['vrf'][vrf]['area'][area]['summary_network_link'] = {}
                lsa_type = ospf_db_dict['process_id'][process_id]['vrf'][vrf]['area'][area]['summary_network_link']
                continue

            p5 = re.compile(r'^\s*Opaque +Area +Link +States +\(Area +(?P<area>[0-9]+)\)')
            m = p5.match(line)
            if m:
                area = m.groupdict()['area']
                if 'area' not in ospf_db_dict['process_id'][process_id]['vrf'][vrf]:
                    ospf_db_dict['process_id'][process_id]['vrf'][vrf]['area'] = {}
                if area not in ospf_db_dict['process_id'][process_id]['vrf'][vrf]['area']:
                    ospf_db_dict['process_id'][process_id]['vrf'][vrf]['area'][area] = {}
                if 'opaque_area_link' not in ospf_db_dict['process_id'][process_id]['vrf'][vrf]['area'][area]:
                    ospf_db_dict['process_id'][process_id]['vrf'][vrf]['area'][area]['opaque_area_link'] = {}
                lsa_type = ospf_db_dict['process_id'][process_id]['vrf'][vrf]['area'][area]['opaque_area_link']
                continue
            if lsa_type is not {}:
                p6 = re.compile(r'\s*(?P<ls_id>[0-9\.]+) +(?P<advrouter>[0-9\.]+) '
                                r'+(?P<age>\d+) +(?P<seq>0[xX][0-9a-fA-F]+) '
                                r'+(?P<cksum>0[xX][0-9a-fA-F]+) +(?P<lnkcnt>\d+)')
                m = p6.match(line)
                if m:
                    ls_id = m.groupdict()['ls_id']
                    advrouter = m.groupdict()['advrouter']
                    age = m.groupdict()['age']
                    seq = m.groupdict()['seq']
                    cksum = m.groupdict()['cksum']
                    lnkcnt = m.groupdict()['lnkcnt']
                    if 'ls_id' not in lsa_type:
                        lsa_type['ls_id'] = {}
                    if ls_id not in lsa_type['ls_id']:
                        lsa_type['ls_id'][ls_id] = {}
                    if 'advrouter' not in lsa_type['ls_id'][ls_id]:
                        lsa_type['ls_id'][ls_id]['advrouter'] = {}
                    if advrouter not in lsa_type['ls_id'][ls_id]['advrouter']:
                        lsa_type['ls_id'][ls_id]['advrouter'][advrouter] = {}
                    lsa_type['ls_id'][ls_id]['advrouter'][advrouter]['age'] = age
                    lsa_type['ls_id'][ls_id]['advrouter'][advrouter]['seq'] = seq
                    lsa_type['ls_id'][ls_id]['advrouter'][advrouter]['cksum'] = cksum
                    lsa_type['ls_id'][ls_id]['advrouter'][advrouter]['lnkcnt'] = lnkcnt
                    continue

                p7 = re.compile(r'\s*(?P<ls_id>[0-9\.]+) +(?P<advrouter>[0-9\.]+) '
                                r'+(?P<age>\d+) +(?P<seq>0[xX][0-9a-fA-F]+) '
                                r'+(?P<cksum>0[xX][0-9a-fA-F]+)')
                m = p7.match(line)
                if m:
                    ls_id = m.groupdict()['ls_id']
                    advrouter = m.groupdict()['advrouter']
                    age = m.groupdict()['age']
                    seq = m.groupdict()['seq']
                    cksum = m.groupdict()['cksum']
                    if 'ls_id' not in lsa_type:
                        lsa_type['ls_id'] = {}
                    if ls_id not in lsa_type['ls_id']:
                        lsa_type['ls_id'][ls_id] = {}
                    if 'advrouter' not in lsa_type['ls_id'][ls_id]:
                        lsa_type['ls_id'][ls_id]['advrouter'] = {}
                    if advrouter not in lsa_type['ls_id'][ls_id]['advrouter']:
                        lsa_type['ls_id'][ls_id]['advrouter'][advrouter] = {}
                    lsa_type['ls_id'][ls_id]['advrouter'][advrouter]['age'] = age
                    lsa_type['ls_id'][ls_id]['advrouter'][advrouter]['seq'] = seq
                    lsa_type['ls_id'][ls_id]['advrouter'][advrouter]['cksum'] = cksum
                    continue
        return ospf_db_dict


    def xml(self):
        ''' parsing mechanism: xml

        Function xml() defines the xml type output parsing mechanism which
        typically contains 3 steps: executing, transforming, returning
        '''
        output =  tcl.q.caas.abstract(device=self.device.handle,
                                      exec='show ospf database | xml')
        result = tcl.cast_any(output[1])

        return result

class ShowOspfDatabaseVrfAll(ShowOspfDatabaseSchema, MetaParser):
    """ parser class - implements detail parsing mechanisms for cli, xml, and
    yang output.
    """
    #*************************
    # schema - class variable
    #
    # Purpose is to make sure the parser always return the output
    # (nested dict) that has the same data structure across all supported
    # parsing mechanisms (cli(), yang(), xml()).


    def cli(self):
        ''' parsing mechanism: cli

        Function cli() defines the cli type output parsing mechanism which
        typically contains 3 steps: executing, transforming, returning
        '''

    def cli(self):
        ''' parsing mechanism: cli

        Function cli() defines the cli type output parsing mechanism which
        typically contains 3 steps: executing, transforming, returning
        '''
        cmd = 'show ospf vrf all database'.format()
        out = self.device.execute(cmd)
        ospf_db_dict = {}
        lsa_type = {}
        for line in out.splitlines():
            line = line.rstrip()
            p1 = re.compile(r'^\s*(?P<key>[a-zA-Z0-9]+) +Router +with +ID '
                            r'\((?P<router_id>[0-9\.]+)\) '
                            r'\(Process ID (?P<process_id>[0-9]+), VRF +(?P<vrf>\S+)\)')
            m = p1.match(line)
            if m:
                router_id = m.groupdict()['router_id']
                process_id = m.groupdict()['process_id']
                vrf = m.groupdict()['vrf']
                if 'process_id' not in ospf_db_dict:
                    ospf_db_dict['process_id'] = {}
                if process_id not in ospf_db_dict['process_id']:
                    ospf_db_dict['process_id'][process_id] = {}
                if 'vrf' not in ospf_db_dict['process_id'][process_id]:
                    ospf_db_dict['process_id'][process_id]['vrf'] = {}
                if vrf not in ospf_db_dict['process_id'][process_id]['vrf']:
                    ospf_db_dict['process_id'][process_id]['vrf'][vrf] = {}
                ospf_db_dict['process_id'][process_id]['vrf'][vrf]['router_id'] = router_id
                continue

            p2 = re.compile(r'^\s*Router +Link +States +\(Area +(?P<area>[0-9]+)\)')
            m = p2.match(line)
            if m:
                area = m.groupdict()['area']
                if 'area' not in ospf_db_dict['process_id'][process_id]['vrf'][vrf]:
                    ospf_db_dict['process_id'][process_id]['vrf'][vrf]['area'] = {}
                if area not in ospf_db_dict['process_id'][process_id]['vrf'][vrf]['area']:
                    ospf_db_dict['process_id'][process_id]['vrf'][vrf]['area'][area] = {}
                if 'router_link' not in ospf_db_dict['process_id'][process_id]['vrf'][vrf]['area'][area]:
                    ospf_db_dict['process_id'][process_id]['vrf'][vrf]['area'][area]['router_link'] = {}
                lsa_type = ospf_db_dict['process_id'][process_id]['vrf'][vrf]['area'][area]['router_link']
                continue

            p3 = re.compile(r'^\s*Net +Link +States +\(Area +(?P<area>[0-9]+)\)')
            m = p3.match(line)
            if m:
                area = m.groupdict()['area']
                if 'area' not in ospf_db_dict['process_id'][process_id]['vrf'][vrf]:
                    ospf_db_dict['process_id'][process_id]['vrf'][vrf]['area'] = {}
                if area not in ospf_db_dict['process_id'][process_id]['vrf'][vrf]['area']:
                    ospf_db_dict['process_id'][process_id]['vrf'][vrf]['area'][area] = {}
                if 'network_link' not in ospf_db_dict['process_id'][process_id]['vrf'][vrf]['area'][area]:
                    ospf_db_dict['process_id'][process_id]['vrf'][vrf]['area'][area]['network_link'] = {}
                lsa_type = ospf_db_dict['process_id'][process_id]['vrf'][vrf]['area'][area]['network_link']
                continue

            p4 = re.compile(r'^\s*Summary +Network +Link +States +\(Area +(?P<area>[0-9]+)\)')
            m = p4.match(line)
            if m:
                area = m.groupdict()['area']
                if 'area' not in ospf_db_dict['process_id'][process_id]['vrf'][vrf]:
                    ospf_db_dict['process_id'][process_id]['vrf'][vrf]['area'] = {}
                if area not in ospf_db_dict['process_id'][process_id]['vrf'][vrf]['area']:
                    ospf_db_dict['process_id'][process_id]['vrf'][vrf]['area'][area] = {}
                if 'summary_network_link' not in ospf_db_dict['process_id'][process_id]['vrf'][vrf]['area'][area]:
                    ospf_db_dict['process_id'][process_id]['vrf'][vrf]['area'][area]['summary_network_link'] = {}
                lsa_type = ospf_db_dict['process_id'][process_id]['vrf'][vrf]['area'][area]['summary_network_link']
                continue

            p5 = re.compile(r'^\s*Opaque +Area +Link +States +\(Area +(?P<area>[0-9]+)\)')
            m = p5.match(line)
            if m:
                area = m.groupdict()['area']
                if 'area' not in ospf_db_dict['process_id'][process_id]['vrf'][vrf]:
                    ospf_db_dict['process_id'][process_id]['vrf'][vrf]['area'] = {}
                if area not in ospf_db_dict['process_id'][process_id]['vrf'][vrf]['area']:
                    ospf_db_dict['process_id'][process_id]['vrf'][vrf]['area'][area] = {}
                if 'opaque_area_link' not in ospf_db_dict['process_id'][process_id]['vrf'][vrf]['area'][area]:
                    ospf_db_dict['process_id'][process_id]['vrf'][vrf]['area'][area]['opaque_area_link'] = {}
                lsa_type = ospf_db_dict['process_id'][process_id]['vrf'][vrf]['area'][area]['opaque_area_link']
                continue
            if lsa_type is not {}:
                p6 = re.compile(r'\s*(?P<ls_id>[0-9\.]+) +(?P<advrouter>[0-9\.]+) '
                                r'+(?P<age>\d+) +(?P<seq>0[xX][0-9a-fA-F]+) '
                                r'+(?P<cksum>0[xX][0-9a-fA-F]+) +(?P<lnkcnt>\d+)')
                m = p6.match(line)
                if m:
                    ls_id = m.groupdict()['ls_id']
                    advrouter = m.groupdict()['advrouter']
                    age = m.groupdict()['age']
                    seq = m.groupdict()['seq']
                    cksum = m.groupdict()['cksum']
                    lnkcnt = m.groupdict()['lnkcnt']
                    if 'ls_id' not in lsa_type:
                        lsa_type['ls_id'] = {}
                    if ls_id not in lsa_type['ls_id']:
                        lsa_type['ls_id'][ls_id] = {}
                    if 'advrouter' not in lsa_type['ls_id'][ls_id]:
                        lsa_type['ls_id'][ls_id]['advrouter'] = {}
                    if advrouter not in lsa_type['ls_id'][ls_id]['advrouter']:
                        lsa_type['ls_id'][ls_id]['advrouter'][advrouter] = {}
                    lsa_type['ls_id'][ls_id]['advrouter'][advrouter]['age'] = age
                    lsa_type['ls_id'][ls_id]['advrouter'][advrouter]['seq'] = seq
                    lsa_type['ls_id'][ls_id]['advrouter'][advrouter]['cksum'] = cksum
                    lsa_type['ls_id'][ls_id]['advrouter'][advrouter]['lnkcnt'] = lnkcnt
                    continue

                p7 = re.compile(r'\s*(?P<ls_id>[0-9\.]+) +(?P<advrouter>[0-9\.]+) '
                                r'+(?P<age>\d+) +(?P<seq>0[xX][0-9a-fA-F]+) '
                                r'+(?P<cksum>0[xX][0-9a-fA-F]+)')
                m = p7.match(line)
                if m:
                    ls_id = m.groupdict()['ls_id']
                    advrouter = m.groupdict()['advrouter']
                    age = m.groupdict()['age']
                    seq = m.groupdict()['seq']
                    cksum = m.groupdict()['cksum']
                    if 'ls_id' not in lsa_type:
                        lsa_type['ls_id'] = {}
                    if ls_id not in lsa_type['ls_id']:
                        lsa_type['ls_id'][ls_id] = {}
                    if 'advrouter' not in lsa_type['ls_id'][ls_id]:
                        lsa_type['ls_id'][ls_id]['advrouter'] = {}
                    if advrouter not in lsa_type['ls_id'][ls_id]['advrouter']:
                        lsa_type['ls_id'][ls_id]['advrouter'][advrouter] = {}
                    lsa_type['ls_id'][ls_id]['advrouter'][advrouter]['age'] = age
                    lsa_type['ls_id'][ls_id]['advrouter'][advrouter]['seq'] = seq
                    lsa_type['ls_id'][ls_id]['advrouter'][advrouter]['cksum'] = cksum
                    continue
        return ospf_db_dict

    def xml(self):
        ''' parsing mechanism: xml

        Function xml() defines the xml type output parsing mechanism which
        typically contains 3 steps: executing, transforming, returning
        '''
        output =  tcl.q.caas.abstract(device=self.device.handle,
                                      exec='show ospf vrf all database | xml')
        result = tcl.cast_any(output[1])

        return result