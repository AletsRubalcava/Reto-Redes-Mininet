from mininet.node import OVSSwitch
from mininet.link import TCLink
from mininet.log import info
from reto_redes.router import Router

# ────────────────────────────────────────────────────────────
#  Clase TiendaSmart
# ────────────────────────────────────────────────────────────
class TiendaSmart:
    # Prefijo para nombrar hosts (evita conflictos con las tiendas normales)
    SITE_PREFIX = "s"

    def __init__(self):
        self.router_wan = None   # Router WAN único
        self.core_sw    = None   # Switch Core L3 único
        self.acc_sw     = None   # Switch Acceso
        self.cam_sw     = None   # Switch Cámaras

    # ──────────────────────────────────────────────────────────
    #  BUILD  (construye nodos y enlaces físicos)
    # ──────────────────────────────────────────────────────────
    def build(self, net, site):
        info('*** [Smart] Creando Router WAN\n')
        self._build_wan(net)

        info('*** [Smart] Creando Switch Core L3\n')
        self._build_core(net)

        info('*** [Smart] Creando Switch Acceso + dispositivos\n')
        self._build_zona(net, site, zona_key='acceso', sw_name='acc_sw1')

        info('*** [Smart] Creando Switch Camaras + dispositivos\n')
        self._build_zona(net, site, zona_key='camaras', sw_name='cam_sw1')

        info('*** [Smart] Configurando uplinks\n')
        self._build_uplinks(net)

    # ──────────────────────────────────────────────────────────
    #  POST-BUILD  (VLANs, RoaS, servidores — después de net.start())
    # ──────────────────────────────────────────────────────────
    def postBuild(self, net, site):
        info('*** [Smart] Configurando VLANs en OVS\n')
        self.apply_vlans(net, site)

        info('*** [Smart] Configurando Router-on-a-Stick\n')
        self.configure_roas(net, site)

        info('*** [Smart] Iniciando servidor HTTP/FTP en Gateway de Pagos\n')
        self.setHTTPserver(net)
        self.setFTPserver(net)

    # ──────────────────────────────────────────────────────────
    #  CONSTRUCCIÓN DE NODOS
    # ──────────────────────────────────────────────────────────
    def _build_wan(self, net):
        # Solo 1 router WAN (sin secundario LTE — menor costo para tienda pequeña)
        self.router_wan = net.addHost(
            'rWAN_s', cls=Router, ip='203.0.113.9/30'
        )

    def _build_core(self, net):
        # Solo 1 switch Core (sin par redundante)
        self.core_sw = net.addSwitch(
            'core_sw1', cls=OVSSwitch, failMode='standalone'
        )
        # Enlace Core → Router WAN (1 Gbps)
        net.addLink(self.core_sw, self.router_wan, cls=TCLink, bw=1)

    def _build_zona(self, net, site, zona_key, sw_name):
        """
        Crea el switch de una zona y conecta todos sus hosts.
        zona_key : 'acceso' o 'camaras'
        sw_name  : nombre del switch en Mininet
        """
        sw = net.addSwitch(sw_name, cls=OVSSwitch, failMode='standalone')

        # Guardamos referencia al switch según la zona
        if zona_key == 'acceso':
            self.acc_sw = sw
        else:
            self.cam_sw = sw

        # Iteramos las VLANs de la zona y creamos los hosts
        for vlan, datos in site[zona_key].items():
            gateway = datos["gateway"]
            prefix  = datos["prefix"]

            for nombre, ip in datos.items():
                if nombre in ["network", "gateway", "broadcast", "prefix"]:
                    continue  # Solo procesar IPs de hosts

                host = net.addHost(
                    f"{self.SITE_PREFIX}_{nombre}",
                    ip=f"{ip}/{prefix}",
                    defaultRoute=f"via {gateway}"
                )
                net.addLink(host, sw, cls=TCLink, bw=1)

    def _build_uplinks(self, net):
        # Switch Acceso  → Switch Core  (10 Gbps trunk)
        net.addLink(self.acc_sw, self.core_sw, cls=TCLink, bw=10)
        # Switch Cámaras → Switch Core  (10 Gbps trunk)
        net.addLink(self.cam_sw, self.core_sw, cls=TCLink, bw=10)

    # ──────────────────────────────────────────────────────────
    #  CONFIGURACIÓN DE VLANs (OVS)
    # ──────────────────────────────────────────────────────────
    def apply_vlans(self, net, site):
        switch_map = {
            'acceso':   self.acc_sw,
            'camaras':  self.cam_sw,
        }

        for zona, vlans in site.items():
            sw = switch_map[zona]
            zona_vlans = set()

            # 1. Puertos de ACCESO: cada host → tag de su VLAN
            for vlan, datos in vlans.items():
                zona_vlans.add(vlan)
                for nombre in datos:
                    if nombre in ["network", "gateway", "broadcast", "prefix"]:
                        continue
                    host = net.get(f"{self.SITE_PREFIX}_{nombre}")
                    _, sw_intf = host.connectionsTo(sw)[0]
                    sw.cmd(f"ovs-vsctl set port {sw_intf.name} tag={vlan}")

            # 2. Puerto TRUNK: switch → core (lleva todas las VLANs de la zona)
            trunk_str = ",".join(str(v) for v in sorted(zona_vlans))
            uplink_intf, core_intf = sw.connectionsTo(self.core_sw)[0]
            sw.cmd(          f"ovs-vsctl set port {uplink_intf.name} trunks={trunk_str}")
            self.core_sw.cmd(f"ovs-vsctl set port {core_intf.name}  trunks={trunk_str}")

    # ──────────────────────────────────────────────────────────
    #  ROUTER-ON-A-STICK (subinterfaces por VLAN)
    # ──────────────────────────────────────────────────────────
    def configure_roas(self, net, site):
        """
        Crea subinterfaces en rWAN_s-eth0 para cada VLAN.
        Cada subinterfaz actúa como default gateway de su VLAN.
        """
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

    # ──────────────────────────────────────────────────────────
    #  SERVIDORES  (Gateway de Pagos reemplaza al POS)
    # ──────────────────────────────────────────────────────────
    def setHTTPserver(self, net):
        gw = net.get('s_gwPagos')
        gw.cmd('mkdir -p /tmp/web_smart')
        gw.cmd(
            'echo "<html>'
            '<head><title>Gateway Pagos Smart</title></head>'
            '<body><h1>Sistema de Cobro Automatico - Smart Store</h1>'
            '<p>Transaccion procesada correctamente.</p>'
            '</body></html>" > /tmp/web_smart/index.html'
        )
        gw.cmd('python3 -m http.server 80 --directory /tmp/web_smart &')

    def setFTPserver(self, net):
        """
        Servidor FTP en el Gateway de Pagos (VLAN 40).
        Simula el repositorio de logs de transacciones.
        """
        gw = net.get('s_gwPagos')
        gw.cmd('mkdir -p /tmp/ftpSmart')
        gw.cmd('echo "Transacciones del dia: 42 cobros exitosos" > /tmp/ftp/transacciones.txt')
        gw.cmd('python3 -m pyftpdlib -p 21 -d /tmp/ftp &')

    def configure_wan_routes(self, net, sitios, wan_ip):
        router = net.get('rWAN_s')
        redes_agregadas = set()

        for otro_nombre, otro_info in sitios.items():
            if otro_info.get('siteName') == 'smart':
                continue

            for nivel, vlans in otro_info['subredes'].items():
                # Saltar claves que no son pisos/zonas (tiendas normales)
                if nivel in ('router_principal', 'router_respaldo'):
                    continue

                for vlan, datos in vlans.items():
                    # datos puede ser un dict de subred o un string (IPs sueltas)
                    if not isinstance(datos, dict):
                        continue

                    network = datos.get('network')
                    if network and network not in redes_agregadas:
                        router.cmd(f"ip route add {network} via {wan_ip}")
                        redes_agregadas.add(network)

            enlace_wan = otro_info.get('enlace_wan')
            if enlace_wan and enlace_wan not in redes_agregadas:
                router.cmd(f"ip route add {enlace_wan} via {wan_ip}")
                redes_agregadas.add(enlace_wan)