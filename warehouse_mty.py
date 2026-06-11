from mininet .net import Mininet
from mininet .link import TCLink
from mininet .cli import CLI
from mininet .log import setLogLevel


class WarehouseNetwork:
    def __init__(self): #creates mininet and starts building
        self.net = Mininet( controller =None , link = TCLink )
        self._build()
    
    def _build(self): #creates all the physical things
        net = self.net

        #adding objects
        # Router 1 
        self.rm = net.addHost('rm') #add router
        #L3 switch
        self.s1 = net.addSwitch ('s1')#add switch

        # Links
        #switch and router
        self.net.addLink (self.rm, self.s1) #main to s1

        #zones in warehouse
        #recepcion
        self.asr = Recepcion(net, self.s1)
        #almacen
        self.asa = almacen(net, self.s1)
        #operacioneSeguridad
        self.asos = operacioneSeguridad(net, self.s1)

    def start(self): #powers everything on = becomes functional
        self.net.start()
        self.rm.cmd('ifconfig rm-eth0 10.0.10.1 netmask 255.255.255.0 up') #link to s1
        self.rm.cmd('sysctl -w net.ipv4.ip_forward=1') #let the routing happen

        self.asr.configure()
        self.asa.configure()
        self.asos.configure()

    def run(self): #calls start -> opens CLI (to interact) -> so we later exit
        self.start() 
        CLI(self.net)         
        self.net.stop()

class Recepcion:
    def __init__(self, net, core_switch): 
        # ADDING HOSTS ---------------------------------------------
        self.asr = net.addSwitch ('asr', dpid='0000000000000002')#add switch

        #PC 
        self.pc_rec = net.addHost ('pc_rec', ip = '10.0.4.2/28')
        #Impresora 
        self.imp_rec = net.addHost ('imp_rec', ip = '10.0.4.18/28')
        #Camara  
        self.cam_rec = net.addHost ('cam_rec', ip = '10.0.3.66/26')
        # -----SECOND LEVEL-----
        #Access Point
        self.ap_rec = net.addHost ('ap_rec') 
        #Dispositivo Personal (from AP)
        self.dp_rec = net.addHost ('dp_rec', ip = '10.0.4.66/26')

        # LINKS ----------------------------------------------------
        net.addLink (self.asr, core_switch) #add link to s1

        #Access Point
        net.addLink (self.ap_rec, self.asr) # ap links asr
        #Dispositivo Personal (from AP)
        net.addLink (self.dp_rec, self.ap_rec) # dp_rec links to ap_rec

        #PC 
        net.addLink(self.pc_rec, self.asr) # pc_rec links to asr
        #Impresora 
        net.addLink(self.imp_rec, self.asr) # imp_rec links to asr
        #Camara  
        net.addLink(self.cam_rec, self.asr) # cam_rec links to asr

    def configure(self):
        #default routes -------------------------------------------
        self.asr.cmd('ip route add default via 10.0.10.1') #asr to s1

        #PC 
        self.pc_rec.cmd('ip route add default via 10.0.4.1')
        #Impresora 
        self.imp_rec.cmd('ip route add default via 10.0.4.17')
        #Camara  
        self.cam_rec.cmd('ip route add default via 10.0.3.65')
        # -----SECOND LEVEL-----
        #Dispositivo Personal (from AP)
        self.dp_rec.cmd('ip route add default via 10.0.4.65')

        #VLANS ----------------------------------------------------
        #pcs
        self.asr.cmd('ovs-vsctl set port asr-eth2 tag=30')
        #impresora
        self.asr.cmd('ovs-vsctl set port asr-eth3 tag=35')
        #cctv
        self.asr.cmd('ovs-vsctl set port asr-eth4 tag=10')
        # -----SECOND LEVEL-----
        #dp
        self.asr.cmd('ovs-vsctl set port asr-eth1 tag=40')

class almacen:
    def __init__(self, net, core_switch):
        # ADDING HOSTS ---------------------------------------------
        self.asa = net.addSwitch ('asa', dpid='0000000000000003')#add switch

        #Camara
        self.cam_alm = net.addHost ('cam_alm', ip = '10.0.3.67/26')
        #PC
        self.pc_alm = net.addHost ('pc_alm', ip = '10.0.3.130/26')
        # -----SECOND LEVEL-----
        #Access Point
        self.ap_alm = net.addHost ('ap_alm')
        #Scanner (from AP)
        self.scan_alm = net.addHost ('scan_alm', ip = '10.0.3.131/26')
        #Tablet (from AP)
        self.tab_alm = net.addHost ('tab_alm', ip = '10.0.3.132/26')
        #Dispositivo Personal (from AP)
        self.dp_alm = net.addHost ('dp_alm', ip = '10.0.4.67/26')
        #Impresora
        self.imp_alm = net.addHost ('imp_alm', ip = '10.0.4.19/28')

        # LINKS ----------------------------------------------------
        #Almacen
        net.addLink (self.asa, core_switch) #add link 

        #Camara
        net.addLink(self.cam_alm, self.asa)
        #PC
        net.addLink(self.pc_alm, self.asa)
        #Impresora
        net.addLink(self.imp_alm, self.asa)
        #Access Point
        net.addLink(self.ap_alm, self.asa)
        #Scanner (from AP)
        net.addLink(self.scan_alm, self.ap_alm)
        #Tablet (from AP)
        net.addLink(self.tab_alm, self.ap_alm)
        #Dispositivo Personal (from AP)
        net.addLink(self.dp_alm, self.ap_alm)

    def configure(self):
        #default routes -------------------------------------------
        self.asa.cmd('ip route add default via 10.0.10.1') #asa to s1

        #Camara
        self.cam_alm.cmd('ip route add default via 10.0.3.65')
        #PC
        self.pc_alm.cmd('ip route add default via 10.0.3.129')
        #Impresora
        self.imp_alm.cmd('ip route add default via 10.0.4.17')
        # -----SECOND LEVEL-----  
        #Scanner (from AP)
        self.scan_alm.cmd('ip route add default via 10.0.3.129')
        #Tablet (from AP)
        self.tab_alm.cmd('ip route add default via 10.0.3.129')
        #Dispositivo Personal (from AP)
        self.dp_alm.cmd('ip route add default via 10.0.4.65')

        #VLANS ----------------------------------------------------
        #cctv
        self.asa.cmd('ovs-vsctl set port asa-eth1 tag=10')
        #pcs
        self.asa.cmd('ovs-vsctl set port asa-eth2 tag=20')
        #impresora
        self.asa.cmd('ovs-vsctl set port asa-eth4 tag=35')
        # -----SECOND LEVEL-----
        #scanner rf
        self.asa.cmd('ovs-vsctl set port asa-eth3 tag=20')
        #tablet
        self.asa.cmd('ovs-vsctl set port asa-eth3 tag=20')
        #dispositivo personal
        self.asa.cmd('ovs-vsctl set port asa-eth3 tag=40')

class operacioneSeguridad:
    def __init__(self, net, core_switch):
        # ADDING HOSTS ---------------------------------------------
        self.asos = net.addSwitch ('asos', dpid='0000000000000004')#add switch

        #PC gestion red
        self.pcred_asos = net.addHost ('pcred_asos', ip = '10.0.4.131/29')
        #PC seguridad
        self.pcseg_asos = net.addHost ('pcseg_asos', ip = '10.0.3.68/26')
        #PC operaciones
        self.pcope_asos = net.addHost ('pcope_asos', ip = '10.0.3.194/26')
        #Camara
        self.cam_asos = net.addHost ('cam_asos', ip = '10.0.3.69/26')
        #Monitor CCTV
        self.mocctv = net.addHost ('mocctv', ip = '10.0.3.70/26')
        #Terminal Gestion Red
        self.term_asos = net.addHost ('term_asos', ip = '10.0.4.132/29')

        # -----SECOND LEVEL-----
        #Access Point 1 operaciones
        self.ap_asos = net.addHost ('ap_asos') 
        #Dispositivo Personal
        self.dp_asos = net.addHost ('dp_asos', ip = '10.0.4.68/26')
        #Tablet
        self.tab_asos = net.addHost ('tab_asos', ip = '10.0.3.195/26')
        # -----SECOND LEVEL -----
        #Access Point 2 seguridad
        self.ap2_asos = net.addHost ('ap2_asos') 
        #Dispositivo Personal
        self.dp2_asos = net.addHost ('dp2_asos', ip = '10.0.4.69/26')

        # LINKS ----------------------------------------------------
        #Operaciones/Seguridad
        net.addLink (self.asos, core_switch) #add link to s1

        #PC gestion red
        net.addLink(self.pcred_asos, self.asos)
        #PC seguridad
        net.addLink(self.pcseg_asos, self.asos)
        #PC operaciones
        net.addLink(self.pcope_asos, self.asos)
        #Access Point 1
        net.addLink(self.ap_asos, self.asos)
        #Dispositivo Personal
        net.addLink(self.dp_asos, self.ap_asos)
        #Tablet
        net.addLink(self.tab_asos, self.ap_asos)
        #Access Point 2
        net.addLink(self.ap2_asos, self.asos)
        #Dispositivo Personal
        net.addLink(self.dp2_asos, self.ap2_asos)
        #Camara
        net.addLink(self.cam_asos, self.asos)
        #Monitor CCTV
        net.addLink(self.mocctv, self.asos)
        #Terminal Gestion Red
        net.addLink(self.term_asos, self.asos)
    
    def configure(self):
        #default routes -------------------------------------------
        self.asos.cmd('ip route add default via 10.0.10.2 metric 1') #asos to s1

        #PC gestion red
        self.pcred_asos.cmd('ip route add default via 10.0.4.129')
        #PC seguridad
        self.pcseg_asos.cmd('ip route add default via 10.0.3.65')
        #PC operaciones
        self.pcope_asos.cmd('ip route add default via 10.0.3.193')
        #Camara
        self.cam_asos.cmd('ip route add default via 10.0.3.65')
        #Monitor CCTV
        self.mocctv.cmd('ip route add default via 10.0.3.65')
        #Terminal Gestion Red
        self.term_asos.cmd('ip route add default via 10.0.4.129')
        #Dispositivo Personal 1
        self.dp_asos.cmd('ip route add default via 10.0.4.65')
        #Tablet
        self.tab_asos.cmd('ip route add default via 10.0.3.193')
        #Dispositivo Personal 2
        self.dp2_asos.cmd('ip route add default via 10.0.4.65')

        # DHCP SERVICE — gestion red PC hosts DHCP server for warehouse network management
        self.pcred_asos.cmd('dnsmasq --interface=pcred_asos-eth0 --dhcp-range=10.0.4.130,10.0.4.134,255.255.255.248,12h &')

        #VLANS -------------------------------------------
        #pc gestion red
        self.asos.cmd('ovs-vsctl set port asos-eth1 tag=99')
        #pc seguridad
        self.asos.cmd('ovs-vsctl set port asos-eth2 tag=10')
        #pc operaciones
        self.asos.cmd('ovs-vsctl set port asos-eth3 tag=25')
        #ap1 (byod)
        self.asos.cmd('ovs-vsctl set port asos-eth4 tag=40')
        #ap2 (byod)
        self.asos.cmd('ovs-vsctl set port asos-eth5 tag=40')
        #camara cctv
        self.asos.cmd('ovs-vsctl set port asos-eth6 tag=10')
        #monitor cctv
        self.asos.cmd('ovs-vsctl set port asos-eth7 tag=10')
        #terminal gestion 
        self.asos.cmd('ovs-vsctl set port asos-eth8 tag=99')


if __name__ == '__main__':
    setLogLevel('info')
    warehouse = WarehouseNetwork()
    warehouse.run()