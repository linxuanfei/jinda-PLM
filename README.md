# 津达立 PLM / Jinda PLM

Phase 1 是一套可独立启动的 PLM 骨架，应用本体是 [InvenTree](https://github.com/inventree/InvenTree)（MIT）。本仓库不替代公司 ERP，不把 PLM 并进 ERP，也不在这里实现库存或财务。连接器编码和线束打样报价编码只有空的插件占位，规则尚未提供。

Phase 1 is a PLM skeleton that runs on its own. The application is [InvenTree](https://github.com/inventree/InvenTree) (MIT). It does not replace the company ERP, it is not merged into the ERP, and it does not implement inventory or finance. Connector numbering and wire-harness sample-quote numbering are empty plugin stubs. Numbering rules have not been provided.

InvenTree 自己带有库存和价格界面。那是上游产品的一部分。Phase 1 不把这些界面配置成公司 ERP，ERP 契约里也不包含库存数量和金额。

InvenTree ships its own stock and pricing screens. Those belong to the upstream product. Phase 1 does not configure them as the company ERP, and the ERP contract includes neither stock quantities nor money.

生产环境按 InvenTree 文档使用官方镜像，不需要把 InvenTree 源码放进本仓库。本仓库收进的是文档要求的 compose 文件，以及津达立自己的占位插件和 ERP 契约。

The production setup follows the InvenTree documentation and uses the published image. The InvenTree source tree is not vendored. This repository contains the compose files that documentation requires, plus Jinda's placeholder plugins and the ERP contract.

文档 / Docs: [Docker installation](https://docs.inventree.org/en/stable/start/docker_install/)（stable，与镜像标签对应的文档）。`docker-compose.yml` 和 `Caddyfile` 取自 InvenTree tag **1.7.3** 的 `contrib/container/`，未改内容。`.env.example` 由同一 tag 的 `.env` 改写。`docker-compose.override.yml` 只把 `./plugins` 挂到官方镜像已设置的 `INVENTREE_PLUGIN_DIR`（`/home/inventree/data/plugins`）。

## 启动 / Start

在本仓库根目录执行。Docker 与 Docker Compose 需要已经安装。

Run these commands from the repository root. Docker and Docker Compose must already be installed.

```bash
cp .env.example .env
```

编辑 `.env`。至少把 `INVENTREE_DB_PASSWORD` 换成数据库口令。它是 PostgreSQL 的口令，不是登录 PLM 的口令。上游示例值是 `pgpassword`，不能拿去实际使用。`INVENTREE_EXT_VOLUME` 默认是 `./inventree-data`。需要换端口时设置 `INVENTREE_HTTP_PORT` / `INVENTREE_HTTPS_PORT`，并让 `INVENTREE_SITE_URL` 带上同一端口。

Edit `.env`. Replace `INVENTREE_DB_PASSWORD` before use. That value is the PostgreSQL password, not the PLM login. The upstream sample value is `pgpassword` and must not be used as-is. `INVENTREE_EXT_VOLUME` defaults to `./inventree-data`. To publish a non-default port, set `INVENTREE_HTTP_PORT` and/or `INVENTREE_HTTPS_PORT`, and include that port in `INVENTREE_SITE_URL`.

然后按 InvenTree 文档执行：

Then run the commands from the InvenTree docker installation guide:

```bash
docker compose run --rm inventree-server invoke update
docker compose run inventree-server invoke superuser
docker compose up -d
```

`invoke update` 会安装依赖、建库、迁移，并收集静态文件。`invoke superuser` 在终端里询问管理员账号。`up -d` 启动 `inventree-db`、`inventree-server`、`inventree-worker`、`inventree-proxy`、`inventree-cache`。

`invoke update` installs dependencies, creates the database, migrates, and collects static files. `invoke superuser` prompts for an administrator account. `up -d` starts `inventree-db`, `inventree-server`, `inventree-worker`, `inventree-proxy`, and `inventree-cache`.

默认站点是 `INVENTREE_SITE_URL`。示例文件里是 <http://localhost>。只在运行 compose 的那台机器上可用。

The site is `INVENTREE_SITE_URL`. The sample file uses <http://localhost>, which is reachable on the machine running compose.

健康检查 / Health check，文档中的未认证端点是 `/api/system/health/`：

```bash
curl -fsS http://localhost/api/system/health/
docker compose ps
```

如果改了 `INVENTREE_HTTP_PORT`，把 `localhost` 换成该端口。代理容器内部还用 `http://127.0.0.1:9090/api/system/health/` 做健康检查。

If `INVENTREE_HTTP_PORT` is set, call that port instead of port 80. Inside the proxy container the health check is `http://127.0.0.1:9090/api/system/health/`.

日志 / Logs:

```bash
docker compose logs inventree-server
```

停止 / Stop:

```bash
docker compose down
```

## 登录 / Login

这条 Docker Compose 路径**没有**预置可登录账号。

This Docker Compose path does **not** come with an account you can log in with.

InvenTree 用户账号文档写明：默认不带任何用户账号。[User Accounts](https://docs.inventree.org/en/stable/start/accounts/)

The user-account documentation says that InvenTree does not ship with any user accounts. [User Accounts](https://docs.inventree.org/en/stable/start/accounts/)

第一次启动用上面的 `docker compose run inventree-server invoke superuser` 创建管理员。文档也允许用环境变量创建，创建后必须从 `.env` 删除。见 [Docker installation](https://docs.inventree.org/en/stable/start/docker_install/) 的 “Create Administrator Account” 和 “Scrub Account Data”。

Create the administrator with `docker compose run inventree-server invoke superuser`, as above. The same page allows environment variables for that first account, and says to remove them from `.env` afterwards. See “Create Administrator Account” and “Scrub Account Data” in the [Docker installation](https://docs.inventree.org/en/stable/start/docker_install/) guide.

上游示例文件把下面两行注释掉了，它们**不是**可用的默认口令，不要启用：

The upstream sample `.env` comments out the following lines. They are **not** a working default password. Do not enable them:

```bash
#INVENTREE_ADMIN_USER=admin
#INVENTREE_ADMIN_PASSWORD=admin
```

来源 / Source: [InvenTree `contrib/container/.env` at tag 1.7.3](https://github.com/inventree/InvenTree/blob/1.7.3/contrib/container/.env)

配置说明里的示例还注释了 `admin_password: inventree`。那同样只是示例，不是本栈的默认登录。[Configuration](https://docs.inventree.org/en/stable/start/config/)

The configuration page also comments an example `admin_password: inventree`. That example is not a default login for this stack. [Configuration](https://docs.inventree.org/en/stable/start/config/)

另一条安装路径（InvenTree installer，本仓库不用）会生成用户名 `admin`，并把随机口令写到 `/etc/inventree/admin_password`。不要把那条路径的账号当成这里的默认登录。[Installer](https://docs.inventree.org/en/stable/start/installer/)

A different install path, the InvenTree installer, is not used here. That path generates username `admin` and writes a random password to `/etc/inventree/admin_password`. Do not treat that account as the login for this compose stack. [Installer](https://docs.inventree.org/en/stable/start/installer/)

数据库用户 `pguser` 只用于 PostgreSQL。

The database user `pguser` is only for PostgreSQL.

## 编码插件 / Coding plugins

两个空插件，没有编码规则：

Two empty plugins. They contain no numbering rules.

| 目录 / Directory | 插件类 / Class | 用途 / Reserved for |
| --- | --- | --- |
| `plugins/jinda_connector_coding/` | `JindaConnectorCodingPlugin` | 连接器编码 / connector part numbering |
| `plugins/jinda_harness_quote_coding/` | `JindaHarnessQuoteCodingPlugin` | 线束打样报价编码 / wire-harness sample-quote numbering |

`INVENTREE_PLUGINS_ENABLED=True` 时，InvenTree 会发现它们，并在管理员于 Admin Center 启用之前保持关闭。即使启用，它们也没有 mixin，不会生成或解析编码。

With `INVENTREE_PLUGINS_ENABLED=True`, InvenTree can discover them. They stay disabled until a staff user enables them in the Admin Center. Enabling them still does not generate or parse a code: the classes have no mixins.

发现方式见 [Developing a Plugin](https://docs.inventree.org/en/stable/plugins/develop/)。新发现的插件默认关闭。

Discovery is described in [Developing a Plugin](https://docs.inventree.org/en/stable/plugins/develop/). Newly discovered plugins are disabled by default.

## ERP 接口 / ERP interface

字段契约在 [`contracts/erp-interface.openapi.yaml`](contracts/erp-interface.openapi.yaml)。它描述以后 ERP 从 PLM 读取物料主数据、BOM 和编码查询的字段。Phase 1 没有进程提供这些路由。契约写明：在真正实现之前，声称实现该契约的服务对每个操作返回 HTTP 501。

The field contract is [`contracts/erp-interface.openapi.yaml`](contracts/erp-interface.openapi.yaml). It lists the fields for a later read, by the ERP, of part master, BOM, and coding lookup. No process in Phase 1 serves those routes. Until an implementation exists, a server that claims the contract returns HTTP 501 for every operation.

编码查询不解析编码。库存数量和金额不在契约里。

The coding lookup does not parse a code. Stock quantities and money are outside the contract.

## 许可 / License

津达立编写的文件使用 MIT，见 `LICENSE`。InvenTree 仍为 MIT，版权属于 InvenTree Developers，见 `NOTICE` 和 `LICENSES/InvenTree-MIT.txt`。

Files written for Jinda are MIT, see `LICENSE`. InvenTree remains MIT, copyright InvenTree Developers, see `NOTICE` and `LICENSES/InvenTree-MIT.txt`.
