from qolsys_client import arm
from qolsys_client import status

qolsysPanel     = "192.168.10.34"
qolsysPort      = 12345
qolsysToken     = "shw9s8"
qolsysTimeout   = 20

# Status
result = status.qolsysStatus(qolsysPanel, qolsysPort, qolsysToken, qolsysTimeout)
print (result)

# Arm Away
# result = arm.qolsysArm(qolsysPanel, qolsysPort, qolsysToken, qolsysTimeout, 0, "away")
# print (result)

# # Arm Stay
# result = arm.qolsysArm(qolsysPanel, qolsysPort, qolsysToken, qolsysTimeout, 0, "stay")
# print (result)

# # Disarm
# result = arm.qolsysArm(qolsysPanel, qolsysPort, qolsysToken, qolsysTimeout, 0, "disarm")
# print (result)
