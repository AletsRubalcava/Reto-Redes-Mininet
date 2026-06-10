# ============================================================
#  ips_smart.py  —  Direcciones IP de la Tienda Smart
#  Coloca este archivo en:  Tiendas/ips_smart.py
# ============================================================
#
#  Bloque asignado: 10.0.10.0/24   (continúa después de Tienda GDL)
#
#  La Tienda Smart tiene DOS zonas en vez de piso1/piso2:
#    "acceso"  → Switch Acceso  (IoT, pagos, WiFi, gestión)
#    "camaras" → Switch Cámaras (CCTV + Cámaras IA)
#
#  VLANs usadas:
#    10  CCTV Seguridad          → Switch Cámaras
#    11  Cámaras IA              → Switch Cámaras
#    20  Sensores IoT Anaquel    → Switch Acceso
#    30  Control Acceso QR       → Switch Acceso
#    40  Gateway Pagos Automát.  → Switch Acceso  (reemplaza al POS)
#    50  Servidor Edge IA        → Switch Acceso
#    60  AP WiFi Clientes (App)  → Switch Acceso
#    99  Gestión Remota NOC      → Switch Acceso
# ============================================================

subredes_smart = {

    # ──────────────────────────────────────────────────────────
    #  SWITCH ACCESO  —  Dispositivos inteligentes y gestión
    # ──────────────────────────────────────────────────────────
    "acceso": {

        20: {   # Sensores IoT en anaqueles (detectan peso/movimiento)
            "network":   "10.0.10.16/29",
            "prefix":    29,
            "gateway":   "10.0.10.17",
            "sensorIoT": "10.0.10.18",
            "broadcast": "10.0.10.23"
        },

        30: {   # Control de Acceso QR (abre/cierra la puerta)
            "network":    "10.0.10.24/29",
            "prefix":     29,
            "gateway":    "10.0.10.25",
            "ctrlAcceso": "10.0.10.26",
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
            "apClientes":  "10.0.10.50",
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

    # ──────────────────────────────────────────────────────────
    #  SWITCH CÁMARAS  —  Tráfico de video aislado del resto
    # ──────────────────────────────────────────────────────────
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
