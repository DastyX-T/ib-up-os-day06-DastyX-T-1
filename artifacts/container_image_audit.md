# Аудит контейнеров и образов

## Запуск готовых контейнеров

Работа начиналась с авторизации в локальном registry, потому что учебные образы находятся в `registry.lab.example.com:5000`. Podman запускает контейнеры без отдельного Docker daemon и может работать от имени обычного пользователя `student`.

```bash
[student@workstation ~]$ podman login registry.lab.example.com:5000
Username: student
Password:
Login Succeeded!
```

Одноразовый контейнер был запущен с командой `echo`. После завершения его можно увидеть через `podman ps -a`, потому что обычный `podman ps` показывает только запущенные контейнеры.

```bash
[student@workstation ~]$ podman run registry.lab.example.com:5000/ubi10/ubi echo "Hello Red Hat!"
Hello Red Hat!
[student@workstation ~]$ podman ps -a
CONTAINER ID  IMAGE                                    COMMAND               STATUS
7a8d4f2b9d91  registry.lab.example.com:5000/ubi10/ubi  echo Hello Red Hat!   Exited (0)
```

Веб-сервер запускался как detached container с именем `my_webserver`. Порт 8080 внутри контейнера пробрасывался на порт 8080 хоста, после чего доступность проверялась через `curl 127.0.0.1:8080`.

```bash
[student@workstation ~]$ podman run -d --name my_webserver -p 8080:8080 registry.lab.example.com:5000/rhel10/httpd-24
f9dc4ce31299c4c53c57c66a2e5f5c33a4bb85be85f2348d0c11646a4dcaa001
[student@workstation ~]$ podman ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
NAMES         STATUS        PORTS
my_webserver  Up 8 seconds  0.0.0.0:8080->8080/tcp
[student@workstation ~]$ curl 127.0.0.1:8080
Hello from the Apache HTTP Server container
```

## Создание образов из Containerfile

Для сборки собственного образа использовался `Containerfile`. Он фиксирует базовый образ и команду запуска, поэтому сборка становится воспроизводимой. Версия `my_image:1.0` собиралась на базе `ubi8/ubi`, а версия `my_image:1.1` на базе `ubi10/ubi`.

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
[student@workstation my_image]$ cat Containerfile
FROM registry.lab.example.com:5000/ubi10/ubi
CMD echo "This container uses the ubi10/ubi image"
[student@workstation my_image]$ podman build -t my_image:1.1 .
STEP 1/2: FROM registry.lab.example.com:5000/ubi10/ubi
STEP 2/2: CMD echo "This container uses the ubi10/ubi image"
COMMIT my_image:1.1
Successfully tagged localhost/my_image:1.1
```

## Публикация и проверка тегов

После сборки оба образа были опубликованы в учебный registry. Теги `1.0` и `1.1` нужны, чтобы различать версии одного приложения или окружения. Проверка `podman search --list-tags` показывает, что registry видит обе версии.

```bash
[student@workstation ~]$ podman image push localhost/my_image:1.0 registry.lab.example.com:5000/my_image:1.0
Writing manifest to image destination
[student@workstation ~]$ podman image push localhost/my_image:1.1 registry.lab.example.com:5000/my_image:1.1
Writing manifest to image destination
```

```bash
[student@workstation ~]$ podman search --list-tags registry.lab.example.com:5000/my_image
NAME                                    TAG
registry.lab.example.com:5000/my_image  1.0
registry.lab.example.com:5000/my_image  1.1
```

## Анализ inspect и сравнение версий

Команда `podman image inspect` выводит JSON-описание образа: ID, слои, архитектуру, переменные окружения, команду запуска и другую техническую информацию. В этой работе inspect использовался для проверки различий между версиями `my_image:1.0` и `my_image:1.1`.

```bash
[student@workstation ~]$ podman image inspect my_image:1.0 --format '{{.Id}} {{.Config.Cmd}}'
46d8e7be33ab [echo This container uses the ubi8/ubi image]
[student@workstation ~]$ podman image inspect my_image:1.1 --format '{{.Id}} {{.Config.Cmd}}'
9fd18bb27140 [echo This container uses the ubi10/ubi image]
```

```bash
[student@workstation ~]$ podman images localhost/my_image
REPOSITORY          TAG         IMAGE ID      CREATED         SIZE
localhost/my_image  1.1         9fd18bb27140  1 minute ago    231 MB
localhost/my_image  1.0         46d8e7be33ab  7 minutes ago   214 MB
```

Вывод подтверждает, что разные версии имеют разные Image ID и разные команды запуска. `This container uses the ubi8/ubi image` относится к версии `1.0`, а `This container uses the ubi10/ubi image` относится к версии `1.1`. Это показывает практическую пользу тегов: можно хранить несколько вариантов образа и точно понимать, какой вариант запускается.

