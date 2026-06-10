# ============================================================
#  topologia_tienda_smart.py  —  Clase TiendaSmart para Mininet
# ============================================================
from mininet.node import Node, OVSSwitch
from mininet.link import TCLink
from mininet.log import info


class Router(Node):
    def config(self, **params):
        super(Router, self).config(**params)
        self.cmd('sysctl -w net.ipv4.ip_forward=1')
        self.cmd('sysctl -w net.ipv4.conf.all.rp_filter=0')
        self.cmd('sysctl -w net.ipv4.conf.default.rp_filter=0')
        self.cmd('modprobe 8021q')

    def terminate(self):
        self.cmd('sysctl -w net.ipv4.ip_forward=0')
        super(Router, self).terminate()


class TiendaSmart:
    SITE_PREFIX = "s"

    def __init__(self):
        self.router_wan = None
        self.core_sw    = None
        self.acc_sw     = None
        self.cam_sw     = None

    def build(self, net, site):
        info('*** [Smart] Creando Router WAN\n')
        self._build_wan(net)

        info('*** [Smart] Creando Switch Core L3\n')
        self._build_core(net)

        info('*** [Smart] Creando Switch Acceso + dispositivos\n')
        self._build_zona(net, site, zona_key='acceso', sw_name='acc_s')

        info('*** [Smart] Creando Switch Camaras + dispositivos\n')
        self._build_zona(net, site, zona_key='camaras', sw_name='cam_s')

        info('*** [Smart] Configurando uplinks\n')
        self._build_uplinks(net)

    def postBuild(self, net, site):
        info('*** [Smart] Configurando VLANs en OVS\n')
        self.apply_vlans(net, site)

        info('*** [Smart] Configurando Router-on-a-Stick\n')
        self.configure_roas(net, site)

        info('*** [Smart] Iniciando servidor HTTP/FTP en Gateway de Pagos\n')
        self.setHTTPserver(net)
        self.setFTPserver(net)

    def _build_wan(self, net):
        # FIX: era 203.0.113.9/30 (mismo que GDL). Siguiente bloque libre: .13
        self.router_wan = net.addHost(
            'rWAN_s', cls=Router, ip='203.0.113.13/30'
        )

    def _build_core(self, net):
        self.core_sw = net.addSwitch(
            'core_s', cls=OVSSwitch, failMode='standalone'
        )
        net.addLink(self.core_sw, self.router_wan, cls=TCLink, bw=1)

    def _build_zona(self, net, site, zona_key, sw_name):
        sw = net.addSwitch(sw_name, cls=OVSSwitch, failMode='standalone')

        if zona_key == 'acceso':
            self.acc_sw = sw
        else:
            self.cam_sw = sw

        for vlan, datos in site[zona_key].items():
            gateway = datos["gateway"]
            prefix  = datos["prefix"]

            for nombre, ip in datos.items():
                if nombre in ["network", "gateway", "broadcast", "prefix"]:
                    continue

                host = net.addHost(
                    f"{self.SITE_PREFIX}_{nombre}",
                    ip=f"{ip}/{prefix}",
                    defaultRoute=f"via {gateway}"
                )
                net.addLink(host, sw, cls=TCLink, bw=1)

    def _build_uplinks(self, net):
        net.addLink(self.acc_sw, self.core_sw, cls=TCLink, bw=10)
        net.addLink(self.cam_sw, self.core_sw, cls=TCLink, bw=10)

    def apply_vlans(self, net, site):
        switch_map = {
            'acceso':  self.acc_sw,
            'camaras': self.cam_sw,
        }

        for zona, vlans in site.items():
            sw = switch_map[zona]
            zona_vlans = set()

            for vlan, datos in vlans.items():
                zona_vlans.add(vlan)
                for nombre in datos:
                    if nombre in ["network", "gateway", "broadcast", "prefix"]:
                        continue
                    host = net.get(f"{self.SITE_PREFIX}_{nombre}")
                    _, sw_intf = host.connectionsTo(sw)[0]
                    sw.cmd(f"ovs-vsctl set port {sw_intf.name} tag={vlan}")

            trunk_str = ",".join(str(v) for v in sorted(zona_vlans))
            uplink_intf, core_intf = sw.connectionsTo(self.core_sw)[0]
            sw.cmd(          f"ovs-vsctl set port {uplink_intf.name} trunks={trunk_str}")
            self.core_sw.cmd(f"ovs-vsctl set port {core_intf.name}  trunks={trunk_str}")

    def configure_roas(self, net, site):
        r = net.get('rWAN_s')
        vlans_done = set()

        for zona, vlans in site.items():
            for vlan, datos in vlans.items():
                if vlan in vlans_done:
                    continue
                vlans_done.add(vlan)

                gateway = datos["gateway"]
                prefix  = datos["prefix"]

                r.cmd(f"ip link add link rWAN_s-eth0 name rWAN_s-eth0.{vlan} type vlan id {vlan}")
                r.cmd(f"ip addr add {gateway}/{prefix} dev rWAN_s-eth0.{vlan}")
                r.cmd(f"ip link set rWAN_s-eth0.{vlan} up")

        r.cmd("ip link set rWAN_s-eth0 up")

    def configure_wan_routes(self, net, sitios, wan_ip):
        router = net.get('rWAN_s')
        redes_agregadas = set()

        for otro_nombre, otro_info in sitios.items():
            if otro_info['siteName'] == self.SITE_PREFIX:
                continue

            for zona, contenido in otro_info['subredes'].items():
                if zona in ['router_principal', 'router_respaldo']:
                    continue
                for _, datos in contenido.items():
                    if not isinstance(datos, dict) or 'network' not in datos:
                        continue
                    network = datos['network']
                    if network not in redes_agregadas:
                        router.cmd(f"ip route add {network} via {wan_ip}")
                        redes_agregadas.add(network)

            enlace_wan = otro_info.get('enlace_wan')
            if enlace_wan and enlace_wan not in redes_agregadas:
                router.cmd(f"ip route add {enlace_wan} via {wan_ip}")
                redes_agregadas.add(enlace_wan)

    def setHTTPserver(self, net):
        gw = net.get('s_gwPagos')
        gw.cmd('mkdir -p /tmp/web')
        gw.cmd(
            'echo "<html><head><title>Gateway Pagos Smart</title></head>'
            '<body><h1>Sistema de Cobro Automatico - Unfinished Smart Store</h1>'
            '<p>Transaccion procesada correctamente.</p>'
            '</body></html>" > /tmp/web/index.html'
        )
        gw.cmd('python3 -m http.server 80 --directory /tmp/web &')

    def setFTPserver(self, net):
        gw = net.get('s_gwPagos')
        gw.cmd('mkdir -p /tmp/ftp')
        gw.cmd('echo "Transacciones del dia: 42 cobros exitosos" > /tmp/ftp/transacciones.txt')
        gw.cmd('python3 -m pyftpdlib -p 21 -d /tmp/ftp &')
