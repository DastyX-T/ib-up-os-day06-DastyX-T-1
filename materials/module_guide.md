# Day06. Установка RHEL и контейнеры Podman

Используйте этот репозиторий вместе с курсом Red Hat Academy. Практические задания выполняйте в виртуальной лаборатории Red Hat Academy, а отчёт, артефакты и доказательства оформляйте здесь, в GitHub.

## Что изучается в этот день

Day06 объединяет две большие темы RHCSA II:

1. **Глава 16. Installing Red Hat Enterprise Linux**
2. **Глава 17. Managing Containers with Podman**

Студент должен не просто прочитать теорию, а пройти связанные Guided Exercises и итоговую Lab, а затем доказать выполнение через GitHub-артефакты.

## Что нужно пройти в Red Hat Academy

### По главе 16

- Installing Red Hat Enterprise Linux Interactively
- Guided Exercise: Install Red Hat Enterprise Linux Interactively
- Automating Red Hat Enterprise Linux Installation with Kickstart
- Guided Exercise: Automate Red Hat Enterprise Linux Installation with Kickstart
- Quiz: Installing Red Hat Enterprise Linux

### По главе 17

- Introduction to Containers
- Quiz: Introduction to Containers
- Running Containers with Podman
- Guided Exercise: Run Containers with Podman
- Creating and Managing Container Images
- Guided Exercise: Create and Manage Container Images
- Lab: Manage Containers with Podman

## Что особенно важно понять

### По установке RHEL

- чем отличаются `binary ISO` и `boot ISO`;
- как работает установщик `Anaconda`;
- какие параметры конфигурируются при ручной установке;
- зачем нужна автоматизация установки через `Kickstart`;
- что делают директивы `%packages`, `%post`, `autopart`, `firstboot`, `rootpw`, `user`, `url`, `repo`;
- как проверять и публиковать Kickstart-файл;
- как проверять результат ручной и автоматической установки.

### По контейнерам

- что такое `container image` и `container instance`;
- чем контейнер отличается от виртуальной машины;
- чем `Podman` отличается от daemon-based инструментов;
- как запускать контейнеры в foreground и detached-режиме;
- как проверять работающие контейнеры;
- как создавать образы из `Containerfile`;
- как публиковать образ в registry;
- как проверять теги и метаданные образа через `podman image inspect`.

## Что обязательно должно попасть в доказательства

### По интерактивной установке

- итоговые проверки `id`, `sudo id`, `lsblk`, `ip addr show ens3`, `hostname`, `cat /etc/resolv.conf`;
- подтверждение просмотра логов установки через `tmux` или install console;
- выводы о том, как была настроена система.

### По Kickstart

- ключевые фрагменты итогового Kickstart-файла;
- вывод `ksvalidator`;
- факт запуска установки через `inst.ks=...`;
- итоговые проверки `nmcli con show ens3`, `hostnamectl`, `lsblk`, `apropos fstab`.

### По Podman и образам

- вход в registry;
- запуск контейнера `Hello Red Hat`;
- контейнер `my_webserver` с пробросом порта;
- сборка и наличие `my_image:1.0` и `my_image:1.1`;
- `podman image push`, `podman search --list-tags`, `podman image inspect`;
- результат `lab grade containers-review`.

## Контрольные вопросы для самопроверки

Ответы на них должны быть отражены в `report.md`, `practice_notes.md`, `install_verification.md` и `container_image_audit.md`.

1. Чем ручная установка через `Anaconda` отличается от установки через `Kickstart`?
2. Почему `ksvalidator` не гарантирует корректность всей установки, хотя и проверяет синтаксис?
3. Зачем нужен параметр `inst.ks=`?
4. Почему контейнер без запущенного процесса останавливается?
5. Чем отличается `container image` от `container instance`?
6. Почему важно проверять `podman image inspect`, а не только `podman images`?
7. Какие доказательства выполнения наиболее надёжны с точки зрения преподавателя?
