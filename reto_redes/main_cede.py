from mininet.net import Mininet
from mininet.node import OVSSwitch
from mininet.link import TCLink
from mininet.cli import CLI
from mininet.log import setLogLevel, info

from reto_redes.Cede.topologia_cede import Headquarters
from reto_redes.Tiendas.topologia_tienda import Tienda
from reto_redes.Tiendas.topologia_tienda_smart import TiendaSmart
from reto_redes.Warehouses.warehouse import Warehouse

from reto_redes.Cede.ips_cede import subredes_cede, dhcp_config_cede
from reto_redes.Tiendas.ips_tiendas import (
    subredes_mty, subredes_cdmx, subredes_gdl, subredes_smart,
)
from reto_redes.Warehouses.ips_warehouses import subredes_wm, subredes_wc

SKIP_KEYS = {'router_principal', 'router_respaldo'}

def _add_wan_routes_central(wan, sitio_info, redes_ya_agregadas):
    nexthop = sitio_info['wan_nexthop']
    skip = sitio_info.get('skip_keys', SKIP_KEYS)
    for nivel, vlans in sitio_info['subredes'].items():
        if nivel in skip:
            continue
        for vlan, datos in vlans.items():
            network = datos['network']
            if network not in redes_ya_agregadas:
                wan.cmd(f"ip route add {network} via {nexthop}")
                redes_ya_agregadas.add(network)

def run():
    setLogLevel('info')
    net = Mininet(link=TCLink, switch=OVSSwitch)

    info('*** Construyendo topología\n')
    hq           = Headquarters()
    tienda_mty   = Tienda()
    tienda_cdmx  = Tienda()
    tienda_gdl   = Tienda()
    tienda_smart = TiendaSmart()
    wh_mty       = Warehouse()
    wh_cdmx      = Warehouse()

    hq.build(net, subredes_cede)
    tienda_mty.build(net,   subredes_mty)
    tienda_cdmx.build(net,  subredes_cdmx)
    tienda_gdl.build(net,   subredes_gdl)
    tienda_smart.build(net, subredes_smart)
    wh_mty.build(net,  subredes_wm,  'wm')
    wh_cdmx.build(net, subredes_wc, 'wc')

    net.addLink(hq.router_wan_principal, tienda_mty.router_wan_pri)    # eth1
    net.addLink(hq.router_wan_principal, tienda_cdmx.router_wan_pri)   # eth2
    net.addLink(hq.router_wan_principal, tienda_gdl.router_wan_pri)    # eth3
    net.addLink(hq.router_wan_principal, tienda_smart.router_wan)      # eth4
    net.addLink(hq.router_wan_principal, wh_mty.router_wan)            # eth5
    net.addLink(hq.router_wan_principal, wh_cdmx.router_wan)           # eth6

    info('*** Iniciando red\n')
    net.start()

    info('*** Aplicando configuración post-inicio\n')
    hq.postBuild(net, subredes_cede, dhcp_config_cede)
    tienda_mty.postBuild(net,   subredes_mty)
    tienda_cdmx.postBuild(net,  subredes_cdmx)
    tienda_gdl.postBuild(net,   subredes_gdl)
    tienda_smart.postBuild(net, subredes_smart)
    wh_mty.postBuild(net,  subredes_wm)
    wh_cdmx.postBuild(net, subredes_wc)

    r_pri = net.get('r_pri')

    enlaces = [
        # (eth_idx, r_pri_ip,      remote_node,   remote_ip,      p2p_net)
        (1, '172.16.1.2/30',  'm_rWAN1',   '172.16.1.1/30',  '172.16.1.0/30'),
        (2, '172.16.1.6/30',  'c_rWAN1',   '172.16.1.5/30',  '172.16.1.4/30'),
        (3, '172.16.1.10/30', 'g_rWAN1',   '172.16.1.9/30',  '172.16.1.8/30'),
        (4, '172.16.1.14/30', 'rWAN_s',    '172.16.1.13/30', '172.16.1.12/30'),
        (5, '172.16.1.18/30', 'wm_rWAN1',  '172.16.1.17/30', '172.16.1.16/30'),
        (6, '172.16.1.22/30', 'wc_rWAN1', '172.16.1.21/30', '172.16.1.20/30'),
    ]

    for eth_idx, pri_ip, remote_name, remote_ip, p2p_net in enlaces:
        r_pri.cmd(f'ip addr add {pri_ip} dev r_pri-eth{eth_idx}')
        r_pri.cmd(f'ip link set r_pri-eth{eth_idx} up')
        r_pri.cmd(f'ip route add {p2p_net} dev r_pri-eth{eth_idx}')
        remote = net.get(remote_name)
        remote_eth = 'rWAN_s-eth1' if remote_name == 'rWAN_s' else f'{remote_name}-eth1'
        remote.cmd(f'ip addr add {remote_ip} dev {remote_eth}')
        remote.cmd(f'ip link set {remote_eth} up')

    sitios = {
        'hq': {
            'siteName':    'hq',
            'subredes':    subredes_cede,
            'wan_ip':      None,
            'wan_nexthop': None,
            'enlace_wan':  None,
            'skip_keys':   set(),
        },
        'mty': {
            'siteName':    'm',
            'subredes':    subredes_mty,
            'wan_ip':      '172.16.1.2',
            'wan_nexthop': '172.16.1.1',
            'enlace_wan':  '172.16.1.0/30',
            'skip_keys':   SKIP_KEYS,
        },
        'cdmx': {
            'siteName':    'c',
            'subredes':    subredes_cdmx,
            'wan_ip':      '172.16.1.6',
            'wan_nexthop': '172.16.1.5',
            'enlace_wan':  '172.16.1.4/30',
            'skip_keys':   SKIP_KEYS,
        },
        'gdl': {
            'siteName':    'g',
            'subredes':    subredes_gdl,
            'wan_ip':      '172.16.1.10',
            'wan_nexthop': '172.16.1.9',
            'enlace_wan':  '172.16.1.8/30',
            'skip_keys':   SKIP_KEYS,
        },
        'smart': {
            'siteName':    'smart',
            'subredes':    subredes_smart,
            'wan_ip':      '172.16.1.14',
            'wan_nexthop': '172.16.1.13',
            'enlace_wan':  '172.16.1.12/30',
            'skip_keys':   SKIP_KEYS,
        },
        'wh_mty': {
            'siteName':    'wm',
            'subredes':    subredes_wm,
            'wan_ip':      '172.16.1.18',
            'wan_nexthop': '172.16.1.17',
            'enlace_wan':  '172.16.1.16/30',
            'skip_keys':   {'router_principal'},
        },
        'wh_cdmx': {
            'siteName':    'wc',
            'subredes':    subredes_wc,
            'wan_ip':      '172.16.1.22',
            'wan_nexthop': '172.16.1.21',
            'enlace_wan':  '172.16.1.20/30',
            'skip_keys':   {'router_principal'},
        },
    }

    tienda_mty.configure_wan_routes(  net, sitios, sitios['mty']['wan_ip'])
    tienda_cdmx.configure_wan_routes( net, sitios, sitios['cdmx']['wan_ip'])
    tienda_gdl.configure_wan_routes(  net, sitios, sitios['gdl']['wan_ip'])
    tienda_smart.configure_wan_routes(net, sitios, sitios['smart']['wan_ip'])
    wh_mty.configure_wan_routes(      net, sitios, sitios['wh_mty']['wan_ip'])
    wh_cdmx.configure_wan_routes(     net, sitios, sitios['wh_cdmx']['wan_ip'])

    redes_agregadas = set()
    for nombre, info_sitio in sitios.items():
        if nombre == 'hq' or info_sitio['wan_nexthop'] is None:
            continue
        _add_wan_routes_central(r_pri, info_sitio, redes_agregadas)

    hq_networks = [
        datos['network']
        for area in subredes_cede.values()
        for datos in area.values()
    ]

    remote_map = {
        'mty':    ('m_rWAN1',       '172.16.1.2'),
        'cdmx':   ('c_rWAN1',       '172.16.1.6'),
        'gdl':    ('g_rWAN1',       '172.16.1.10'),
        'smart':  ('rWAN_s',        '172.16.1.14'),
        'wh_mty': ('wm_rWAN1',  '172.16.1.18'),
        'wh_cdmx':('wc_rWAN1', '172.16.1.22'),
    }
    for sitio_key, (router_name, nexthop_hq) in remote_map.items():
        router = net.get(router_name)
        for network in hq_networks:
            router.cmd(f"ip route add {network} via {nexthop_hq}")

    info('\n*** Red lista\n')
    CLI(net)

    info('*** Deteniendo red\n')
    net.stop()

if __name__ == '__main__':
    run()