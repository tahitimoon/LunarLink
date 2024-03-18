cur_path=`pwd`
#docker rm mysql
docker run -p 3308:3306 --name mysql5.7 --restart always -v $cur_path/logs:/logs -v $cur_path/data:/var/lib/mysql -v $cur_path/conf.d/my.cnf:/etc/mysql/mysql.conf.d/mysqld.cnf -v $cur_path/run:/var/run/mysql -e MYSQL_ROOT_PASSWORD=123456 -d mysql:5.7
