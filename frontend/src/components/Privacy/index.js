import React from "react";

export default function Privacy() {
  const sections = [
    {
      title: "1. Общие положения",
      content:
        "Настоящая политика конфиденциальности описывает, как система «Агрегатор экономически значимых новостей» собирает, хранит и обрабатывает персональные данные пользователей.",
    },
    {
      title: "2. Какие данные мы собираем",
      items: [
        "Адрес электронной почты (email)",
        "Хеш пароля (хранится в зашифрованном виде)",
        "Подписки на категории и компании (предпочтения)",
        "Закладки новостей (поведенческие данные)",
      ],
      note: "Мы не собираем: ФИО, номер телефона, адрес, данные паспорта или иные чувствительные персональные данные.",
    },
    {
      title: "3. Цели обработки данных",
      items: [
        "Аутентификация и авторизация пользователя",
        "Персонализация ленты новостей",
        "Сохранение закладок",
        "Улучшение качества классификации новостей",
      ],
    },
    {
      title: "4. Защита данных",
      content:
        "Пароли хранятся в хешированном виде с использованием алгоритма PBKDF2. Доступ к API осуществляется через JWT-токены с коротким временем жизни (15 минут).",
    },
    {
      title: "5. Права пользователя",
      items: [
        "Право на доступ к своим данным",
        "Право на удаление аккаунта (анонимизация данных)",
        "Право на отзыв согласия на обработку данных",
      ],
    },
    {
      title: "6. Хранение данных",
      content:
        "Данные хранятся локально в базе данных PostgreSQL. Система не передаёт данные третьим лицам.",
    },
  ];

  return (
    <div className="mx-auto max-w-3xl space-y-8">
      <h2 className="text-3xl font-bold tracking-tight">Политика конфиденциальности</h2>
      {sections.map((section, i) => (
        <div key={i} className="rounded-lg border bg-card p-6 shadow-sm space-y-3">
          <h3 className="text-lg font-semibold">{section.title}</h3>
          {section.content && <p className="text-sm text-muted-foreground">{section.content}</p>}
          {section.items && (
            <ul className="list-disc pl-6 space-y-1 text-sm text-muted-foreground">
              {section.items.map((item, j) => (
                <li key={j}>{item}</li>
              ))}
            </ul>
          )}
          {section.note && (
            <p className="text-sm text-muted-foreground italic">{section.note}</p>
          )}
        </div>
      ))}
    </div>
  );
}
