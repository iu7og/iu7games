# IU7Games

[![Codacy Badge](https://api.codacy.com/project/badge/Grade/7847b7ccad584ba3bb5c6648ba38f48d)](https://app.codacy.com/gh/IU7OG-Team/iu7games?utm_source=github.com&utm_medium=referral&utm_content=IU7OG-Team/iu7games&utm_campaign=Badge_Grade_Dashboard)

## О проекте
Соревновательная система для оттачивания навыков программирования, созданная для студентов кафедры ИУ7 МГТУ им. Н.Э. Баумана, проходящих курс **"Программирование на Си"**.

## Как начать играть 

В своём ученическом репозитории создать ветку `<gamename>`, 
где `<gamename>` может быть:
* `NUM63RSgame`
* `7EQUEENCEgame`
* `XOgame`
* `STRgame`
* `TEEN48game`

В этой ветке изменить файл `.gitlab-ci.yml` в соответствии с приведенным ниже:
```yaml
image: hackfeed/iu7games
build:
  script:
    - $CI_COMMIT_REF_NAME
  after_script:
    - rm -f *.o
  artifacts:
    paths:
      - ./*.so
```

После изменения `.gitlab-ci.yml`, ознакомиться с правилами игры:

* [Правила **NUM63RSgame**](https://git.iu7.bmstu.ru/IU7-Projects/iu7games/wikis/NUM63RSgame-Greeting#показания-к-выполнению-задания)
* [Правила **7EQUEENCEgame**](https://git.iu7.bmstu.ru/IU7-Projects/iu7games/wikis/7EQUEENCEgame-Greeting#показания-к-выполнению-задания)
* [Правила **XOgame**](https://git.iu7.bmstu.ru/IU7-Projects/iu7games/wikis/XOgame-Greeting#показания-к-выполнению-задания)
* [Правила **STRgame**](https://git.iu7.bmstu.ru/IU7-Projects/iu7games/wikis/STRgame-Greeting#показания-к-выполнению-задания)
* [Правила **TEEN48game**](https://git.iu7.bmstu.ru/IU7-Projects/iu7games/wikis/TEEN48game-Greeting#показания-к-выполнению-задания)

Вы восхитительны! Можно начинать соревноваться!

## Результаты

* [**NUM63RSgame**](NUM63RSgame-Leaderboard)
* [**7EQUEENCEgame**](7EQUEENCEgame-Leaderboard)
* [**XOgame**](XOgame-Leaderboard)
* [**STRgame**](STRgame-Leaderboard)
* [**TEEN48game**](TEEN48game-Leaderboard)

## Changelog

В ожидании релиза :)
