subredes_mty = {
    "router_principal": "203.0.113.1/30",
    "router_respaldo": "198.51.100.1/30",
    "piso1": {
        10: {
            "network": "10.0.6.32/27",
            "prefix": 27,
            "gateway": "10.0.6.33",
            "cctv1": "10.0.6.34",
            "broadcast": "10.0.6.63"
        },
        20: {
            "network": "10.0.6.64/26",
            "gateway": "10.0.6.65",
            "prefix": 26,
            "pcSto": "10.0.6.66",
            "tabSto": "10.0.6.67",
            "scan": "10.0.6.68",
            "broadcast": "10.0.6.127"
        },
        22: {
            "network": "10.0.6.128/29",
            "gateway": "10.0.6.129",
            "prefix": 29,
            "pos": "10.0.6.130",
            "broadcast": "10.0.6.135"
        },
        25: {
            "network": "10.0.6.192/26",
            "gateway": "10.0.6.193",
            "prefix": 26,
            "telVenI": "10.0.6.194",
            "tv": "10.0.6.195",
            "broadcast": "10.0.6.255"
        },
        40: {
            "network": "10.0.7.32/27",
            "gateway": "10.0.7.33",
            "prefix": 27,
            "telVenC": "10.0.7.34",
            "broadcast": "10.0.7.63"
        },
    },
    "piso2": {
        10: {
                "network": "10.0.6.32/27",
                "prefix": 27,
                "gateway": "10.0.6.33",
                "monSec": "10.0.6.35",
                "cctv2": "10.0.6.36",
                "pcSec": "10.0.6.37",
                "apSec": "10.0.6.38",
                "broadcast": "10.0.6.63"
            },
        25: {
            "network": "10.0.6.192/26",
            "gateway": "10.0.6.193",
            "prefix": 26,
            "telSegI": "10.0.6.196",
            "telDirI": "10.0.6.197",
            "broadcast": "10.0.6.255"
        },
        30: {
            "network": "10.0.7.0/28",
            "gateway": "10.0.7.1",
            "prefix": 28,
            "pcDir": "10.0.7.2",
            "impr": "10.0.7.3",
            "apDir": "10.0.7.4",
            "broadcast": "10.0.7.15"
        },
        99: {
            "network": "10.0.7.64/29",
            "gateway": "10.0.7.65",
            "prefix": 29,
            "pcRed": "10.0.7.66",
            "termRed": "10.0.7.67",
            "broadcast": "10.0.7.71"
        }
    }
}

subredes_cdmx = {
    "router_principal": "203.0.113.5/30",
    "router_respaldo": "198.51.100.5/30",
    "piso1": {
        10: {
            "network": "10.0.7.96/27",
            "prefix": 27,
            "gateway": "10.0.7.97",
            "cctv1": "10.0.7.98",
            "broadcast": "10.0.7.127"
        },
        20: {
            "network": "10.0.7.128/26",
            "gateway": "10.0.7.129",
            "prefix": 26,
            "pcSto": "10.0.7.130",
            "tabSto": "10.0.7.131",
            "scan": "10.0.7.132",
            "broadcast": "10.0.7.191"
        },
        22: {
            "network": "10.0.7.192/28",
            "gateway": "10.0.7.193",
            "prefix": 28,
            "pos": "10.0.7.194",
            "broadcast": "10.0.7.207"
        },
        25: {
            "network": "10.0.8.0/26",
            "gateway": "10.0.8.1",
            "prefix": 26,
            "telVenI": "10.0.8.2",
            "tv": "10.0.8.3",
            "broadcast": "10.0.8.63"
        },
        40: {
            "network": "10.0.8.96/27",
            "gateway": "10.0.8.97",
            "prefix": 27,
            "telVenC": "10.0.8.98",
            "broadcast": "10.0.8.126"
        },
    },
    "piso2": {
        10: {
            "network": "10.0.7.96/27",
            "prefix": 27,
            "gateway": "10.0.7.97",
            "monSec": "10.0.7.99",
            "cctv2": "10.0.7.100",
            "pcSec": "10.0.7.101",
            "apSec": "10.0.7.102",
            "broadcast": "10.0.7.127"
        },
        25: {
            "network": "10.0.8.0/26",
            "gateway": "10.0.8.1",
            "prefix": 26,
            "telSegI": "10.0.8.4",
            "telDirI": "10.0.8.5",
            "broadcast": "10.0.8.63"
        },
        30: {
            "network": "10.0.8.64/28",
            "gateway": "10.0.8.65",
            "prefix": 28,
            "pcDir": "10.0.8.66",
            "impr": "10.0.8.67",
            "apDir": "10.0.8.68",
            "broadcast": "10.0.8.79"
        },
        99: {
            "network": "10.0.8.128/29",
            "gateway": "10.0.8.129",
            "prefix": 29,
            "pcRed": "10.0.8.130",
            "termRed": "10.0.8.131",
            "broadcast": "10.0.8.135"
        }
    }
}

subredes_gdl = {
    "router_principal": "203.0.113.9/30",
    "router_respaldo": "198.51.100.9/30",
    "piso1": {
        10: {
            "network": "10.0.8.160/27",
            "prefix": 27,
            "gateway": "10.0.8.161",
            "cctv1": "10.0.8.162",
            "broadcast": "10.0.8.191"
        },
        20: {
            "network": "10.0.8.192/26",
            "gateway": "10.0.8.193",
            "prefix": 26,
            "pcSto": "10.0.8.194",
            "tabSto": "10.0.8.195",
            "scan": "10.0.8.196",
            "broadcast": "10.0.8.255"
        },
        22: {
            "network": "10.0.9.0/29",
            "gateway": "10.0.9.1",
            "prefix": 29,
            "pos": "10.0.9.2",
            "broadcast": "10.0.9.7"
        },
        25: {
            "network": "10.0.9.64/26",
            "gateway": "10.0.9.65",
            "prefix": 26,
            "telVenI": "10.0.9.66",
            "tv": "10.0.9.67",
            "apVenI": "10.0.9.68",
            "broadcast": "10.0.9.127"
        },
        40: {
            "network": "10.0.9.160/27",
            "gateway": "10.0.9.161",
            "prefix": 27,
            "telVenC": "10.0.9.162",
            "apVenC": "10.0.9.163",
            "broadcast": "10.0.9.191"
        },
    },
    "piso2": {
        10: {
            "network": "10.0.8.160/27",
            "prefix": 27,
            "gateway": "10.0.8.161",
            "monSec": "10.0.8.163",
            "cctv2": "10.0.8.164",
            "pcSec": "10.0.8.165",
            "apSec": "10.0.8.166",
            "broadcast": "10.0.8.191"
        },
        25: {
            "network": "10.0.9.64/26",
            "gateway": "10.0.9.65",
            "prefix": 26,
            "telSegI": "10.0.9.70",
            "telDirI": "10.0.9.69",
            "broadcast": "10.0.9.127"
        },
        30: {
            "network": "10.0.9.128/28",
            "gateway": "10.0.9.129",
            "prefix": 28,
            "pcDir": "10.0.9.130",
            "impr": "10.0.9.131",
            "apDir": "10.0.9.132",
            "broadcast": "10.0.9.143"
        },
        99: {
            "network": "10.0.9.192/29",
            "gateway": "10.0.9.193",
            "prefix": 29,
            "pcRed": "10.0.9.194",
            "termRed": "10.0.9.195",
            "broadcast": "10.0.9.199"
        }
    }
}

subredes_smart = {
    "acceso": {
        20: {   # Sensores IoT en anaqueles (detectan peso/movimiento)
            "network":   "10.0.10.16/29",
            "prefix":    29,
            "gateway":   "10.0.10.17",
            "senIoT": "10.0.10.18",
            "broadcast": "10.0.10.23"
        },
        30: {   # Control de Acceso QR (abre/cierra la puerta)
            "network":    "10.0.10.24/29",
            "prefix":     29,
            "gateway":    "10.0.10.25",
            "ctrlAcc": "10.0.10.26",
            "broadcast":  "10.0.10.31"
        },
        40: {   # Gateway de Pagos Automático (reemplaza al POS)
            "network":   "10.0.10.32/29",
            "prefix":    29,
            "gateway":   "10.0.10.33",
            "gwPagos":   "10.0.10.34",
            "broadcast": "10.0.10.39"
        },
        50: {   # Servidor Edge IA (procesa video localmente)
            "network":   "10.0.10.40/29",
            "prefix":    29,
            "gateway":   "10.0.10.41",
            "edgeIA":    "10.0.10.42",
            "broadcast": "10.0.10.47"
        },
        60: {   # AP WiFi para la app del cliente
            "network":     "10.0.10.48/29",
            "prefix":      29,
            "gateway":     "10.0.10.49",
            "apC":  "10.0.10.50",
            "broadcast":   "10.0.10.55"
        },
        99: {   # Gestión Remota NOC (IT corporativo administra en remoto)
            "network":   "10.0.10.56/29",
            "prefix":    29,
            "gateway":   "10.0.10.57",
            "pcRed":     "10.0.10.58",
            "termRed":   "10.0.10.59",
            "broadcast": "10.0.10.63"
        },
    },
    "camaras": {
        10: {   # CCTV Seguridad (cámaras tradicionales de grabación)
            "network":   "10.0.10.0/29",
            "prefix":    29,
            "gateway":   "10.0.10.1",
            "cctv":      "10.0.10.2",
            "broadcast": "10.0.10.7"
        },
        11: {   # Cámaras IA (visión computacional, detectan productos)
            "network":   "10.0.10.8/29",
            "prefix":    29,
            "gateway":   "10.0.10.9",
            "camIA":     "10.0.10.10",
            "broadcast": "10.0.10.15"
        },
    }
}