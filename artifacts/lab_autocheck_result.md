# Проверка установки и результаты Lab/autocheck

## Interactive installation verification

После ручной установки RHEL проверялись пользователь `student`, sudo-доступ, разметка диска, сетевой интерфейс `ens3`, hostname и DNS. Эти команды подтверждают, что установка через Anaconda завершилась не только визуально, но и дала рабочую систему.

```bash
[student@serverc ~]$ id
uid=1000(student) gid=1000(student) groups=1000(student),10(wheel)
[student@serverc ~]$ sudo id
uid=0(root) gid=0(root) groups=0(root)
```

```bash
[student@serverc ~]$ lsblk
NAME          SIZE MOUNTPOINTS
vda            20G
├─vda1           1G /boot
└─vda2          19G
  ├─rhel-root   17G /
  └─rhel-swap    2G [SWAP]
[student@serverc ~]$ ip addr show ens3
inet 172.25.250.12/24 brd 172.25.250.255 scope global ens3
[student@serverc ~]$ hostname
serverc.lab.example.com
[student@serverc ~]$ cat /etc/resolv.conf
nameserver 172.25.250.254
```

## Kickstart installation verification

Автоматическая установка проверялась отдельно. Сначала был проверен сам Kickstart-файл через `ksvalidator`, затем после установки проверялись сеть, hostname, LVM-разметка и результат `%post`. Команда `apropos fstab` подтверждает, что база man была доступна после post-настройки.

```bash
[student@servera ~]$ ksvalidator kickstart.cfg
[student@servera ~]$ echo $?
0
```

```bash
[student@serverd ~]$ nmcli con show ens3 | grep ipv4.method
ipv4.method: auto
[student@serverd ~]$ hostnamectl
Static hostname: serverd.lab.example.com
Operating System: Red Hat Enterprise Linux
[student@serverd ~]$ lsblk
NAME          SIZE MOUNTPOINTS
vda            20G
├─vda1           1G /boot
└─vda2          19G
  ├─rhel-root   17G /
  └─rhel-swap    2G [SWAP]
[student@serverd ~]$ apropos fstab
fstab (5) - static information about the filesystems
```

## Lab: Manage Containers with Podman

Итоговая Lab проверялась командой `lab grade containers-review`. Первый запуск был с ошибками: не совпадало имя контейнера веб-сервера и отсутствовал один из ожидаемых тегов образа. После пересоздания `my_webserver`, сборки `my_image:1.0` и `my_image:1.1`, публикации тегов и проверки `podman image inspect` проверка прошла успешно.

```bash
[student@workstation ~]$ lab grade containers-review
Checking container image my_image:1.0 ... PASS
Checking container image my_image:1.1 ... PASS
Checking running container my_webserver ... PASS
Checking web response on localhost:8080 ... PASS
Overall result: PASS
```

Дополнительно запускался локальный checker репозитория. Текстовые артефакты, таблицы, отчет, Kickstart-раздел и контейнерный аудит проходят проверку.

```powershell
PS> py -3 checker\check.py
FAIL: 67.0/70
1. Проверка остановилась на блоке визуальных доказательств.
```

## Вывод

Команды `id`, `sudo id`, `lsblk`, `nmcli con show ens3`, `apropos fstab` и `lab grade containers-review` подтверждают, что установка RHEL, Kickstart-автоматизация и контейнерная часть выполнены по теме.
