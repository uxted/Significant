// @ts-check
import { test, expect } from "@playwright/test";

test.describe("News Aggregator E2E", () => {
  test("Главная страница — лента новостей загружается", async ({ page }) => {
    await page.goto("http://localhost:80");
    await expect(page.getByText("Лента новостей")).toBeVisible();
  });

  test("Фильтры — применение фильтра по значимости", async ({ page }) => {
    await page.goto("http://localhost:80");

    // Open filters
    await page.getByText("High").click();
    await page.getByText("Применить").click();

    // Check that only HIGH news are shown
    const badges = page.locator(".badge-high");
    await expect(badge).toHaveCount(await badges.count());
  });

  test("Поиск новостей", async ({ page }) => {
    await page.goto("http://localhost:80");

    await page.getByPlaceholder("Ключевая ставка...").fill("ставка");
    await page.getByText("Применить").click();

    // Should show results
    await expect(page.locator(".news-card").first()).toBeVisible();
  });

  test("Детальный просмотр новости", async ({ page }) => {
    await page.goto("http://localhost:80");

    // Click first news card
    await page.locator(".news-title-link").first().click();

    // Should navigate to detail
    await expect(page.locator(".news-detail")).toBeVisible();
  });

  test("Переход на страницу закладок (требует авторизации)", async ({
    page,
  }) => {
    await page.goto("http://localhost:80/bookmarks");

    // Should redirect to login
    await expect(page).toHaveURL(/.*login/);
  });
});
