from mininet.net import Mininet
from mininet.node import OVSSwitch
from mininet.link import TCLink
from mininet.cli import CLI
from mininet.log import setLogLevel, info

from reto_redes.Tiendas.topologia_tienda import Tienda
from reto_redes.Tiendas.topologia_tienda_smart import TiendaSmart
from reto_redes.router import Router
from reto_redes.Tiendas.ips_tiendas import (
    subredes_mty,
    subredes_cdmx,
    subredes_gdl,
    subredes_smart,
)
import os

SKIP_KEYS = {'router_principal', 'router_respaldo'}

def _add_wan_routes_central(wan, sitio_info, redes_ya_agregadas):
    """Agrega rutas en el nodo WAN central hacia un sitio."""
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
    os.system("pkill -9 dnsmasq 2>/dev/null")

    net = Mininet(link=TCLink, switch=OVSSwitch)

    info('*** Construyendo tiendas\n')

    tienda_mty   = Tienda()
    tienda_cdmx  = Tienda()
    tienda_gdl   = Tienda()
    tienda_smart = TiendaSmart()

    tienda_mty.build(net, subredes_mty)
    tienda_cdmx.build(net, subredes_cdmx)
    tienda_gdl.build(net, subredes_gdl)
    tienda_smart.build(net, subredes_smart)

    info('*** Creando Router WAN Central\n')
    wan = net.addHost('WAN', cls=Router)

    net.addLink(tienda_mty.router_wan_pri,  wan)
    net.addLink(tienda_cdmx.router_wan_pri, wan) 
    net.addLink(tienda_gdl.router_wan_pri,  wan)
    net.addLink(tienda_smart.router_wan,    wan) 

    info('*** Iniciando red\n')
    net.start()

    tienda_mty.postBuild(net, subredes_mty)
    tienda_cdmx.postBuild(net, subredes_cdmx)
    tienda_gdl.postBuild(net, subredes_gdl)
    tienda_smart.postBuild(net, subredes_smart)

    net.get('m_rWAN1').cmd('ip addr add 172.16.1.1/30  dev m_rWAN1-eth1')
    wan.cmd(                'ip addr add 172.16.1.2/30  dev WAN-eth0')

    net.get('c_rWAN1').cmd('ip addr add 172.16.1.5/30  dev c_rWAN1-eth1')
    wan.cmd(                'ip addr add 172.16.1.6/30  dev WAN-eth1')

    net.get('g_rWAN1').cmd('ip addr add 172.16.1.9/30  dev g_rWAN1-eth1')
    wan.cmd(                'ip addr add 172.16.1.10/30 dev WAN-eth2')

    net.get('rWAN_s').cmd(  'ip addr add 172.16.1.13/30 dev rWAN_s-eth1')
    wan.cmd(                'ip addr add 172.16.1.14/30 dev WAN-eth3')

    net.get('m_rWAN1').cmd('ip link set m_rWAN1-eth1 up')
    net.get('c_rWAN1').cmd('ip link set c_rWAN1-eth1 up')
    net.get('g_rWAN1').cmd('ip link set g_rWAN1-eth1 up')
    net.get('rWAN_s').cmd(  'ip link set rWAN_s-eth1  up')

    wan.cmd('ip link set WAN-eth0 up')
    wan.cmd('ip link set WAN-eth1 up')
    wan.cmd('ip link set WAN-eth2 up')
    wan.cmd('ip link set WAN-eth3 up')

    sitios = {
        'mty':  {
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
        'gdl':  {
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

    tienda_mty.configure_wan_routes(  net, sitios, sitios['mty']['wan_ip'])
    tienda_cdmx.configure_wan_routes( net, sitios, sitios['cdmx']['wan_ip'])
    tienda_gdl.configure_wan_routes(  net, sitios, sitios['gdl']['wan_ip'])
    tienda_smart.configure_wan_routes(net, sitios, sitios['smart']['wan_ip'])

    redes_agregadas_wan = set()
    for sitio_info in sitios.values():
        _add_wan_routes_central(wan, sitio_info, redes_agregadas_wan)

    wan.cmd('ip route add 172.16.1.0/30  dev WAN-eth0')
    wan.cmd('ip route add 172.16.1.4/30  dev WAN-eth1')
    wan.cmd('ip route add 172.16.1.8/30  dev WAN-eth2')
    wan.cmd('ip route add 172.16.1.12/30 dev WAN-eth3')

    info('\n*** Topología lista\n')
    CLI(net)
    net.stop()

if __name__ == '__main__':
    run()