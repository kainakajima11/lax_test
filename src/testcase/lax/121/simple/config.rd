XYZFile input.rd
ParaFile para.rd
TimeStep 1
TotalStep 100
ObserveStep 1
FileStep 100
BondStep 1000000000
SaveRestartStep 10
NGPUs 0
MPIGridX 1
MPIGridY 2
MPIGridZ 1
CUTOFF 3.4
MARGIN 1.0
GhostFactor 20.0
NNPModelPath /nfshome17/knakajima/vasp_work/train/H2O_density1.0/frozen_models/allegro_frozen_229000.pth
OMPGridX 1
OMPGridY 1
OMPGridZ 1
ShowMask 1
ReadVelocity 1
Thermo Berendsen
AimTemp 300.0
InitTemp 300.0
FinalTemp" 300.0
ThermoFreq" 1000
DelR 0.0001
MaxR 0.1
NNPFlagCalculateForce 1