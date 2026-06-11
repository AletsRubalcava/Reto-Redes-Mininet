from mininet.net import Mininet
from mininet.node import OVSSwitch
from mininet.link import TCLink
from mininet.cli import CLI
from mininet.log import setLogLevel, info

from reto_redes.Cede.topologia_cede import Headquarters
from reto_redes.Tiendas.topologia_tienda import Tienda
from reto_redes.Tiendas.topologia_tienda_smart import TiendaSmart

from reto_redes.Cede.ips_cede import subredes_cede, dhcp_config_cede
from reto_redes.Tiendas.ips_tiendas import (
    subredes_mty,
    subredes_cdmx,
    subredes_gdl,
    subredes_smart,
)

SKIP_KEYS = {'router_principal', 'router_respaldo'}

def _add_wan_routes_central(wan, sitio_info, redes_ya_agregadas):
    """Agrega rutas en r_pri hacia las subredes de un sitio remoto."""
    nexthop = sitio_info['wan_nexthop']
    for nivel, vlans in sitio_info['subredes'].items():
        if nivel in SKIP_KEYS:
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

    hq.build(net, subredes_cede)
    tienda_mty.build(net,   subredes_mty)
    tienda_cdmx.build(net,  subredes_cdmx)
    tienda_gdl.build(net,   subredes_gdl)
    tienda_smart.build(net, subredes_smart)

    # ── Enlaces WAN: r_pri es el hub central ─────────────────────────────────
    # r_pri-eth0 → core_sw1 (ROAS, ya existe)
    # r_pri-eth1 → m_rWAN1  (Monterrey)
    # r_pri-eth2 → c_rWAN1  (CDMX)
    # r_pri-eth3 → g_rWAN1  (Guadalajara)
    # r_pri-eth4 → rWAN_s   (Smart)
    net.addLink(hq.router_wan_principal, tienda_mty.router_wan_pri)
    net.addLink(hq.router_wan_principal, tienda_cdmx.router_wan_pri)
    net.addLink(hq.router_wan_principal, tienda_gdl.router_wan_pri)
    net.addLink(hq.router_wan_principal, tienda_smart.router_wan)

    info('*** Iniciando red\n')
    net.start()

    info('*** Aplicando configuración post-inicio\n')
    hq.postBuild(net, subredes_cede, dhcp_config_cede)
    tienda_mty.postBuild(net,   subredes_mty)
    tienda_cdmx.postBuild(net,  subredes_cdmx)
    tienda_gdl.postBuild(net,   subredes_gdl)
    tienda_smart.postBuild(net, subredes_smart)

    r_pri = net.get('r_pri')

    # ── IPs enlaces WAN ───────────────────────────────────────────────────────
    # HQ ↔ MTY
    r_pri.cmd(               'ip addr add 172.16.1.2/30  dev r_pri-eth1')
    r_pri.cmd(               'ip link set r_pri-eth1 up')
    net.get('m_rWAN1').cmd(  'ip addr add 172.16.1.1/30  dev m_rWAN1-eth1')
    net.get('m_rWAN1').cmd(  'ip link set m_rWAN1-eth1 up')

    # HQ ↔ CDMX
    r_pri.cmd(               'ip addr add 172.16.1.6/30  dev r_pri-eth2')
    r_pri.cmd(               'ip link set r_pri-eth2 up')
    net.get('c_rWAN1').cmd(  'ip addr add 172.16.1.5/30  dev c_rWAN1-eth1')
    net.get('c_rWAN1').cmd(  'ip link set c_rWAN1-eth1 up')

    # HQ ↔ GDL
    r_pri.cmd(               'ip addr add 172.16.1.10/30 dev r_pri-eth3')
    r_pri.cmd(               'ip link set r_pri-eth3 up')
    net.get('g_rWAN1').cmd(  'ip addr add 172.16.1.9/30  dev g_rWAN1-eth1')
    net.get('g_rWAN1').cmd(  'ip link set g_rWAN1-eth1 up')

    # HQ ↔ Smart
    r_pri.cmd(               'ip addr add 172.16.1.14/30 dev r_pri-eth4')
    r_pri.cmd(               'ip link set r_pri-eth4 up')
    net.get('rWAN_s').cmd(   'ip addr add 172.16.1.13/30 dev rWAN_s-eth1')
    net.get('rWAN_s').cmd(   'ip link set rWAN_s-eth1 up')

    # Rutas de los enlaces p2p en r_pri
    r_pri.cmd('ip route add 172.16.1.0/30  dev r_pri-eth1')
    r_pri.cmd('ip route add 172.16.1.4/30  dev r_pri-eth2')
    r_pri.cmd('ip route add 172.16.1.8/30  dev r_pri-eth3')
    r_pri.cmd('ip route add 172.16.1.12/30 dev r_pri-eth4')

    # ── Tabla de sitios ───────────────────────────────────────────────────────
    sitios = {
        'hq': {
            'siteName':    'hq',
            'subredes':    subredes_cede,
            'wan_ip':      '172.16.1.2',   # IP de r_pri en cada enlace (no importa para HQ)
            'wan_nexthop': None,
            'enlace_wan':  None,
        },
        'mty': {
            'siteName':    'm',
            'subredes':    subredes_mty,
            'wan_ip':      '172.16.1.2',
            'wan_nexthop': '172.16.1.1',
            'enlace_wan':  '172.16.1.0/30',
        },
        'cdmx': {
            'siteName':    'c',
            'subredes':    subredes_cdmx,
            'wan_ip':      '172.16.1.6',
            'wan_nexthop': '172.16.1.5',
            'enlace_wan':  '172.16.1.4/30',
        },
        'gdl': {
            'siteName':    'g',
            'subredes':    subredes_gdl,
            'wan_ip':      '172.16.1.10',
            'wan_nexthop': '172.16.1.9',
            'enlace_wan':  '172.16.1.8/30',
        },
        'smart': {
            'siteName':    'smart',
            'subredes':    subredes_smart,
            'wan_ip':      '172.16.1.14',
            'wan_nexthop': '172.16.1.13',
            'enlace_wan':  '172.16.1.12/30',
        },
    }

    # ── Rutas en cada tienda hacia todos los demás sitios ────────────────────
    tienda_mty.configure_wan_routes(  net, sitios, sitios['mty']['wan_ip'])
    tienda_cdmx.configure_wan_routes( net, sitios, sitios['cdmx']['wan_ip'])
    tienda_gdl.configure_wan_routes(  net, sitios, sitios['gdl']['wan_ip'])
    tienda_smart.configure_wan_routes(net, sitios, sitios['smart']['wan_ip'])

    # ── Rutas en r_pri hacia cada tienda ─────────────────────────────────────
    redes_agregadas = set()
    for nombre, info_sitio in sitios.items():
        if nombre == 'hq':
            continue
        _add_wan_routes_central(r_pri, info_sitio, redes_agregadas)

    # ── Rutas de HQ hacia tiendas (para que rWAN_s y rWAN1s sepan volver) ───
    # Cada router de tienda necesita rutas hacia HQ
    hq_networks = [datos['network']
                   for area in subredes_cede.values()
                   for datos in area.values()]

    for nombre, info_sitio in sitios.items():
        if nombre == 'hq':
            continue
        nexthop_hacia_hq = info_sitio['wan_ip']   # IP de r_pri en ese enlace
        router_name = f"{info_sitio['siteName']}_rWAN1" if nombre != 'smart' else 'rWAN_s'
        router = net.get(router_name)
        for network in hq_networks:
            router.cmd(f"ip route add {network} via {nexthop_hacia_hq}")

    info('\n' + '='*60 + '\n')
    info('  HEADQUARTERS + TIENDAS  |  Red lista\n')
    info('='*60 + '\n\n')

    CLI(net)

    info('*** Deteniendo red\n')
    net.stop()

if __name__ == '__main__':
    run()