# ============================================================
#  main_smart.py  —  Punto de entrada para la Tienda Smart
#  Coloca este archivo en:  Reto-Redes-Mininet/main_smart.py
#  Ejecutar con:  sudo python3 main_smart.py
# ============================================================

from mininet.net import Mininet
from mininet.node import OVSSwitch
from mininet.link import TCLink
from mininet.cli import CLI
from mininet.log import setLogLevel, info

from Tiendas.topologia_tienda_smart import TiendaSmart
from Tiendas.ips_smart import subredes_smart


def run():
    setLogLevel('info')

    net = Mininet(link=TCLink, switch=OVSSwitch)

    info('*** Construyendo topologia de la Tienda Smart\n')
    tienda = TiendaSmart()
    tienda.build(net, subredes_smart)

    info('*** Iniciando red\n')
    net.start()
    tienda.postBuild(net, subredes_smart)

    info('\n*** Tienda Smart lista. Ingresando al CLI de Mininet ***\n')
    info('--- COMANDOS UTILES ---\n')
    info('  nodes                          → lista todos los nodos\n')
    info('  pingall                        → verifica conectividad general\n')
    info('  s_gwPagos ping -c3 s_edgeIA    → VLAN 40 habla con VLAN 50\n')
    info('  s_cctv ping -c3 s_camIA        → ambas camaras (Switch Camaras)\n')
    info('  s_sensorIoT ping -c3 s_gwPagos → IoT habla con Pagos\n')
    info('  s_gwPagos curl http://10.0.10.34 → prueba servidor HTTP\n')
    info('-----------------------\n\n')
    CLI(net)

    info('*** Deteniendo red\n')
    net.stop()


if __name__ == '__main__':
    run()
