from qolsys_client import status

qolsysPanel     = "192.168.0.20"
qolsysPort      = 12345
qolsysToken     = "abc123"
qolsysTimeout   = 20

result = status.qolsysStatus(qolsysPanel, qolsysPort, qolsysToken, qolsysTimeout)
print (result)
