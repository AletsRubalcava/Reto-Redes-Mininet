from mininet.node import OVSSwitch
from mininet.link import TCLink
from mininet.log import info
from ..router import Router
from ipaddress import ip_network
class Tienda:

    def __init__(self):
        self.router_wan_pri = None
        self.router_wan_sec = None
        self.core_sw1 = None
        self.core_sw2 = None
        self.acc_sw_p1 = None
        self.acc_sw_p2 = None

    def build(self, net, site):
        self.siteName = self._getSiteName(site)

        info('*** Creando routers WAN\n')
        self._build_wan(net, site)

        info('*** Creando Core Stack (Capa 3)\n')
        self._build_core(net)

        info('*** Creando Piso 1\n')
        self._build_piso1(net, site, self.siteName)

        info('*** Creando Piso 2\n')
        self._build_piso2(net, site, self.siteName)

        info('*** Configurando enlaces trunk/inter-capas\n')
        self._build_uplinks(net)

    def postBuild(self, net, site):

        info('*** Setting VLANs\n')
        self.apply_vlans(net, site)

        self.configure_roas(net, site)

        info('*** Setting Application servers\n')
        self.setHTTPserver(net)
        self.setFTPserver(net)

        info('*** Setting DHCP server\n')
        self.setDHCPserver(net, site)

        info('*** DHCP server listo\n')

        import time
        #time.sleep(2)

        info('*** Solicitando DHCP\n')
        #self.requestDHCP(net, site)

        info('*** DHCP terminado\n')

    def _build_wan(self, net, site):
        self.router_wan_pri = net.addHost(f'{self.siteName}_rWAN1', cls=Router, ip=site['router_principal'])
        self.router_wan_sec = net.addHost(f'{self.siteName}_rWAN2', cls=Router, ip=site['router_respaldo'])

    def _build_core(self, net):
        self.core_sw1 = net.addSwitch(f'{self.siteName}_core_sw1', cls=OVSSwitch, failMode='standalone')
        self.core_sw2 = net.addSwitch(f'{self.siteName}_core_sw2', cls=OVSSwitch, failMode='standalone')
        net.addLink(self.core_sw1, self.core_sw2, cls=TCLink, bw=10)
        net.addLink(self.core_sw1, self.router_wan_pri, cls=TCLink, bw=1)
        net.addLink(self.core_sw2, self.router_wan_sec, cls=TCLink, bw=1)

    def _build_piso1(self, net, site, siteName):
        self.acc_sw_p1 = net.addSwitch(
            f'{siteName}_swP1',
            cls=OVSSwitch,
            failMode='standalone'
        )

        for _, datos in site['piso1'].items():

            gateway = datos["gateway"]
            prefix = datos["prefix"]

            for nombre, ip in datos.items():

                if nombre in ["network", "gateway", "broadcast", "prefix"]:
                    continue

                if ip == "dhcp":

                    host = net.addHost(
                        f"{siteName}_{nombre}", ip=None
                    )

                else:

                    host = net.addHost(
                        f"{siteName}_{nombre}",
                        ip=f"{ip}/{prefix}",
                        defaultRoute=f"via {gateway}"
                    )

                net.addLink(host, self.acc_sw_p1, cls=TCLink, bw=1)

    def _build_piso2(self, net, site, siteName):
        self.acc_sw_p2 = net.addSwitch(
            f'{siteName}_swP2',
            cls=OVSSwitch,
            failMode='standalone'
        )

        for _, datos in site['piso2'].items():
            gateway = datos["gateway"]
            prefix = datos["prefix"]

            for nombre, ip in datos.items():
                if nombre in ["network", "gateway", "broadcast", "prefix"]:
                    continue

                if ip == "dhcp":
                    host = net.addHost(f"{siteName}_{nombre}")
                else:
                    host = net.addHost(
                        f"{siteName}_{nombre}",
                        ip=f"{ip}/{prefix}",
                        defaultRoute=f"via {gateway}"
                    )
                net.addLink(host, self.acc_sw_p2, cls=TCLink, bw=1)

    def _build_uplinks(self, net):
        net.addLink(self.acc_sw_p1, self.core_sw1, cls=TCLink, bw=10)
        net.addLink(self.acc_sw_p2, self.core_sw1, cls=TCLink, bw=10)

    def apply_vlans(self, net, site):
        for piso, vlans in site.items():
            sw = self.acc_sw_p1 if piso == "piso1" else self.acc_sw_p2
            if piso in ["router_principal", "router_respaldo"]:
                continue
            for vlan, datos in vlans.items():
                for nombre in datos:
                    if nombre in ["network", "gateway", "broadcast", "prefix"]:
                        continue
                    host = net.get(f"{self.siteName}_{nombre}")
                    _, switch_intf = host.connectionsTo(sw)[0]
                    sw.cmd(f"ovs-vsctl set port {switch_intf.name} tag={vlan}")

        vlans_p1 = set(site.get("piso1", {}).keys())
        vlans_p2 = set(site.get("piso2", {}).keys())
        trunk_str_p1 = ",".join(str(v) for v in sorted(vlans_p1))
        trunk_str_p2 = ",".join(str(v) for v in sorted(vlans_p2))

        _, p1_to_core = self.acc_sw_p1.connectionsTo(self.core_sw1)[0]
        _, p2_to_core = self.acc_sw_p2.connectionsTo(self.core_sw1)[0]
        p1_uplink_intf, _ = self.acc_sw_p1.connectionsTo(self.core_sw1)[0]
        p2_uplink_intf, _ = self.acc_sw_p2.connectionsTo(self.core_sw1)[0]

        self.acc_sw_p1.cmd(f"ovs-vsctl set port {p1_uplink_intf.name} trunks={trunk_str_p1}")
        self.acc_sw_p2.cmd(f"ovs-vsctl set port {p2_uplink_intf.name} trunks={trunk_str_p2}")
        self.core_sw1.cmd(f"ovs-vsctl set port {p1_to_core.name} trunks={trunk_str_p1}")
        self.core_sw1.cmd(f"ovs-vsctl set port {p2_to_core.name} trunks={trunk_str_p2}")

    def configure_roas(self, net, site):
        r = net.get(f"{self.siteName}_rWAN1")
        router_if = f"{self.siteName}_rWAN1-eth0"
        vlans_done = set()

        for piso, vlans in site.items():
            if piso in ["router_principal", "router_respaldo"]:
                continue
            for vlan, datos in vlans.items():
                if vlan in vlans_done:
                    continue
                vlans_done.add(vlan)
                gateway = datos["gateway"]
                prefix = datos["prefix"]
                r.cmd(f"ip link add link {router_if} name {router_if}.{vlan} type vlan id {vlan}")
                r.cmd(f"ip addr add {gateway}/{prefix} dev {router_if}.{vlan}")
                r.cmd(f"ip link set {router_if}.{vlan} up")

        r.cmd(f"ip link set {router_if} up")

    def setHTTPserver(self, net):
        pos = net.get(f"{self.siteName}_pos")
        web_dir = f'/tmp/web_{self.siteName}'
        pos.cmd(f'mkdir -p {web_dir}')
        pos.cmd(f'echo "<html><head><title>POS {self.siteName.upper()}</title></head>'
                f'<body><h1>Sistema POS Tienda {self.siteName.upper()}</h1>'
                f'</body></html>" > {web_dir}/index.html')
        pos.cmd(f'python3 -m http.server 80 --directory {web_dir} &')

    def setFTPserver(self, net):
        pos = net.get(f"{self.siteName}_pos")
        pos.cmd('mkdir -p /tmp/ftp')
        pos.cmd('echo "Ventas del dia" > /tmp/ftp/ventas.txt')
        pos.cmd('python3 -m pyftpdlib -p 21 -d /tmp/ftp &')

    def _getSiteName(self, site):
        network = site['piso1'][10]['network']
        if network == "10.0.6.32/27":
            return "m"
        elif network == "10.0.7.96/27":
            return "c"
        elif network == "10.0.8.160/27":
            return "g"
        return "x"

    def configure_wan_routes(self, net, sitios, wan_ip):
        router = net.get(f"{self.siteName}_rWAN1")
        redes_agregadas = set()

        for otro_nombre, otro_info in sitios.items():
            if otro_info['siteName'] == self.siteName:
                continue
            for piso, vlans in otro_info['subredes'].items():
                if piso in ['router_principal', 'router_respaldo']:
                    continue
                for vlan, datos in vlans.items():
                    network = datos['network']
                    if network not in redes_agregadas:
                        router.cmd(f"ip route add {network} via {wan_ip}")
                        redes_agregadas.add(network)
            enlace_wan = otro_info['enlace_wan']
            if enlace_wan not in redes_agregadas:
                router.cmd(f"ip route add {enlace_wan} via {wan_ip}")
                redes_agregadas.add(enlace_wan)

    def setDHCPserver(self, net, site):
        router = net.get(f"{self.siteName}_rWAN1")
        vlans_done = set()
        for piso, vlans in site.items():
            if piso in ["router_principal", "router_respaldo"]:
                continue
            for vlan, datos in vlans.items():
                if vlan in vlans_done:
                    continue
                vlans_done.add(vlan)

                red = ip_network(datos["network"])
                gateway = datos["gateway"]

                hosts = list(red.hosts())
                start = str(hosts[1])
                end = str(hosts[-1])

                router.cmd(
                    f"dnsmasq "
                    f"--interface={self.siteName}_rWAN1-eth0.{vlan} "
                    f"--dhcp-range={start},{end},{red.netmask},12h "
                    f"--dhcp-option=3,{gateway} "
                    f"--dhcp-authoritative "
                    f"--pid-file=/tmp/dnsmasq_{vlan}.pid &"
                )

    def requestDHCP(self, net, site):
        for piso, vlans in site.items():
            if piso in ["router_principal", "router_respaldo"]:
                continue
            for vlan, datos in vlans.items():
                for nombre, ip in datos.items():
                    if nombre in ["network", "gateway", "broadcast", "prefix"]:
                        continue
                    if ip == "dhcp":
                        host = net.get(f"{self.siteName}_{nombre}")
                        info(f"*** Solicitando DHCP para {host.name}\n")
                        host.cmd(
                            f"dhclient -1 -v {host.name}-eth0"
                        )