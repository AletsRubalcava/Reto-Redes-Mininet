# Subredes representativas de la Headquarters - Cede MTY
# Cada area mapea un switch de acceso en la topologia fisica.

subredes_cede = {

    # ÁREA 1: Dirección General, Recursos Humanos, Atención al Cliente
    # Switch: Acceso Dirección & RH & ATC
    "area_dir_rh_atc": {

        40: {  # Dirección General
            "network":   "10.0.0.96/27",
            "prefix":    27,
            "gateway":   "10.0.0.97",
            "broadcast": "10.0.0.127",
            "lap_dir":   "10.0.0.98",   
            "tab_dir":   "10.0.0.99",   
            "tv_dir":    "10.0.0.100",  
        },
        20: {  # Recursos Humanos
            "network":   "10.0.0.32/27",
            "prefix":    27,
            "gateway":   "10.0.0.33",
            "broadcast": "10.0.0.63",
            "pc_rh":     "10.0.0.34",   
            "lap_rh":    "10.0.0.35",   
        },
        50: {  # Atención al Cliente
            "network":   "10.0.0.128/25",
            "prefix":    25,
            "gateway":   "10.0.0.129",
            "broadcast": "10.0.0.255",
            "pc_atc":    "10.0.0.130",  
        },
        60: {  # Cámaras en esta área
            "network":   "10.0.1.0/26",
            "prefix":    26,
            "gateway":   "10.0.1.1",
            "broadcast": "10.0.1.63",
            "cam_dir":   "10.0.1.2",    
        },
        100: {  # Impresoras en esta área
            "network":   "10.0.3.0/27",
            "prefix":    27,
            "gateway":   "10.0.3.1",
            "broadcast": "10.0.3.31",
            "imp_dir":   "10.0.3.2",   
        },
        80: {  # Dispositivos Invitados
            "network":   "10.0.1.128/25",
            "prefix":    25,
            "gateway":   "10.0.1.129",
            "broadcast": "10.0.1.255",
            "gst_dir":   "10.0.1.130",  
        },
        90: {  # Dispositivos BYOD
            "network":   "10.0.2.0/24",
            "prefix":    24,
            "gateway":   "10.0.2.1",
            "broadcast": "10.0.2.255",
            "byod_dir":  "10.0.2.2",  
        },
    },

    # ÁREA 2: Finanzas y TI
    # Switch: Acceso FInanzas & TI
    "area_fin_ti": {

        10: {  # Finanzas
            "network":   "10.0.0.0/27",
            "prefix":    27,
            "gateway":   "10.0.0.1",
            "broadcast": "10.0.0.31",
            "lap_fin":   "10.0.0.2",   
            "pc_fin":    "10.0.0.3",
            "pc_fin2":   "dhcp"
        },
        30: {  # TI
            "network":   "10.0.0.64/27",
            "prefix":    27,
            "gateway":   "10.0.0.65",
            "broadcast": "10.0.0.95",
            "pc_ti":     "10.0.0.66",   
            "term_ti":   "10.0.0.67",   
            "lap_ti":    "10.0.0.68",   
        },
        60: {  # Cámaras en esta área
            "network":   "10.0.1.0/26",
            "prefix":    26,
            "gateway":   "10.0.1.1",
            "broadcast": "10.0.1.63",
            "cam_fin":   "10.0.1.4",    
        },
        100: {  # Impresoras en esta área
            "network":   "10.0.3.0/27",
            "prefix":    27,
            "gateway":   "10.0.3.1",
            "broadcast": "10.0.3.31",
            "imp_fin":   "10.0.3.3",  
        },
        90: {  # Dispositivos BYOD
            "network":   "10.0.2.0/24",
            "prefix":    24,
            "gateway":   "10.0.2.1",
            "broadcast": "10.0.2.255",
            "byod_fin":  "10.0.2.3", 
        },
    },

    # ÁREA 3: Marketing Digital y Operaciones Retail
    # Switch : Acceso Marketing Digital & Operaciones
    "area_mkt_ops": {

        50: {
            "network":   "10.0.0.128/25",
            "prefix":    25,
            "gateway":   "10.0.0.129",
            "broadcast": "10.0.0.255",
            "pc_mkt":    "10.0.0.131",   
            "lap_mkt":   "10.0.0.132",
            "tab_mkt":   "10.0.0.133",
            "pc_ops":    "10.0.0.134",
            "lap_ops":   "10.0.0.135",
            "tab_ops":   "10.0.0.136",
            "pc_mkt2":   "dhcp",        
            "tab_ops2":  "dhcp",
        },
        60: {  # Cámaras en esta área
            "network":   "10.0.1.0/26",
            "prefix":    26,
            "gateway":   "10.0.1.1",
            "broadcast": "10.0.1.63",
            "cam_mkt":   "10.0.1.5",    
        },
        100: {  # Impresoras en esta área
            "network":   "10.0.3.0/27",
            "prefix":    27,
            "gateway":   "10.0.3.1",
            "broadcast": "10.0.3.31",
            "imp_mkt":   "10.0.3.4",    
        },
        90: {  # Dispositivos BYOD
            "network":   "10.0.2.0/24",
            "prefix":    24,
            "gateway":   "10.0.2.1",
            "broadcast": "10.0.2.255",
            "byod_mkt":  "10.0.2.4",    
        },
    },

    # ÁREA 4: Seguridad  + Data Center 
    # Switch : Acceso Seguridad
    "area_seguridad": {

        60: {  # Seguridad Corporativa
            "network":   "10.0.1.0/26",
            "prefix":    26,
            "gateway":   "10.0.1.1",
            "broadcast": "10.0.1.63",
            "pc_seg":    "10.0.1.6",   
            "cam_seg":   "10.0.1.7",    
            "mon_seg":   "10.0.1.8",    
        },
        70: {  # Gestión de Red
            "network":   "10.0.1.64/27",
            "prefix":    27,
            "gateway":   "10.0.1.65",
            "broadcast": "10.0.1.95",
            "pc_noc":    "10.0.1.66",   
            "lap_noc":   "10.0.1.67",   
        },
        90: {  # Dispositivos BYOD
            "network":   "10.0.2.0/24",
            "prefix":    24,
            "gateway":   "10.0.2.1",
            "broadcast": "10.0.2.255",
            "byod_seg":  "10.0.2.5", 
            "byod_seg2": "dhcp",
        },
    },

    # ÁREA 5: Servidor
    # Conectado directamente al Switch Core L3
    "area_datacenter": {

        70: {  # Servidor 
            "network":   "10.0.1.64/27",
            "prefix":    27,
            "gateway":   "10.0.1.65",
            "broadcast": "10.0.1.95",
            "servidor":  "10.0.1.68",  
        },
    },
}

dhcp_config_cede = {
    10:  {  # Finanzas
        "subred":   "10.0.0.0",
        "mascara":  "255.255.255.224",
        "rango_ini": "10.0.0.20",
        "rango_fin": "10.0.0.30",
        "gateway":  "10.0.0.1",
        "dns":      "10.0.1.68",
        "lease":    "12h",
    },
    20:  {  # Recursos Humanos
        "subred":   "10.0.0.32",
        "mascara":  "255.255.255.224",
        "rango_ini": "10.0.0.50",
        "rango_fin": "10.0.0.62",
        "gateway":  "10.0.0.33",
        "dns":      "10.0.1.68",
        "lease":    "12h",
    },
    30:  {  # TI
        "subred":   "10.0.0.64",
        "mascara":  "255.255.255.224",
        "rango_ini": "10.0.0.80",
        "rango_fin": "10.0.0.94",
        "gateway":  "10.0.0.65",
        "dns":      "10.0.1.68",
        "lease":    "12h",
    },
    40:  {  # Dirección General
        "subred":   "10.0.0.96",
        "mascara":  "255.255.255.224",
        "rango_ini": "10.0.0.110",
        "rango_fin": "10.0.0.126",
        "gateway":  "10.0.0.97",
        "dns":      "10.0.1.68",
        "lease":    "12h",
    },
    50:  {  # Usuarios Corporativos
        "subred":   "10.0.0.128",
        "mascara":  "255.255.255.128",
        "rango_ini": "10.0.0.200",
        "rango_fin": "10.0.0.254",
        "gateway":  "10.0.0.129",
        "dns":      "10.0.1.68",
        "lease":    "12h",
    },
    60:  {  # CCTV / Seguridad
        "subred":   "10.0.1.0",
        "mascara":  "255.255.255.192",
        "rango_ini": "10.0.1.20",
        "rango_fin": "10.0.1.62",
        "gateway":  "10.0.1.1",
        "dns":      "10.0.1.68",
        "lease":    "12h",
    },
    70:  {  # Servidores / NOC
        "subred":   "10.0.1.64",
        "mascara":  "255.255.255.224",
        "rango_ini": "10.0.1.75",
        "rango_fin": "10.0.1.94",
        "gateway":  "10.0.1.65",
        "dns":      "10.0.1.68",
        "lease":    "12h",
    },
    80:  {  # Guest
        "subred":   "10.0.1.128",
        "mascara":  "255.255.255.128",
        "rango_ini": "10.0.1.150",
        "rango_fin": "10.0.1.254",
        "gateway":  "10.0.1.129",
        "dns":      "10.0.1.68",
        "lease":    "1h",
    },
    90:  {  # BYOD Empleados
        "subred":   "10.0.2.0",
        "mascara":  "255.255.255.0",
        "rango_ini": "10.0.2.50",
        "rango_fin": "10.0.2.254",
        "gateway":  "10.0.2.1",
        "dns":      "10.0.1.68",
        "lease":    "8h",
    },
    100: {  # Impresoras
        "subred":   "10.0.3.0",
        "mascara":  "255.255.255.224",
        "rango_ini": "10.0.3.10",
        "rango_fin": "10.0.3.30",
        "gateway":  "10.0.3.1",
        "dns":      "10.0.1.68",
        "lease":    "12h",
    },
}
