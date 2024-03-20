-- init.sql
-- 切换到mysql数据库
use mysql;
-- 设置用户访问的ip
update user set Host='%' where User='root';
-- 刷新配置
flush privileges;
