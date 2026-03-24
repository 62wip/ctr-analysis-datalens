#import "@preview/gantty:0.5.1" as gantty

#import gantty: (
  gantt,
  sidebar.default-sidebar-drawer,
  field.default-field-drawer,
  milestones.default-milestones-drawer,
  dividers.default-dividers-drawer,
  task.default-tasks-drawer,
  dependencies.default-dependencies-drawer,
  dependencies.orthogonal-dependencies-drawer
)

#import gantty.header: (
  default-headers-drawer,
  default-month-header,
  default-week-header,
  create-custom-month-header,
  _default-gridlines
)

#let russian-short-months = (
  "Янв", "Фев", "Мар", "Апр", "Май", "Июн",
  "Июл", "Авг", "Сен", "Окт", "Ноя", "Дек"
)

#let russian-month-header  = (
  name: "russian-month",
  function: create-custom-month-header(
    (date) => {
      let month-name = russian-short-months.at(date.month() - 1)
      align(center + horizon, strong(month-name))
    },
    "russian-month",
    gridlines-style: (stroke: gray + 0.5pt),
  )
)

#let drawer = (
  sidebar: gantty.sidebar.default-sidebar-drawer.with(
    formatters: (
      (task => align(left, text(16pt, weight: "bold", task.name))),
      (task => align(center, text(14pt, weight: "regular", task.name))),
    ),
    dividers: (
      (stroke: black + 1pt),
      (stroke: gray + 0.5pt),
    ),
    max-width: auto,
  ),
  field: default-field-drawer,
  headers: default-headers-drawer.with(
    headers: (
      russian-month-header,
      // default-month-header(
      //   gridlines-style: (stroke: gray + 0.5pt)
      // ),
    )
  ),
  dividers: default-dividers-drawer,
  tasks: default-tasks-drawer.with(
    styles: (
      (uncompleted: (style: (fill: blue), width: 20pt)),
      (uncompleted: (style: (fill: green), width: 12pt))
    )
  ),
  dependencies: orthogonal-dependencies-drawer.with(
    buldge: 15pt,
    style: (
      stroke: rgb("#000000d0") + 0.75pt,
      mark: (end: "straight"),
    ),
  ),
  // dependencies: default-dependencies-drawer.with(
  //   curviness: 50%,
  //   absolute-curviness: 35pt,
  //   style: (
  //     stroke: rgb("#0000008c") + 0.75pt,
  //     mark: (end: "barbed"),
  //   ),
  // ),
  milestones: default-milestones-drawer.with(
    milestone-content: (milestone) => {
      let months = ("января", "февраля", "марта", "апреля", "мая", "июня",
                   "июля", "августа", "сентября", "октября", "ноября", "декабря")
      
      let day = milestone.date.day()
      let month-name = months.at(milestone.date.month() - 1)
      let year = milestone.date.year()
      let date-str = str(day) + " " + month-name + " " + str(year)
      
      align(center + horizon, [
        #text(14pt, weight: "bold", smallcaps(milestone.name))
        #text(12pt, "\n" + date-str)
      ])
    },
    today-content: none
  )
)


#set page(flipped: true)

#figure(
  gantt(
    yaml("gantt_work_plain.yaml"),
    drawer: drawer
  ),
  caption: "Диаграмма Ганта выполнения курсовой работы"
) <fig:gantt_work_plan>

#set page(flipped: false)