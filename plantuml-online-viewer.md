# PlantUML在线查看方法

## 方法1：PlantUML官方在线编辑器

1. 访问：https://www.plantuml.com/plantuml/uml/
2. 复制下面的代码
3. 粘贴到编辑器
4. 自动生成图片

## 系统登录流程图代码

```plantuml
@startuml
title 系统登录流程

skinparam backgroundColor #FFFFFF
skinparam defaultFontName Arial
skinparam defaultFontSize 14

actor 用户 as user
participant "前端" as front
participant "后端" as backend
database "数据库" as db

== 用户登录 ==

user -> front: 输入账号密码
activate front

front -> front: 验证格式
note right: 邮箱格式\n密码长度

front -> backend: POST /api/login
activate backend

backend -> db: 查询用户
activate db
db --> backend: 用户信息
deactivate db

alt 密码正确
    backend -> backend: 生成JWT
    backend --> front: 返回Token
    deactivate backend

    front -> front: 保存Token
    front --> user: ✓ 登录成功
    deactivate front

else 密码错误
    backend --> front: 401错误
    deactivate backend

    front --> user: ✗ 密码错误
    deactivate front
end

@enduml
```

## 方法2：VS Code + PlantUML插件

1. 安装VS Code
2. 安装PlantUML插件
3. 创建`.puml`文件
4. 按`Alt+D`预览

## 方法3：在线渲染服务

使用PlantUML服务器：
- 官方：http://www.plantuml.com/plantuml/uml/
- 备用：https://plantuml.com/zh/

## 当前问题

本地Python编码方法有误，PlantUML服务器无法识别。
建议直接使用在线编辑器查看。

---

*创建时间：2026-03-02 23:20*
