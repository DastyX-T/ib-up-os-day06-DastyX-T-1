# Таблица доказательств выполнения Day06

| № | Evidence item | Файл или раздел | Что подтверждается | Статус |
|---|---|---|---|---|
| 1 | Interactive install summary or logs | `artifacts/install_verification.md` | Описан экран Anaconda Summary, ручная установка RHEL и просмотр tmux/logs | Заполнено |
| 2 | Interactive install verification | `artifacts/install_verification.md` | Команды `id`, `sudo id`, `lsblk`, `ip addr show ens3`, `hostname`, `cat /etc/resolv.conf` после ручной установки | Заполнено |
| 3 | Kickstart validation | `artifacts/install_verification.md` | Успешный запуск `ksvalidator kickstart.cfg` без ошибок синтаксиса | Заполнено |
| 4 | Kickstart install verification | `artifacts/install_verification.md`, `artifacts/lab_autocheck_result.md` | Проверка установки через `inst.ks=`, DHCP, hostname, LVM/autopart и `%post` | Заполнено |
| 5 | Hello Red Hat container run | `artifacts/container_image_audit.md` | Запуск `podman run ... echo "Hello Red Hat!"` и завершение контейнера со статусом `Exited (0)` | Заполнено |
| 6 | Detached webserver container | `artifacts/container_image_audit.md` | Контейнер `my_webserver` запущен с `-d`, порт 8080 проброшен, `curl 127.0.0.1:8080` отвечает | Заполнено |
| 7 | Image build and tags | `artifacts/container_image_audit.md` | Сборка `my_image:1.0` и `my_image:1.1` через `podman build`, наличие разных тегов | Заполнено |
| 8 | Image inspect or push | `artifacts/container_image_audit.md` | `podman image inspect`, `podman image push` и `podman search --list-tags` подтверждают параметры и публикацию образов | Заполнено |
| 9 | Lab grade containers-review | `artifacts/lab_autocheck_result.md` | Итоговая проверка Red Hat Academy `lab grade containers-review` завершена с PASS | Заполнено |
| 10 | Local checker and final report | `report.md`, `student/reflection.md`, `artifacts/lab_autocheck_result.md` | Локальный checker, итоговый отчет и рефлексия заполнены перед сдачей | Заполнено |

## Итоговая заметка

Журнал связывает каждый обязательный этап с текстовым артефактом репозитория: интерактивной установкой, Kickstart, Podman, сборкой образов, проверкой Lab и локальным checker.
