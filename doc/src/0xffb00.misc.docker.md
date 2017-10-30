## Docker

### unix:///var/run/docker.sock permission issue

```
# require log out and login back in after command executed to take effect

$ sudo usermod -a -G docker $USER
```

### remove dangling image `<none>:<none>`

```
$ docker rmi -f $(docker images -f "dangling=true" -q)
```