from mininet.net import Mininet
from mininet.cli import CLI
from mininet.log import setLogLevel, info
from mininet.link import TCLink

from reto_redes.Warehouses.warehouse import Warehouse
from reto_redes.Warehouses.ips_warehouses import subredes_cdmx, subredes_mty

"""
    # =========================
    # WAREHOUSE CDMX
    # =========================
    info("*** Creando Warehouse WC\n")
    wc = Warehouse()
    wc.build(net, subredes_cdmx, "wc")

    # =========================
    # WAN LINK ENTRE ROUTERS
    # =========================
    info("*** Conectando WAN entre WM y WC\n")

        net.addLink(
        wm.router_wan,
        #wc.router_wan,
        cls=TCLink,
        bw=1
    )
"""

def build_topology():

    net = Mininet(controller=None, link=TCLink)

    # =========================
    # WAREHOUSE MONTERREY
    # =========================
    info("*** Creando Warehouse WM\n")
    wm = Warehouse()
    wm.build(net, subredes_mty, "wm")

    return net, wm, wc


if __name__ == "__main__":

    setLogLevel("info")

    net, wm, wc = build_topology()

    net.start()

    # =========================
    # CONFIG POST BUILD
    # =========================
    info("\n*** Config WM\n")
    wm.postBuild(net, subredes_mty)

    info("\n*** Config WC\n")
    wc.postBuild(net, subredes_cdmx)

    # =========================
    # WAN IP SETUP (CRÍTICO)
    # =========================
    info("\n*** Configurando WAN IPs\n")

    # WM router
    wm.router_wan.cmd("ip addr add 203.0.113.21/30 dev wm_rWAN1-eth1")
    wm.router_wan.cmd("ip link set wm_rWAN1-eth1 up")

    # WC router
    wc.router_wan.cmd("ip addr add 203.0.113.25/30 dev wc_rWAN1-eth1")
    wc.router_wan.cmd("ip link set wc_rWAN1-eth1 up")

    # =========================
    # RUTAS ENTRE WAREHOUSES
    # =========================
    info("\n*** Configurando rutas WAN\n")

    wm.router_wan.cmd("ip route add 10.0.0.0/8 via 203.0.113.26")
    wc.router_wan.cmd("ip route add 10.0.0.0/8 via 203.0.113.22")

    # fallback simple (si quieres más realista luego lo mejoramos)
    wm.router_wan.cmd("ip route add 10.0.0.0/8 dev wm_rWAN1-eth1")
    wc.router_wan.cmd("ip route add 10.0.0.0/8 dev wc_rWAN1-eth1")

    info("\n*** LISTO. CLI ABIERTA\n")
    CLI(net)

    net.stop()