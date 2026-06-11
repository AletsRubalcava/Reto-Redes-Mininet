from mininet.node import Node, OVSSwitch
from mininet.link import TCLink
from mininet.log import info

# Clase Router
class Router(Node):
    """Nodo con IP activado. Actúa como router/gateway."""

    def config(self, **params):
        super(Router, self).config(**params)
        self.cmd('sysctl -w net.ipv4.ip_forward=1')
        self.cmd('sysctl -w net.ipv4.conf.all.rp_filter=0')
        self.cmd('sysctl -w net.ipv4.conf.default.rp_filter=0')
        self.cmd('modprobe 8021q')

    def terminate(self):
        self.cmd('sysctl -w net.ipv4.ip_forward=0')
        super(Router, self).terminate()


# Clase Headquarters 
class Headquarters:

    def __init__(self):
        # Routers WAN
        self.router_wan_principal = None
        self.router_wan_respaldo  = None

        # Switches Core L3
        self.core_sw1 = None
        self.core_sw2 = None

        # Switches de acceso
        self.sw_dir_rh_atc = None   
        self.sw_fin_ti     = None  
        self.sw_mkt_ops    = None  
        self.sw_seguridad  = None  

    def build(self, net, site):
        info('*** [HQ] Creando routers WAN\n')
        self._build_wan(net)

        info('*** [HQ] Creando Core Stack (Capa 3)\n')
        self._build_core(net)

        info('*** [HQ] Creando Área 1: Dirección, RH, Atención al Cliente\n')
        self._build_area_dir_rh_atc(net, site)

        info('*** [HQ] Creando Área 2: Finanzas y TI\n')
        self._build_area_fin_ti(net, site)

        info('*** [HQ] Creando Área 3: Marketing Digital y Operaciones\n')
        self._build_area_mkt_ops(net, site)

        info('*** [HQ] Creando Área 4: Seguridad Corporativa + Data Center NOC\n')
        self._build_area_seguridad(net, site)

        info('*** [HQ] Creando Área 5: Servidor (conexión directa al Core)\n')
        self._build_area_datacenter(net, site)

        info('*** [HQ] Configurando enlaces trunk entre capas\n')
        self._build_uplinks(net)

    def postBuild(self, net, site, dhcp_config):
        info('*** [HQ] Aplicando tags VLAN en switches de acceso\n')
        self.apply_vlans(net, site)

        info('*** [HQ] Configurando sub-interfaces ROAS en router principal\n')
        self.configure_roas(net, site)

        info('*** [HQ] Configurando servidor DNS\n')
        self.configure_dns(net)

        info('*** [HQ] Configurando servidor DHCP\n')
        self.configure_dhcp(net, dhcp_config)

        info('*** [HQ] Levantando servidor HTTP (ERP simulado)\n')
        self.set_servidor_http(net)

    # apply_vlans
    def apply_vlans(self, net, site):

        area_switch_map = {
            'area_dir_rh_atc': self.sw_dir_rh_atc,
            'area_fin_ti':     self.sw_fin_ti,
            'area_mkt_ops':    self.sw_mkt_ops,
            'area_seguridad':  self.sw_seguridad,
        }
        for area_nombre, vlans in site.items():

            if area_nombre == 'area_datacenter':
                continue 

            sw = area_switch_map[area_nombre]

            for vlan, datos in vlans.items():
                for nombre in datos:
                    if nombre in ['network', 'gateway', 'broadcast', 'prefix']:
                        continue

                    host = net.get(nombre)
                    _, sw_intf = host.connectionsTo(sw)[0]
                    sw.cmd(f'ovs-vsctl set port {sw_intf.name} tag={vlan}')

        servidor = net.get('servidor')
        _, core_intf = servidor.connectionsTo(self.core_sw1)[0]
        self.core_sw1.cmd(f'ovs-vsctl set port {core_intf.name} tag=70')

        uplink_config = [
            (self.sw_dir_rh_atc, self.core_sw1, site['area_dir_rh_atc']),
            (self.sw_fin_ti,     self.core_sw1, site['area_fin_ti']),
            (self.sw_mkt_ops,    self.core_sw1, site['area_mkt_ops']),
            (self.sw_seguridad,  self.core_sw2, site['area_seguridad']),
        ]

        for acc_sw, core_sw, area_vlans in uplink_config:
            vlans_del_area = sorted(area_vlans.keys())
            trunk_str = ','.join(str(v) for v in vlans_del_area)

            # Puerto del switch de acceso hacia el core
            acc_uplink, core_downlink = acc_sw.connectionsTo(core_sw)[0]
            acc_sw.cmd(f'ovs-vsctl set port {acc_uplink.name} trunks={trunk_str}')

            # Puerto del core hacia el switch de acceso
            core_sw.cmd(f'ovs-vsctl set port {core_downlink.name} trunks={trunk_str}')

        todas_vlans = set()
        for area_vlans in site.values():
            todas_vlans.update(area_vlans.keys())
        trunk_total = ','.join(str(v) for v in sorted(todas_vlans))

        c1_intf, c2_intf = self.core_sw1.connectionsTo(self.core_sw2)[0]
        self.core_sw1.cmd(f'ovs-vsctl set port {c1_intf.name} trunks={trunk_total}')
        self.core_sw2.cmd(f'ovs-vsctl set port {c2_intf.name} trunks={trunk_total}')

        r = net.get('r_pri')
        core_r_intf, _ = self.core_sw1.connectionsTo(r)[0]
        self.core_sw1.cmd(f'ovs-vsctl set port {core_r_intf.name} trunks={trunk_total}')

    # configure_roas
    def configure_roas(self, net, site):
        r = net.get('r_pri')

        _, r_intf = self.core_sw1.connectionsTo(r)[0]
        base_intf = r_intf.name

        r.cmd(f'ip link set {base_intf} up')

        vlans_done = set()

        for area_vlans in site.values():
            for vlan, datos in area_vlans.items():
                if vlan in vlans_done:
                    continue
                vlans_done.add(vlan)

                gateway = datos['gateway']
                prefix  = datos['prefix']

                r.cmd(f'ip link add link {base_intf} name {base_intf}.{vlan} type vlan id {vlan}')
                r.cmd(f'ip addr add {gateway}/{prefix} dev {base_intf}.{vlan}')
                r.cmd(f'ip link set {base_intf}.{vlan} up')

        info(f'*** [HQ] ROAS configurado sobre interfaz {base_intf}\n')

    # set_servidor_http
    def set_servidor_http(self, net):
        srv = net.get('servidor')

        srv.cmd('mkdir -p /tmp/web')
        srv.cmd("""echo '<html>
    <head><title>ERP Unfinished</title></head>
    <body>
        <h1>ERP Corporativo — Unfinished HQ</h1>
        <p>Servidor: 10.0.1.68 | VLAN 70 | Data Center MTY</p>
    </body>
</html>' > /tmp/web/index.html""")

        srv.cmd('python3 -m http.server 80 --directory /tmp/web &')

    # WAN 
    def _build_wan(self, net):
        self.router_wan_principal = net.addHost('r_pri', cls=Router, ip=None) # Router WAN Principal
    
        self.router_wan_respaldo = net.addHost('r_sec', cls=Router, ip=None) # Router WAN Respaldo

    # Core Stack  dos switches L3 interconectados
    def _build_core(self, net):
        self.core_sw1 = net.addSwitch('s1', cls=OVSSwitch, failMode='standalone')  # Switch Core L3 Principal
        self.core_sw2 = net.addSwitch('s2', cls=OVSSwitch, failMode='standalone')  # Switch Core L3 Respaldo

        # Enlace entre los dos core switches (trunk interno, 10 Gbps)
        net.addLink(self.core_sw1, self.core_sw2, cls=TCLink, bw=10)

        # Core sw1 
        net.addLink(self.core_sw1, self.router_wan_principal, cls=TCLink, bw=1)

        # Core sw2 
        net.addLink(self.core_sw2, self.router_wan_respaldo, cls=TCLink, bw=1)

    # Área 1 — Dirección General, Recursos Humanos, Atención al Cliente
    def _build_area_dir_rh_atc(self, net, site):
        self.sw_dir_rh_atc = net.addSwitch('s3', cls=OVSSwitch, failMode='standalone')  # Switch Acceso Dirección, RH, ATC

        self._add_hosts_to_switch(net, site['area_dir_rh_atc'], self.sw_dir_rh_atc)

    # Área 2 — Finanzas y TI
    def _build_area_fin_ti(self, net, site):
        self.sw_fin_ti = net.addSwitch('s4', cls=OVSSwitch, failMode='standalone')  # Switch Acceso Finanzas y TI

        self._add_hosts_to_switch(net, site['area_fin_ti'], self.sw_fin_ti)

    # Área 3 — Marketing Digital y Operaciones Retail
    def _build_area_mkt_ops(self, net, site):
        self.sw_mkt_ops = net.addSwitch('s5', cls=OVSSwitch, failMode='standalone')  # Switch Acceso Marketing y Operaciones

        self._add_hosts_to_switch(net, site['area_mkt_ops'], self.sw_mkt_ops)

    # Área 4 — Seguridad Corporativa + Data Center
    def _build_area_seguridad(self, net, site):
        self.sw_seguridad = net.addSwitch('s6', cls=OVSSwitch, failMode='standalone')  # Switch Acceso Seguridad
        
        self._add_hosts_to_switch(net, site['area_seguridad'], self.sw_seguridad)

    def _build_area_datacenter(self, net, site):
        datos_vlan70 = site['area_datacenter'][70]
        gateway = datos_vlan70['gateway']
        prefix  = datos_vlan70['prefix']

        host = net.addHost(
            'servidor',
            ip=f"{datos_vlan70['servidor']}/{prefix}",
            defaultRoute=f"via {gateway}"
        )
        net.addLink(host, self.core_sw1, cls=TCLink, bw=10)

    # Uplinks entre switches de acceso y Core
    def _build_uplinks(self, net):
        net.addLink(self.sw_dir_rh_atc, self.core_sw1, cls=TCLink, bw=10)
        net.addLink(self.sw_fin_ti,     self.core_sw1, cls=TCLink, bw=10)
        net.addLink(self.sw_mkt_ops,    self.core_sw1, cls=TCLink, bw=10)
        net.addLink(self.sw_seguridad,  self.core_sw2, cls=TCLink, bw=10)

    def _add_hosts_to_switch(self, net, area_vlans, switch):
        for vlan, datos in area_vlans.items():
            gateway = datos['gateway']
            prefix  = datos['prefix']

            for nombre, ip in datos.items():
                if nombre in ['network', 'gateway', 'broadcast', 'prefix']:
                    continue

                if ip == 'dhcp':
                    host = net.addHost(nombre, ip='0.0.0.0', defaultRoute=f'via {gateway}')
                else:
                    host = net.addHost(
                        nombre,
                        ip=f"{ip}/{prefix}",
                        defaultRoute=f"via {gateway}"
                    )
                net.addLink(host, switch, cls=TCLink, bw=1)
    
    # configure_dns
    def configure_dns(self, net):
        srv = net.get('servidor')

        # Crear archivo de configuración dnsmasq para DNS
        srv.cmd('mkdir -p /tmp/dns')
        srv.cmd("""cat > /tmp/dns/dnsmasq.conf << 'EOF'
port=53
domain-needed
bogus-priv
no-resolv

domain=unfinished.local

address=/erp.unfinished.local/10.0.1.68
address=/dns.unfinished.local/10.0.1.68
address=/web.unfinished.local/10.0.1.68
address=/noc.unfinished.local/10.0.1.64

listen-address=10.0.1.68
bind-interfaces

log-queries
log-facility=/tmp/dns/dnsmasq.log
EOF""")

        # Matar instancia previa si existe
        srv.cmd('pkill -f "dns/dnsmasq.conf" 2>/dev/null; sleep 1')

        # Levantar dnsmasq en modo DNS
        srv.cmd('dnsmasq --conf-file=/tmp/dns/dnsmasq.conf --pid-file=/tmp/dns/dnsmasq.pid')

        info('*** [HQ] DNS escuchando en 10.0.1.68:53\n')

    # configure_dhcp()
    def configure_dhcp(self, net, dhcp_config):
        r = net.get('r_pri')

        r.cmd('mkdir -p /tmp/dhcp')
        r.cmd('touch /tmp/dhcp/leases.txt')
        r.cmd('pkill -f dhcp-vlan 2>/dev/null; sleep 1')

        for vlan, cfg in dhcp_config.items():
            intf = f'r_pri-eth0.{vlan}'
            conf_file = f'/tmp/dhcp/dhcp-vlan{vlan}.conf'
            pid_file  = f'/tmp/dhcp/dhcp-vlan{vlan}.pid'

            conf = (
                f'port=0\n'
                f'interface={intf}\n'
                f'bind-interfaces\n'
                f'dhcp-range={cfg["rango_ini"]},{cfg["rango_fin"]},{cfg["mascara"]},{cfg["lease"]}\n'
                f'dhcp-option=3,{cfg["gateway"]}\n'
                f'dhcp-option=6,{cfg["dns"]}\n'
                f'dhcp-leasefile=/tmp/dhcp/leases-vlan{vlan}.txt\n'
                f'log-dhcp\n'
                f'log-facility=/tmp/dhcp/dhcp-vlan{vlan}.log\n'
            )

            r.cmd(f"echo '{conf}' > {conf_file}")
            r.cmd(f'dnsmasq --conf-file={conf_file} --pid-file={pid_file}')

        info(f'*** [HQ] DHCP corriendo en router — {len(dhcp_config)} instancias (una por VLAN)\n')