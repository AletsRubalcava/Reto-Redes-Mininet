from mininet.net import Mininet
from mininet.node import OVSSwitch

from mininet.link import TCLink
from mininet.cli import CLI
from mininet.log import setLogLevel, info

from Tiendas.topologia_tienda import Tienda, Router
from Tiendas.ips_tiendas import (
    subredes_mty,
    subredes_cdmx,
    subredes_gdl
)

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

    tienda_mty.build(net, subredes_mty)
    tienda_cdmx.build(net, subredes_cdmx)
    tienda_gdl.build(net, subredes_gdl)

    info('*** Creando Router WAN Central\n')

    wan = net.addHost(
        'WAN',
        cls=Router
    )

    net.addLink(tienda_mty.router_wan_pri, wan)
    net.addLink(tienda_cdmx.router_wan_pri, wan)
    net.addLink(tienda_gdl.router_wan_pri, wan)

    info('*** Iniciando red\n')

    net.start()

    tienda_mty.postBuild(net, subredes_mty)
    tienda_cdmx.postBuild(net, subredes_cdmx)
    tienda_gdl.postBuild(net, subredes_gdl)

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
    # Levantar interfaces
    #
    net.get('m_rWAN1').cmd('ip link set m_rWAN1-eth1 up')
    net.get('c_rWAN1').cmd('ip link set c_rWAN1-eth1 up')
    net.get('g_rWAN1').cmd('ip link set g_rWAN1-eth1 up')

    wan.cmd('ip link set WAN-eth0 up')
    wan.cmd('ip link set WAN-eth1 up')
    wan.cmd('ip link set WAN-eth2 up')

    sitios = {
    'mty': {'siteName': 'm', 'subredes': subredes_mty, 'wan_ip': '172.16.1.2', 'wan_nexthop': '172.16.1.1'},
    'cdmx': {'siteName': 'c', 'subredes': subredes_cdmx, 'wan_ip': '172.16.1.6', 'wan_nexthop': '172.16.1.5'},
    'gdl': {'siteName': 'g', 'subredes': subredes_gdl, 'wan_ip': '172.16.1.10', 'wan_nexthop': '172.16.1.9'},
}

    tienda_mty.configure_wan_routes(net, sitios, sitios['mty']['wan_ip'])
    tienda_cdmx.configure_wan_routes(net, sitios, sitios['cdmx']['wan_ip'])
    tienda_gdl.configure_wan_routes(net, sitios, sitios['gdl']['wan_ip'])

    # WAN central
    redes_agregadas_wan = set()
    for sitio_nombre, sitio_info in sitios.items():
        for piso, vlans in sitio_info['subredes'].items():
            if piso in ['router_principal', 'router_respaldo']:
                continue
            for vlan, datos in vlans.items():
                network = datos['network']
                if network not in redes_agregadas_wan:
                    wan.cmd(f"ip route add {network} via {sitio_info['wan_nexthop']}")
                    redes_agregadas_wan.add(network)

    info('\n*** Topología lista\n')
    CLI(net)

    net.stop()

if __name__ == '__main__':
    run()