#set document(
  title: "Анализ и визуализация данных с использованием Yandex DataLens: исследование по прогнозированию CTR",
  author: "Грицан Максим Андреевич",
  date: datetime(year: 2025, month: 1, day: 1),
)

// Настройки страницы (ГОСТ)
#set page(
  paper: "a4",
  margin: (left: 3cm, right: 1.5cm, top: 2cm, bottom: 2cm),
  numbering: "1",
  number-align: center,
)

// Настройки текста
#set text(
  font: "New Computer Modern",
  size: 14pt,
  lang: "ru",
)

// Межстрочный интервал 1.5
#set par(
  leading: 0.65em,
  first-line-indent: 1.25cm,
  justify: true,
)

// Настройки заголовков
#set heading(numbering: "1.1")

// Настройки списков
#set enum(numbering: "1.1.")

// Настройка маркеров для маркированных списков
#set list(marker: ([•], [--]))

// Увеличиваем расстояние между номером и названием раздела
#show heading: it => {
  if it.numbering != none {
    let number = if it.numbering != none {
      counter(heading).display(it.numbering)
      h(1em)
    }
    number
    it.body
  } else {
    it
  }
}

#show heading.where(level: 1): it => {
  set text(size: 16pt, weight: "bold")
  set block(above: 1.5em, below: 1em)
  set par(first-line-indent: 0pt)
  it
}

#show heading.where(level: 2): it => {
  set text(size: 14pt, weight: "bold")
  set block(above: 1.2em, below: 0.8em)
  set par(first-line-indent: 0pt)
  it
}

// Настройки для рисунков и таблиц
#show figure.where(kind: image): set figure(supplement: [Рисунок])
#show figure.where(kind: table): set figure(supplement: [Таблица])

// Нумерация рисунков и таблиц по секциям
#set figure(numbering: num => {
  let h = counter(heading).get().first()
  let c = num
  numbering("1.1", h, c)
})

#show figure: it => {
  set align(center)
  it
}

// Настройки для кода
#show raw.where(block: true): it => {
  set block(
    fill: rgb("#fafafa"),
    stroke: 0.5pt + rgb("#e0e0e0"),
    inset: 8pt,
    radius: 4pt,
    width: 100%,
  )
  set text(size: 10pt, font: "New Computer Modern Mono")
  it
}

// Настройки ссылок
#show link: set text(fill: blue)

// Настройка формата ссылок на таблицы и рисунки (только номер)
#show ref: it => {
  let el = it.element
  if el != none and el.func() == figure {
    // Получаем номер секции и номер внутри секции
    let loc = el.location()
    let section = counter(heading).at(loc).first()
    let fig_counter = counter(figure.where(kind: el.kind)).at(loc).last()

    // Возвращаем только номер в формате "секция.номер"
    link(loc, [#section.#fig_counter])
  } else {
    it
  }
}

// =============================================================
#include "title.typ"
#pagebreak()
#counter(page).update(1)

#include "annotation.typ"
#pagebreak()

#set page(numbering: "1")

#show outline.entry.where(level: 1): it => {
  v(1em, weak: true)
  strong(it)
}

#outline(
  title: [Содержание],
  indent: auto,
)
#pagebreak()

#include "glossary.typ"
#pagebreak()

#include "introduction.typ"
#pagebreak()

#include "dataset_description.typ"
#pagebreak()

#include "lit_overview.typ"
#pagebreak()

#include "dashboard_layout.typ"
#pagebreak()

#include "catboost_learning.typ"
#pagebreak()

#include "data_preporation_and_loading.typ"
#pagebreak()

// #include "conclusion.typ"
// #pagebreak()

#bibliography("bibliography.bib", title: "Список литературы", style: "gost-r-705-2008-numeric")
