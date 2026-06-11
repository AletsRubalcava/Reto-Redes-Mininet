from mininet.net import Mininet
from mininet.node import OVSSwitch
from mininet.link import TCLink
from mininet.cli import CLI
from mininet.log import setLogLevel, info

from Cede.topologia_cede import Headquarters
from Cede.ips_cede import subredes_cede, dhcp_config_cede

def run():
    setLogLevel('info')

    net = Mininet(link=TCLink, switch=OVSSwitch)

    # Construir topología
    info('*** Construyendo topología de la Headquarters\n')
    hq = Headquarters()
    hq.build(net, subredes_cede)

    # Iniciar red
    info('*** Iniciando red\n')
    net.start()

    # Configurar VLANs, ROAS y servicios 
    info('*** Aplicando configuración post-inicio\n')
    hq.postBuild(net, subredes_cede, dhcp_config_cede)

    info('\n' + '='*60 + '\n')
    info('  HEADQUARTERS - CEDE MTY  |  Red lista\n')
    info('='*60 + '\n')
    info('\n  VLANs activas:\n')
    info('    VLAN 10  -> Finanzas            10.0.0.0/27\n')
    info('    VLAN 20  -> Recursos Humanos    10.0.0.32/27\n')
    info('    VLAN 30  -> TI                  10.0.0.64/27\n')
    info('    VLAN 40  -> Dirección General   10.0.0.96/27\n')
    info('    VLAN 50  -> Usuarios Corp.      10.0.0.128/25\n')
    info('    VLAN 60  -> CCTV / Seguridad    10.0.1.0/26\n')
    info('    VLAN 70  -> Servidores / NOC    10.0.1.64/27\n')
    info('    VLAN 80  -> Guest               10.0.1.128/25\n')
    info('    VLAN 90  -> BYOD Empleados      10.0.2.0/24\n')
    info('    VLAN 100 -> Impresoras          10.0.3.0/27\n')
    info('\n  Comandos útiles dentro del CLI:\n')
    info('    nodes              -> lista todos los nodos\n')
    info('    links              -> lista todos los enlaces\n')
    info('    pingall            -> prueba conectividad entre todos los hosts\n')
    info('    h1 ping h2         -> ping entre hosts específicos\n')
    info('    h1 ip addr         -> ver IPs asignadas a un host\n')
    info('    xterm h1           -> abrir terminal gráfica en un host\n')
    info('='*60 + '\n\n')

    # Abrir CLI interactivo
    CLI(net)

    # Apagar red al salir del CLI 
    info('*** Deteniendo red\n')
    net.stop()


if __name__ == '__main__':
    run()