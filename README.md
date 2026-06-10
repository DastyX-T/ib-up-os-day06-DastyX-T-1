[![Review Assignment Due Date](https://classroom.github.com/assets/deadline-readme-button-22041afd0340ce965d47ae6ef1cefeee28c7c493a6346c4f15d667ab976d596c.svg)](https://classroom.github.com/a/4b-Lwi0x)
# IB-UP-OS-Day06-Task. Installing Red Hat Enterprise Linux and managing containers with Podman

Это шестое задание предмета `IB-UP-OS` по материалам RHCSA II. В этот день вы изучаете интерактивную установку Red Hat Enterprise Linux, автоматизацию установки через Kickstart, а также запуск контейнеров и управление образами с помощью Podman.

Основной учебный курс проходите в системе Red Hat Academy. Русскоязычные материалы в этом репозитории предназначены для обучения на привычном языке, но не заменяют оригинальный курс. Все Guided Exercises и Lab выполняйте в виртуальной лаборатории Red Hat Academy.

В GitHub нужно загрузить не только итоговый отчёт, но и доказательства выполнения:

- заполненные артефакты по Guided Exercises;
- журнал команд и ошибок;
- результаты встроенной проверки Lab;
- отдельные проверочные выводы по интерактивной установке и Kickstart;
- отдельный аудит по контейнерам и образам;
- скриншоты с подписями и token;
- личную рефлексию по сложности и удобству такого формата работы.

## Что нужно подготовить

1. Аккаунт GitHub.
2. Доступ к GitHub Classroom assignment от преподавателя.
3. Установленный Git или GitHub Desktop.
4. VS Code или другой редактор Markdown.
5. Python 3.10 или новее для локальной проверки.
6. Доступ к Red Hat Academy и виртуальной лаборатории курса.

Если GitHub-аккаунта ещё нет, зарегистрируйтесь:

```text
https://github.com/signup
```

Желательно использовать тот же email, который используется в учебной системе колледжа.

## Основные термины

- `Anaconda` — установщик Red Hat Enterprise Linux.
- `binary ISO` — полноценный установочный ISO с пакетами BaseOS и AppStream.
- `boot ISO` — облегчённый ISO, который требует сетевой источник пакетов.
- `Kickstart` — файл автоматизированной установки RHEL.
- `ksvalidator` — утилита проверки синтаксиса Kickstart.
- `inst.ks=` — параметр загрузки, указывающий путь к Kickstart-файлу.
- `Podman` — daemonless-инструмент для локального управления контейнерами.
- `container image` — неизменяемый шаблон контейнера.
- `container instance` — исполняемый экземпляр образа контейнера.
- `Containerfile` — файл инструкций для сборки образа.
- `registry` — хранилище контейнерных образов.
- `detached container` — контейнер, работающий в фоне.
- `port mapping` — проброс порта хоста в порт контейнера.

## Структура репозитория

```text
.
├── README.md
├── manifest.json
├── report.md
├── student/
│   ├── submission.yaml
│   └── reflection.md
├── materials/
│   ├── module_guide.md
│   ├── chapter_16_installing_red_hat_enterprise_linux_ru.md
│   └── chapter_17_managing_containers_with_podman_ru.md
├── artifacts/
│   ├── concepts_table.md
│   ├── guided_exercises_log.md
│   ├── practice_notes.md
│   ├── lab_autocheck_result.md
│   ├── install_verification.md
│   ├── container_image_audit.md
│   ├── evidence_log.md
│   ├── verification_checklist.md
│   └── screenshots/
│       └── README.md
├── tools/
│   ├── make_token.py
│   └── customize_template.py
└── checker/
    └── check.py
```

## Порядок выполнения

### Перед началом. Работайте в локальном репозитории

Работу нужно выполнять в локальной копии репозитория на своём компьютере. В локальной папке вы заполняете файлы, запускаете проверку, сохраняете изменения через `commit` и отправляете их в GitHub через `push`.

Базовый цикл работы:

```powershell
git status
git add <ИМЕНА_ИЗМЕНЁННЫХ_ФАЙЛОВ>
git commit -m "<ВАШ_TOKEN> краткое описание изменений"
git push
```

После генерации token заменяйте `<ВАШ_TOKEN>` на свой учебный token, например `DAY06-A1B2`. Минимум 7 commit message должны содержать token. Коммиты должны отражать этапы работы, а не создаваться формально в конце.

### Шаг 1. Принять задание

1. Откройте ссылку GitHub Classroom, которую дал преподаватель.
2. Примите задание.
3. Дождитесь создания личного репозитория.
4. Откройте созданный репозиторий.

Имя student repo должно начинаться с:

```text
ib-up-os-day06-
```

### Шаг 2. Клонировать репозиторий

```powershell
git clone <URL_ВАШЕГО_РЕПОЗИТОРИЯ>
cd <ИМЯ_ПАПКИ_РЕПОЗИТОРИЯ>
```

### Шаг 3. Сгенерировать token

```powershell
python tools/make_token.py <ваш_github_login>
```

Пример:

```powershell
python tools/make_token.py student-login
```

Скопируйте token в:

- `student/submission.yaml`;
- `student/reflection.md`;
- подписи к скриншотам;
- сообщения коммитов.

Первый commit:

```powershell
git add student/submission.yaml student/reflection.md
git commit -m "<ВАШ_TOKEN> fill submission and token"
git push
```

### Шаг 4. Заполнить служебные файлы

Заполните:

- [`student/submission.yaml`](./student/submission.yaml)
- [`student/reflection.md`](./student/reflection.md)

В `reflection.md` обязательно укажите:

- что именно оказалось сложным в этом дне;
- насколько удобен формат Red Hat Academy + GitHub-отчёт;
- где вы потратили больше всего времени;
- что нужно повторить после дня 6.

### Шаг 5. Изучить материалы глав 16-17

Откройте:

- [`materials/module_guide.md`](./materials/module_guide.md)
- [`materials/chapter_16_installing_red_hat_enterprise_linux_ru.md`](./materials/chapter_16_installing_red_hat_enterprise_linux_ru.md)
- [`materials/chapter_17_managing_containers_with_podman_ru.md`](./materials/chapter_17_managing_containers_with_podman_ru.md)

Это не краткий конспект, а развёрнутый перевод учебного материала. Читайте его параллельно с курсом Red Hat Academy.

После изучения заполните:

- [`artifacts/concepts_table.md`](./artifacts/concepts_table.md)

Таблица должна содержать минимум 14 заполненных строк. В каждой строке нужно дать объяснение своими словами и привести команду, пример или ситуацию применения.

Второй commit:

```powershell
git add materials artifacts/concepts_table.md
git commit -m "<ВАШ_TOKEN> add chapter notes and concepts"
git push
```

### Шаг 6. Guided Exercise: интерактивная установка RHEL

Выполните в виртуальной лаборатории Red Hat Academy:

- `Guided Exercise: Install Red Hat Enterprise Linux Interactively`

Обязательно зафиксируйте:

- запуск `lab start installing-install`;
- ключевые шаги в `Anaconda`;
- просмотр логов через `tmux` во время установки;
- итоговые проверки `id`, `sudo id`, `lsblk`, `ip addr show ens3`, `hostname`, `cat /etc/resolv.conf`.

По этому упражнению заполните:

- [`artifacts/guided_exercises_log.md`](./artifacts/guided_exercises_log.md);
- [`artifacts/practice_notes.md`](./artifacts/practice_notes.md);
- [`artifacts/install_verification.md`](./artifacts/install_verification.md).

Третий commit:

```powershell
git add artifacts/guided_exercises_log.md artifacts/practice_notes.md artifacts/install_verification.md
git commit -m "<ВАШ_TOKEN> log interactive install"
git push
```

### Шаг 7. Guided Exercise: установка через Kickstart

Выполните:

- `Guided Exercise: Automate Red Hat Enterprise Linux Installation with Kickstart`

Обязательно зафиксируйте:

- редактирование Kickstart-файла;
- команды `ksvalidator` и публикацию файла через HTTP;
- запуск установки с параметром `inst.ks=http://servera.lab.example.com/kickstart.cfg`;
- итоговые проверки `nmcli con show ens3`, `hostnamectl`, `lsblk`, `apropos fstab`.

Если что-то не прошло с первого раза, это нужно явно описать, а не скрывать.

Продолжайте заполнять:

- [`artifacts/guided_exercises_log.md`](./artifacts/guided_exercises_log.md);
- [`artifacts/practice_notes.md`](./artifacts/practice_notes.md);
- [`artifacts/install_verification.md`](./artifacts/install_verification.md).

Четвёртый commit:

```powershell
git add artifacts/guided_exercises_log.md artifacts/practice_notes.md artifacts/install_verification.md
git commit -m "<ВАШ_TOKEN> add kickstart verification"
git push
```

### Шаг 8. Guided Exercises: запуск контейнеров и работа с образами

Выполните:

- `Guided Exercise: Run Containers with Podman`
- `Guided Exercise: Create and Manage Container Images`

Обязательно зафиксируйте:

- `podman login`;
- `podman run`, `podman ps`, `podman rm`;
- запуск `my_webserver` и `curl 127.0.0.1:8080`;
- `podman build`, `podman images`;
- работу с `my_image:1.0` и `my_image:1.1`;
- `podman image push`, `podman search --list-tags`, `podman image inspect`.

Заполните:

- [`artifacts/guided_exercises_log.md`](./artifacts/guided_exercises_log.md);
- [`artifacts/practice_notes.md`](./artifacts/practice_notes.md);
- [`artifacts/container_image_audit.md`](./artifacts/container_image_audit.md).

Пятый commit:

```powershell
git add artifacts/guided_exercises_log.md artifacts/practice_notes.md artifacts/container_image_audit.md
git commit -m "<ВАШ_TOKEN> add podman guided exercises"
git push
```

### Шаг 9. Lab: Manage Containers with Podman

Выполните:

- `Lab: Manage Containers with Podman`

После выполнения:

1. Запустите встроенную проверку `lab grade containers-review`.
2. Если есть ошибки, зафиксируйте первую неуспешную проверку.
3. Исправьте конфигурацию.
4. Повторите проверку до успешного результата.
5. Заполните [`artifacts/lab_autocheck_result.md`](./artifacts/lab_autocheck_result.md).

Если первая проверка не прошла, обязательно укажите:

- что именно не было засчитано;
- как вы диагностировали проблему;
- что исправили;
- какой результат получили после исправления.

Шестой commit:

```powershell
git add artifacts/lab_autocheck_result.md artifacts/practice_notes.md artifacts/container_image_audit.md
git commit -m "<ВАШ_TOKEN> add lab grade and fixes"
git push
```

### Шаг 10. Собрать доказательства и скриншоты

Заполните:

- [`artifacts/evidence_log.md`](./artifacts/evidence_log.md);
- [`artifacts/screenshots/README.md`](./artifacts/screenshots/README.md);
- [`artifacts/verification_checklist.md`](./artifacts/verification_checklist.md).

Добавьте минимум 10 скриншотов в папку:

```text
artifacts/screenshots/
```

Обязательные скриншоты:

1. `interactive-install-summary-or-console.png`
2. `interactive-install-verification.png`
3. `kickstart-ksvalidator.png`
4. `kickstart-install-verification.png`
5. `podman-hello-run.png`
6. `podman-webserver-detached.png`
7. `podman-image-build-tags.png`
8. `podman-inspect-or-push.png`
9. `containers-review-grade.png`
10. `local-checker-and-report.png`

Перед созданием каждого скриншота выведите в терминал свой token, например:

```bash
echo DAY06-XXXX
```

Это не заменяет проверку содержимого, но сильно облегчает ручную верификацию, что скриншот относится именно к вашей работе.

Скриншоты должны быть вставлены прямо в `artifacts/screenshots/README.md`. Отдельно лежащие файлы без встраивания в Markdown не засчитываются.

Седьмой commit:

```powershell
git add artifacts/evidence_log.md artifacts/screenshots artifacts/verification_checklist.md
git commit -m "<ВАШ_TOKEN> add screenshots and evidence"
git push
```

### Шаг 11. Заполнить итоговый отчёт

Заполните:

- [`report.md`](./report.md)

В отчёте обязательно должны быть отражены:

- интерактивная установка RHEL;
- роль `Anaconda` и то, что вы настраивали вручную;
- смысл `Kickstart` и что именно вы меняли в файле;
- работа `Podman`, `Containerfile` и образов `my_image:1.0` / `my_image:1.1`;
- результаты `lab grade containers-review`;
- ваши собственные выводы по теме.

Формальный короткий ответ не засчитывается. В отчёте должны быть термины и действия по теме раздела, а не общие фразы.

Восьмой commit:

```powershell
git add report.md
git commit -m "<ВАШ_TOKEN> finish report"
git push
```

### Шаг 12. Запустить локальную проверку

Установите зависимость:

```powershell
pip install pyyaml
```

Запустите checker:

```powershell
python checker/check.py
```

Если всё выполнено:

```text
OK: 70/70
```

Если есть замечания:

```text
FAIL: X/70
1. ...
2. ...
```

Исправьте замечания, снова запустите проверку, затем сделайте итоговый commit:

```powershell
git add .
git commit -m "<ВАШ_TOKEN> complete task"
git push
```

## Почему это задание нельзя нормально закрыть одним фальшивым отчётом

Техническая проверка и ручная проверка вместе смотрят на следующее:

- минимум 8 коммитов в истории;
- минимум 7 commit message с token;
- наличие изменений всех ключевых файлов именно в истории коммитов;
- наличие 10 точных скриншотов с корректными путями;
- наличие code block с реальными командами и фрагментами вывода;
- наличие отдельных файлов проверки по установке и по контейнерам;
- наличие специальных терминов и команд, привязанных к теме;
- AI-проверку скриншотов и анти-повтор между работами.

Это не делает списывание невозможным, но существенно повышает цену фальшивой сдачи по сравнению с реальным выполнением упражнений.

## Что будет проверяться

Автопроверка оценивает:

- корректность `student/submission.yaml`;
- корректность token;
- полноту `reflection.md`;
- заполнение ключевых разделов `report.md`;
- заполнение таблиц и журналов в `artifacts/`;
- наличие чеклиста;
- наличие встроенных изображений и подписей;
- отсутствие битых ссылок на скриншоты;
- минимальное количество коммитов;
- наличие token в commit history;
- наличие обязательных файлов и этапов в истории коммитов;
- наличие обязательных терминов, команд и структурированных фрагментов вывода в артефактах.

AI и преподаватель дополнительно оценивают:

- содержательность ответов;
- непротиворечивость доказательств;
- соответствие отчёта реальным действиям;
- признаки одинаковых или сгенерированных без понимания ответов.

## Минимальный набор того, что должно быть в сдаче

1. Заполненный `submission.yaml`.
2. Заполненный `reflection.md` с token.
3. Полный `report.md`.
4. `concepts_table.md` минимум на 14 строк.
5. `guided_exercises_log.md` минимум на 5 строк.
6. `practice_notes.md` с реальными code block.
7. `lab_autocheck_result.md` с первой и финальной проверкой.
8. `install_verification.md`.
9. `container_image_audit.md`.
10. `evidence_log.md`.
11. Скриншоты, встроенные прямо в `artifacts/screenshots/README.md`.
12. Не меньше 8 коммитов в истории, из них минимум 7 с token в сообщении коммита.
