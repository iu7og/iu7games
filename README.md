# IU7Games

## О проекте
Соревновательная система для оттачивания навыков программирования, созданная для студентов кафедры ИУ7 МГТУ им. Н.Э. Баумана, проходящих курс **"Программирование на Си"**.

<!-- ## Как начать играть 

В своём ученическом репозитории создать ветку `<gamename>`, 
где `<gamename>` может быть:
*   `NUM63RSgame`  
*   `7EQUEENCEgame`
*   `XOgame`
*   `STRgame`
*   `TEEN48game`
*   `TR4V31game`
*   `T3TR15game`
*   `R3463NTgame`
*   `W00DCUTT3Rgame`

В этой ветке изменить файл `.gitlab-ci.yml` в соответствии с приведенным ниже:
```yaml
image: hackfeed/iu7games
build:
  script:
    - $CI_COMMIT_REF_NAME
  after_script:
    - rm -f *.o
  coverage: '/lines[\.]+\: (\d+\.\d+)\%/'
  artifacts:
    paths:
      - ./*.so
      - ./*game/*_codecoverage
```

После изменения `.gitlab-ci.yml`, ознакомиться с правилами игры:

*   [**Инструкция для практикантов, весна 2020**](https://git.iu7.bmstu.ru/IU7-Projects/iu7games/wikis/STAIU7HOME)
*   [Правила **NUM63RSgame**](https://git.iu7.bmstu.ru/IU7-Projects/iu7games/wikis/NUM63RSgame-Greeting#показания-к-выполнению-задания)
*   [Правила **7EQUEENCEgame**](https://git.iu7.bmstu.ru/IU7-Projects/iu7games/wikis/7EQUEENCEgame-Greeting#показания-к-выполнению-задания)
*   [Правила **XOgame**](https://git.iu7.bmstu.ru/IU7-Projects/iu7games/wikis/XOgame-Greeting#показания-к-выполнению-задания)
*   [Правила **STRgame**](https://git.iu7.bmstu.ru/IU7-Projects/iu7games/wikis/STRgame-Greeting#показания-к-выполнению-задания)
*   [Правила **TEEN48game**](https://git.iu7.bmstu.ru/IU7-Projects/iu7games/wikis/TEEN48game-Greeting#показания-к-выполнению-задания)
*   [Правила **TR4V31game**](https://git.iu7.bmstu.ru/IU7-Projects/iu7games/-/wikis/TR4V31game-Greeting#показания-к-выполнению-задания)
*   [Правила **T3TR15game**](https://git.iu7.bmstu.ru/IU7-Projects/iu7games/-/wikis/T3TR15game-Greeting)
*   [Правила **R3463NTgame**](https://git.iu7.bmstu.ru/IU7-Projects/iu7games/-/wikis/R3463NTgame-Greeting)
*   [Правила **W00DCUTT3Rgame**](https://git.iu7.bmstu.ru/IU7-Projects/iu7games/-/wikis/W00DCUTT3Rgame-Greeting)

Вы восхитительны! Можно начинать соревноваться!

## Результаты

*   [**NUM63RSgame**](https://git.iu7.bmstu.ru/IU7-Projects/iu7games/-/wikis/NUM63RSgame-Leaderboard)
*   [**NUM63RSgame Practice 2020**](https://git.iu7.bmstu.ru/IU7-Projects/iu7games/-/wikis/NUM63RSgame_practice-Leaderboard)
*   [**7EQUEENCEgame**](https://git.iu7.bmstu.ru/IU7-Projects/iu7games/-/wikis/7EQUEENCEgame-Leaderboard)
*   [**7EQUEENCEgame Practice 2020**](https://git.iu7.bmstu.ru/IU7-Projects/iu7games/-/wikis/7EQUEENCEgame_practice-Leaderboard)
*   [**XOgame**](https://git.iu7.bmstu.ru/IU7-Projects/iu7games/-/wikis/XOgame-Leaderboard)
*   [**XOgame Practice 2020**](https://git.iu7.bmstu.ru/IU7-Projects/iu7games/-/wikis/XOgame_practice-Leaderboard)
*   [**STRgame**](https://git.iu7.bmstu.ru/IU7-Projects/iu7games/-/wikis/STRgame-Leaderboard)
*   [**STRgame Practice 2020**](https://git.iu7.bmstu.ru/IU7-Projects/iu7games/-/wikis/STRgame_practice-Leaderboard)
*   [**TEEN48game**](https://git.iu7.bmstu.ru/IU7-Projects/iu7games/-/wikis/TEEN48game-Leaderboard)
*   [**TEEN48game Practice 2020**](https://git.iu7.bmstu.ru/IU7-Projects/iu7games/-/wikis/TEEN48game_practice-Leaderboard)
*   [**TR4V31game**](https://git.iu7.bmstu.ru/IU7-Projects/iu7games/-/wikis/TR4V31game-Leaderboard)
*   [**T3TR15game**](https://git.iu7.bmstu.ru/IU7-Projects/iu7games/-/wikis/T3TR15game-Leaderboard)
*   [**R3463NTgame**](https://git.iu7.bmstu.ru/IU7-Projects/iu7games/-/wikis/R3463NTgame-Leaderboard)
*   [**W00DCUTT3Rgame**](https://git.iu7.bmstu.ru/IU7-Projects/iu7games/-/wikis/W00DCUTT3Rgame-Leaderboard)

## Changelog

## 2.4.0 (22.12.2020)
* Открытая девятая игра **W00DCUTT3Rgame**.

## 2.3.0 (05.12.2020)
* Открытая восьмая игра **R3463NTgame**.

## 2.2.0 (28.10.2020)
* Открытая седьмая игра **T3TR15game**.

## 2.1.0 (24.09.2020) 
* Открытая шестая игра **TRAVELgame**.

### 2.0.0 (04.05.2020)
*   Открыта пятая игра **TEEN48game**. Запуск **#STAIU7HOME Spring Algorithm Practice**

### 1.3.0 (27.04.2020)
*   Открыта четвертая игра **STRgame**

### 1.2.0 (28.03.2020)
*   Открыта третья игра **XOgame**

### 1.1.0 (07.03.2020)
*   Открыта вторая игра **7EQUEENCEgame**

### 1.0.2 (04.03.2020)
*   Изменен интервал для NUM63RSgame для уменьшения вероятности зависания деплоя

### 1.0.1 (27.02.2020)
*   Исправлено отображение изменения позиции в лидербордах

### 1.0.0 (22.02.2020)
*   Открыта первая игра **NUM63RSgame** -->
