# ADR-0001：assets/ 为模板唯一真相源，脚本零内嵌字符串

状态：已采纳

## 背景

初始化器 `scripts/init_workspace.py` 要为目标项目生成一整套骨架（入口文档、docs、skills、`.agent/` 簇记、技术栈基线）。早期实现把模板内容以大段字符串内嵌在 Python 脚本里，与 `assets/` 下的文件双份维护：改一处忘改另一处就会漂移，且模板无法直接用 diff 审阅。

## 决策

`assets/` 是模板的**唯一真相源**。`init_workspace.py` 只负责遍历 `assets/skeleton/` 与 `assets/stacks/<stack>/`、渲染 `{{VAR}}` 占位符、写入目标项目，**脚本内不含任何内嵌模板字符串**。修改模板一律直接改 `assets/` 下的文件。

## 备选方案

- 脚本内嵌字符串：被否，双份漂移、难审阅。
- 用 manifest 文件登记路径映射：被否，多一层配置且路径镜像目标项目后「遍历即拷贝」已足够，无需映射。

## 后果

- 改模板只改 `assets/`，零脚本改动，diff 清晰。
- 新增占位符须同时改 `build_context`，否则脚本会在写完后扫到残留 `{{VAR}}` 并告警（`validate.sh` 也校验占位符集合一致）。
- 脚本被拷贝/软链到任意位置都能用 `Path(__file__).resolve().parent.parent / "assets"` 定位模板。
