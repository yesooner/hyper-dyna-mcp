# K 文件关键字集成设计

## 目标

在 HyperMesh 中直接操作 K 文件关键字（*MAT, *SECTION, *CONTACT 等），而不是导出 .k 文件。

## 核心原则

1. **K 文件格式为本** — 所有操作必须符合 LS-DYNA K 文件格式规范
2. **不闪退** — 严格的错误处理和格式验证
3. **双向映射** — K 文件关键字 ↔ HyperMesh 对象

## 关键字映射表

### 1. 材料 (*MAT)

```
K 文件: *MAT_ELASTIC
  MID, RHO, E, PR, DA, DB

HyperMesh: 
  *createentity mats name="MAT_ELASTIC_1"
  hm_setvalue mats id=1 STATUS=2 MAT_TYPE=ELASTIC
  hm_setvalue mats id=1 RHO=7.85e-9
  hm_setvalue mats id=1 E=210000
  hm_setvalue mats id=1 PR=0.3
```

### 2. 截面 (*SECTION)

```
K 文件: *SECTION_SHELL
  SECID, ELFORM, SHRF, NIP

HyperMesh:
  *createentity props name="SECTION_SHELL_1"
  hm_setvalue props id=1 STATUS=2 SECTION_TYPE=SHELL
  hm_setvalue props id=1 ELFORM=16
  hm_setvalue props id=1 SHRF=0.833
  hm_setvalue props id=1 NIP=3
```

### 3. 部件 (*PART)

```
K 文件: *PART
  Title
  PID, SECID, MID, EOSID, HGID

HyperMesh:
  *createentity comps name="Part_1"
  hm_setvalue comps id=1 STATUS=2 PROPERTYID=1
  hm_setvalue comps id=1 MATERIALID=1
```

### 4. 节点 (*NODE)

```
K 文件: *NODE
  NID, X, Y, Z, TC, RC

HyperMesh:
  *createnode X Y Z 0 0 0
```

### 5. 单元 (*ELEMENT)

```
K 文件: *ELEMENT_SHELL
  EID, PID, N1, N2, N3, N4

HyperMesh:
  *createmark nodes 1 N1 N2 N3 N4
  *element 1 0 N1 N2 N3 N4
```

### 6. 接触 (*CONTACT)

```
K 文件: *CONTACT_AUTOMATIC_SURFACE_TO_SURFACE
  SSID, MSID, SSTYP, MSTYP, FS, FD

HyperMesh:
  *createentity groups name="CONTACT_1"
  hm_setvalue groups id=1 STATUS=2 GROUP_TYPE=CONTACT
  hm_setvalue groups id=1 CARD_IMAGE=CONTACT_AUTOMATIC_SURFACE_TO_SURFACE
  hm_setvalue groups id=1 SSID=1
  hm_setvalue groups id=1 MSID=2
  hm_setvalue groups id=1 FS=0.3
  hm_setvalue groups id=1 FD=0.3
```

### 7. 边界条件 (*BOUNDARY)

```
K 文件: *BOUNDARY_SPC_SET
  NSID, CID, DOFX, DOFY, DOFZ, DOFRX, DOFRY, DOFRZ

HyperMesh:
  *createentity groups name="BC_1"
  hm_setvalue groups id=1 STATUS=2 GROUP_TYPE=BOUNDARY
  hm_setvalue groups id=1 CARD_IMAGE=BOUNDARY_SPC_SET
  hm_setvalue groups id=1 NSID=1
  hm_setvalue groups id=1 DOFX=1
  hm_setvalue groups id=1 DOFY=1
  hm_setvalue groups id=1 DOFZ=1
```

### 8. 载荷 (*LOAD)

```
K 文件: *LOAD_SEGMENT
  LCID, SF

HyperMesh:
  *createentity groups name="LOAD_1"
  hm_setvalue groups id=1 STATUS=2 GROUP_TYPE=LOAD
  hm_setvalue groups id=1 CARD_IMAGE=LOAD_SEGMENT
  hm_setvalue groups id=1 LCID=1
  hm_setvalue groups id=1 SF=1.0
```

## 实现方案

### 方案 A: 逐关键字创建

1. 解析 K 文件
2. 按顺序创建每个关键字对应的 HyperMesh 对象
3. 优点：简单直接
4. 缺点：需要处理依赖关系（如 PART 依赖于 SECTION 和 MATERIAL）

### 方案 B: 分层创建

1. 先创建底层对象（NODE, MATERIAL, SECTION）
2. 再创建高层对象（PART, ELEMENT）
3. 最后创建关系对象（CONTACT, BOUNDARY, LOAD）
4. 优点：依赖关系清晰
5. 缺点：需要多遍处理

### 推荐方案 B

分层创建，每层验证后再进入下一层。

## 错误处理

1. **格式验证** — 每个字段必须符合 K 文件格式规范
2. **ID 冲突检测** — 不允许重复的 MID, SECID, PID 等
3. **引用完整性** — PART 引用的 MATERIAL 和 SECTION 必须存在
4. **空集合检测** — SET 不能为空
5. **事务回滚** — 任何步骤失败，撤销所有已创建的对象

## 验证流程

1. 解析 K 文件 → 验证格式
2. 创建 HyperMesh 对象 → 验证创建成功
3. 查询对象 → 验证数量和属性
4. 保存为 .hm 文件 → 验证文件大小
5. 重新加载 → 验证对象完整性
