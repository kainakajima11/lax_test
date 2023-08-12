# Lax Test
laxのテストを行う。<br>
条件を自分で指定してテストを行えるrun_lax_test.pyと<br>
用意してあるテストケースを用いたテストが行えるrun_lax_testcases.pyを使用できます。
## Add path
以下を.bashrcに追記してください.
```
export PYTHONPATH="${PYTHONPATH}:$HOME/lax_test/src"
export PATH="${PATH}:$HOME/lax_test/src/scripts"
```
## How to use
md_config.yamlを用意します.
```
# 共通部分
calc_dir: /nfshome17/knakajima/vasp_work/lax/lax_tester/ # 計算を実行する場所
allowable_error: { # 許容誤差
x: 0.0001, # position
y: 0.0001,
z: 0.0001,
vx: 0.0001, # velocity
vy: 0.0001,
vz: 0.0001,
temp: 0.1, # temperature
Kin_E: 0.01, # energy
# Pot_E: 0.01,
}

# run_lax_testのみ
loop_num: 1 # None # 何回テストを行うか
cell: [30,30,30] # [20,20,20] # セルの大きさ
pack_num: 40 # 30 # 何個水原子を詰めるか
laich_mask_info: [ # laichのconfigに書かれる
"#fix 1 rigid x y -",
"#press 1 z 1 0"
]
lax_mask_info: [ # laxのconfigに書かれる
"#fix 1 rigid x y -",
"#pressz 1 1 0"
]
md_config: { # mdの条件(laxのconfig)
Mode: MD,
ForceField: Reaxff,
XYZFile: input.rd,
ParaFile: para.rd,
TimeStep: 1, # fs
TotalStep: 100,
ObserveStep: 1,
FileStep: 100,
BondStep: 1000000000,
SaveRestartStep: 10,
NGPUs: 0,
MPIGridX: 3,
MPIGridY: 3,
MPIGridZ: 3,
CUTOFF: 3.4,
MARGIN: 1.0,
GhostFactor: 40.0,
NNPModelPath: /nfshome17/knakajima/vasp_work/train/H2O_density1.0/frozen_models/allegro_frozen_229000.pth,
OMPGridX: 1,
OMPGridY: 1,
OMPGridZ: 1,
ShowMask: 1,
ReadVelocity: 1,
Thermo: Berendsen,
AimTemp: 300.0,
InitTemp: 300.0,
FinalTemp": 300.0,
ThermoFreq": 1000,
DelR: 0.0001,
MaxR: 0.1,
NNPFlagCalculateForce: 1,
}

# run_lax_testcasesのみ
testcases_path: /nfshome17/knakajima/lax_test/src/testcase # lax_test内のtestcase dir
```
md_config.yamlを用意したら<br>
run_lax_test.pyの場合
```
run_lax_test.py md_config.yaml
```
run_lax_testcases.pyの場合
```
run_lax_testcases.py md_config.yaml
```
のようにして実行することができます.



