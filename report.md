# IB-UP-OS-Day06-Task. Installing Red Hat Enterprise Linux and managing containers with Podman

## Интерактивная установка RHEL

В этой работе я выполнил установку Red Hat Enterprise Linux через установщик Anaconda. Во время установки вручную настраивал основные параметры системы: выбирал профиль установки `Minimal Install`, задавал hostname, сетевые параметры, часовой пояс, пароль пользователя `root`, создавал пользователя `student` и указывал диск для установки системы

После завершения установки дополнительно проверял корректность настройки системы. Для этого использовал команды `id`, `sudo id`, `lsblk`, `ip addr show ens3`, `hostname` и `cat /etc/resolv.conf`. Также ознакомился с журналами установки через `tmux`, где можно просматривать логи Anaconda, информацию о работе с дисками и процессе установки пакетов. Это позволило лучше понять процесс установки и способы диагностики возможных ошибок.

```bash
id
sudo id
lsblk
ip addr show ens3
hostname
cat /etc/resolv.conf
```

## Автоматизация установки через Kickstart

Kickstart нужен для автоматизации установки RHEL. Вместо ручного заполнения экранов Anaconda параметры заранее описываются в `kickstart.cfg`, а установщик получает этот файл через параметр загрузки `inst.ks=`. В работе использовался путь `inst.ks=http://servera.lab.example.com/kickstart.cfg`, то есть Anaconda скачивала сценарий установки с веб-сервера.

В Kickstart-файле были важны директивы `text`, `firstboot --disable`, `autopart --type=lvm`, сетевые настройки, `%packages` и `%post`. Секция `%packages` задавала набор устанавливаемых пакетов, а `%post` выполняла команды после установки системы. Перед запуском автоматической установки конфигурация проверялась через `ksvalidator`, потому что синтаксическая ошибка в Kickstart ломает весь автоматический процесс. Также проверялись права на опубликованный файл, чтобы установщик не получал HTTP 403.

```bash
ksvalidator kickstart.cfg
sudo cp kickstart.cfg /var/www/html/kickstart.cfg
sudo chmod 644 /var/www/html/kickstart.cfg
curl -I http://servera.lab.example.com/kickstart.cfg
```

## Запуск контейнеров с помощью Podman

Podman использовался для запуска контейнеров без Docker daemon. Сначала выполнялся вход в учебный registry через `podman login registry.lab.example.com:5000`, затем запускался контейнер на базе UBI с командой `podman run ... echo "Hello Red Hat!"`. После выполнения одноразовой команды контейнер завершался, поэтому проверка выполнялась через `podman ps -a`.

Для сервиса использовался контейнер `my_webserver`. Он запускался в `detached`-режиме через `podman run -d --name my_webserver -p 8080:8080 ...`, чтобы процесс продолжал работать в фоне. Затем проверялись статус контейнера через `podman ps` и ответ веб-сервера через `curl 127.0.0.1:8080`. Такой сценарий показывает базовую модель Podman: образ хранит файловую систему и команду запуска, а container instance является конкретным запущенным экземпляром.

```bash
podman login registry.lab.example.com:5000
podman run registry.lab.example.com:5000/ubi10/ubi echo "Hello Red Hat!"
podman ps -a
podman run -d --name my_webserver -p 8080:8080 registry.lab.example.com:5000/rhel10/httpd-24
curl 127.0.0.1:8080
```

## Создание и управление образами контейнеров

Собственные образы создавались через `Containerfile`. В нем задавался базовый образ в инструкции `FROM` и команда запуска в `CMD`. Первая версия `my_image:1.0` использовала `ubi8/ubi`, а версия `my_image:1.1` использовала `ubi10/ubi`. После изменения `Containerfile` выполнялся `podman build`, и каждый тег получил свой Image ID.

Дальше образы публиковались в registry через `podman image push`, а наличие тегов проверялось через `podman search --list-tags`. Для технической проверки использовался `podman image inspect`: через него видно `Config.Cmd`, базовые параметры, слои и различия между `my_image:1.0` и `my_image:1.1`. Это важно, потому что тег сам по себе не доказывает содержимое образа, а inspect показывает фактическую конфигурацию.

```bash
podman build -t my_image:1.0 .
podman build -t my_image:1.1 .
podman image push localhost/my_image:1.0 registry.lab.example.com:5000/my_image:1.0
podman search --list-tags registry.lab.example.com:5000/my_image
podman image inspect my_image:1.1
```

## Итог и выводы

В результате была отработана полная цепочка: ручная установка RHEL через Anaconda, автоматизация через Kickstart, запуск готовых контейнеров в Podman, сборка собственных образов из Containerfile и проверка Lab `containers-review`. Команда `lab grade containers-review` показала, что контейнеры, образы и теги подготовлены в ожидаемом виде.

Главный вывод по установке RHEL: интерактивный режим удобен для понимания процесса и диагностики, а Kickstart нужен для воспроизводимой установки без ручных кликов. Главный вывод по контейнерам: Podman разделяет образ и запущенный контейнер, а теги и `podman image inspect` помогают контролировать версии. Самыми полезными командами для контроля результата стали `lsblk`, `nmcli`, `ksvalidator`, `podman ps`, `podman build`, `podman image inspect` и `lab grade containers-review`.


