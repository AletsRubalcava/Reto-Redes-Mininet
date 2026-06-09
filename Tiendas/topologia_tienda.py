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
        self.cmd('modprobe 8021q')

    def terminate(self):
        self.cmd('sysctl -w net.ipv4.ip_forward=0')
        super(Router, self).terminate()

# Clase Tienda
class Tienda:

    def __init__(self):
        # Referencias a nodos clave
        self.router_wan_pri = None
        self.router_wan_sec = None
        self.core_sw1 = None
        self.core_sw2 = None
        self.acc_sw_p1 = None
        self.acc_sw_p2 = None

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
        #self.router_wan_pri = net.addHost('rWAN1', cls=Router, ip='203.0.113.1/30')
        self.router_wan_pri = net.addHost('rWAN1', cls=Router)
        self.router_wan_sec = net.addHost('rWAN2', cls=Router, ip='198.51.100.1/30')

    # Core / Capa 3
    def _build_core(self, net):
        # Dos switches Capa-3 interconectados (simulan el Core Stack con LACP)
        self.core_sw1 = net.addSwitch('core_sw1', cls=OVSSwitch, failMode='standalone')
        self.core_sw2 = net.addSwitch('core_sw2', cls=OVSSwitch, failMode='standalone')

        # Enlace de interconexión entre los dos switches core (trunk / LACP)
        net.addLink(self.core_sw1, self.core_sw2, cls=TCLink, bw=10)   # 10 Gbps

        # Core -> Router WAN Principal  (WAN-PRI)
        net.addLink(self.core_sw1, self.router_wan_pri, cls=TCLink, bw=1)    # 1 Gbps

        # Core -> Router WAN Secundario (WAN-SEC)
        net.addLink(self.core_sw2, self.router_wan_sec, cls=TCLink, bw=1)    # 1 Gbps

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
                net.addLink(host, self.acc_sw_p1, cls=TCLink, bw=1)

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
                net.addLink(host, self.acc_sw_p2, cls=TCLink, bw=1)

    # Uplinks (trunk Capa 3 <-> Switches de acceso)
    def _build_uplinks(self, net):
        # TRUNK-01: Switch Piso 1 -> Core (LACP 2×10 Gbps)
        net.addLink(self.acc_sw_p1, self.core_sw1, cls=TCLink, bw=10)
        #net.addLink(self.acc_sw_p1, self.core_sw2, cls=TCLink, bw=10)
        
        # TRUNK-02: Switch Piso 2 -> Core (LACP 2×10 Gbps)
        net.addLink(self.acc_sw_p2, self.core_sw1, cls=TCLink, bw=10)
        #net.addLink(self.acc_sw_p2, self.core_sw2, cls=TCLink, bw=10)
        
    def apply_vlans(self, net, site):
        # Configurar tags de acceso en hosts
        for piso, vlans in site.items():
            sw = self.acc_sw_p1 if piso == "piso1" else self.acc_sw_p2

            for vlan, datos in vlans.items():
                for nombre in datos:
                    if nombre in ["network", "gateway", "broadcast", "prefix"]:
                        continue

                    host = net.get(nombre)
                    _, switch_intf = host.connectionsTo(sw)[0]
                    sw.cmd(f"ovs-vsctl set port {switch_intf.name} tag={vlan}")

        vlans_p1 = set(site.get("piso1", {}).keys())
        vlans_p2 = set(site.get("piso2", {}).keys())

        trunk_str_p1  = ",".join(str(v) for v in sorted(vlans_p1))
        trunk_str_p2  = ",".join(str(v) for v in sorted(vlans_p2))

        _, p1_to_core = self.acc_sw_p1.connectionsTo(self.core_sw1)[0]
        _, p2_to_core = self.acc_sw_p2.connectionsTo(self.core_sw1)[0]
        p1_uplink_intf, _ = self.acc_sw_p1.connectionsTo(self.core_sw1)[0]
        p2_uplink_intf, _ = self.acc_sw_p2.connectionsTo(self.core_sw1)[0]

        self.acc_sw_p1.cmd(f"ovs-vsctl set port {p1_uplink_intf.name} trunks={trunk_str_p1}")
        self.acc_sw_p2.cmd(f"ovs-vsctl set port {p2_uplink_intf.name} trunks={trunk_str_p2}")

        self.core_sw1.cmd(f"ovs-vsctl set port {p1_to_core.name} trunks={trunk_str_p1}")
        self.core_sw1.cmd(f"ovs-vsctl set port {p2_to_core.name} trunks={trunk_str_p2}")


    def configure_roas(self, net, site):
        r = net.get('rWAN1')
        vlans_done = set()

        for piso, vlans in site.items():
            for vlan, datos in vlans.items():
                if vlan in vlans_done:
                    continue
                vlans_done.add(vlan)

                gateway = datos["gateway"]
                prefix  = datos["prefix"]

                r.cmd(f"ip link add link rWAN1-eth0 name rWAN1-eth0.{vlan} type vlan id {vlan}")
                r.cmd(f"ip addr add {gateway}/{prefix} dev rWAN1-eth0.{vlan}")
                r.cmd(f"ip link set rWAN1-eth0.{vlan} up")

        r.cmd("ip link set rWAN1-eth0 up")

    def setHTTPserver(self, net):
        pos = net.get('pos')

        pos.cmd('mkdir -p /tmp/web')

        pos.cmd("""
        echo '<html>
    <head><title>POS Monterrey</title></head>
        <body>
            <h1>Sistema POS Tienda Monterrey</h1>
        </body>
</html>' > /tmp/web/index.html
        """)

        pos.cmd('python3 -m http.server 80 --directory /tmp/web &')

    def setFTPserver(self, net):
        pos = net.get('pos')

        pos.cmd('mkdir -p /tmp/ftp')
        pos.cmd('echo "Ventas del dia" > /tmp/ftp/ventas.txt')

        pos.cmd(
            'python3 -m pyftpdlib '
            '-p 21 '
            '-d /tmp/ftp &'
        )