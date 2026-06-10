# Проверка установки RHEL

## Интерактивная установка RHEL

Интерактивная установка выполнялась через Anaconda с ISO RHEL. Вручную настраивались `Minimal Install`, hostname, сеть, пароль `root`, пользователь `student`, диск назначения и часовой пояс. В `tmux` просматривались логи Anaconda, storage.log и packaging.log, чтобы видеть ход установки и ошибки на этапе разметки или установки пакетов.

```bash
echo DAY06-1B5D
tmux list-windows
0:main* 1:anaconda-log 2:storage-log 3:packaging-log
```

Проверка пользователя и прав sudo:

```bash
[student@serverc ~]$ id
uid=1000(student) gid=1000(student) groups=1000(student),10(wheel)
[student@serverc ~]$ sudo id
uid=0(root) gid=0(root) groups=0(root)
```

Проверка диска после установки:

```bash
[student@serverc ~]$ lsblk
NAME          MAJ:MIN RM SIZE RO TYPE MOUNTPOINTS
vda           252:0    0  20G  0 disk
├─vda1        252:1    0   1G  0 part /boot
└─vda2        252:2    0  19G  0 part
  ├─rhel-root 253:0    0  17G  0 lvm  /
  └─rhel-swap 253:1    0   2G  0 lvm  [SWAP]
```

Проверка сети, hostname и DNS:

```bash
[student@serverc ~]$ ip addr show ens3
2: ens3: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 1500
    inet 172.25.250.12/24 brd 172.25.250.255 scope global noprefixroute ens3
[student@serverc ~]$ hostname
serverc.lab.example.com
[student@serverc ~]$ cat /etc/resolv.conf
search lab.example.com example.com
nameserver 172.25.250.254
```

## Установка через Kickstart

Kickstart использовался для повторяемой автоматической установки. В файле `kickstart.cfg` были проверены директивы `text`, `firstboot --disable`, `autopart --type=lvm`, сетевые параметры, `%packages` и `%post`. Параметр `inst.ks=http://servera.lab.example.com/kickstart.cfg` передавался установщику при загрузке, чтобы Anaconda забрала готовый сценарий установки.

```bash
[student@servera ~]$ grep -E '^(text|firstboot|autopart|network|%packages|%post)' kickstart.cfg
text
firstboot --disable
autopart --type=lvm
network --bootproto=dhcp --device=ens3 --activate
%packages
%post
```

Проверка синтаксиса:

```bash
[student@servera ~]$ ksvalidator kickstart.cfg
[student@servera ~]$ echo $?
0
```

Публикация файла и строка запуска:

```bash
[student@servera ~]$ sudo cp kickstart.cfg /var/www/html/kickstart.cfg
[student@servera ~]$ sudo chmod 644 /var/www/html/kickstart.cfg
[student@servera ~]$ curl -I http://servera.lab.example.com/kickstart.cfg
HTTP/1.1 200 OK
```

```text
inst.ks=http://servera.lab.example.com/kickstart.cfg
```

Проверки после автоматической установки:

```bash
[student@localhost ~]$ nmcli con show ens3 | grep ipv4.method
ipv4.method: auto
[student@localhost ~]$ hostnamectl
Static hostname: serverd.lab.example.com
Operating System: Red Hat Enterprise Linux
[student@localhost ~]$ apropos fstab
fstab (5) - static information about the filesystems
```

## Сравнение ручной установки и Kickstart

При ручной установке решения принимались в Anaconda: выбор диска, сетевых настроек, пользователя и профиля установки. Такой режим удобен для первого знакомства и диагностики, потому что можно видеть каждый экран и логи `tmux`.

При Kickstart эти же действия заранее описаны в `kickstart.cfg`. Директива `autopart` создает LVM-разметку автоматически, `%packages` задает набор пакетов, `%post` выполняет команды после установки, а `inst.ks=` указывает установщику, где скачать файл. Этот способ лучше подходит для повторяемого развертывания нескольких одинаковых машин.

```bash
[student@serverd ~]$ lsblk
NAME          SIZE MOUNTPOINTS
vda            20G
├─vda1           1G /boot
└─vda2          19G
  ├─rhel-root   17G /
  └─rhel-swap    2G [SWAP]
[student@serverd ~]$ sudo id
uid=0(root) gid=0(root) groups=0(root)
```
