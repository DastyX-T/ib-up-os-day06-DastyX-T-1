# Проверочный список Day06

- [x] Заполнен `student/submission.yaml`
- [x] Сгенерирован и указан token `DAY06-1B5D`
- [x] Token добавлен в `student/reflection.md`
- [x] Обновлен `student/reflection.md`
- [x] Изучена тема интерактивной установки RHEL
- [x] Изучена тема Kickstart
- [x] Изучена тема Podman
- [x] Заполнен `artifacts/concepts_table.md`
- [x] Заполнен `artifacts/guided_exercises_log.md`
- [x] Выполнен этап `Install Red Hat Enterprise Linux Interactively`
- [x] В отчете описана роль Anaconda
- [x] Указан профиль `Minimal Install`
- [x] Указаны пользователи `root` и `student`
- [x] Указан просмотр логов через `tmux`
- [x] Проверены `id` и `sudo id`
- [x] Проверен `lsblk`
- [x] Проверен `ip addr show ens3`
- [x] Проверены `hostname` и `cat /etc/resolv.conf`
- [x] Выполнен этап `Automate Red Hat Enterprise Linux Installation with Kickstart`
- [x] Описаны изменения в `kickstart.cfg`
- [x] Указана директива `autopart`
- [x] Указана секция `%packages`
- [x] Указана секция `%post`
- [x] Запущен `ksvalidator`
- [x] Указан параметр `inst.ks=http://servera.lab.example.com/kickstart.cfg`
- [x] Проверены `nmcli con show ens3` и `hostnamectl`
- [x] Проверен `apropos fstab`
- [x] Выполнен этап `Run Containers with Podman`
- [x] Выполнен `podman login`
- [x] Выполнен `podman run` для Hello Red Hat
- [x] Запущен detached container `my_webserver`
- [x] Проверен `podman ps -a`
- [x] Проверен `curl 127.0.0.1:8080`
- [x] Выполнен этап `Create and Manage Container Images`
- [x] Создан `Containerfile`
- [x] Собран образ `my_image:1.0`
- [x] Собран образ `my_image:1.1`
- [x] Выполнен `podman image push`
- [x] Проверены теги через `podman search --list-tags`
- [x] Выполнен `podman image inspect`
- [x] Выполнена Lab `Manage Containers with Podman`
- [x] Запущен `lab grade containers-review`
- [x] Заполнен `artifacts/practice_notes.md`
- [x] Заполнен `artifacts/lab_autocheck_result.md`
- [x] Заполнен `artifacts/install_verification.md`
- [x] Заполнен `artifacts/container_image_audit.md`
- [x] Заполнен `artifacts/evidence_log.md`
- [x] Заполнен `report.md`
- [x] Запущен локальный checker
- [x] Проверено, что текстовые артефакты проходят локальную проверку

## Итог

Текстовые артефакты, отчет, журнал доказательств и проверочные разделы заполнены. После добавления недостающих визуальных доказательств нужно повторно запустить `py -3 checker\check.py`.
