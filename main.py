from mininet.net import Mininet
from mininet.node import OVSSwitch, Controller
from mininet.link import TCLink
from mininet.cli import CLI
from mininet.log import setLogLevel, info
from Tiendas.topologia_tienda import Tienda
from Tiendas.ips_tiendas import subredes_mty

def run():
    setLogLevel('info')

    net = Mininet(link=TCLink, switch=OVSSwitch)

    info('*** Construyendo topología de la Tienda\n')
    tienda = Tienda()
    tienda.build(net, subredes_mty)

    info('*** Iniciando red\n')
    net.start()

    info('*** Setting VLANs\n')
    tienda.apply_vlans(net, subredes_mty)
    tienda.configure_roas(net, subredes_mty)

    info('\n*** Topología lista. Ingresando al CLI de Mininet ***\n')
    info('    Tip: ejecuta "nodes" para ver todos los nodos\n')
    info('    Tip: ejecuta "links" para ver todos los enlaces\n')
    info('    Tip: ejecuta "pingall" para verificar conectividad básica\n\n')
    CLI(net)

    info('*** Deteniendo red\n')
    net.stop()

if __name__ == '__main__':
    run()
