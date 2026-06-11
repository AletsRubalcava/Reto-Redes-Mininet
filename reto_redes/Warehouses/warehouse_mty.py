from mininet .link import TCLink
from mininet .cli import CLI
from mininet .log import info
from mininet.node import OVSSwitch
from reto_redes.router import Router
from ipaddress import ip_network

class Warehouse:

    def __init__(self):
        self.siteName = None
        self.router_wan = None
        self.core_sw = None
        self.sw_recepcion = None
        self.sw_almacen = None
        self.sw_operaciones = None
    
    def build(self, net, site, siteName):

        self.siteName = siteName

        self._build_wan(net, site)
        self._build_core(net)

        self._build_zona(
            net,
            site,
            "recepcion",
            f"{siteName}_r_sw1"
        )

        self._build_zona(
            net,
            site,
            "almacen",
            f"{siteName}_a_sw1"
        )

        self._build_zona(
            net,
            site,
            "operaciones",
            f"{siteName}_o_sw1"
        )

        self._build_uplinks(net)

    def postBuild(self, net, site):
        self.apply_vlans(net, site)

        self.configure_roas(net, site)

        #self.setDHCPserver(net, site)

        import time
        time.sleep(2)

        #self.requestDHCP(net, site)

    def _build_wan(self, net, site):

        self.router_wan = net.addHost(
            f"{self.siteName}_rWAN1",
            cls=Router,
            ip=site["router_principal"]
        )

    def _build_core(self, net):

        self.core_sw = net.addSwitch(
            f"{self.siteName}_c_sw1",
            cls=OVSSwitch,
            failMode="standalone"
        )

        net.addLink(
            self.core_sw,
            self.router_wan,
            cls=TCLink,
            bw=1
        )

    def _build_zona(self, net, site, zona, sw_name):

        sw = net.addSwitch(
            sw_name,
            cls=OVSSwitch,
            failMode="standalone"
        )

        if zona == "recepcion":
            self.sw_recepcion = sw

        elif zona == "almacen":
            self.sw_almacen = sw

        else:
            self.sw_operaciones = sw

        for vlan, datos in site[zona].items():

            gateway = datos["gateway"]
            prefix = datos["prefix"]

            for nombre, ip in datos.items():

                if nombre in [
                    "network",
                    "gateway",
                    "broadcast",
                    "prefix"
                ]:
                    continue

                if ip == "dhcp":
                    host = net.addHost(f"{self.siteName}_{nombre}",ip=None)
                else:
                    host = net.addHost(f"{self.siteName}_{nombre}",ip=f"{ip}/{prefix}",defaultRoute=f"via {gateway}")

                net.addLink(host,sw,cls=TCLink,bw=1)

    def _build_uplinks(self, net):
        net.addLink(
            self.sw_recepcion,
            self.core_sw,
            cls=TCLink,
            bw=10
        )

        net.addLink(
            self.sw_almacen,
            self.core_sw,
            cls=TCLink,
            bw=10
        )

        net.addLink(
            self.sw_operaciones,
            self.core_sw,
            cls=TCLink,
            bw=10
        )

    def apply_vlans(self, net, site):

        switch_map = {
            "recepcion": self.sw_recepcion,
            "almacen": self.sw_almacen,
            "operaciones": self.sw_operaciones
        }

        for zona, vlans in site.items():
            if zona in ["router_principal"]:
                continue

            sw = switch_map[zona]

            zona_vlans = set()

            for vlan, datos in vlans.items():

                zona_vlans.add(vlan)

                for nombre in datos:

                    if nombre in [
                        "network",
                        "gateway",
                        "broadcast",
                        "prefix"
                    ]:
                        continue

                    host = net.get(f"{self.siteName}_{nombre}")
                    _, sw_intf = host.connectionsTo(sw)[0]

                    sw.cmd(
                        f"ovs-vsctl set port {sw_intf.name} tag={vlan}"
                    )

            trunk_str = ",".join(
                str(v)
                for v in sorted(zona_vlans)
            )

            uplink_intf, core_intf = sw.connectionsTo(self.core_sw)[0]

            sw.cmd(
                f"ovs-vsctl set port {uplink_intf.name} trunks={trunk_str}"
            )

            self.core_sw.cmd(
                f"ovs-vsctl set port {core_intf.name} trunks={trunk_str}"
            )

    def configure_roas(self, net, site):

        r = net.get(f"{self.siteName}_rWAN1")

        vlans_done = set()

        for zona, vlans in site.items():
            if zona in ["router_principal"]:
                continue

            for vlan, datos in vlans.items():

                if vlan in vlans_done:
                    continue

                vlans_done.add(vlan)

                gateway = datos["gateway"]
                prefix = datos["prefix"]

                router_if = f"{self.siteName}_rWAN1-eth0"

                r.cmd(
                    f"ip link add "
                    f"link {router_if} "
                    f"name {router_if}.{vlan} "
                    f"type vlan id {vlan}"
                )

                r.cmd(
                    f"ip addr add "
                    f"{gateway}/{prefix} "
                    f"dev {router_if}.{vlan}"
                )

                r.cmd(
                    f"ip link set "
                    f"{router_if}.{vlan} up"
                )

        r.cmd(
            f"ip link set {router_if} up"
        )

        from ipaddress import ip_network

    def setDHCPserver(self, net, site):

        router = net.get(f"{self.siteName}_rWAN1")

        vlans_done = set()

        for zona, vlans in site.items():
            if zona in ["router_principal"]:
                continue

            for vlan, datos in vlans.items():

                if vlan in vlans_done:
                    continue

                vlans_done.add(vlan)

                red = ip_network(
                    datos["network"]
                )

                hosts = list(red.hosts())

                start = str(hosts[1])
                end = str(hosts[-1])

                router.cmd(
                    f"dnsmasq "
                    f"--interface={self.siteName}_rWAN1-eth0.{vlan} "
                    f"--dhcp-range={start},{end},{red.netmask},12h "
                    f"--dhcp-option=3,{datos['gateway']} "
                    f"--dhcp-authoritative "
                    f"--pid-file=/tmp/w_dhcp_{vlan}.pid &"
                )

    def requestDHCP(self, net, site):

        for zona, vlans in site.items():
            if zona in ["router_principal"]:
                continue

            for vlan, datos in vlans.items():

                for nombre, ip in datos.items():

                    if nombre in [
                        "network",
                        "gateway",
                        "broadcast",
                        "prefix"
                    ]:
                        continue

                    if ip == "dhcp":

                        host = net.get(
                            f"{self.siteName}_{nombre}"
                        )

                        info(
                            f"*** DHCP {host.name}\n"
                        )

                        host.cmd(
                            f"dhclient -1 -v {host.name}-eth0"
                        )