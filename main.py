from mininet.net import Mininet
from mininet.node import OVSSwitch
from mininet.link import TCLink
from mininet.cli import CLI
from mininet.log import setLogLevel, info

from Tiendas.topologia_tienda import Tienda, Router
from Tiendas.topologia_tienda_smart import TiendaSmart
from Tiendas.ips_tiendas import (
    subredes_mty,
    subredes_cdmx,
    subredes_gdl
)
from Tiendas.ips_smart import subredes_smart

def run():

    setLogLevel('info')

    net = Mininet(
        link=TCLink,
        switch=OVSSwitch
    )

    info('*** Construyendo tiendas\n')

    tienda_mty = Tienda()
    tienda_cdmx = Tienda()
    tienda_gdl = Tienda()
    tienda_smart = TiendaSmart()

    tienda_mty.build(net, subredes_mty)
    tienda_cdmx.build(net, subredes_cdmx)
    tienda_gdl.build(net, subredes_gdl)
    tienda_smart.build(net, subredes_smart)

    info('*** Creando Router WAN Central\n')

    wan = net.addHost('WAN', cls=Router)

    net.addLink(tienda_mty.router_wan_pri, wan)
    net.addLink(tienda_cdmx.router_wan_pri, wan)
    net.addLink(tienda_gdl.router_wan_pri, wan)
    net.addLink(tienda_smart.router_wan, wan)

    info('*** Iniciando red\n')

    net.start()

    tienda_mty.postBuild(net, subredes_mty)
    tienda_cdmx.postBuild(net, subredes_cdmx)
    tienda_gdl.postBuild(net, subredes_gdl)
    tienda_smart.postBuild(net, subredes_smart)

    #
    # MTY <-> WAN
    #
    net.get('m_rWAN1').cmd('ip addr add 172.16.1.1/30 dev m_rWAN1-eth1')
    wan.cmd('ip addr add 172.16.1.2/30 dev WAN-eth0')

    #
    # CDMX <-> WAN
    #
    net.get('c_rWAN1').cmd('ip addr add 172.16.1.5/30 dev c_rWAN1-eth1')
    wan.cmd('ip addr add 172.16.1.6/30 dev WAN-eth1')

    #
    # GDL <-> WAN
    #
    net.get('g_rWAN1').cmd('ip addr add 172.16.1.9/30 dev g_rWAN1-eth1')
    wan.cmd('ip addr add 172.16.1.10/30 dev WAN-eth2')

    #
    # SMART <-> WAN
    #
    net.get('rWAN_s').cmd('ip addr add 172.16.1.13/30 dev rWAN_s-eth1')
    wan.cmd('ip addr add 172.16.1.14/30 dev WAN-eth3')

    #
    # Levantar interfaces
    #
    net.get('m_rWAN1').cmd('ip link set m_rWAN1-eth1 up')
    net.get('c_rWAN1').cmd('ip link set c_rWAN1-eth1 up')
    net.get('g_rWAN1').cmd('ip link set g_rWAN1-eth1 up')
    net.get('rWAN_s').cmd('ip link set rWAN_s-eth1 up')

    wan.cmd('ip link set WAN-eth0 up')
    wan.cmd('ip link set WAN-eth1 up')
    wan.cmd('ip link set WAN-eth2 up')
    wan.cmd('ip link set WAN-eth3 up')

    sitios = {
        'mty':   {'siteName': 'm', 'subredes': subredes_mty,   'wan_ip': '172.16.1.2',  'wan_nexthop': '172.16.1.1',  'enlace_wan': '172.16.1.0/30'},
        'cdmx':  {'siteName': 'c', 'subredes': subredes_cdmx,  'wan_ip': '172.16.1.6',  'wan_nexthop': '172.16.1.5',  'enlace_wan': '172.16.1.4/30'},
        'gdl':   {'siteName': 'g', 'subredes': subredes_gdl,   'wan_ip': '172.16.1.10', 'wan_nexthop': '172.16.1.9',  'enlace_wan': '172.16.1.8/30'},
        'smart': {'siteName': 's', 'subredes': subredes_smart,  'wan_ip': '172.16.1.14', 'wan_nexthop': '172.16.1.13', 'enlace_wan': '172.16.1.12/30'},
    }

    tienda_mty.configure_wan_routes(net, sitios, sitios['mty']['wan_ip'])
    tienda_cdmx.configure_wan_routes(net, sitios, sitios['cdmx']['wan_ip'])
    tienda_gdl.configure_wan_routes(net, sitios, sitios['gdl']['wan_ip'])
    tienda_smart.configure_wan_routes(net, sitios, sitios['smart']['wan_ip'])

    # WAN central
    redes_agregadas_wan = set()
    for sitio_nombre, sitio_info in sitios.items():
        for zona, vlans in sitio_info['subredes'].items():
            if zona in ['router_principal', 'router_respaldo']:
                continue
            for _, datos in vlans.items():
                if not isinstance(datos, dict) or 'network' not in datos:
                    continue
                network = datos['network']
                if network not in redes_agregadas_wan:
                    wan.cmd(f"ip route add {network} via {sitio_info['wan_nexthop']}")
                    redes_agregadas_wan.add(network)

    wan.cmd('ip route add 172.16.1.0/30 dev WAN-eth0')
    wan.cmd('ip route add 172.16.1.4/30 dev WAN-eth1')
    wan.cmd('ip route add 172.16.1.8/30 dev WAN-eth2')
    wan.cmd('ip route add 172.16.1.12/30 dev WAN-eth3')

    info('\n*** Topología lista\n')
    CLI(net)

    net.stop()

if __name__ == '__main__':
    run()
