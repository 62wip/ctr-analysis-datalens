// = Название первой главы

// Пример ссылки на Рисунок @fig:choosen_words_graph и на Таблицу @tab:table1 и на Листинг @lst:listing1.

// == Пример вставки и оформления рисунка

// Текст

// #figure(
//   image("images/select_sentences/choosen_words.png", width: 50%),
//   caption: [График распределения сложности выбранных слов],
// ) <fig:choosen_words_graph>

// == Пример вставки и оформления кода

// Пример того как ссылаться на Листинг @lst:listing1.

// #figure(
//   ```python
//   def sched_save():
//       schedule.every().hour.do(log_saver)
//       while True:
//           schedule.run_pending()
//           time.sleep(1)
//   ```,
//   caption: [Использование schedule в коде],
// ) <lst:listing1>

// == Пример вставки и оформления таблицы

// Пример того как ссылаться на Таблицу @tab:table1 по тексту.

// #figure(
//   table(
//     columns: 3,
//     align: (left, center, right),
//     [*Value 1*], [*Value 2*], [*Value 3*],
//     [$alpha$], [$beta$], [$gamma$],
//     [1], [1110.1], [a],
//     [2], [10.1], [b],
//     [3], [23.113231], [c],
//   ),
//   caption: [Your first table.],
// ) <tab:table1>
