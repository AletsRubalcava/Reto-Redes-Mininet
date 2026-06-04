from mininet.node import Node, OVSSwitch
from mininet.link import TCLink
from mininet.log import info

# Clase Router
class Router(Node):
    """Nodo con IP forwarding activado y RP filter desactivado."""

    def config(self, **params):
        super(Router, self).config(**params)
        self.cmd('sysctl -w net.ipv4.ip_forward=1')
        self.cmd('sysctl -w net.ipv4.conf.all.rp_filter=0')
        self.cmd('sysctl -w net.ipv4.conf.default.rp_filter=0')

    def terminate(self):
        self.cmd('sysctl -w net.ipv4.ip_forward=0')
        super(Router, self).terminate()

# Clase Tienda
class Tienda:

    def __init__(self):
        # Referencias a nodos clave (se llenan en build)
        self.router_wan_pri  = None
        self.router_wan_sec  = None
        self.core_sw1        = None   # Switch Intermedio Capa 3 – izquierdo
        self.core_sw2        = None   # Switch Intermedio Capa 3 – derecho
        self.acc_sw_p1       = None   # Switch Acceso Piso 1
        self.acc_sw_p2       = None   # Switch Acceso Piso 2

    # Build
    def build(self, net, site):
        info('*** Creando routers WAN\n')
        self._build_wan(net)

        info('*** Creando Core Stack (Capa 3)\n')
        self._build_core(net)

        info('*** Creando Piso 1\n')
        self._build_piso1(net, site)

        info('*** Creando Piso 2\n')
        self._build_piso2(net, site)

        info('*** Configurando enlaces trunk/inter-capas\n')
        self._build_uplinks(net)

    # WAN
    def _build_wan(self, net):
        self.router_wan_pri = net.addHost(
            'rWAN1', cls=Router,
            ip='203.0.113.1/30'
        )
        self.router_wan_sec = net.addHost(
            'rWAN2', cls=Router,
            ip='198.51.100.1/30'
        )

    # Core / Capa 3
    def _build_core(self, net):
        # Dos switches Capa-3 interconectados (simulan el Core Stack con LACP)
        self.core_sw1 = net.addSwitch('core_sw1', cls=OVSSwitch, failMode='standalone')
        self.core_sw2 = net.addSwitch('core_sw2', cls=OVSSwitch, failMode='standalone')

        # Enlace de interconexión entre los dos switches core (trunk / LACP)
        net.addLink(self.core_sw1, self.core_sw2, cls=TCLink, bw=10000)   # 10 Gbps

        # Core -> Router WAN Principal  (WAN-PRI)
        net.addLink(self.core_sw1, self.router_wan_pri, cls=TCLink, bw=1000)    # 1 Gbps

        # Core -> Router WAN Secundario (WAN-SEC)
        net.addLink(self.core_sw2, self.router_wan_sec, cls=TCLink, bw=1000)    # 1 Gbps

    # Piso 1
    def _build_piso1(self, net, site):
        self.acc_sw_p1 = net.addSwitch('swP1', cls=OVSSwitch, failMode='standalone')

        for _, datos in site['piso1'].items():
            gateway = datos["gateway"]
            prefix = datos["prefix"]
            for nombre, ip in datos.items():

                if nombre in ["network", "gateway", "broadcast", "prefix"]:
                    continue

                host = net.addHost(nombre, ip=f"{ip}/{prefix}",defaultRoute=f"via {gateway}")
                net.addLink(host, self.acc_sw_p1, cls=TCLink, bw=1000)

    # Piso 2
    def _build_piso2(self, net, site):
        self.acc_sw_p2 = net.addSwitch('swP2', cls=OVSSwitch, failMode='standalone')

        for _, datos in site['piso2'].items():
            gateway = datos["gateway"]
            prefix = datos["prefix"]
            for nombre, ip in datos.items():

                if nombre in ["network", "gateway", "broadcast", "prefix"]:
                    continue

                host = net.addHost(nombre, ip=f"{ip}/{prefix}",defaultRoute=f"via {gateway}")
                net.addLink(host, self.acc_sw_p2, cls=TCLink, bw=1000)

    # Uplinks (trunk Capa 3 <-> Switches de acceso)
    def _build_uplinks(self, net):
        # TRUNK-01: Switch Piso 1 -> Core (LACP 2×10 Gbps)
        net.addLink(self.acc_sw_p1, self.core_sw1,
                    cls=TCLink, bw=10000)
        net.addLink(self.acc_sw_p1, self.core_sw2,   # segundo enlace LACP
                    cls=TCLink, bw=10000)
        
        # TRUNK-02: Switch Piso 2 -> Core (LACP 2×10 Gbps)
        net.addLink(self.acc_sw_p2, self.core_sw1,
                    cls=TCLink, bw=10000)
        net.addLink(self.acc_sw_p2, self.core_sw2,   # segundo enlace LACP
                    cls=TCLink, bw=10000)