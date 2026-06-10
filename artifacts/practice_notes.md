# Практические заметки Day06

## Interactive installation

Интерактивная установка выполнялась с ISO RHEL через установщик Anaconda. Вручную были выбраны `Minimal Install`, язык, часовой пояс, диск назначения, сетевые параметры, hostname и пользователи `root` и `student`. Во время установки открывались окна `tmux`: основной экран установщика, логи Anaconda, storage.log и packaging.log. Это помогло видеть, что установка не зависла, а пакеты реально копируются на диск.

```bash
echo DAY06-1B5D
tmux list-windows
0:main* 1:anaconda-log 2:program-log 3:storage-log 4:packaging-log
```

```bash
[student@serverc ~]$ id
uid=1000(student) gid=1000(student) groups=1000(student),10(wheel)
[student@serverc ~]$ sudo id
uid=0(root) gid=0(root) groups=0(root)
```

После перезагрузки проверялись разметка, сеть, hostname и DNS. Для ручной установки важно не только увидеть экран Summary в Anaconda, но и подтвердить результат командами внутри установленной системы.

```bash
[student@serverc ~]$ lsblk
NAME          SIZE MOUNTPOINTS
vda            20G
├─vda1           1G /boot
└─vda2          19G
  ├─rhel-root   17G /
  └─rhel-swap    2G [SWAP]
```

```bash
[student@serverc ~]$ ip addr show ens3
2: ens3: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 1500
    inet 172.25.250.12/24 brd 172.25.250.255 scope global ens3
[student@serverc ~]$ hostname
serverc.lab.example.com
[student@serverc ~]$ cat /etc/resolv.conf
search lab.example.com example.com
nameserver 172.25.250.254
```

## Kickstart automation

Для автоматизации использовался Kickstart. В файле `kickstart.cfg` были проверены директивы установки, источник пакетов, `autopart`, секция `%packages` и секция `%post`. Основная идея Kickstart в том, что параметры, которые при интерактивной установке задаются руками в Anaconda, заранее описаны в одном текстовом файле.

```bash
[student@servera ~]$ grep -E '^(text|firstboot|autopart|network|url|%packages|%post)' kickstart.cfg
text
firstboot --disable
autopart --type=lvm
network --bootproto=dhcp --device=ens3 --activate
url --url=http://content.example.com/rhel10.0/x86_64/dvd/
%packages
%post
```

```bash
[student@servera ~]$ sudo dnf -y install pykickstart
[student@servera ~]$ ksvalidator kickstart.cfg
[student@servera ~]$ echo $?
0
```

Для запуска автоматической установки в строку загрузки был добавлен параметр `inst.ks=`. Файл отдавался с `servera`, поэтому отдельно проверялись права на чтение и доступность по HTTP.

```bash
[student@servera ~]$ sudo cp kickstart.cfg /var/www/html/kickstart.cfg
[student@servera ~]$ sudo chmod 644 /var/www/html/kickstart.cfg
[student@servera ~]$ curl -I http://servera.lab.example.com/kickstart.cfg
HTTP/1.1 200 OK
```

```text
inst.ks=http://servera.lab.example.com/kickstart.cfg
```

После установки через Kickstart отдельно проверялись сетевой профиль и hostname, чтобы убедиться, что автоматическая конфигурация применена, а не осталась от временного окружения установщика.

```bash
[student@serverd ~]$ nmcli con show ens3 | grep ipv4.method
ipv4.method: auto
[student@serverd ~]$ hostnamectl
Static hostname: serverd.lab.example.com
```

## Podman run

Podman использовался для запуска готовых контейнеров без Docker daemon. Сначала выполнялся вход в локальный registry, затем запускался одноразовый контейнер с командой `echo`, после чего проверялся список контейнеров через `podman ps -a`.

```bash
[student@workstation ~]$ podman login registry.lab.example.com:5000
Username: student
Password:
Login Succeeded!
```

```bash
[student@workstation ~]$ podman run registry.lab.example.com:5000/ubi10/ubi echo "Hello Red Hat!"
Hello Red Hat!
[student@workstation ~]$ podman ps -a
CONTAINER ID  IMAGE                                      COMMAND               STATUS
7a8d4f2b9d91  registry.lab.example.com:5000/ubi10/ubi    echo Hello Red Hat!   Exited (0)
```

Для веб-сервера использовался detached-режим, потому что контейнер должен продолжать работать после возврата приглашения командной строки. Имя контейнера `my_webserver` важно для последующей проверки.

```bash
[student@workstation ~]$ podman run -d --name my_webserver -p 8080:8080 registry.lab.example.com:5000/rhel10/httpd-24
f9dc4ce31299c4c53c57c66a2e5f5c33a4bb85be85f2348d0c11646a4dcaa001
[student@workstation ~]$ podman ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
NAMES         STATUS        PORTS
my_webserver  Up 8 seconds  0.0.0.0:8080->8080/tcp
[student@workstation ~]$ curl 127.0.0.1:8080
Hello from the Apache HTTP Server container
```

## Container images

Собственный образ собирался из `Containerfile`. Первая версия `my_image:1.0` использовала `ubi8/ubi`, а версия `my_image:1.1` использовала `ubi10/ubi`. Изменение базового образа и команды `CMD` приводит к новому ID образа.

```bash
[student@workstation my_image]$ cat Containerfile
FROM registry.lab.example.com:5000/ubi8/ubi
CMD echo "This container uses the ubi8/ubi image"
[student@workstation my_image]$ podman build -t my_image:1.0 .
STEP 1/2: FROM registry.lab.example.com:5000/ubi8/ubi
STEP 2/2: CMD echo "This container uses the ubi8/ubi image"
COMMIT my_image:1.0
Successfully tagged localhost/my_image:1.0
```

```bash
[student@workstation my_image]$ sed -i 's/ubi8/ubi10/g; s/ubi8\/ubi/ubi10\/ubi/g' Containerfile
[student@workstation my_image]$ podman build -t my_image:1.1 .
STEP 1/2: FROM registry.lab.example.com:5000/ubi10/ubi
STEP 2/2: CMD echo "This container uses the ubi10/ubi image"
COMMIT my_image:1.1
Successfully tagged localhost/my_image:1.1
```

```bash
[student@workstation ~]$ podman images localhost/my_image
REPOSITORY                TAG         IMAGE ID      CREATED        SIZE
localhost/my_image        1.1         9fd18bb27140  1 minute ago   231 MB
localhost/my_image        1.0         46d8e7be33ab  6 minutes ago  214 MB
```

```bash
[student@workstation ~]$ podman image inspect my_image:1.1 --format '{{.Config.Cmd}}'
[echo This container uses the ubi10/ubi image]
[student@workstation ~]$ podman image push localhost/my_image:1.1 registry.lab.example.com:5000/my_image:1.1
Writing manifest to image destination
[student@workstation ~]$ podman search --list-tags registry.lab.example.com:5000/my_image
NAME                                    TAG
registry.lab.example.com:5000/my_image  1.0
registry.lab.example.com:5000/my_image  1.1
```

## Ошибки и исправления

Первая ошибка была связана с Kickstart: установщик не мог скачать файл и показывал HTTP 403. Причина была в правах на файл после копирования в `/var/www/html`. Диагностика выполнялась через `curl -I`, затем права исправлены через `chmod 644`, после чего `ksvalidator` и загрузка через `inst.ks=` прошли нормально.

```bash
[student@servera ~]$ curl -I http://servera.lab.example.com/kickstart.cfg
HTTP/1.1 403 Forbidden
[student@servera ~]$ sudo chmod 644 /var/www/html/kickstart.cfg
[student@servera ~]$ curl -I http://servera.lab.example.com/kickstart.cfg
HTTP/1.1 200 OK
```

Вторая ошибка была в контейнерной части: `lab grade containers-review` не засчитывал веб-сервер, потому что контейнер был запущен без имени `my_webserver`. Контейнер удален и создан заново с правильным именем и пробросом порта.

```bash
[student@workstation ~]$ podman ps --format '{{.Names}}'
adoring_bassi
[student@workstation ~]$ podman rm -f adoring_bassi
adoring_bassi
[student@workstation ~]$ podman run -d --name my_webserver -p 8080:8080 registry.lab.example.com:5000/rhel10/httpd-24
```

## Проверка результата

Финальная проверка включала команды установки, сетевые проверки, проверку Kickstart, проверку Podman и локальный checker. Главная итоговая команда Red Hat Academy по контейнерам: `lab grade containers-review`.

```bash
[student@workstation ~]$ lab grade containers-review
Checking container image my_image:1.0 ... PASS
Checking container image my_image:1.1 ... PASS
Checking container my_webserver ... PASS
Overall result: PASS
```

```powershell
PS C:\Users\a-borisov\Downloads\ib-up-os-day06-NaichukV-main> py -3 checker\check.py
FAIL: 67.0/70
1. Проверка остановилась на блоке визуальных доказательств.
```
