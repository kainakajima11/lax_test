# Lax Test
laxのテストを行う。<br>
## Add path
以下を.bashrcに追記してください.
```
export PYTHONPATH="${PYTHONPATH}:$HOME/lax_test/src"
export PATH="${PATH}:$HOME/lax_test/src/scripts"
```
## How to use
test_configを用意します。
```
laich_cmd: "~/Laich/src/build/laich" # laichの実行コマンド
lax_cmd: "~/lax/src/build/lax" # laxの実行コマンド
calc_dir: "lax_test_calc" # testが行われるdir

mode: "free" # free only # to do : testcase, random

para: # input_pathの数だけ
- [C, H, O, N, Si]
- [C, H, O, N, Si]

input_paths: # input fileのpath # 複数指定可能
- /nfshome17/knakajima/lax_test/src/testcase/lax/111/simple/input.rd
- /nfshome17/knakajima/lax_test/src/testcase/lax/112/simple/input.rd

input_names:  # input_fileごとのテストの名前 # Noneなら0,1,2...
- H2O
- H2O_2

mask_info: # lax用のmask_info # 複数指定可能
- []
- [move 1 - - y 1 z 1]
- [move 1 - - y 0 - -, press 1 1 -]

mask_info_names:
- nothing
- move
- press_fix

OMPGrid: # OMPGrid 111 -> (x,y,z) = (1,1,1)
- 111
- 222 

MPIGrid: # MPIGrid # OMPGridと同サイズにする
- 111
- 222

set_initial_velocity: True # 初期速度をtest側で設定するか

md_config: { # mdの条件(lax用)
Mode: [MD],
ForceField: [Reaxff],
XYZFile: [input.rd],
ParaFile: [para.rd],
TimeStep: [1], # fs
TotalStep: [10],
ObserveStep: [1],
FileStep: [10],
BondStep: [1000000000],
SaveRestartStep: [100],
NGPUs: [0], 
CUTOFF: [3.4],
MARGIN: [1.0],
GhostFactor: [40.0],
NNPModelPath: [/nfshome17/knakajima/vasp_work/train/H2O_density1.0/frozen_models/allegro_frozen_229000.pth,
/nfshome17/knakajima/vasp_work/train/H2O_density1.0/frozen_models/allegro_frozen_129000.pth],
ShowMask: [1],
ReadVelocity: [1],
Thermo: [Berendsen],
AimTemp: [300.0],
InitTemp: [300.0],
FinalTemp: [300.0],
# ThermoFreq: [100],
DelR: [0.0001],
MaxR: [0.1],
NNPFlagCalculateForce: [1],
}
# サイズは1もしくはinput_pathsと同サイズにする.

allowable_error: { # 許容誤差
x: 0.001, # position
y: 0.001,
z: 0.001,
vx: 0.001, # velocity
vy: 0.001,
vz: 0.001,
cell: 0.01, # cell_size
temp: 0.1, # temperature
Kin_E: 0.01, # kinetic energy
Pot_E: 0.01, # potential energy
}
```
test_lax.pyを実行する.
```
test_lax.py test_config.py
```

