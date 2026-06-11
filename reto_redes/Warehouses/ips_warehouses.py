subredes_wm = {
    "router_principal": "203.0.113.21/30",
    "recepcion": {
        10: {
            "network": "10.0.3.64/26",
            "prefix": 26,
            "gateway": "10.0.3.65",
            "cctv1": "dhcp",
            "broadcast": "10.0.3.127"
        },
        30: {
            "network": "10.0.4.0/28",
            "prefix": 28,
            "gateway": "10.0.4.1",
            "pcRec": "10.0.4.2",
            "apRec": "10.0.4.3",
            "broadcast": "10.0.4.15"
        },
        35: {
            "network": "10.0.4.16/28",
            "prefix": 28,
            "gateway": "10.0.4.17",
            "impRec": "10.0.4.18",
            "broadcast": "10.0.4.31"
        },
        40: {
            "network": "10.0.4.64/26",
            "prefix": 26,
            "gateway": "10.0.4.65",
            "telRec": "10.0.4.66",
            "broadcast": "10.0.4.127"
        },
    },
    "almacen": {
        10: {
            "network": "10.0.3.64/26",
            "prefix": 26,
            "gateway": "10.0.3.65",
            "cctv2": "10.0.3.66",
            "broadcast": "10.0.3.127"
        },
        20: {
            "network": "10.0.3.128/26",
            "prefix": 26,
            "gateway": "10.0.3.129",
            "pcAlm": "10.0.3.130",
            "apAlm": "10.0.3.131",
            "scan": "10.0.3.132",
            "tabAlm": "10.0.3.133",
            "broadcast": "10.0.3.191"
        },
        35: {
            "network": "10.0.4.16/28",
            "prefix": 28,
            "gateway": "10.0.4.17",
            "impAlm": "10.0.4.19",
            "broadcast": "10.0.4.31"
        },
        40: {
            "network": "10.0.4.64/26",
            "prefix": 26,
            "gateway": "10.0.4.65",
            "telAlm": "10.0.4.67",
            "broadcast": "10.0.4.127"
        },
    },
    "operaciones": {
        10: {
            "network": "10.0.3.64/26",
            "prefix": 26,
            "gateway": "10.0.3.65",
            "cctv3": "10.0.3.67",
            "mon": "10.0.3.68",
            "apSec": "10.0.3.69",
            "pcSec": "10.0.3.70",
            "broadcast": "10.0.3.127"
        },
        25: {
            "network": "10.0.3.192/26",
            "prefix": 26,
            "gateway": "10.0.3.193",
            "pcOp": "10.0.3.194",
            "apOp": "10.0.3.195",
            "tabOp": "10.0.3.196",
            "broadcast": "10.0.3.255"
        },
        40: {
            "network": "10.0.4.64/26",
            "prefix": 26,
            "gateway": "10.0.4.65",
            "telOp": "10.0.4.68",
            "telSec": "10.0.4.69",
            "broadcast": "10.0.4.127"
        },
        99: {
            "network": "10.0.4.128/29",
            "prefix": 29,
            "gateway": "10.0.4.129",
            "pcRed": "10.0.4.130",
            "termRed": "10.0.4.131",
            "broadcast": "10.0.4.135"
        }
    }
}

subredes_wc = {
    "router_principal": "203.0.113.25/30",
    "recepcion": {
        10: {
            "network": "10.0.4.192/26",
            "prefix": 26,
            "gateway": "10.0.4.193",
            "cctv1": "dhcp",
            "broadcast": "10.0.4.255"
        },
        30: {
            "network": "10.0.5.128/27",
            "prefix": 27,
            "gateway": "10.0.5.129",
            "pcRec": "10.0.5.130",
            "apRec": "10.0.5.131",
            "broadcast": "10.0.5.159"
        },
        35: {
            "network": "10.0.5.160/28",
            "prefix": 28,
            "gateway": "10.0.5.161",
            "impRec": "10.0.5.162",
            "broadcast": "10.0.5.175"
        },
        40: {
            "network": "10.0.5.192/26",
            "prefix": 26,
            "gateway": "10.0.5.193",
            "telRec": "10.0.5.194",
            "broadcast": "10.0.5.255"
        },
    },
    "almacen": {
        10: {
            "network": "10.0.4.192/26",
            "prefix": 26,
            "gateway": "10.0.4.193",
            "cctv2": "10.0.4.194",
            "broadcast": "10.0.4.255"
        },
        20: {
            "network": "10.0.5.0/26",
            "prefix": 26,
            "gateway": "10.0.5.1",
            "pcAlm": "10.0.5.2",
            "apAlm": "10.0.5.3",
            "scan": "10.0.5.4",
            "tabAlm": "10.0.5.5",
            "broadcast": "10.0.5.63"
        },
        35: {
            "network": "10.0.5.160/28",
            "prefix": 28,
            "gateway": "10.0.5.161",
            "impAlm": "10.0.5.162",
            "broadcast": "10.0.5.175"
        },
        40: {
            "network": "10.0.5.192/26",
            "prefix": 26,
            "gateway": "10.0.5.193",
            "telAlm": "10.0.5.194",
            "broadcast": "10.0.5.255"
        },
    },
    "operaciones": {
        10: {
            "network": "10.0.4.192/26",
            "prefix": 26,
            "gateway": "10.0.4.193",
            "cctv3": "10.0.4.194",
            "mon": "10.0.4.195",
            "apSec": "10.0.4.196",
            "pcSec": "10.0.4.197",
            "broadcast": "10.0.4.255"
        },
        25: {
            "network": "10.0.5.64/26",
            "prefix": 26,
            "gateway": "10.0.5.65",
            "pcOp": "10.0.5.66",
            "apOp": "10.0.5.67",
            "tabOp": "10.0.5.68",
            "broadcast": "10.0.5.127"
        },
        40: {
            "network": "10.0.5.192/26",
            "prefix": 26,
            "gateway": "10.0.5.193",
            "telOp": "10.0.5.194",
            "telSec": "10.0.5.195",
            "broadcast": "10.0.5.255"
        },
        99: {
            "network": "10.0.6.0/29",
            "prefix": 29,
            "gateway": "10.0.6.1",
            "pcRed": "10.0.6.2",
            "termRed": "10.0.6.3",
            "broadcast": "10.0.6.7"
        }
    }
}