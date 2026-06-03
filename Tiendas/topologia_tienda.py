#!/usr/bin/env python3
"""
Topología Mininet - Red de Tienda Retail (2 Pisos)
===================================================
Estructura:
    - 2 Routers WAN (Principal + Secundario LTE/5G)
    - 2 Switches Capa 3 (Core Stack en modo LACP/trunk)
    - 2 Switches de Acceso (Piso 1 y Piso 2)
    - Hosts organizados por VLAN en cada piso

VLANs:
    VLAN 10  - CCTV / Video Vigilancia
    VLAN 20  - Almacén / PCs generales / Tablet / Scanner RF
    VLAN 22  - POS (Puntos de Venta) - exclusiva
    VLAN 25  - Empleados (Smart TV, Tablet, Dispositivos personales)
    VLAN 30  - Gerencia / Seguridad / Impresoras
    VLAN 40  - Clientes (Wi-Fi invitados)
    VLAN 99  - Gestión de Red (management)
"""

from mininet.net import Mininet
from mininet.node import Node, OVSSwitch, Controller
from mininet.link import TCLink
from mininet.cli import CLI
from mininet.log import info

# ---------------------------------------------------------------------------
# Clases base
# ---------------------------------------------------------------------------

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


# ---------------------------------------------------------------------------
# Clase Tienda - engloba toda la red de la sucursal
# ---------------------------------------------------------------------------

class Tienda:
    """
    Modela la red completa de una tienda retail de 2 pisos.

    Esquema de direccionamiento:
        WAN principal  : 203.0.113.0/30   (simulado)
        WAN secundario : 198.51.100.0/30  (simulado)
        Core ↔ Piso 1  : 10.0.0.0/30
        Core ↔ Piso 2  : 10.0.0.4/30
        VLAN 10        : 10.10.10.0/24
        VLAN 20        : 10.10.20.0/24
        VLAN 22        : 10.10.22.0/24
        VLAN 25        : 10.10.25.0/24
        VLAN 30        : 10.10.30.0/24
        VLAN 40        : 10.10.40.0/24
        VLAN 99        : 10.10.99.0/24
    """

    def __init__(self):
        # Referencias a nodos clave (se llenan en build)
        self.router_wan_pri  = None
        self.router_wan_sec  = None
        self.core_sw1        = None   # Switch Intermedio Capa 3 – izquierdo
        self.core_sw2        = None   # Switch Intermedio Capa 3 – derecho
        self.acc_sw_p1       = None   # Switch Acceso Piso 1
        self.acc_sw_p2       = None   # Switch Acceso Piso 2

    # ------------------------------------------------------------------
    # Método principal
    # ------------------------------------------------------------------

    def build(self, net):
        info('*** Creando routers WAN\n')
        self._build_wan(net)

        info('*** Creando Core Stack (Capa 3)\n')
        self._build_core(net)

        info('*** Creando Piso 1\n')
        self._build_piso1(net)

        info('*** Creando Piso 2\n')
        self._build_piso2(net)

        info('*** Configurando enlaces trunk/inter-capas\n')
        self._build_uplinks(net)

    # ------------------------------------------------------------------
    # WAN
    # ------------------------------------------------------------------

    def _build_wan(self, net):
        self.router_wan_pri = net.addHost(
            'rWAN1', cls=Router,
            ip='203.0.113.1/30'
        )
        self.router_wan_sec = net.addHost(
            'rWAN2', cls=Router,
            ip='198.51.100.1/30'
        )

    # ------------------------------------------------------------------
    # Core / Capa 3
    # ------------------------------------------------------------------

    def _build_core(self, net):
        # Dos switches Capa-3 interconectados (simulan el Core Stack con LACP)
        self.core_sw1 = net.addSwitch('coreS1', cls=OVSSwitch, failMode='standalone')
        self.core_sw2 = net.addSwitch('coreS2', cls=OVSSwitch, failMode='standalone')

        # Enlace de interconexión entre los dos switches core (trunk / LACP)
        net.addLink(self.core_sw1, self.core_sw2,
                    cls=TCLink, bw=10000)   # 10 Gbps

        # Core → Router WAN Principal  (WAN-PRI)
        net.addLink(self.core_sw1, self.router_wan_pri,
                    cls=TCLink, bw=1000)    # 1 Gbps

        # Core → Router WAN Secundario (WAN-SEC)
        net.addLink(self.core_sw2, self.router_wan_sec,
                    cls=TCLink, bw=1000)    # 1 Gbps

    # ------------------------------------------------------------------
    # Piso 1
    # ------------------------------------------------------------------

    def _build_piso1(self, net):
        self.acc_sw_p1 = net.addSwitch('swP1', cls=OVSSwitch, failMode='standalone')

        # --- VLAN 10 - CCTV ---
        net.addHost('cctvP1',
                    ip='10.10.10.11/24',
                    defaultRoute='via 10.10.10.1')

        # --- VLAN 22 - POS ---
        net.addHost('posP1',
                    ip='10.10.22.10/24',
                    defaultRoute='via 10.10.22.1')

        # --- VLAN 20 - Almacén (PC + Tablet + Scanner RF) ---
        net.addHost('pcAlmacen',
                    ip='10.10.20.10/24',
                    defaultRoute='via 10.10.20.1')
        net.addHost('tabletEmp',
                    ip='10.10.20.11/24',
                    defaultRoute='via 10.10.20.1')
        net.addHost('scannerRF',
                    ip='10.10.20.12/24',
                    defaultRoute='via 10.10.20.1')

        # --- VLAN 25 - Empleados (Smart TV + Disp. Personal) ---
        net.addHost('smartTV',
                    ip='10.10.25.10/24',
                    defaultRoute='via 10.10.25.1')
        net.addHost('dispPersEmpP1',
                    ip='10.10.25.11/24',
                    defaultRoute='via 10.10.25.1')

        # --- VLAN 40 - AP Clientes ---
        net.addHost('apClientes',
                    ip='10.10.40.10/24',
                    defaultRoute='via 10.10.40.1')
        # Host cliente representativo (dispositivo conectado al AP)
        net.addHost('dispCliente',
                    ip='10.10.40.20/24',
                    defaultRoute='via 10.10.40.1')

        # --- AP Interno (trunk hacia empleados) ---
        net.addHost('apInternoP1',
                    ip='10.10.25.50/24',
                    defaultRoute='via 10.10.25.1')

        # Conexiones al switch de piso 1
        for host_name in [
            'cctvP1', 'posP1', 'pcAlmacen', 'tabletEmp', 'scannerRF',
            'smartTV', 'dispPersEmpP1', 'apClientes', 'dispCliente',
            'apInternoP1'
        ]:
            net.addLink(net.get(host_name), self.acc_sw_p1,
                        cls=TCLink, bw=1000)

    # ------------------------------------------------------------------
    # Piso 2
    # ------------------------------------------------------------------

    def _build_piso2(self, net):
        self.acc_sw_p2 = net.addSwitch('swP2', cls=OVSSwitch, failMode='standalone')

        # --- VLAN 10 - CCTV (Monitor + Cámara) ---
        net.addHost('monCCTV',
                    ip='10.10.10.21/24',
                    defaultRoute='via 10.10.10.1')
        net.addHost('cctvP2',
                    ip='10.10.10.22/24',
                    defaultRoute='via 10.10.10.1')

        # --- VLAN 10 - PC Seguridad ---
        net.addHost('pcSeguridad',
                    ip='10.10.10.30/24',
                    defaultRoute='via 10.10.10.1')

        # --- VLAN 30 - Gerencia / Impresora ---
        net.addHost('pcGerencia',
                    ip='10.10.30.10/24',
                    defaultRoute='via 10.10.30.1')
        net.addHost('impresora',
                    ip='10.10.30.20/24',
                    defaultRoute='via 10.10.30.1')

        # --- VLAN 25 - Disp. Personal Empleado ---
        net.addHost('dispPersEmpP2',
                    ip='10.10.25.21/24',
                    defaultRoute='via 10.10.25.1')

        # --- VLAN 99 - Gestión de Red ---
        net.addHost('pcGestRed',
                    ip='10.10.99.10/24',
                    defaultRoute='via 10.10.99.1')
        net.addHost('termGestRed',
                    ip='10.10.99.11/24',
                    defaultRoute='via 10.10.99.1')

        # --- AP Interno Piso 2 ---
        net.addHost('apInternoP2',
                    ip='10.10.25.51/24',
                    defaultRoute='via 10.10.25.1')

        # Conexiones al switch de piso 2
        for host_name in [
            'monCCTV', 'cctvP2', 'pcSeguridad',
            'pcGerencia', 'impresora', 'dispPersEmpP2',
            'pcGestRed', 'termGestRed', 'apInternoP2'
        ]:
            net.addLink(net.get(host_name), self.acc_sw_p2,
                        cls=TCLink, bw=1000)

    # ------------------------------------------------------------------
    # Uplinks (trunk Capa 3 ↔ Switches de acceso)
    # ------------------------------------------------------------------

    def _build_uplinks(self, net):
        # TRUNK-01: Switch Piso 1 → Core (LACP 2×10 Gbps)
        net.addLink(self.acc_sw_p1, self.core_sw1,
                    cls=TCLink, bw=10000)
        net.addLink(self.acc_sw_p1, self.core_sw2,   # segundo enlace LACP
                    cls=TCLink, bw=10000)

        # TRUNK-02: Switch Piso 2 → Core (LACP 2×10 Gbps)
        net.addLink(self.acc_sw_p2, self.core_sw1,
                    cls=TCLink, bw=10000)
        net.addLink(self.acc_sw_p2, self.core_sw2,   # segundo enlace LACP
                    cls=TCLink, bw=10000)